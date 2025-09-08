# -*- coding: utf-8 -*- 
# @Time : 2024-12-03 14:39 
# @Author : JaredChen
# @File : PartNumberHelper.py 
# @Software : PyCharm
# @Description ：更新compare_table表每个字段的逻辑

class PartNumberHelper:
    # 这个表可以不改
    kit_part_oe_table = 'tsj_oe_numbers'
    # oe对应的车型表，tecdoc和精时的改成对应的
    part_oe_car_table = 'simple_js_part_modellist'
    # 套装过程表，tecdoc和精时的改成对应的
    compare_table = 'simple_js_runing_kit_compare'
    # 车型id字段，tecdoc为tecdoc_modelid
    ids = 'simple_jsmodel_id'

    @staticmethod
    def get_part_importance(part_number):
        """
        零件编号重要度
        判断零件编号的重要性（例如：TC,TN,TR,TG 为重要，其他为次要）。
        Args:
            part_number:
        Returns:
            1/0/-1
        """
        important_parts = ['TC', 'TN', 'TR', 'TG', 'VT', 'TB', 'IP']  #重要零件编号
        non_important_parts = ['FB', 'OS', 'GS', 'SG', 'FP', 'SP', 'BU', 'VA', 'PG', 'WU', 'GK', 'TV', 'TS','LU']  #次要零件编号
        part_prefix = part_number[:2] #获取零件编号的前两位

        if part_prefix in important_parts:
            return 1 #重要
        elif part_prefix in non_important_parts:
            return 0 #次要
        return -1 #默认-1

    @staticmethod
    def f_partnumber_hasoe(kit_number,part_number,db):
        """
        零件编号是否有OE号
        判断零件编号是否在 `tsj_oe_numbers` 中有对应的非空且不等于空字符串的 OE 号。
        Args:
            kit_number:
            db:
        Returns:
            1/0/-1
        """
        try:
            cursor = db.get_cursor()
            # 检查 tsj_oe_numbers 表中是否存在该零件编号并且 OE 号非空且不等于 ''
            query = f"""
            SELECT 1
            FROM {PartNumberHelper.kit_part_oe_table}
            WHERE `套件编号` = %s
            AND `零件编号` = %s
            AND `oe_number` IS NOT NULL
            AND `oe_number` != ''
            LIMIT 1
            """
            cursor.execute(query, (kit_number, part_number))
            result = cursor.fetchone()
            return 1 if result else 0  # 如果有符合条件的记录，返回 1，否则返回 0
        except Exception as e:
            print(f"查询失败: {e}")
            return -1 # 默认返回 -1

    @staticmethod
    def check_vehicle_model_for_oe(part_number,db):
        """
        配件OE号是否有车型
        判断配件编号的 OE 号在 `simple_js_part_modellist` 表中是否存在。
        如果存在，则表示配件有车型。
        Args:
            part_number:
            db:
        Returns:
            1/0/-1
        """
        try:
            cursor = db.get_cursor()
            # 检查 simple_js_part_modellist 表中是否存在该 OE 号
            query = f"""
                    SELECT 1
                    FROM {PartNumberHelper.part_oe_car_table}
                    WHERE `oe_number` = (SELECT `oe_number` FROM tsj_oe_numbers WHERE `零件编号` = %s LIMIT 1)
                    LIMIT 1
                    """
            cursor.execute(query, (part_number,))
            result = cursor.fetchone()
            return 1 if result else 0  # 如果存在 OE 号，则返回 1，否则返回 0
        except Exception as e:
            print(f"查询失败: {e}")
            return -1  # 默认返回 -1

    @staticmethod
    def check_kit_compare(kit_number,part_number,db):
        """
        套装是否进入到比对
        Args:
            kit_number:
            part_number:
            db:
        Returns:
            1/0
        """
        part_importance = PartNumberHelper.get_part_importance(part_number)
        has_oe = PartNumberHelper.f_partnumber_hasoe(kit_number, part_number, db)
        has_vehicle_model = PartNumberHelper.check_vehicle_model_for_oe(part_number, db)
        # 如果所有条件都为 1，则套装进入比对
        if part_importance == 1 and has_oe == 1 and has_vehicle_model == 1:
            return 1  # 进入比对
        return 0  # 不进入比对

    @staticmethod
    def get_vehicle_model_ids(kit_number,part_number,db):
        """
        获取零件的所有车型 ID（通过零件的所有 OE 号在 simple_js_part_modellist 表中查找车型 ID），
        并用逗号连接返回。
        Args:
            kit_number:
            part_number:
            db:

        Returns:
            ','.join(model_ids)/''
        """
        try:
            cursor = db.get_cursor()
            # 查询 tsj_oe_numbers 中该零件的所有 OE 号
            oe_query = f"""
                    SELECT `oe_number`
                    FROM {PartNumberHelper.kit_part_oe_table}
                    WHERE `套件编号` = %s AND `零件编号` = %s
                    """
            cursor.execute(oe_query, (kit_number, part_number))
            oe_numbers = cursor.fetchall()
            if not oe_numbers:
                return ''  # 如果没有找到 OE 号，返回空字符串
            # 将所有 OE 号提取为一个元组，用于 IN 查询
            oe_numbers = tuple(row[0] for row in oe_numbers)
            # 查询 simple_js_part_modellist 表中对应的车型 ID
            model_query = f"""
                        SELECT DISTINCT {PartNumberHelper.ids}
                        FROM {PartNumberHelper.part_oe_car_table}
                        WHERE `oe_number` IN ({','.join(['%s'] * len(oe_numbers))})
                        """
            cursor.execute(model_query, oe_numbers)
            model_ids = cursor.fetchall()
            # 提取车型 ID 并用逗号连接返回
            model_ids = [str(row[0]) for row in model_ids]
            return ','.join(model_ids)
        except Exception as e:
            print(f"查询车型 ID 失败: {e}")
            return ''  # 如果查询失败，返回空字符串

    @staticmethod
    def get_common_model_ids(kit_number,db):
        """
        获取某套件编号下重要配件的车型 ID 的交集。
        如果存在重要配件的车型 ID 为空，则返回空字符串。
        Args:
            kit_number:
            db:
        Returns:
            ','.join(sorted(common_model_ids))/''
        """
        try:
            cursor = db.get_cursor()
            # 查询该套件下所有重要度为1的配件的车型 ID
            query = f"""
                    SELECT `零件ids`
                    FROM {PartNumberHelper.compare_table}
                    WHERE `套件编号` = %s AND `零件编号重要度` = 1
                    """
            cursor.execute(query, (kit_number,))
            parts_model_ids = cursor.fetchall()
            # 如果没有重要配件，直接返回空字符串
            if not parts_model_ids:
                return ''
            # 提取所有非空的车型 ID 列表
            model_id_sets = []
            for part in parts_model_ids:
                part_ids = part[0]  # 零件ids
                if not part_ids:  # 如果车型 ID 为空
                    return ''  # 存在重要配件的车型 ID 为空，直接返回空
                model_id_sets.append(set(part_ids.split(',')))
            # 计算交集
            common_model_ids = set.intersection(*model_id_sets) if model_id_sets else set()
            # 返回交集结果，用逗号拼接
            return ','.join(sorted(common_model_ids))
        except Exception as e:
            print(f"获取套件车型交集失败: {e}")
            return ''











































