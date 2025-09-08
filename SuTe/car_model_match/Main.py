# -*- coding: utf-8 -*- 
# @Time : 2024-12-03 10:36 
# @Author : JaredChen
# @File : Main.py
# @Software : PyCharm
# @Description ：调度整个流程

from MysqlConnection import MysqlConnection
from UpdateFields import UpdateFields

class Main:
    def __init__(self):
        self.db = MysqlConnection()
        self.db.connect()

    def run(self):
        update_fields = UpdateFields(self.db)
        print("开始更新零件级别字段...")
        update_fields.update_all_parts_fields()
        print("开始更新套件交集字段...")
        update_fields.update_kit_common_model_ids()
        print("更新流程完成！")

    def close(self):
        self.db.close()

if __name__ == '__main__':
    main_app = Main()
    main_app.run()
    main_app.close()