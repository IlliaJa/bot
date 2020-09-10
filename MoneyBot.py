import telebot
from telebot import types
from datetime import date
from aiohttp import web
import ssl
import MoneyBotCreate as ezmoney
from apscheduler.schedulers.background import BackgroundScheduler
#import plotting
from work_with_db import Db
#import matplotlib.pyplot as plt
import schedule as sch
import re
import logging

api_token = '1318941045:AAFZvhv3Tdfa8JgdN99Z7ptAfRb64gmIor0'
webhook_host = '88.155.138.153'
webhook_port = 8443  # 443, 80, 88 or 8443 (port need to be 'open')
webhook_listen = '0.0.0.0'  # In some VPS you may need to put here the IP addr

webhook_ssl_cert = './url_cert.pem'  # Path to the ssl certificate
webhook_ssl_priv = './url_private.key'  # Path to the ssl private key
webhook_url_base = "https://{}:{}".format(webhook_host, webhook_port)
webhook_url_path = "/{}/".format(api_token)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)
bot = telebot.TeleBot(api_token)
app = web.Application()


scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(sch.everyday_pays_job, 'cron', minute='*')


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id,
                     'Easy money for you, bitch')


# @bot.message_handler(commands=['stat'])
# def stat_message(message):
#     query = '''
#     select category, sum(amount) as amount
#     from payments
#     where uid = {}
#     and strftime('%Y-%m', DATE('now', '-7 days')) =
#         strftime('%Y-%m', date(date, 'unixepoch', 'localtime'))
#     group by category;
#     '''.format(message.from_user.id)
#     result = Db.process_query(query)
#     labels, sizes = [], []
#     for row in result:
#         labels.append(row[0])
#         sizes.append(row[1])
#     fig, ax = plotting.plot_pie(labels, sizes)
#     img = plotting.fig2img(fig)
#     bot.send_photo(message.chat.id, img)


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


# handler schedule categories
@bot.callback_query_handler(func=lambda query: query.data in categories)
def schedule_category(callback_query):
    """
    Handles schedule category and sets it for user and write schedule
    :param callback_query: is a string that can be split on (category, user_id)
    :return:
    """
    data = callback_query.data
    user_id = callback_query.message.from_user.id
    sch.temp_schedule[user_id]['category'] = data
    user = sch.temp_schedule[user_id]
    user_days = [0, 0, 0, 0, 0, 0, 0]
    for day in user['days']:
        user_days[sch.days.index(day)] = 1
    Db.save_to_db((user_id, user_days,))


# handler schedule days
@bot.callback_query_handler(func=lambda query: query.data in sch.days)
def schedule_days(callback_query):
    """
    This function is run when user adds a day to the schedule.
    If we have "Done" we send a message to choose a category, if not we add day to the schedule and wait
    :param callback_query: is a string that can be split on (day of week, user_id)
    :return: None
    """
    data = callback_query.data
    current_days = sch.temp_schedule[callback_query.from_user.id]['days']
    if data != 'Done':
        if data not in current_days:
            current_days.append(data)
            bot.answer_callback_query(callback_query_id=callback_query.id, show_alert=False,
                                      text='Added ' + data)
        else:
            bot.answer_callback_query(callback_query_id=callback_query.id, show_alert=False,
                                      text='Гнида картавая, думаешь самый умный блять, в очко свое дава раза нажми!')
    else:
        markup = types.InlineKeyboardMarkup()
        for c in categories:
            markup.add(types.InlineKeyboardButton(text=c,
                                                  callback_data=c + ';' + str(callback_query.message.from_user.id)))
        message = callback_query.message
        bot.send_message(message.chat.id, 'Which category?', reply_markup=markup)
        bot.delete_message(message.chat.id, message.message_id)


# handler of just payments
@bot.callback_query_handler(func=lambda query: re.match(r'^\d*;\w*$', query.data))
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
    try:
        Db.save_to_db(save_data)
        bot.send_message(callback_query.message.chat.id,
                         "I've written " + callback[0] + ' UAH to ' + callback[1])
    except Exception as er:
        bot.send_message(callback_query.message.chat.id, er)
    finally:
        bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)


@bot.message_handler(commands=['add_schedule'])
def add_schedule(message):
    """
    Is the first step in adding schedule. InlineKeyboard must be handled by schedule_days()

    :param message: '/add_schedule' + ' ' + amount of payment
    :return: None
    """
    amount = message.text.split(' ')[1]
    if amount.isdigit():
        markup = types.InlineKeyboardMarkup()
        for day in sch.days:
            markup.add(types.InlineKeyboardButton(text=day, callback_data=day))
        bot.send_message(message.chat.id, 'Which days?', reply_markup=markup)
        sch.temp_schedule[message.from_user.id] = {'message_id': message.message_id,
                                                   'chat_id': message.chat.id,
                                                   'amount': amount,
                                                   'days': []}
    else:
        bot.send_message(message.chat.id, 'You should send amount of payment')


@bot.message_handler()
def text_message(message):
    """
    Starts an usual payments, InlineKeyboard must be handled by add_payment()
    :param message: just integer, if not write to user
    :return:
    """
    if message.isdigit():
        markup = types.InlineKeyboardMarkup()
        for c in categories:
            markup.add(types.InlineKeyboardButton(text=c,
                                                  callback_data=str(message.text) + ';' + c))
        bot.send_message(message.chat.id, message.text + ' UAH. Which category?', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Type a number.')
    bot.delete_message(message.chat.id, message.message_id)


# Process webhook calls
async def handle(request, bot):
    if request.match_info.get('token') == bot.token:
        request_body_dict = await request.json()
        update = telebot.types.Update.de_json(request_body_dict)
        bot.process_new_updates([update])
        return web.Response()
    else:
        return web.Response(status=403)


categories = ['Home', 'Gadgets', 'Folks', 'Fun', 'Food', 'Transport']

# Remove webhook, it fails sometimes the set if there is a previous webhook
bot.remove_webhook()

# Set webhook
bot.set_webhook(url=webhook_url_base + webhook_url_path,
                certificate=open(webhook_ssl_cert, 'r'))

# Build ssl context
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(webhook_ssl_cert, webhook_ssl_priv)

# Start aiohttp server
web.run_app(
    app,
    host=webhook_listen,
    port=webhook_port,
    ssl_context=context,
)
