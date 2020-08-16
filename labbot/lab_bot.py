import logging
from tempfile import NamedTemporaryFile


from telegram.update import Update
from telegram.message import Message
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, File, ReplyKeyboardMarkup,
                      KeyboardButton)

from .utils import is_even
from labirinth import Labyrinth
from .patterns import NUMBER, START_CONV_PATTERN, START_CONV_TEXT
from .conv_helper import add_messages_to_delete, end_conv, delete_messages, continue_conv


logger = logging.getLogger(__name__)

BLOCK_SIZE = 64
LIMIT = 150

START_CONV, CHOSE_MODE, GENERATE_LAB, SOLVE_LAB = range(4)

GENERATE, SOLVE = range(2)


@continue_conv(START_CONV)
def start(update: Update, context: CallbackContext):
    message: Message = update.message
    button = KeyboardButton(START_CONV_TEXT, callback_data=START_CONV_TEXT)
    message.reply_text('Press GO to start.', reply_markup=ReplyKeyboardMarkup([[button]]))


@continue_conv(CHOSE_MODE)
def start_conv(update: Update, context: CallbackContext):
    message: Message = update.message
    add_messages_to_delete(context, message)
    keyboard = [
        [
            InlineKeyboardButton('Generate', callback_data=str(GENERATE)),
            InlineKeyboardButton('Solve', callback_data=str(SOLVE)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    add_messages_to_delete(context, message.reply_text('➖➖➖➖➖➖➖➖', reply_markup=reply_markup))


def chose_mode(update: Update, context: CallbackContext):
    query: CallbackQuery = update.callback_query
    query.answer()
    mode = int(query.data)

    add_messages_to_delete(context, query.message)

    if mode == GENERATE:
        query.edit_message_text('Enter lab size (e.g 64):')
        return GENERATE_LAB

    if mode == SOLVE:
        query.edit_message_text('Send labyrinth(PLS in document mode).')
        return SOLVE_LAB

    raise ValueError('Wrong mode.')


@end_conv
@delete_messages
def generate_lab(update: Update, context: CallbackContext):
    message: Message = update.message

    lab_size = int(message.text)

    if is_even(lab_size):
        lab_size += 1

    if lab_size > LIMIT:
        message.reply_text(f'Size is too long(max: {LIMIT}).😞')
        return None

    add_messages_to_delete(context, message.reply_text("I got size. I'm generating labyrinth ⚙️⚙️⚙️"))
    lab = Labyrinth(lab_size, lab_size)
    lab.generate()

    with NamedTemporaryFile(suffix='.jpg') as lab_image:
        lab.save_as_image(path=lab_image.name)
        message.delete()
        message.reply_document(lab_image)


@end_conv
@delete_messages
def solve_lab(update: Update, context: CallbackContext):
    message: Message = update.message

    add_messages_to_delete(context, message.reply_text("I got labyrinth. I'm solving its."))

    lab_file: File = message.document.get_file()
    with NamedTemporaryFile(suffix='.jpg') as lab_image:
        lab_file.download(lab_image.name)
        lab = Labyrinth.from_image(lab_image.name)

    lab.solve()

    with NamedTemporaryFile(suffix='.jpg') as solved_lab:
        lab.save_as_image(solved_lab.name)
        message.reply_document(solved_lab)


start_command = CommandHandler('start', start)

conversation = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex(START_CONV_PATTERN), start_conv)],
    states={
        CHOSE_MODE: [CallbackQueryHandler(chose_mode)],
        GENERATE_LAB: [MessageHandler(Filters.regex(NUMBER), generate_lab)],
        SOLVE_LAB: [MessageHandler(Filters.document, solve_lab)],
    },
    fallbacks=[start_command],
)
