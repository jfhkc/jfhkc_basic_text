# -*- coding: utf-8 -*- 
# @Time : 2024/12/3 14:59 
# @Author : JaredChen
# @File : UpdateFields.py 
# @Software : PyCharm
# @Description ：调用PartNumberHelper来更新compare_table表
from PartNumberHelper import PartNumberHelper

class UpdateFields:
    def __init__(self,db):
        self.db = db
        self.cursor = db.get_cursor()
        self.PartNumberHelper = PartNumberHelper()

    def update_all_parts_fields(self):
        """
        更新所有零件级别字段
        Returns:
        """
        try:
            self.cursor.execute(f"""
            SELECT auto_id, `套件编号`, `零件编号`
            FROM {self.PartNumberHelper.compare_table}
            WHERE `零件编号` IS NOT NULL AND `套件编号` IS NOT NULL
            """)
            rows = self.cursor.fetchall()
            for row in rows:
                auto_id, kit_number, part_number = row
                self.update_fields_for_row(auto_id, kit_number, part_number)
            self.db.conn.commit()
            print("零件级别字段更新完成")
        except Exception as e:
            self.db.conn.rollback()
            print(f"零件级别字段更新失败{e}")


    def update_fields_for_row(self,auto_id,kit_number,part_number):
        """
        更新某一行的零件级别字段（零件ids 等）。
        Args:
            auto_id:
            kit_number:
            part_number:
        Returns:
        """
        # 赋值零件编号重要度
        part_importance = PartNumberHelper.get_part_importance(part_number)
        # 赋值零件编号是否有OE号
        has_oe = PartNumberHelper.f_partnumber_hasoe(kit_number, part_number, self.db)
        # 赋值配件OE号是否有车型
        has_vehicle_model = PartNumberHelper.check_vehicle_model_for_oe(part_number, self.db)
        # 计算套装是否进入到比对
        is_in_comparison = PartNumberHelper.check_kit_compare(kit_number, part_number, self.db)
        # 查询零件的所有车型 ID，并用逗号拼接
        part_model_ids = PartNumberHelper.get_vehicle_model_ids(kit_number, part_number, self.db)
        # 更新字段
        update_query = f"""
                UPDATE {self.PartNumberHelper.compare_table} 
                SET 
                    `零件编号重要度` = %s,
                    `零件编号是否有OE号` = %s,
                    `配件OE号是否有车型` = %s,
                    `套装是否进入到比对` = %s,
                    `零件ids` = %s
                WHERE auto_id = %s
                """
        self.cursor.execute(update_query, (
            part_importance,  # 1 或 0
            has_oe,  # 1 或 0
            has_vehicle_model,  # 1 或 0
            is_in_comparison,  # 1 或 0
            part_model_ids,  # 零件的车型 IDs
            auto_id
        ))

    def update_kit_common_model_ids(self):
        """
        更新套件交集字段，并同时更新套装是否有车型。
        Returns:

        """
        try:
            # 查询所有套件编号
            self.cursor.execute(f"""
                    SELECT DISTINCT `套件编号`
                    FROM {self.PartNumberHelper.compare_table}
                    WHERE `套件编号` IS NOT NULL
                    """)
            kits = self.cursor.fetchall()

            for kit in kits:
                kit_number = kit[0]

                # 获取套件下重要零件的车型 ID 交集
                common_model_ids = PartNumberHelper.get_common_model_ids(kit_number, self.db)

                # 是否有交集
                has_common_models = 1 if common_model_ids else 0

                # 更新交集字段
                update_query = f"""
                        UPDATE {self.PartNumberHelper.compare_table} 
                        SET `同一个套件下零件编号比对时是否有同等车型` = %s,
                            `同一个套件下零件编号比对时同等车型ids` = %s
                        WHERE `套件编号` = %s
                        """
                self.cursor.execute(update_query, (
                    has_common_models,  # 是否存在交集
                    common_model_ids,  # 交集车型 ID
                    kit_number
                ))

                # 更新“套装是否有车型”字段
                update_has_model_query = f"""
                        UPDATE {self.PartNumberHelper.compare_table} 
                        SET `套装是否有车型` = %s
                        WHERE `套件编号` = %s
                        """
                self.cursor.execute(update_has_model_query, (
                    has_common_models,  # 如果交集不为空，则表示套装有车型
                    kit_number
                ))

            self.db.conn.commit()
            print("套件交集字段和套装是否有车型字段更新完成")

        except Exception as e:
            self.db.conn.rollback()
            print(f"更新套件交集字段失败: {e}")

