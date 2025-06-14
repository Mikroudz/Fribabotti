from dotenv import dotenv_values
from io import BytesIO
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackQueryHandler,
)

from database import create_db_and_tables, get_session

from models.user.crud import create_user

from handlers.course_handler import course_conv_handler

from handlers.game_handler import game_conv_handler
from handlers.group_handler import new_group_conv_handler, edit_group_conv_handler


secrets = dotenv_values(".env")


log_level = logging.INFO if secrets.get("DEV_MODE", False) else logging.WARNING
logging.getLogger("httpcore").setLevel(logging.WARNING)

logging.getLogger("httpx").setLevel(logging.WARNING)
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


if __name__ == "__main__":
    create_db_and_tables()
    application = ApplicationBuilder().token(secrets["BOT_SECRET"]).build()

    start_handler = CommandHandler("start", start)
    # cmd_create_game_group = CommandHandler("create_group", create_game_group)

    # cmd_get_courses = CommandHandler("tracks", get_courses)

    # application.add_handler(cmd_create_game_group)

    application.add_handler(start_handler)
    # application.add_handler(cmd_get_courses)

    application.add_handler(course_conv_handler)
    application.add_handler(edit_group_conv_handler)
    application.add_handler(new_group_conv_handler)
    application.add_handler(game_conv_handler)

    application.run_polling()
