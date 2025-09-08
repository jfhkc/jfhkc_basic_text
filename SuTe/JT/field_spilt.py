import pandas as pd
'''
    原始数据：BMW G450 X (K16)	2008 to 2009	JTF403	JTR8
    格式化后：
'''
input_file = "D:/KTM_d.xlsx"
output_file = "D:/JT_t_output3.xlsx"

# 读取数据（假设用制表符分隔）
    # 方法 1：直接读取（假设没有合并单元格或复杂格式）
df = pd.read_excel(input_file, header=None)  # 不指定列名（header=None）



print("Columns in each row:", [len(row) for row in df.values[:5]]) 

# 获取存在的JTF和JTR
df["JTF"] = df[2].str.extract(r"(JTF\d+)")
df["JTR"] = df[3].str.extract(r"(JTR\d+)")
df["JTA"] = df[3].str.extract(r"(JTA\d+)")

# df["brand"]=df[0].str.split().str[0]

# # 拆分成两行（仅当 JTF 或 JTR 存在时）
df_jtf = df[[0, 1, 2, 3, "JTF"]].dropna(subset=["JTF"]).rename(columns={"JTF": 4})  # 替换原第5列为JTF
df_jtr = df[[0, 1, 2, 3, "JTR"]].dropna(subset=["JTR"]).rename(columns={"JTR": 4})
df_jta = df[[0, 1, 2, 3, "JTA"]].dropna(subset=["JTA"]).rename(columns={"JTA": 4})
# 合并
sprocketSplit = pd.concat([df_jtf, df_jtr,df_jta], ignore_index=True)
print(sprocketSplit.head())
sprocketSplit["brand"] = sprocketSplit[0].str.split().str[0]
sprocketSplit["year"] = sprocketSplit[1].str.split().str[0]
print(sprocketSplit["brand"].head())
print(sprocketSplit["year"].head())

result= sprocketSplit[[0,"brand","brand",1,"year",2,3,4]].copy()
print(result.head())
print("开始写入到表格中")

# result.to_csv(output_file, sep="\t", index=False, header=False)
result.to_excel(output_file,index=False,header=False,engine="openpyxl")

