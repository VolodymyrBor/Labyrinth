import logging
from tempfile import NamedTemporaryFile

from telegram.update import Update
from telegram.message import Message
from telegram.ext.callbackcontext import CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, File
from telegram.ext import (Updater, CommandHandler, Dispatcher, ConversationHandler, MessageHandler,
                          Filters, CallbackQueryHandler)

from labirinth import Labyrinth
from bot_settings import TOKEN
from labbot.patterns import NUMBER
from labirinth.utils import is_even


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

BLOCK_SIZE = 64


CHOSE_MODE, GENERATE_LAB, SOLVE_LAB = range(3)

GENERATE, SOLVE = range(2)


def start(update: Update, context: CallbackContext):
    message: Message = update.message

    keyboard = [
        [
            InlineKeyboardButton('Generate', callback_data=str(GENERATE)),
            InlineKeyboardButton('Solve', callback_data=str(SOLVE)),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    message.reply_text('➖➖➖➖➖➖➖➖', reply_markup=reply_markup)
    return CHOSE_MODE


def chose_mode(update: Update, context: CallbackContext):
    query: CallbackQuery = update.callback_query
    query.answer()
    mode = int(query.data)
    if mode == GENERATE:
        query.edit_message_text('Enter lab size (e.g 64):')
        return GENERATE_LAB

    if mode == SOLVE:
        query.edit_message_text('Send lab in doc.')
        return SOLVE_LAB

    raise ValueError('Wrong mode.')


def generate_lab(update: Update, context: CallbackContext):
    message: Message = update.message

    lab_size = int(message.text)

    if is_even(lab_size):
        lab_size += 1

    message.reply_text("I got size. I'm generating labyrinth ⚙️⚙️⚙️")

    lab = Labyrinth(lab_size, lab_size)
    lab.generate()

    with NamedTemporaryFile(suffix='.jpg') as lab_image:
        lab.save_as_image(path=lab_image.name)
        message.delete()
        message.reply_document(lab_image)

    return ConversationHandler.END


def solve_lab(update: Update, context: CallbackContext):
    message: Message = update.message

    message.reply_text("I got labyrinth. I'm solving its.")

    lab_file: File = message.document.get_file()
    with NamedTemporaryFile(suffix='.jpg') as lab_image:
        lab_file.download(lab_image.name)
        lab = Labyrinth.from_image(lab_image.name)

    lab.solve()

    with NamedTemporaryFile(suffix='.jpg') as solved_lab:
        lab.save_as_image(solved_lab.name)
        message.reply_document(solved_lab)

    return ConversationHandler.END


start_command = CommandHandler('start', start)

conversation = ConversationHandler(
    entry_points=[start_command],
    states={
        CHOSE_MODE: [CallbackQueryHandler(chose_mode)],
        GENERATE_LAB: [MessageHandler(Filters.regex(NUMBER), generate_lab)],
        SOLVE_LAB: [MessageHandler(Filters.document, solve_lab)],
    },
    fallbacks=[start_command],
)


def main():
    updater = Updater(TOKEN, use_context=True)
    db: Dispatcher = updater.dispatcher
    db.add_handler(conversation)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
