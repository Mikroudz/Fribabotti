from dotenv import dotenv_values
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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


from models.user.crud import create_user
from models.course.crud import read_courses, create_course, read_course

from models.track.crud import (
    upsert_track,
    read_tracks_as_text_list,
    delete_track,
)

from models.game.crud import read_games, create_game


secrets = dotenv_values(".env")


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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with get_session() as s:
        create_user(s, update.message.from_user)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Score tracking bot",
    )


async def create_game_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Send me receipt as an image and I will add it to database!",
    )


async def get_courses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "Courses:\n"
    with get_session() as s:
        courses = read_courses(s)
    for course in courses:
        for k, v in course:
            msg += f"{k}: {v}, "
        msg += "\n"
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
    )


async def add_game_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.answer()
    keyboard = [
        [InlineKeyboardButton(f"Cancel", callback_data=f"cancel")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    prompt_message = await query.edit_message_text(
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

    return ConversationHandler.END


async def delete_game():
    pass


async def edit_game():
    pass


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

    await update.message.reply_text(
        text="Select which game to add course", reply_markup=reply_markup
    )

    return CHOOSE_COURSE_ACTION_ROUTE


async def present_add_edit_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    route = query.data
    await query.answer()

    game_id = route.split(":")[1]

    with get_session() as s:
        courses = read_courses(s, game_id)
    keyboard = [
        [
            InlineKeyboardButton(
                f"Create new course", callback_data=f"create_course:{game_id}"
            )
        ],
        [
            InlineKeyboardButton(
                f"{course.name}", callback_data=f"edit_course:{course.id}"
            )
            for course in courses
        ],
    ]
    context.user_data["selected_game"] = game_id

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "Choose course to edit or create new", reply_markup=reply_markup
    )

    return CHOOSE_COURSE_ACTION_ROUTE


async def add_course_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    route = query.data
    await query.answer()
    game_id = route.split(":")[1]
    keyboard = [
        [InlineKeyboardButton(f"Back", callback_data=f"select_game:{game_id}")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.user_data["selected_game"] = game_id

    prompt_message = await query.edit_message_text(
        "Send name of the new course", reply_markup=reply_markup
    )
    context.user_data["prompt_message_id"] = prompt_message.message_id

    return ADD_COURSE_ROUTE


async def process_course_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    course_name = update.message.text
    game_id = context.user_data.get("selected_game")
    keyboard = [
        [InlineKeyboardButton(f"Back", callback_data=f"select_game:{game_id}")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    prompt_msg_id = context.user_data.get("prompt_message_id")
    await context.bot.edit_message_reply_markup(
        chat_id=update.effective_chat.id, message_id=prompt_msg_id, reply_markup=None
    )

    if len(course_name) > 128 or len(course_name) < 1:

        prompt_message = await update.message.reply_text(
            "Course name should be between 1 and 128",
            reply_markup=reply_markup,
        )
        context.user_data["prompt_message_id"] = prompt_message.message_id
        return ADD_COURSE_ROUTE

    context.user_data["course_name"] = course_name
    prompt_message = await update.message.reply_text(
        f"Send location for course {course_name}",
        reply_markup=reply_markup,
    )
    context.user_data["prompt_message_id"] = prompt_message.message_id

    return ADD_COURSE_LOCATION


async def delete_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    route = query.data
    await query.answer()
    game_id = route.split(":")[1]


async def edit_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    route = query.data
    course_id = route.split(":")[1]
    await query.answer()

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
    ]
    with get_session() as s:
        course = read_course(s, course_id)

    reply_markup = InlineKeyboardMarkup(keyboard)
    prompt_message = await query.edit_message_text(
        f"Select action for course {course.name}",
        reply_markup=reply_markup,
    )

    context.user_data["prompt_message_id"] = prompt_message.message_id
    return CHOOSE_COURSE_ACTION_ROUTE


async def edit_tracks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    route = query.data
    await query.answer()

    course_id = route.split(":")[1]
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

    prompt_msg = await query.edit_message_text(
        track_msg + track_list,
        reply_markup=reply_markup,
    )
    context.user_data["track_prompt_id"] = prompt_msg.message_id
    return ADD_TRACKS


async def process_course_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text
    prompt_msg_id = context.user_data.get("prompt_message_id")
    await context.bot.edit_message_reply_markup(
        chat_id=update.effective_chat.id,
        message_id=prompt_msg_id,
        reply_markup=None,
    )
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
                delete_track(s, int(track_id))
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
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=track_msg_prompt_id,
            text=track_msg + tracks_list,
            reply_markup=reply_markup,
        )

    return ADD_TRACKS


async def course_added(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("course_location"):
        del context.user_data["course_location"]
    if context.user_data.get("course_name"):
        del context.user_data["course_name"]
    track_msg_prompt_id = context.user_data.get("track_prompt_id")
    await context.bot.edit_message_reply_markup(
        chat_id=update.effective_chat.id,
        message_id=track_msg_prompt_id,
        reply_markup=None,
    )
    await update.effective_chat.send_message("Track saved!")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Action cancelled.")
    # TODO: delete data from user context

    return ConversationHandler.END


course_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("coursemenu", start_edit_courses)],
    states={
        CHOOSE_COURSE_ACTION_ROUTE: [
            CallbackQueryHandler(add_game_name, pattern="^select_game:$"),
            CallbackQueryHandler(
                present_add_edit_course, pattern="^select_game:" + ".+$"
            ),
            CallbackQueryHandler(edit_course, pattern="^edit_course:" + ".*$"),
            CallbackQueryHandler(add_course_name, pattern="^create_course:" + ".*$"),
            CallbackQueryHandler(edit_tracks, pattern="^edit_tracks:.*$"),
        ],
        ADD_COURSE_ROUTE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, process_course_name)
        ],
        ADD_COURSE_LOCATION: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                process_course_location,
            )
        ],
        ADD_TRACKS: [
            CallbackQueryHandler(course_added, pattern="^tracks_save$"),
            CommandHandler("done", course_added),
            CommandHandler("cancel", course_added),
            MessageHandler(filters.TEXT | filters.COMMAND, add_tracks),
        ],
        ADD_GAME_ROUTE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, add_game_done)
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
