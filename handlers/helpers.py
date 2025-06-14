from typing import Callable, Any
import functools
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ContextTypes
import logging
import inspect

logger = logging.getLogger(__name__)


def handler_helper(
    answer_query: bool = True,
    force_inline: bool = False,
    remove_keyboard: bool = False,
    callback_param_validator: type | Callable[..., Any] = None,
):
    """Telegram handler helper decorator

    Args:
      answer_query: (default True) If true replies automatically to callback queries
      remove_keyboard: (default False) If true tries to remove keyboard on message based on "prompt_message_id" in user_data
      callback_param_validator: Validate callback param value (the "123" from "some_param:123")

    """

    def handler_helper_outer_wrapper(fn: Callable):
        fn_signature = inspect.signature(fn)
        fn_params = fn_signature.parameters

        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            # Expects the update and context objects to be first arguments
            update: Update = args[0]
            context: ContextTypes.DEFAULT_TYPE = args[1]
            param = None
            if context.user_data.get("is_inline") or force_inline:
                query = update.callback_query
                if answer_query:
                    await query.answer()
                from_user_id: int = query.from_user.id
                route = query.data
                # Try getting a param from callback
                if route and isinstance(route, str) and ":" in route:
                    param = route.split(":")[1]
                    if isinstance(callback_param_validator, type):
                        try:
                            param = callback_param_validator(param)
                        except Exception as e:
                            logger.warning(e)
            else:
                from_user_id = update.message.from_user.id

            if remove_keyboard and context.user_data.get("prompt_message_id"):
                await context.bot.edit_message_reply_markup(
                    chat_id=update.effective_chat.id,
                    reply_markup=None,
                    message_id=context.user_data.get("prompt_message_id"),
                )
                del context.user_data["prompt_message_id"]

            helper_kwargs = {
                "from_user_id": from_user_id,
                "cb_param": param,
            }

            has_var_keyword = any(p.kind == p.VAR_KEYWORD for p in fn_params.values())
            final_kwargs = kwargs.copy()

            for key, value in helper_kwargs.items():
                if key in fn_params or has_var_keyword:
                    final_kwargs[key] = value

            return await fn(*args, **final_kwargs)

        return wrapper

    return handler_helper_outer_wrapper
