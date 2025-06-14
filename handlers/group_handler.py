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

from datetime import datetime

from models.user_group.crud import (
    read_groups,
    read_group,
    read_group_members,
    edit_group,
    delete_group,
    create_group,
)

(
    EDIT_GROUP_ROUTE,
    EDIT_GROUP_NAME_ROUTE,
    DELETE_GROUP_ROUTE,
    NEW_GROUP_PROCESS_NAME,
) = range(4)


async def group_start_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    with get_session() as s:
        user_groups = read_groups(s, update.message.from_user.id)

    keyboard = [
        [
            InlineKeyboardButton(group.name, callback_data=f"edit_group:{group.id}")
            for group in user_groups
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        text="Select group to edit from below:", reply_markup=reply_markup
    )

    return EDIT_GROUP_ROUTE


async def group_edit_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    route = query.data

    group_id = route.split(":")[1]

    keyboard = [
        [
            InlineKeyboardButton(
                f"Edit name", callback_data=f"edit_group_name:{group_id}"
            ),
            InlineKeyboardButton(
                f"Show players", callback_data=f"show_players:{group_id}"
            ),
            InlineKeyboardButton(
                f"Delete group", callback_data=f"delete_group:{group_id}"
            ),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    with get_session() as s:
        group = read_group(s, group_id)

    prompt_message = await query.edit_message_text(
        f"Select action for group {group.name}",
        reply_markup=reply_markup,
    )

    context.user_data["prompt_message_id"] = prompt_message.message_id
    return EDIT_GROUP_ROUTE


async def group_show_players(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    route = query.data

    group_id = route.split(":")[1]
    with get_session() as s:
        members = read_group_members(s, group_id)
    members_str = "Group members:\n"
    members_str += "".join([f"{user.username}\n" for user in members])
    await update.effective_chat.send_message(members_str)

    return EDIT_GROUP_ROUTE


async def group_edit_name_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    route = query.data

    group_id = route.split(":")[1]
    with get_session() as s:
        group = read_group(s, group_id)

    keyboard = [
        [
            InlineKeyboardButton(f"Back", callback_data=f"edit_group:{group_id}"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    prompt_message = await query.edit_message_text(
        f"Send new name for {group.name}:",
        reply_markup=reply_markup,
    )
    context.user_data["prompt_message_id"] = prompt_message.message_id
    context.user_data["group_id"] = group_id

    return EDIT_GROUP_NAME_ROUTE


async def process_group_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_name = update.message.text
    prompt_msg_id = context.user_data.get("prompt_message_id")
    await context.bot.edit_message_reply_markup(
        chat_id=update.effective_chat.id,
        message_id=prompt_msg_id,
        reply_markup=None,
    )
    if len(group_name) > 1 and len(group_name) < 128:
        group_id = context.user_data.get("group_id")

        with get_session() as s:
            edit_group(s, group_name, group_id)

        await update.effective_chat.send_message("Group name changed!")

        return EDIT_GROUP_ROUTE
    else:
        keyboard = [
            [
                InlineKeyboardButton(f"Back", callback_data=f"edit_group:{group_id}"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.effective_chat.send_message(
            "Name should be between 1 and 128 characters", reply_markup=reply_markup
        )

        return EDIT_GROUP_NAME_ROUTE


async def group_delete_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    route = query.data

    group_id = route.split(":")[1]
    context.user_data["group_id"] = group_id
    with get_session() as s:
        group = read_group(s, group_id)

    keyboard = [
        [
            InlineKeyboardButton(f"Cancel", callback_data=f"edit_group:{group_id}"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    prompt_message = await query.edit_message_text(
        f'Write "yes" to delete {group.name} and all associated sessions',
        reply_markup=reply_markup,
    )
    context.user_data["prompt_message_id"] = prompt_message.message_id

    return


async def group_delete_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    delete_confirm = update.message.text
    group_id = context.user_data.get("group_id")

    if delete_confirm == "yes":
        with get_session() as s:
            delete_group(s, group_id)
        prompt_msg_id = context.user_data.get("prompt_message_id")
        await context.bot.edit_message_reply_markup(
            chat_id=update.effective_chat.id,
            message_id=prompt_msg_id,
            reply_markup=None,
        )
        await update.effective_chat.send_message("Group has been deleted")
    else:
        return DELETE_GROUP_ROUTE

    return ConversationHandler.END


async def group_create_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text="Give your group a name:")
    return NEW_GROUP_PROCESS_NAME


async def newgroup_name_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_name = update.message.text

    if len(group_name) > 1 and len(group_name) < 128:
        with get_session() as s:
            create_group(s, group_name, update.message.from_user.id)
        await update.message.reply_text(text="Group has been created!")
    else:
        await update.message.reply_text(
            text="Name should be between 1 and 128 characters"
        )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Action cancelled.")
    # TODO: delete data from user context

    return ConversationHandler.END


new_group_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("newgroup", group_create_start)],
    states={
        NEW_GROUP_PROCESS_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, newgroup_name_process)
        ]
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)


edit_group_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("groupmenu", group_start_menu)],
    states={
        EDIT_GROUP_ROUTE: [
            CallbackQueryHandler(group_edit_menu, pattern="^edit_group:.*$"),
            CallbackQueryHandler(group_show_players, pattern="^show_players:.*$"),
            CallbackQueryHandler(
                group_edit_name_process, pattern="^edit_group_name:.*$"
            ),
            CallbackQueryHandler(group_delete_menu, pattern="^delete_group:.*$"),
        ],
        EDIT_GROUP_NAME_ROUTE: [
            MessageHandler(filters.TEXT | filters.COMMAND, process_group_name)
        ],
        DELETE_GROUP_ROUTE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, group_delete_process)
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
