# -*- coding: utf-8 -*- 
# @Time : 2024/12/4 14:56 
# @Author : JaredChen
# @File : id_car.py 
# @Software : PyCharm
# @Description ：通过车型id关联出车型
import pymysql
import pandas as pd
from sqlalchemy import create_engine, text
# oe对应的车型表，更改成对应的
part_oe_car_table = 'tecdoc_part_modellist'
# 套装和ids对照表更改成对应的
compare_table_result = 'tecdoc_runing_kit_compare_result'
# id名称，精时的为simple_jsmodelid
car_id = 'tecdoc_model_id'
# 要得到的套装车型表
car_kit_result = 'tecdoc_kit_result'

db_config = {
    "host": "localhost",  # 替换为你的数据库地址
    "port": 3306,
    "user": "root",  # 替换为你的用户名
    "password": "123456",  # 替换为你的密码
    "database": "huiguo_analysis",  # 替换为你的数据库名
    "charset": "utf8mb4"
}

# 使用 SQLAlchemy 创建引擎
engine = create_engine(
    f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}?charset={db_config['charset']}"
)

# 获取数据
# 读取 simple_js_runing_kit_compare_result 表数据
df_kit = pd.read_sql(f"SELECT id, `套件编号`, `同等车型ids` FROM {compare_table_result};", engine)


# 读取 simple_js_part_modellist 表数据
if part_oe_car_table == 'simple_js_part_modellist':
    df_model = pd.read_sql(f"""
        SELECT {car_id}, brand, factory, series, model, model_year, cc, engine_no, fuel_type, kw, hp, date_begin, date_end
        FROM {part_oe_car_table};
    """, engine)
else:
    df_model = pd.read_sql(f"""
            SELECT {car_id},Make AS brand,Factory AS factory,Modelrange AS series,Model AS model,Generation AS model_year,CC AS cc,Enginecode AS engine_no,Fuel AS fuel_type,KW AS kw,PS AS hp,`Year From-Month From` AS date_begin,`Year Till-Month Till` AS date_end
            FROM {part_oe_car_table};
        """, engine)

# 强制转换 car_id 列为整数类型
df_model[car_id] = df_model[car_id].fillna(0).astype(int).astype(str)


# 拆分同等车型ids并匹配
def split_and_match(row):
    # 拆分 `同等车型ids`，生成列表
    model_ids = row["同等车型ids"].split(",")

    # 打印拆分的进度
    print(f"正在拆分套件编号: {row['套件编号']}，拆分的车型数: {len(model_ids)}")
    # 过滤并匹配车型信息

    matched_models = df_model[df_model[car_id].astype(str).isin(model_ids)].copy()

    matched_models.insert(0, "套件编号", row["套件编号"])  # 添加套件编号列
    return matched_models


# 对每个套件编号的记录拆分和匹配
result_df = pd.concat(df_kit.apply(split_and_match, axis=1).tolist(), ignore_index=True)
# 判断表是否存在，存在则删除
drop_table_query = f"DROP TABLE IF EXISTS {car_kit_result};"

# 创建新表 simple_js_kit_result
create_table_query = f"""
CREATE TABLE IF NOT EXISTS {car_kit_result} (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `套件编号` VARCHAR(255) NOT NULL,
    {car_id} INT NOT NULL,
    `brand` VARCHAR(100) CHARACTER SET utf8 DEFAULT NULL COMMENT '品牌名称',
    `factory` VARCHAR(100) CHARACTER SET utf8 DEFAULT NULL COMMENT '厂家',
    `series` VARCHAR(100) CHARACTER SET utf8 DEFAULT NULL COMMENT '车系',
    `model` VARCHAR(100) CHARACTER SET utf8 DEFAULT NULL COMMENT '车型',
    `model_year` VARCHAR(100) CHARACTER SET utf8 DEFAULT NULL COMMENT '年款',
    `cc` VARCHAR(100) CHARACTER SET utf8 DEFAULT NULL COMMENT '排量',
    `engine_no` VARCHAR(500) CHARACTER SET utf8 DEFAULT NULL COMMENT '发动机型号',
    `fuel_type` VARCHAR(100) CHARACTER SET utf8 DEFAULT NULL COMMENT '燃油类型',
    `kw` VARCHAR(50) CHARACTER SET utf8 DEFAULT '' COMMENT '功率(Kw)',
    `hp` VARCHAR(50) CHARACTER SET utf8 DEFAULT '' COMMENT '最大马力(Ps)',
    `date_begin` VARCHAR(100) CHARACTER SET utf8 DEFAULT NULL COMMENT '上市日期',
    `date_end` VARCHAR(100) CHARACTER SET utf8 DEFAULT NULL COMMENT '停产日期'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

# 使用 SQLAlchemy 执行 SQL 语句
with engine.connect() as conn:
    # 删除已有表
    print("正在删除已有的表 (如果存在)...")
    conn.execute(text(drop_table_query))  # 删除表

    # 创建新表
    print("正在创建新表...")
    conn.execute(text(create_table_query))  # 创建新表

    # 分批写入数据库
    batch_size = 1000  # 每次插入的行数
    for i in range(0, len(result_df), batch_size):
        batch = result_df.iloc[i: i + batch_size]

        # 打印正在插入的套件编号
        print(f"正在插入套件编号: {batch['套件编号'].iloc[0]} 到 {batch['套件编号'].iloc[-1]}")

        # 批量插入数据
        try:
            batch.to_sql(
                car_kit_result,
                con=engine,
                if_exists="append",  # 表已存在时追加数据
                index=False,  # 不写入索引
                method="multi"  # 优化批量插入
            )
        except Exception as e:
            print(f"插入失败，错误: {e}")


print(f"数据已成功写入到 {car_kit_result} 表！")

