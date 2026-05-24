from dotenv import dotenv_values
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
)

import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import uvicorn
from fastapi import FastAPI

from utils.env_settings import get_settings

from routes import auth, course, device_routes, games, score, group

from database import create_db_and_tables, get_session

from models.user.crud import create_user

from handlers.course_handler import course_conv_handler

from handlers.game_handler import game_conv_handler
from handlers.group_handler import (
    new_group_conv_handler,
    edit_group_conv_handler,
    join_group_invite,
)

from handlers.register_device_handler import register_device_conv_handler

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


async def run_bot():
    application = ApplicationBuilder().token(get_settings().telegram_bot_secret).build()

    start_handler = CommandHandler("start", start)
    join_group_invite_handler = CommandHandler("joingroup", join_group_invite)

    application.add_handler(start_handler)
    application.add_handler(join_group_invite_handler)

    application.add_handler(course_conv_handler)
    application.add_handler(edit_group_conv_handler)
    application.add_handler(new_group_conv_handler)
    application.add_handler(game_conv_handler)
    application.add_handler(register_device_conv_handler)

    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        print("Telegram bot is shutting...")
        await application.updater.stop()
        await application.stop()
        await application.shutdown()
        print("Telegram bot shut down...")


app = FastAPI()
app.include_router(device_routes.router)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(games.router, prefix="/api/v1")
app.include_router(score.router, prefix="/api/v1")
app.include_router(course.router, prefix="/api/v1")
app.include_router(group.router, prefix="/api/v1")


async def main():
    create_db_and_tables()
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        loop="asyncio",
        reload=True,
    )
    server = uvicorn.Server(config)

    await asyncio.gather(server.serve(), run_bot(), return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(main())
