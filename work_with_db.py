import sqlite3


class Db:
    @staticmethod
    def process_query(query):
        c, curr = Db.init_db()
        curr.execute(query)
        res = curr.fetchall()
        Db.close_conn(c)
        return res

    @staticmethod
    def save_to_db(data):
        c, curr = Db.init_db()
        Db.write_to_db(c, curr, data)
        Db.close_conn(c)

    @staticmethod
    def init_db():
        conn = sqlite3.connect('payments.db')
        cur = conn.cursor()
        return conn, cur

    @staticmethod
    def write_to_db(c, cur, data):
        """
        :param cur:
        :param data: {'table' :table_name, 'data': {column_name: value_to_insert, }
        :return: nothing
        """
        columns_str = '('
        values_str = '('
        for column in data['data']:
            columns_str += str(column) + ','
            # need to add quotes if datatype is text
            if column in ['category', 'note']:
                values_str += '"' + str(data['data'][column]) + '"' + ','
            else:
                values_str += str(data['data'][column]) + ','
        columns_str = columns_str.rstrip(',') + ')'
        values_str = values_str.rstrip(',') + ')'
        cur.execute('''
        insert into {0}
        {1}
        values {2}
        '''.format(data['table'], columns_str, values_str))
        c.commit()

    @staticmethod
    def close_conn(c):
        c.close()
