from dotenv import dotenv_values
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.helpers import escape_markdown
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackQueryHandler,
)
import re

from database import get_session

from utils.formatting import par_score_format

from models.course.crud import (
    read_courses,
    create_course,
    read_course,
    update_course,
)
from models.course.model import CourseUpdate

from models.track.crud import (
    upsert_track,
    read_tracks_as_text_list,
    delete_track,
)

from models.game.crud import read_games, create_game

from models.game_session.crud import read_game_session_user

from models.score.crud import read_course_user_top_scores

secrets = dotenv_values(".env")

from .helpers import handler_helper

log_level = logging.INFO if secrets.get("DEV_MODE", False) else logging.WARNING
logging.getLogger("httpx").setLevel(log_level)
logging.getLogger("httpcore").setLevel(log_level)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

(
    CHOOSE_COURSE_ACTION_ROUTE,
    ADD_COURSE_LOCATION,
    EDIT_COURSE_ROUTE,
    ADD_COURSE_ROUTE,
    ADD_GAME_ROUTE,
    ADD_TRACKS,
) = range(6)


@handler_helper(force_inline=True, remove_keyboard=True)
async def add_game_name(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton(f"Cancel", callback_data=f"start")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    prompt_message = await update.callback_query.edit_message_text(
        text="Write name for new game type", reply_markup=reply_markup
    )
    context.user_data["prompt_message_id"] = prompt_message.message_id
    return ADD_GAME_ROUTE


async def add_game_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    game_name = update.message.text

    prompt_id = context.user_data.get("prompt_message_id")
    await context.bot.edit_message_reply_markup(
        chat_id=update.effective_chat.id, message_id=prompt_id, reply_markup=None
    )

    if len(game_name) < 128 and len(game_name) > 0:
        with get_session() as s:
            create_game(s, game_name)
        await update.message.reply_text(text=f"Game type {game_name} added!")
    else:
        keyboard = [
            [InlineKeyboardButton(f"Cancel", callback_data=f"cancel")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        prompt_message = await update.message.reply_text(
            "Game name should be between 1 and 128 characters",
            reply_markup=reply_markup,
        )
        context.user_data["prompt_message_id"] = prompt_message.message_id
        return ADD_GAME_ROUTE
    if context.user_data.get("is_inline"):
        del context.user_data["is_inline"]
    if context.user_data.get("prompt_message_id"):
        del context.user_data["prompt_message_id"]
    return ConversationHandler.END


@handler_helper(remove_keyboard=True)
async def start_edit_courses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with get_session() as s:
        games = read_games(s)
    keyboard = [
        [InlineKeyboardButton(f"Add new game", callback_data=f"select_game:")],
        [
            InlineKeyboardButton(f"{game.name}", callback_data=f"select_game:{game.id}")
            for game in games
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    prompt_message = await update.effective_chat.send_message(
        text="Select game to edit or add new", reply_markup=reply_markup
    )
    context.user_data["is_inline"] = True
    context.user_data["prompt_message_id"] = prompt_message.message_id
    return CHOOSE_COURSE_ACTION_ROUTE


@handler_helper(force_inline=True, callback_param_validator=int)
async def present_add_edit_course(
    update: Update, context: ContextTypes.DEFAULT_TYPE, cb_param: int
):
    game_id = cb_param
    if context.user_data.get("editing_course"):
        del context.user_data["editing_course"]
    with get_session() as s:
        courses = read_courses(s, game_id)

    courses = [courses[i : i + 3] for i in range(0, len(courses), 3)]
    keyboard_course_select = [
        [
            InlineKeyboardButton(
                f"{course.name}", callback_data=f"edit_course:{course.id}"
            )
            for course in course_group
        ]
        for course_group in courses
    ]
    keyboard = [
        [
            InlineKeyboardButton(
                f"Create new course", callback_data=f"create_course:{game_id}"
            )
        ],
    ]
    context.user_data["selected_game"] = game_id
    keyboard += keyboard_course_select
    reply_markup = InlineKeyboardMarkup(keyboard)

    prompt_message = await update.callback_query.edit_message_text(
        "Choose course to edit or create new", reply_markup=reply_markup
    )
    context.user_data["prompt_message_id"] = prompt_message.message_id

    return CHOOSE_COURSE_ACTION_ROUTE


@handler_helper(force_inline=True, callback_param_validator=int)
async def add_course_name(
    update: Update, context: ContextTypes.DEFAULT_TYPE, cb_param: int
):
    param_id = cb_param
    course = context.user_data.get("editing_course")

    if course:
        callback_data = f"edit_course:{param_id}"
    else:
        context.user_data["selected_game"] = param_id
        callback_data = f"select_game:{param_id}"

    keyboard = [
        [InlineKeyboardButton(f"Back", callback_data=callback_data)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    msg = (
        f'Send new name for course {course.get("name")}:'
        if course and "name" in course
        else "Send name for the new course:"
    )

    prompt_message = await update.callback_query.edit_message_text(
        msg, reply_markup=reply_markup
    )
    context.user_data["prompt_message_id"] = prompt_message.message_id
    context.user_data["is_inline"] = False

    return ADD_COURSE_ROUTE


@handler_helper(force_inline=True, callback_param_validator=int, remove_keyboard=True)
async def edit_course_location(
    update: Update, context: ContextTypes.DEFAULT_TYPE, cb_param: int
):
    course_id = cb_param
    course = context.user_data.get("editing_course")
    keyboard = [
        [InlineKeyboardButton(f"Cancel", callback_data=f"edit_course:{course_id}")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    prompt_message = await update.callback_query.edit_message_text(
        f'Send new course location for {course.get("name")}:',
        reply_markup=reply_markup,
    )
    context.user_data["prompt_message_id"] = prompt_message.message_id
    return ADD_COURSE_LOCATION


@handler_helper(remove_keyboard=True)
async def process_edit_course_location(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    course_location = update.message.text
    course = context.user_data.get("editing_course")

    with get_session() as s:
        update_course(s, course.get("id"), CourseUpdate(location=course_location))
    await update.message.reply_text(
        f"New course location saved!",
    )

    return await start_edit_courses(update, context)


@handler_helper(remove_keyboard=True)
async def process_course_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    course_name = update.message.text

    course = context.user_data.get("editing_course")

    if course:
        callback_data = f'edit_course:{course.get("id")}'
    else:
        game_id = context.user_data.get("selected_game")
        callback_data = f"select_game:{game_id}"

    keyboard = [[InlineKeyboardButton(f"Back", callback_data=callback_data)]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if len(course_name) > 128 or len(course_name) < 1:

        prompt_message = await update.message.reply_text(
            "Course name should be between 1 and 128",
            reply_markup=reply_markup,
        )
        context.user_data["prompt_message_id"] = prompt_message.message_id
        return ADD_COURSE_ROUTE

    if course:
        with get_session() as s:
            update_course(s, course.get("id"), CourseUpdate(name=course_name))
        await update.message.reply_text(
            f"New course name saved!",
        )
        return await start_edit_courses(update, context)
    else:
        context.user_data["course_name"] = course_name
        prompt_message = await update.message.reply_text(
            f"Send location for course {course_name}",
            reply_markup=reply_markup,
        )
        context.user_data["prompt_message_id"] = prompt_message.message_id
        return ADD_COURSE_LOCATION


@handler_helper(force_inline=True, callback_param_validator=int, remove_keyboard=True)
async def course_delete(
    update: Update, context: ContextTypes.DEFAULT_TYPE, cb_param: int
):
    course_id = cb_param

    with get_session() as s:
        pass
        # delete_course(s, course_id)
    await update.effective_chat.send_message("Course deletion not implemented")
    return await start_edit_courses(update, context)


@handler_helper(force_inline=True, callback_param_validator=int)
async def edit_course(
    update: Update, context: ContextTypes.DEFAULT_TYPE, cb_param: int, from_user_id: int
):

    course_id = cb_param
    course_gamesessions = []
    course_session_top_scores = []
    with get_session() as s:
        course = read_course(s, course_id)
        course_gamesessions, _ = read_game_session_user(
            s, user_id=from_user_id, active=None, course_id=course_id
        )
        course_session_top_scores = read_course_user_top_scores(
            s, user_id=from_user_id, course_id=course_id
        )

    keyboard = [
        [
            InlineKeyboardButton(
                f"Edit name", callback_data=f"edit_course_name:{course_id}"
            ),
            InlineKeyboardButton(
                f"Edit location", callback_data=f"edit_course_location:{course_id}"
            ),
            InlineKeyboardButton(
                f"Edit tracks", callback_data=f"edit_tracks:{course_id}"
            ),
            InlineKeyboardButton(
                f"Delete course", callback_data=f"delete_course:{course_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                f"Back", callback_data=f"select_game:{course.game_id}"
            ),
        ],
    ]

    context.user_data["editing_course"] = course.model_dump()

    reply_markup = InlineKeyboardMarkup(keyboard)
    course_info_text = (
        f"Select action for course {course.name}\nLocation: {course.location}"
    )

    if len(course_gamesessions) > 0:
        course_info_text += "\n\Your top 5 total scores:\n"
        games_display = []
        for top_score in course_session_top_scores[0:4]:

            session_data = next(
                (game for game in course_gamesessions if game.id == top_score[0]), None
            )
            games_display.append(
                f"{session_data.started_at_local(None, False).strftime('%Y-%m-%d')} Score: {par_score_format(top_score[1])} id: {session_data.id}",
            )
        course_info_text += "\n".join(games_display)

    prompt_message = await update.callback_query.edit_message_text(
        course_info_text,
        reply_markup=reply_markup,
    )

    context.user_data["prompt_message_id"] = prompt_message.message_id
    return CHOOSE_COURSE_ACTION_ROUTE


@handler_helper(force_inline=True, callback_param_validator=int)
async def edit_tracks(
    update: Update, context: ContextTypes.DEFAULT_TYPE, cb_param: int
):
    course_id = cb_param
    context.user_data["course_id"] = course_id

    with get_session() as s:
        course = read_course(s, course_id)
        track_list = read_tracks_as_text_list(s, course_id)
    track_msg = f"Send tracks for course {course.name}\nIn format <track number> <par>"
    context.user_data["track_msg"] = track_msg
    keyboard = [
        [InlineKeyboardButton(f"Done", callback_data="tracks_save")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    prompt_msg = await update.callback_query.edit_message_text(
        track_msg + track_list,
        reply_markup=reply_markup,
    )
    context.user_data["track_prompt_id"] = prompt_msg.message_id
    context.user_data["is_inline"] = True
    context.user_data["track_last_msg"] = ""

    return ADD_TRACKS


@handler_helper(remove_keyboard=True)
async def process_course_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text
    if len(message_text) > 128 or len(message_text) < 2:
        keyboard = [
            [InlineKeyboardButton(f"Cancel", callback_data="cancel")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        prompt_message = await update.message.reply_text(
            "Course location should be between 1 and 128", reply_markup=reply_markup
        )
        context.user_data["prompt_message_id"] = prompt_message.message_id
        return ADD_COURSE_LOCATION
    if context.user_data.get("editing_course"):
        return await process_edit_course_location(update, context)

    course_name = context.user_data.get("course_name")
    with get_session() as s:
        new_course = create_course(
            s, course_name, message_text, context.user_data.get("selected_game")
        )
        context.user_data["course_id"] = new_course.id
    keyboard = [
        [InlineKeyboardButton(f"Done", callback_data="tracks_save")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    track_msg = f"Send tracks for course {course_name}\nIn format <track number> <par>"
    prompt_msg = await update.message.reply_text(
        track_msg,
        reply_markup=reply_markup,
    )
    context.user_data["track_prompt_id"] = prompt_msg.message_id
    context.user_data["is_inline"] = True

    context.user_data["track_msg"] = track_msg
    return ADD_TRACKS


async def add_tracks(update: Update, context: ContextTypes.DEFAULT_TYPE):

    track_raw = update.message.text

    track_msg_prompt_id = context.user_data.get("track_prompt_id")
    course_id = context.user_data.get("course_id")
    tracks_have_updated = False

    if track_raw.startswith("/del"):
        track_id = track_raw.split("_")[-1]
        if track_id.isdigit():
            with get_session() as s:
                delete_track(s, int(track_id), course_id)
            tracks_have_updated = True
    elif re.match(r"^\d{1,24} \d{1,24}$", track_raw):
        if len(track_raw.split(" ")) == 2:
            print("updating track")
            track, par = tuple(track_raw.split(" "))
            if track.isdigit() and par.isdigit():
                with get_session() as s:
                    upsert_track(s, track, par, course_id)
                tracks_have_updated = True
    else:
        await update.message.reply_text(
            f"Track is invalid. Format should be <track num> <par>"
        )
    if tracks_have_updated:
        with get_session() as s:
            tracks_list = read_tracks_as_text_list(s, course_id)
        track_msg = context.user_data.get("track_msg")
        keyboard = [
            [InlineKeyboardButton(f"Done", callback_data="tracks_save")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if context.user_data.get("track_last_msg") != track_msg + tracks_list:
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=track_msg_prompt_id,
                text=track_msg + tracks_list,
                reply_markup=reply_markup,
            )
            context.user_data["prompt_message_id"] = context.user_data.get(
                "track_prompt_id"
            )
        context.user_data["track_last_msg"] = track_msg + tracks_list
    context.user_data["is_inline"] = True
    return ADD_TRACKS


@handler_helper(remove_keyboard=True)
async def course_added(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("course_location"):
        del context.user_data["course_location"]
    if context.user_data.get("course_name"):
        del context.user_data["course_name"]
    if context.user_data.get("editing_course"):
        del context.user_data["editing_course"]
    if context.user_data.get("is_inline"):
        del context.user_data["is_inline"]
    if context.user_data.get("prompt_message_id"):
        del context.user_data["prompt_message_id"]
    context.user_data["track_last_msg"] = ""

    await update.effective_chat.send_message("Track saved!")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Action cancelled.")
    # TODO: delete data from user context
    if context.user_data.get("course_location"):
        del context.user_data["course_location"]
    if context.user_data.get("course_name"):
        del context.user_data["course_name"]
    if context.user_data.get("editing_course"):
        del context.user_data["editing_course"]
    if context.user_data.get("is_inline"):
        del context.user_data["is_inline"]
    if context.user_data.get("prompt_message_id"):
        del context.user_data["prompt_message_id"]
    context.user_data["track_last_msg"] = ""

    return ConversationHandler.END


course_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("coursemenu", start_edit_courses)],
    states={
        CHOOSE_COURSE_ACTION_ROUTE: [
            CallbackQueryHandler(start_edit_courses, pattern="^start$"),
            CallbackQueryHandler(add_game_name, pattern="^select_game:$"),
            CallbackQueryHandler(
                present_add_edit_course, pattern="^select_game:" + ".+$"
            ),
            CallbackQueryHandler(edit_course, pattern="^edit_course:" + ".*$"),
            CallbackQueryHandler(
                add_course_name, pattern="^(create_course|edit_course_name):.*$"
            ),
            CallbackQueryHandler(
                edit_course_location, pattern="^edit_course_location:.*$"
            ),
            CallbackQueryHandler(course_delete, pattern="^delete_course:" + ".*$"),
            CallbackQueryHandler(edit_tracks, pattern="^edit_tracks:.*$"),
        ],
        ADD_COURSE_ROUTE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, process_course_name),
            CallbackQueryHandler(  # for back button
                present_add_edit_course, pattern="^select_game:" + ".+$"
            ),
        ],
        ADD_COURSE_LOCATION: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                process_course_location,
            ),
            CallbackQueryHandler(  # for back button
                present_add_edit_course, pattern="^select_game:" + ".+$"
            ),
        ],
        ADD_TRACKS: [
            CallbackQueryHandler(course_added, pattern="^tracks_save$"),
            CommandHandler("done", course_added),
            CommandHandler("cancel", course_added),
            MessageHandler(filters.TEXT | filters.COMMAND, add_tracks),
        ],
        ADD_GAME_ROUTE: [
            CallbackQueryHandler(start_edit_courses, pattern="^start$"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, add_game_done),
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
