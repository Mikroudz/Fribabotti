from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.helpers import escape_markdown
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackQueryHandler,
)
from datetime import datetime, timedelta

from database import get_session
from utils.generate_result_card import create_result_card_image

from models.course.crud import read_courses


from models.score.crud import (
    read_scores,
    upsert_score,
    read_users_scores,
    read_session_username_score_full,
    read_course_best_user_scores,
)
from models.game.crud import read_games

from models.user_group.crud import read_groups

from models.game_session.crud import (
    read_game_session_user_groups,
    read_game_session_user,
    create_game_session,
    read_game_session,
    end_game_session,
    reopen_game_session,
    read_game_session_course,
    join_game_session,
    read_user_session_time,
)

from .helpers import handler_helper, log_tg_action

from utils.formatting import par_score_format

GAME_MAIN_MENU_ROUTE, GAME_SESSION_SELECTED_ROUTE = range(2)

CURRENT_TIMEZONE = "Europe/Helsinki"


@log_tg_action()
@handler_helper()
async def start_game_menu(
    update: Update, context: ContextTypes.DEFAULT_TYPE, from_user_id: int
):
    is_new_conversation = True
    if context.user_data.get("is_inline"):
        is_new_conversation = False

    with get_session() as s:
        user_active_games = read_game_session_user(s, from_user_id, active=True)
        user_groups_active_games = read_game_session_user_groups(s, from_user_id)
        user_game_count, user_time_played_sec = read_user_session_time(
            s, from_user_id, datetime.now() - timedelta(days=14)
        )

    user_has_active_games = (
        len(user_active_games) > 0 or len(user_groups_active_games) > 0
    )

    user_session_active_games_keyboard = [
        [
            InlineKeyboardButton(
                f"{game.course.name} {game.started_at_local(None, False).strftime('%Y-%m-%d')}",
                callback_data=f"session_selected:{game.id}",
            )
        ]
        for game, _ in user_active_games
    ]

    keyboard = [
        *user_session_active_games_keyboard,
        [
            InlineKeyboardButton("New Game Session", callback_data=f"new_session:"),
            InlineKeyboardButton("Old Games", callback_data=f"old_sessions:0"),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    ongoing_games_msg = (
        "Ongoing games in your groups"
        if user_has_active_games
        else "No game session active. Start a new one!"
    )
    ongoing_games_msg += (
        "\nPress /gs_* to join a game\n" if len(user_groups_active_games) > 0 else ""
    )
    ongoing_games_msg += "\n".join(
        [
            f"{session.course.name} {session.started_at} /gs_{session.id}"
            for session in user_groups_active_games
        ]
    )
    minutes, sec = divmod(user_time_played_sec, 60)
    hours, minutes = divmod(minutes, 60)
    ongoing_games_msg += (
        f"\nTime played last two weeks: {hours}h {minutes}min\nGames: {user_game_count}"
    )
    if is_new_conversation:
        prompt_message = await update.message.reply_text(
            text=escape_markdown(ongoing_games_msg, version=2),
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN_V2,
        )
    else:
        prompt_message = await update.callback_query.edit_message_text(
            text=escape_markdown(ongoing_games_msg, version=2),
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN_V2,
        )
    context.user_data["prompt_message_id"] = prompt_message.message_id
    context.user_data["is_inline"] = True
    context.user_data["from_command"] = False

    return GAME_MAIN_MENU_ROUTE


@log_tg_action()
@handler_helper(force_inline=True, callback_param_validator=int)
async def reply_scorecard(
    update: Update, context: ContextTypes.DEFAULT_TYPE, cb_param: int
):
    session_id = cb_param
    with get_session() as s:
        course = read_game_session_course(s, session_id)
        scores = read_session_username_score_full(s, session_id, course.id)
        game_session = read_game_session(s, session_id)

    results_card = create_result_card_image(course, scores, game_session)

    await context.bot.send_photo(photo=results_card, chat_id=update.effective_chat.id)
    return GAME_MAIN_MENU_ROUTE


@log_tg_action()
async def session_selected_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session_id = None
    # TODO: make this better
    if not update.message:
        # Maybe might need to use from_command as forcing this path?
        context.user_data["from_command"] = False
        query = update.callback_query
        await query.answer()
        route = query.data
        session_id = route.split(":")[1]
    else:
        # This fnc is called only when message starts with "/gs_"
        context.user_data["from_command"] = True
        cmd = update.message.text
        session_id = cmd.split("_")[1]
        if not session_id.isdigit():
            return GAME_MAIN_MENU_ROUTE

    with get_session() as s:
        game_session = read_game_session(s, session_id)
        scores_total = read_users_scores(s, session_id)
    # Escape if user gave incorrect ID
    if game_session is None:
        return GAME_MAIN_MENU_ROUTE

    # Remove keypad only if we have a session to show
    if context.user_data.get("prompt_message_id"):
        await context.bot.edit_message_reply_markup(
            chat_id=update.effective_chat.id,
            reply_markup=None,
            message_id=context.user_data.get("prompt_message_id"),
        )

    add_scores_button = None
    if game_session.ended_at:
        end_open_session = InlineKeyboardButton(
            "Open session", callback_data=f"open_session:{session_id}"
        )
    else:
        add_scores_button = InlineKeyboardButton(
            "Add scores", callback_data=f"add_score:{session_id}"
        )
        end_open_session = InlineKeyboardButton(
            "End session", callback_data=f"end_session:{session_id}"
        )

    keyboard = [
        [
            InlineKeyboardButton(
                "Get Scores", callback_data=f"get_scorecard:{session_id}"
            )
        ],
        [InlineKeyboardButton("Back", callback_data=f"start"), end_open_session],
    ]
    if add_scores_button:
        keyboard.insert(0, [add_scores_button])

    reply_markup = InlineKeyboardMarkup(keyboard)

    session_msg = (
        f"Game Session course *{escape_markdown(game_session.course.name, 2)}*\n"
    )
    session_msg += f"Group *{escape_markdown(game_session.user_group.name, 2)}*\n"

    session_msg += f"Started {escape_markdown(game_session.started_at_local(), 2)}\n"
    if game_session.ended_at:
        session_msg += f"Ended {escape_markdown(game_session.ended_at_local(), 2)}\n"
        time_diff = (
            game_session.ended_at_local(None, False)
            - game_session.started_at_local(None, False)
        ).total_seconds()
        minutes, sec = divmod(time_diff, 60)
        hours, minutes = divmod(minutes, 60)

        session_msg += f"Playtime: {int(hours)}h {int(minutes)}min\n"

    prompt_msg = None
    if len(scores_total) > 0:
        scores_msg = "\nCurrent stats:\n"
        for user, score in scores_total:
            scores_msg += f"{user.username} {par_score_format(score)}\n"

        session_msg += escape_markdown(scores_msg, 2)
    if not context.user_data.get("from_command"):
        prompt_msg = await query.edit_message_text(
            text=session_msg,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN_V2,
        )
    else:
        prompt_msg = await update.message.reply_text(
            text=session_msg,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN_V2,
        )

    context.user_data["prompt_message_id"] = prompt_msg.message_id
    context.user_data["is_inline"] = True

    return GAME_MAIN_MENU_ROUTE


@log_tg_action()
@handler_helper(force_inline=True)
async def new_session_select_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with get_session() as s:
        games = read_games(s)
    keyboard = [
        [
            InlineKeyboardButton(f"{game.name}", callback_data=f"select_game:{game.id}")
            for game in games
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    msg = (
        "Which game you are playing?"
        if len(games) > 0
        else "No game types saved. Create first with /coursemenu command"
    )
    if context.user_data.get("is_inline"):
        await update.callback_query.edit_message_text(
            text=escape_markdown(msg, version=2),
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN_V2,
        )
    if len(games) == 0:
        return ConversationHandler.END
    return GAME_MAIN_MENU_ROUTE


@log_tg_action()
@handler_helper(force_inline=True, callback_param_validator=int)
async def list_old_sessions(
    update: Update, context: ContextTypes.DEFAULT_TYPE, cb_param: int, from_user_id
):
    page_id = cb_param
    context.user_data["is_inline"] = True
    context.user_data["from_command"] = True

    show_items_on_page = 10

    with get_session() as s:
        game_sessions = read_game_session_user(s, from_user_id, active=False)

    session_msg = f"Old sessions\n{len(game_sessions)} found\n\n"
    session_msg += "\n".join(
        [
            f"{session.course.name} {session.ended_at_local()} {par_score_format(score)} /gs_{session.id}"
            for session, score in game_sessions[
                (page_id) * show_items_on_page : (page_id) * show_items_on_page
                + show_items_on_page
            ]
        ]
    )
    score_menu_buttons = []

    if page_id > 0:
        score_menu_buttons.append(
            InlineKeyboardButton(
                f"Prev page", callback_data=f"old_sessions:{page_id-1}"
            )
        )

    if len(game_sessions) // show_items_on_page > page_id:
        score_menu_buttons.append(
            InlineKeyboardButton(
                f"Next page", callback_data=f"old_sessions:{page_id+1}"
            )
        )

    keyboard = [
        score_menu_buttons,
        [InlineKeyboardButton(f"Back", callback_data=f"start")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        text=escape_markdown(session_msg, 2),
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN_V2,
    )

    return GAME_MAIN_MENU_ROUTE


@log_tg_action()
@handler_helper(force_inline=True, callback_param_validator=int)
async def new_session_select_course(
    update: Update, context: ContextTypes.DEFAULT_TYPE, cb_param: int
):
    game_id = cb_param

    with get_session() as s:
        courses = read_courses(s, game_id)
    courses = [courses[i : i + 3] for i in range(0, len(courses), 3)]
    keyboard_course_select = [
        [
            InlineKeyboardButton(
                f"{course.name}", callback_data=f"select_course:{course.id}"
            )
            for course in course_group
        ]
        for course_group in courses
    ]
    reply_markup = InlineKeyboardMarkup(keyboard_course_select)
    msg = (
        "Choose course from below for new game session"
        if len(courses) > 0
        else "No courses are saved. Add first one with /coursemenu"
    )

    await update.callback_query.edit_message_text(
        escape_markdown(msg, version=2),
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    if len(courses) == 0:
        return ConversationHandler.END
    return GAME_MAIN_MENU_ROUTE


@log_tg_action()
@handler_helper(force_inline=True, callback_param_validator=int)
async def new_session_select_user_group(
    update: Update, context: ContextTypes.DEFAULT_TYPE, cb_param: int, from_user_id
):
    course_id = cb_param
    context.user_data["course_id"] = course_id
    with get_session() as s:
        groups = read_groups(s, from_user_id)
    keyboard = [
        [
            InlineKeyboardButton(
                f"{group.name}", callback_data=f"select_user_group:{group.id}"
            )
            for group in groups
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = "Choose which group to start the game in\nAll group members can join ongoing games"
    if len(groups) == 0:
        msg = "You do not belong to any groups!\nCreate new with /newgroup or join to existing group"
    prompt_message = await update.callback_query.edit_message_text(
        msg,
        reply_markup=reply_markup,
    )
    if len(groups) == 0:
        return ConversationHandler.END
    context.user_data["prompt_message_id"] = prompt_message.message_id
    context.user_data["is_inline"] = True

    return GAME_MAIN_MENU_ROUTE


@log_tg_action()
@handler_helper(force_inline=True, callback_param_validator=int, remove_keyboard=True)
async def create_new_game_session(
    update: Update, context: ContextTypes.DEFAULT_TYPE, cb_param, from_user_id
):
    user_group_id = cb_param
    course_id = context.user_data.get("course_id")

    with get_session() as s:
        game_session = create_game_session(s, from_user_id, course_id, user_group_id)

    await update.effective_chat.send_message(
        f"Game session started!\nCourse {game_session.course.name}"
    )
    # Redirect user to the session
    # update.callback_query.data = f"session_selected:{game_session.id}"
    context.user_data["game_session_id"] = game_session.id
    context.user_data["not_inline"] = False
    return await selected_game_session(update, context)


@log_tg_action()
@handler_helper(force_inline=True, callback_param_validator=int, remove_keyboard=True)
async def game_session_end(
    update: Update, context: ContextTypes.DEFAULT_TYPE, cb_param: int
):
    session_id = cb_param
    with get_session() as s:
        game_session = end_game_session(s, session_id)
    if game_session:
        await update.effective_chat.send_message(
            f"Session ended {game_session.ended_at_local()}"
        )
    return await session_selected_actions(update, context)


@log_tg_action()
@handler_helper(force_inline=True, callback_param_validator=int, remove_keyboard=True)
async def game_session_reopened(
    update: Update, context: ContextTypes.DEFAULT_TYPE, cb_param: int
):
    session_id = cb_param
    with get_session() as s:
        reopen_game_session(s, session_id)
    context.user_data["from_command"] = False

    return await session_selected_actions(update, context)


@log_tg_action()
@handler_helper(remove_keyboard=False)
async def selected_game_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # do we have saved session
    session_id = context.user_data.get("game_session_id")
    query = update.callback_query
    if not session_id:
        # most probably we came from callback so add the session
        await query.answer()
        route = query.data
        session_id = route.split(":")[1]
        context.user_data["game_session_id"] = session_id
    if context.user_data.get("current_track_num", None) != None:
        del context.user_data["current_track_num"]
    if context.user_data.get("current_track_idx", None) != None:
        del context.user_data["current_track_idx"]
    context.user_data["last_msg"] = ""
    user_id = query.from_user.id
    # Check if user has joined the session
    with get_session() as s:
        join_game_session(s, session_id=session_id, user_id=user_id)
    # This just handles the input inbetween transitions to keep state clear
    return await game_session_process(update, context)


def save_score(context: ContextTypes.DEFAULT_TYPE, score: int, user_id: int):
    game_session_id = context.user_data.get("game_session_id")
    current_track_num = context.user_data.get("current_track_number")

    with get_session() as s:
        return upsert_score(s, score, current_track_num, user_id, game_session_id)


async def game_sesssion_save_score_text(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    context.user_data["not_inline"] = True
    score = update.message.text
    try:
        score_num = int(score)
        save_score(context, score_num, update.message.from_user.id)
    except ValueError:
        # Keep current track
        context.user_data["force_track_idx"] = context.user_data.get(
            "current_track_idx"
        )
        await update.effective_chat.send_message("Invalid number")

    return await game_session_process(update, context)


@log_tg_action()
@handler_helper(force_inline=True, callback_param_validator=int)
async def game_sesssion_save_score(
    update: Update, context: ContextTypes.DEFAULT_TYPE, cb_param: int, from_user_id
):
    score = cb_param
    save_score(context, score, from_user_id)
    current_track_num = context.user_data.get("current_track_number")
    await update.callback_query.answer(
        text=f"Track {current_track_num} score {score} saved!"
    )

    return await game_session_process(update, context)


@log_tg_action()
async def game_session_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_inline_msg = not context.user_data.get("not_inline", False)
    context.user_data["not_inline"] = False
    force_track_idx = None
    from_user_id = None

    if is_inline_msg:
        query = update.callback_query
        await query.answer()
        route = query.data
        from_user_id = query.from_user.id
        if route.startswith("move_to_track"):
            force_track_idx = int(route.split(":")[1])
    else:
        # Check if we have forced track in user_data
        force_track_idx = context.user_data.get("force_track_idx")
        if force_track_idx != None:
            del context.user_data["force_track_idx"]
        from_user_id = update.message.from_user.id

    game_session_id = context.user_data.get("game_session_id")
    course_top_scores = {}
    # TODO: if another user ends the game, what should we do?
    with get_session() as s:
        score_and_track = read_scores(s, game_session_id, from_user_id)
        tops = read_course_best_user_scores(
            s, user_id=from_user_id, session_id=game_session_id
        )
        course_top_scores = dict({key: [sc, tm] for key, sc, tm in tops})

    current_track_idx = context.user_data.get("current_track_idx")

    if force_track_idx != None:
        current_track_idx = force_track_idx
    else:
        if current_track_idx == None:
            # These are ordered by track number so use index here
            current_track_idx = 0
        else:
            current_track_idx = current_track_idx + 1
    if len(score_and_track) <= current_track_idx:
        # We are at end, don't go to next and prompt to end the game
        current_track_idx = current_track_idx - 1
    context.user_data["current_track_idx"] = current_track_idx
    context.user_data["current_track_number"] = score_and_track[current_track_idx][
        1
    ].track_number

    total_score = sum([score.score for score, _ in score_and_track if score])
    current_track = score_and_track[current_track_idx][1]
    current_track_score = score_and_track[current_track_idx][0]

    updated_msg = f"*Track {current_track.track_number}* par {escape_markdown(str(current_track.par), 2)}"
    updated_msg += (
        f"\nSaved Score: {escape_markdown(par_score_format(current_track_score.score), 2)}"
        if current_track_score
        else ""
    )
    updated_msg += "\n\n"
    updated_msg += (
        f"Course total: {escape_markdown(par_score_format(total_score), 2)}\n"
    )

    if current_track.track_number in course_top_scores:
        track_best = course_top_scores[current_track.track_number]
        updated_msg += f"Personal Best: {escape_markdown(par_score_format(track_best[0]), 2)}, {escape_markdown(track_best[1].strftime('%Y-%m-%d'), 2)}\n"

    markup_data = ""
    score_menu_buttons = []
    if current_track_idx > 0:
        callback = f"move_to_track:{current_track_idx-1}"
        markup_data += "prev" + callback
        score_menu_buttons.append(InlineKeyboardButton(f"prev", callback_data=callback))
    if current_track_idx < len(score_and_track) - 1:
        callback = f"move_to_track:{current_track_idx+1}"
        markup_data += "next" + callback
        score_menu_buttons.append(InlineKeyboardButton(f"next", callback_data=callback))
    else:
        score_menu_buttons.append(
            InlineKeyboardButton(f"Exit", callback_data=f"exit_game:{game_session_id}")
        )
    markup_data += "".join([f"submit_score:{i}" for i in range(-1, 4)])
    keyboard = [
        [
            InlineKeyboardButton(par_score_format(i), callback_data=f"submit_score:{i}")
            for i in range(-1, 4)
        ],
        score_menu_buttons,
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    # hotfix to check if markup/msg has changed, otherwise we get error from api

    current_msg = markup_data + updated_msg
    prompt_message = None
    prompt_message_id = None
    if context.user_data.get("prompt_message_id"):
        prompt_message_id = context.user_data.get("prompt_message_id")
        # context.user_data["prompt_message_id"] = prompt_message.message_id

    # send new message
    if not is_inline_msg:
        prompt_message = await update.effective_chat.send_message(
            updated_msg,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        # Clean buttons from old msg
        if prompt_message_id:
            await context.bot.edit_message_reply_markup(
                chat_id=update.effective_chat.id,
                message_id=prompt_message_id,
                reply_markup=None,
            )

    else:  # use old message
        # Check if content has changed
        last_msg = context.user_data.get("last_msg")

        if not (last_msg and last_msg == current_msg):
            prompt_message = await query.edit_message_text(
                text=updated_msg,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN_V2,
            )
    if prompt_message != None:
        context.user_data["prompt_message_id"] = prompt_message.message_id
    context.user_data["last_msg"] = current_msg
    return GAME_SESSION_SELECTED_ROUTE


@log_tg_action()
async def game_session_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["from_command"] = False
    return await session_selected_actions(update, context)


@log_tg_action()
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Action cancelled.")
    # TODO: delete data from user context
    if context.user_data.get("is_inline"):
        del context.user_data["is_inline"]
    if context.user_data.get("prompt_message_id"):
        del context.user_data["prompt_message_id"]
    return ConversationHandler.END


game_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("game", start_game_menu)],
    states={
        GAME_MAIN_MENU_ROUTE: [
            CallbackQueryHandler(start_game_menu, pattern="^start$"),
            CallbackQueryHandler(
                session_selected_actions, pattern="^session_selected.*$"
            ),
            MessageHandler(filters.Regex(r"^/gs_.*$"), session_selected_actions),
            CallbackQueryHandler(new_session_select_game, pattern="^new_session:$"),
            CallbackQueryHandler(new_session_select_course, pattern="^select_game.*$"),
            CallbackQueryHandler(
                new_session_select_user_group, pattern="^select_course.*$"
            ),
            CallbackQueryHandler(
                create_new_game_session, pattern="^select_user_group.*$"
            ),
            CallbackQueryHandler(selected_game_session, pattern="^add_score:.*$"),
            CallbackQueryHandler(game_session_reopened, pattern="^open_session:.*$"),
            CallbackQueryHandler(game_session_end, pattern="^end_session:.*$"),
            CallbackQueryHandler(list_old_sessions, pattern="^old_sessions:.*$"),
            CallbackQueryHandler(reply_scorecard, pattern="^get_scorecard:.*$"),
        ],
        GAME_SESSION_SELECTED_ROUTE: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, game_sesssion_save_score_text
            ),
            CallbackQueryHandler(game_sesssion_save_score, pattern="^submit_score.*$"),
            CallbackQueryHandler(game_session_process, pattern="^session_selected.*$"),
            CallbackQueryHandler(game_session_process, pattern="^move_to_track.*$"),
            CallbackQueryHandler(game_session_done, pattern="^exit_game:.*$"),
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
