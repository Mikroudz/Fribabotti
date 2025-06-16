from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackQueryHandler,
)
from telegram.constants import ParseMode
from telegram.helpers import escape_markdown

from database import get_session
from .helpers import handler_helper
from models.user_group.model import UpdateUserGroup

from models.user_group.crud import (
    read_groups,
    read_group,
    read_group_members,
    edit_group,
    delete_group,
    create_group,
    invite_join_group,
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
        [InlineKeyboardButton("New Group", callback_data="new_group")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = "Select group to edit from below:"
    if len(user_groups) == 0:
        msg = "Create new group or join existing with /joingroup"
    await update.effective_chat.send_message(text=msg, reply_markup=reply_markup)

    return EDIT_GROUP_ROUTE


# just to move from start menu to creation
@handler_helper(force_inline=True)
async def group_to_create_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("moving to create new group")
    return await group_create_start(update, context)


@handler_helper(force_inline=True, callback_param_validator=int)
async def group_edit_menu(
    update: Update, context: ContextTypes.DEFAULT_TYPE, cb_param: int
):
    group_id = cb_param

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

    prompt_message = await update.callback_query.edit_message_text(
        (
            f"Select action for group {escape_markdown(group.name)}\n"
            f"Invite users to this group: `/joingroup {group.invite_code}`"
        ),
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN_V2,
    )

    context.user_data["prompt_message_id"] = prompt_message.message_id
    return EDIT_GROUP_ROUTE


@handler_helper(force_inline=True, callback_param_validator=int)
async def group_show_players(
    update: Update, context: ContextTypes.DEFAULT_TYPE, cb_param: int
):
    group_id = cb_param
    with get_session() as s:
        members = read_group_members(s, group_id)
    members_str = "Group members:\n"
    members_str += "".join([f"{user.username}\n" for user in members])
    await update.effective_chat.send_message(members_str)

    return EDIT_GROUP_ROUTE


@handler_helper(force_inline=True, callback_param_validator=int)
async def group_edit_name_process(
    update: Update, context: ContextTypes.DEFAULT_TYPE, cb_param: int
):
    group_id = cb_param
    with get_session() as s:
        group = read_group(s, group_id)

    keyboard = [
        [
            InlineKeyboardButton(f"Back", callback_data=f"start"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    prompt_message = await update.callback_query.edit_message_text(
        f"Send new name for {group.name}:",
        reply_markup=reply_markup,
    )
    context.user_data["prompt_message_id"] = prompt_message.message_id
    context.user_data["group_id"] = group_id

    return EDIT_GROUP_NAME_ROUTE


@handler_helper(remove_keyboard=True)
async def process_group_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_name = update.message.text

    if len(group_name) > 1 and len(group_name) < 128:
        group_id = context.user_data.get("group_id")

        with get_session() as s:
            edit_group(s, group_id, UpdateUserGroup(name=group_name), False)

        await update.effective_chat.send_message("Group name changed!")

        return EDIT_GROUP_ROUTE
    else:
        keyboard = [
            [
                InlineKeyboardButton(f"Back", callback_data=f"start"),
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
            InlineKeyboardButton(f"Cancel", callback_data=f"start"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    prompt_message = await query.edit_message_text(
        f'Write "yes" to delete {group.name} and all associated sessions',
        reply_markup=reply_markup,
    )
    context.user_data["prompt_message_id"] = prompt_message.message_id

    return EDIT_GROUP_ROUTE


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


@handler_helper(force_inline=True, remove_keyboard=True)
async def group_create_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        text="Give your group a name:", chat_id=update.effective_chat.id
    )
    return NEW_GROUP_PROCESS_NAME


async def newgroup_name_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_name = update.message.text
    print("processing name for group")
    msg = "Name should be between 1 and 128 characters"
    if len(group_name) > 1 and len(group_name) < 128:
        with get_session() as s:
            created_group = create_group(
                s, group_name, False, update.message.from_user.id
            )

        msg = "Group has been created!"
    await update.message.reply_text(text=msg)
    return await cancel(update, context)


async def join_group_invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group = None
    if len(context.args) == 1 and len(context.args[0]) == 16:
        invite = context.args[0]
        with get_session() as s:
            group = invite_join_group(s, invite, update.message.from_user.id)
    msg = f"Cannot find group with given invite code"
    if group:
        msg = f"Joined group {group.name}!"

    await update.effective_message.reply_text(msg)


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
            CallbackQueryHandler(group_to_create_group, pattern="^new_group$"),
        ],
        EDIT_GROUP_NAME_ROUTE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, process_group_name),
            CallbackQueryHandler(group_start_menu, pattern="^start$"),
        ],
        DELETE_GROUP_ROUTE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, group_delete_process),
            CallbackQueryHandler(group_start_menu, pattern="^start$"),
        ],
        NEW_GROUP_PROCESS_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, newgroup_name_process),
            CallbackQueryHandler(group_start_menu, pattern="^start$"),
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
