# import pandas as pd

# df = pd.read_excel('D://yst0806.xlsx')
# print("文件中的列名:", df.columns.tolist())
# print(df.head())
# # results = []
# # for _, row in df.iterrows():
# #     values = row['oe'].split()
# #     for value in values:
# #         results.append({
# #             'main_value': row['p_num'], 
# #         })
# results = []
# for _, row in df.iterrows():
#     if pd.isna(row['oe']):
#         print(f"警告: 第 {_+1} 行oe列为空")
#         continue
    
#     # 将值转换为字符串并分割
#     values = str(row['oe']).split()
#     for value in values:
#         # 清洗值并添加到结果
#         clean_value = value.strip()
#         if clean_value:  # 确保值不为空
#             results.append({
#                 'p_num': row['p_num'],
#                 'oe_value': clean_value
#             })

# # 创建新DataFrame
# result_df = pd.DataFrame(results)

# # 保存结果
# result_df.to_excel('D://yst_out_end.xlsx', index=False)
# print("完成----------------")

import pandas as pd

#供应商编号保留0
df = pd.read_excel('D://yst0806.xlsx', dtype={'p_num': str})

results = []
for _, row in df.iterrows():
    p_num = str(row['p_num']).strip()
    if not p_num: continue
    
    if pd.isna(row['oe']): continue
    
    values = str(row['oe']).split()
    for value in values:
        clean_value = value.strip()
        if clean_value:
            results.append({
                '供应商编号': p_num,
                'oe': clean_value
            })

result_df = pd.DataFrame(results)

result_df.to_csv('D://yst_out_0.csv', index=False)
print("已保存")