
#!/usr/bin/env python
# developer : ruslan spiridonoff 
# thanks to  python-telegram-bot 
# This program is dedicated to the public domain under the CC0 license.


import logging

from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard = [['late', 'moca'],
                  ['double', 'single'],
                  ['hot_chocolat', 'turkish cafe'],
                  ['address'],
                  ['Done']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
reply_keyboard = [['1', '2', '3'],
                  ['4', '5', '6'],
                  ['7', '8', '9']]
numbers = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def facts_to_str(user_data):
    facts = list()

    for key, value in user_data.items():
        facts.append('{} - {}'.format(key, value))

    return "\n".join(facts).join(['\n', '\n'])


def start(update, context):
    update.message.reply_text(
        "welcom,how can i help you ?",

        reply_markup=markup)

    return CHOOSING


def regular_choice(update, context):
    text = update.message.text
    context.user_data['choice'] = text
    update.message.reply_text(
        'ok how many {} do you want ?'.format(text.lower()),
        reply_keyboard=numbers)

    return TYPING_REPLY


def custom_choice(update, context):
    text = update.message.text
    context.user_data['choice'] = text
    update.message.reply_text('enter you address ', reply_keyboard=numbers)

    return TYPING_REPLY


def received_information(update, context):
    user_data = context.user_data
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    del user_data['choice']

    update.message.reply_text("your order :"
                              "{} "
                              "if you want to change just click .".format(
                                  facts_to_str(user_data)),
                              reply_markup=markup)

    return CHOOSING


def done(update, context):
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']

    update.message.reply_text("your total"
                              "{}"
                              "untile next time".format(facts_to_str(user_data)))

    user_data.clear()
    return ConversationHandler.END


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(
        "token", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        per_message=True,
        entry_points=[CommandHandler('start', start)],

        states={
            CHOOSING: [MessageHandler(Filters.regex('^(late|double|single|turk|hot_chocolat|moca)$'),
                                      regular_choice),
                       MessageHandler(Filters.regex('^address$'),
                                      custom_choice)
                       ],

            TYPING_CHOICE: [
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                               regular_choice)],

            TYPING_REPLY: [
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                               received_information)],
        },

        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)]
    )

    dp.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
    print(dp)
    print(updater)


if __name__ == '__main__':
    main()
