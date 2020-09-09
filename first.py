import telebot
from telebot import types
from datetime import date
from aiohttp import web
import ssl
import MoneyBotCreate as ezmoney
from apscheduler.schedulers.background import BackgroundScheduler
import plotting
from work_with_db import Db
import matplotlib.pyplot as plt
import schedule as sch
import re

bot = telebot.TeleBot('1318941045:AAFZvhv3Tdfa8JgdN99Z7ptAfRb64gmIor0')
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(sch.everyday_pays_job, 'cron', minute='*')


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id,
                     'Easy money for you, bitch')


@bot.message_handler(commands=['stat'])
def stat_message(message):
    query = '''
    select category, sum(amount) as amount
    from payments
    where uid = {}
    and strftime('%Y-%m', DATE('now', '-7 days')) =
        strftime('%Y-%m', date(date, 'unixepoch', 'localtime'))
    group by category;
    '''.format(message.from_user.id)
    result = Db.process_query(query)
    labels, sizes = [], []
    for row in result:
        labels.append(row[0])
        sizes.append(row[1])
    fig, ax = plotting.plot_pie(labels, sizes)
    img = plotting.fig2img(fig)
    bot.send_photo(message.chat.id, img)


@bot.message_handler(commands=['help'])
def help_message(message):
    mes_text = '''
        Coming soon
    '''
    bot.send_message(message.chat.id, mes_text)


@bot.message_handler(commands=['pays'])
def pays_message(message):
    c, cur = Db.init_db()
    uid = (message.from_user.id,)
    cur.execute('''
    select * from payments
    where uid = ?
    ''', uid)
    for row in cur.fetchall():
        bot.send_message(message.chat.id, str(row))
    bot.send_message(message.chat.id, 'suka bomg')





def add_payment(callback_query):
    """
    Handles just payments from text_message()

    callback_query can be split on (float amount, text category)
    :param callback_query:
    :return:
    """
    callback = callback_query.data.split(';')
    save_data = {
        'table': 'payments',
        'data': {
            'uid': callback_query.from_user.id,
            'date': callback_query.message.date,
            'amount': callback[0],
            'category': callback[1]
        }
    }
    Db.save_to_db(save_data)
    bot.send_message(callback_query.message.chat.id, "I've written " + callback[0] + ' UAH to ' + callback[1])
    bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)





@bot.message_handler(content_types=['text'])
def text_message(message):
    """
    Starts an usual payments, InlineKeyboard must be handled by add_payment()
    :param message: just integer, if not write to user
    :return:
    """
    try:
        int(message.text)
        markup = types.InlineKeyboardMarkup()
        for c in categories:
            markup.add(types.InlineKeyboardButton(text=c,
                                                  callback_data=str(message.text) + ';' + c))
        msg = bot.send_message(message.chat.id, message.text + ' UAH. Which category?', reply_markup=markup)
        bot.register_next_step_handler(msg, add_payment)
    except ValueError:
        bot.send_message(message.chat.id, 'Type a number.')
    finally:
        bot.delete_message(message.chat.id, message.message_id)


categories = ['Home', 'Gadgets', 'Folks', 'Fun', 'Food', 'Transport']

bot.enable_save_next_step_handlers(delay=1)
bot.load_next_step_handlers()
bot.polling()
