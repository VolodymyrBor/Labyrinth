import logging

from telegram.ext import Updater, Dispatcher

from bot_settings import TOKEN
from labbot import start_command, conversation


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def run_bot():
    updater = Updater(TOKEN, use_context=True)
    db: Dispatcher = updater.dispatcher
    db.add_handler(start_command)
    db.add_handler(conversation)

    logging.info("Bot's starting ...")

    updater.start_polling()
    updater.idle()

    logging.info('Bot closed.')


if __name__ == '__main__':
    run_bot()
