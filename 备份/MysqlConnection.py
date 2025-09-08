# -*- coding: utf-8 -*- 
# @Time : 2024-12-03 14:22 
# @Author : JaredChen
# @File : MysqlConnection.py
# @Software : PyCharm
# @Description ：mysql连接

import pymysql

class MysqlConnection:
    def __init__(self,host='localhost',port=3306,user='root',password='123456',database='huiguo_analysis'):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            charset='utf8mb4'
        )
        self.cursor = self.conn.cursor()

    def get_cursor(self):
        if not self.cursor:
            self.connect()  # 自动重连
        return self.cursor

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()