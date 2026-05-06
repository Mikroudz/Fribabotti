from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.helpers import escape_markdown
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
)

from database import get_session

from models.device_sessions.crud import (
    create_device_session,
    delete_unidentified_device_sessions,
)

AWAITING_DEVICE_CODE = 1

CURRENT_TIMEZONE = "Europe/Helsinki"


async def start_registering(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    with get_session() as s:
        # 1. Cleanup existing unidentified sessions for this user so they get a fresh start
        delete_unidentified_device_sessions(s, user_id)

    msg = (
        "⌚️ *Device Registration*\n\n"
        "Please enter the numeric code displayed on your watch screen\.\n\n"
        "_\(Send /cancel to abort at any time\)_"
    )

    await update.effective_chat.send_message(text=msg, parse_mode=ParseMode.MARKDOWN_V2)

    return AWAITING_DEVICE_CODE


async def receive_device_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    # Validate that the user sent a valid integer code
    if not text.isdigit():
        await update.message.reply_text(
            "The code must be a number. Please try again or send /cancel."
        )
        return AWAITING_DEVICE_CODE

    device_code = int(text)

    with get_session() as s:
        # Create the new device session awaiting the watch to pair
        create_device_session(s, device_id=device_code, user_id=user_id)

    msg = (
        f"✅ Code `{device_code}` received!\n\n"
        "Your watch should now pair automatically. "
        "If it fails to connect, please run /register_device to try again."
    )
    await update.message.reply_text(
        text=escape_markdown(msg, 1), parse_mode=ParseMode.MARKDOWN
    )

    # Exit the conversation
    return ConversationHandler.END


async def cancel_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    with get_session() as s:
        # Cleanup any pending registrations on exit
        delete_unidentified_device_sessions(s, user_id)

    await update.message.reply_text("Device registration cancelled.")
    return ConversationHandler.END


register_device_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("register_device", start_registering)],
    states={
        # Only accept text that isn't a command
        AWAITING_DEVICE_CODE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_device_code)
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel_registration)],
)
