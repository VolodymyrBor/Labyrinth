import logging
from functools import wraps
from typing import Callable, Optional, List

from telegram import Update, Message, TelegramError
from telegram.ext import ConversationHandler
from telegram.ext.callbackcontext import CallbackContext


_MESSAGES_TO_DELETE = 'to_delete_messages'


ConvHandler = Callable[[Update, CallbackContext], Optional[int]]


def get_messages_to_delete(context: CallbackContext) -> List[Message]:
    """Get from chat context messages that need to be delete.

    :param context: CallBackContext
    :return: Messages
    """
    return context.chat_data.get(_MESSAGES_TO_DELETE, [])


def add_messages_to_delete(context: CallbackContext, message: Message):
    """Insert message to list of messages that will be deleted in chat context.

    :param context: CallBackContext
    :param message: message
    """
    chat_data: dict = context.chat_data
    messages = chat_data.setdefault(_MESSAGES_TO_DELETE, [])
    messages.append(message)


def delete_messages(func: ConvHandler) -> ConvHandler:
    """After work this func messages that was added through func 'add_messages_to_delete' will be deleted.

    :param func:
    :return:
    """
    @wraps(func)
    def wrapper(update: Update, context: CallbackContext):
        result = func(update, context)
        to_delete_message = get_messages_to_delete(context)
        for message in to_delete_message:
            try:
                message.delete()
            except TelegramError as err:
                logging.debug(err)
        return result
    return wrapper


def end_conv(func: ConvHandler) -> ConvHandler:
    """This func closes conversion.

    :param func:
    :return:
    """
    @wraps(func)
    def wrapper(update: Update, context: CallbackContext) -> int:
        func(update, context)
        return ConversationHandler.END
    return wrapper


def continue_conv(stage: int) -> Callable:
    def decorator(func: ConvHandler) -> ConvHandler:
        @wraps(func)
        def wrapper(update: Update, context: CallbackContext) -> int:
            func(update, context)
            return stage
        return wrapper
    return decorator

