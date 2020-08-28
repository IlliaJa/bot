import telebot
from telebot import types
import requests
import json
from datetime import date
from aiohttp import web
import ssl
import MoneyBotCreate as ezmoney
import sqlite3

bot = telebot.TeleBot('1318941045:AAFZvhv3Tdfa8JgdN99Z7ptAfRb64gmIor0')


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id,
                     'Easy money for you, bitch')


@bot.message_handler(commands=['help'])
def help_message(message):
    mes_text = '''
        Coming soon
    '''
    bot.send_message(message.chat.id, mes_text)


@bot.message_handler(commands=['mypays'])
def mypays_message(message):
    c, cur = init_db()
    uid = (message.from_user.id,)
    cur.execute('''
    select * from payments
    where uid = ?
    ''', uid)
    for row in cur.fetchall():
        bot.send_message(message.chat.id, str(row))
    bot.send_message(message.chat.id, 'suka bomg')


@bot.message_handler(commands=['create'])
def create_message(message):
    c, cur = init_db()
    cr_table(cur)
    close_conn(c)


@bot.callback_query_handler(func=lambda call: True)
def query_text(callback_query):
    bot.send_message(callback_query.message.chat.id, 'Writen ' + str(callback_query.data))
    save_to_db(callback_query.data.split(';'))
    bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)


@bot.message_handler()
def text_message(message):
    try:
        int(message.text)
        markup = types.InlineKeyboardMarkup()
        for c in ['Home', 'Gadgets', 'Folks', 'Fun', 'Food', 'Transport']:
            markup.add(types.InlineKeyboardButton(text=c,
                                                  callback_data=str(message.from_user.id) + ';' + str(message.date) +
                                                                ';' + str(message.text) + ';' + c + ';note'))
        bot.send_message(message.chat.id, message.text + ' UAH. Which category?', reply_markup=markup)
    except ValueError:
        bot.send_message(message.chat.id, 'Type a number.')
    finally:
        bot.delete_message(message.chat.id, message.message_id)


def save_to_db(data):
    c, curr = init_db()
    write_to_db(c, curr, data)
    close_conn(c)


def init_db():
    conn = sqlite3.connect('payments.db')
    cur = conn.cursor()
    return conn, cur


def write_to_db(c, cur, data):
    """
    :param cur:
    :param data: (uid int, date date, sum float, category text, note text
    :return: nothing
    """
    cur.execute('''
    insert into payments
    (uid, date, sum, category, note)
    values(?,?,?,?,?)
    ''', data)
    c.commit()


def cr_table(cur):
    cur.execute('''
    create table payments (
        id integer primary key autoincrement,
        uid bigint,
        date date, 
        sum float, 
        category text, 
        note text
    )
    ''')


def close_conn(c):
    c.close()


bot.polling()
