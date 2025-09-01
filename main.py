from dotenv import dotenv_values
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
)

from database import create_db_and_tables, get_session

from models.user.crud import create_user

from handlers.course_handler import course_conv_handler

from handlers.game_handler import game_conv_handler
from handlers.group_handler import (
    new_group_conv_handler,
    edit_group_conv_handler,
    join_group_invite,
)

secrets = dotenv_values(".env")

log_level = logging.INFO if secrets.get("DEV_MODE", False) else logging.WARNING
logging.getLogger("httpcore").setLevel(logging.WARNING)

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("handlers.helpers").setLevel(
    logging.DEBUG if secrets.get("DEV_MODE", False) else logging.WARNING
)
logging.getLogger("models.game_session.crud").setLevel(
    logging.DEBUG if secrets.get("DEV_MODE", False) else logging.WARNING
)


logging.basicConfig(
    format="%(asctime)s [%(levelname)s][%(name)s] %(message)s", level=log_level
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with get_session() as s:
        create_user(s, update.message.from_user)

    msg = "Track scores\nJoin a group or create new /groupmenu\nAdd courses /coursemenu\nStart or join a game /game"
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
    )


if __name__ == "__main__":
    create_db_and_tables()
    application = ApplicationBuilder().token(secrets["BOT_SECRET"]).build()

    start_handler = CommandHandler("start", start)
    join_group_invite_handler = CommandHandler("joingroup", join_group_invite)

    application.add_handler(start_handler)
    application.add_handler(join_group_invite_handler)

    application.add_handler(course_conv_handler)
    application.add_handler(edit_group_conv_handler)
    application.add_handler(new_group_conv_handler)
    application.add_handler(game_conv_handler)

    application.run_polling()
