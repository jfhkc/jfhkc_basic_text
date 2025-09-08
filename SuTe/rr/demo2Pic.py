import os.path

import fake_useragent
import requests
from lxml import etree

import os

# 定义图片保存路径并确保目录存在
save_dir = "D:/Projects/VSProjectsSuTe/JT/JT_pics/"
os.makedirs(save_dir, exist_ok=True) 

# url
url = "https://pic.netbian.com/4kdongwu/"
# UA伪装
head = {
    "User-Agent": fake_useragent.UserAgent().random
}

# 发送请求
resp = requests.get(url, headers=head)
resp.encoding = 'gbk'
# 获取响应的数据
# print(resp.json())
resp_text = resp.text

# 数据解析
tree = etree.HTML(resp_text)
li_list = tree.xpath("//div[@class='slist']/ul/li")
print(li_list)

# 新建一个文件夹
if not os.path.exists("./picLic"):
    os.mkdir("./picLib")

for li in li_list:
    pic_url = "https://pic.netbian.com" + li.xpath("./a/img/@src")[0]
    pic_name = li.xpath("./a/img/@alt")[0]
    print(pic_name)
    # 发送请求图片地址
    pic_resp = requests.get(pic_url, headers=head)
    # 获取响应的数据
    pic_content = pic_resp.content
    with open(f"./picLib/{pic_name}.jpg", "wb") as fp:
        fp.write(pic_content)
    break
