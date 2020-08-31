from work_with_db import Db
import datetime as dt
from time import time


def add_to_schedule():
    query = '''
    insert into schedule
    values(?, ?, ?, ?, ?)
    '''
    Db.save_to_db('schedule', data)


def everyday_pays_job():
    query = '''
    select *
    from schedule'''
    tasks = Db.process_query(query)
    # days is a string like a 1100110. Seven days, one if we have to add
    for task in tasks:
        if tasks[1][dt.datetime.today().weekday()] == 1:
            data = (None, task[0], time(), task[1], task[2], task[3])
            Db.save_to_db('payments', data)


days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'Done']

temp_schedule = {}
