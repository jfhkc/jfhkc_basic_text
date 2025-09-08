import base64
import re
import time

import pymysql
from fontTools.ttLib import TTFont
# 人人车爬虫
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options

# 记录主键，排除可能出现重复的主键
car_id_list = []

# 写入数据库
# 建表语句
"""
create table rrCar(
    car_id bigint PRIMARY KEY
    , car_brand varchar(255)
    , car_title varchar(255)
    , car_year int
    , car_mile float
    , car_price float
	, create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	, update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP on UPDATE CURRENT_TIMESTAMP
);
"""


def mysql_insert(conn, cur, car_data):

    try:
        insert_sql = 'insert into project.rrCar(car_id,car_brand, car_title, car_year, car_mile, car_price) values(%s,%s,%s,%s,%s,%s)'
        cur.executemany(insert_sql, car_data)
    except Exception as e:
        print(e)
        print("failure")
    else:
        conn.commit()
        print("Success")


# 字体解析
def font_analysis(driver):
    style_text = driver.find_element(By.XPATH, "//style[1]").get_attribute("innerHTML")

    base64_str = re.match("(.*?)base64,(.*?)'(.*?)", style_text).group(2)
    base64_bytes = base64.decodebytes(base64_str.encode())
    with open("./rrcar.ttf", 'wb') as fp:
        fp.write(base64_bytes)

    ttf = TTFont("./rrcar.ttf")
    # 数字 与  uni编码对应关系
    li = ttf.getGlyphOrder()[1:]
    # uni编码 与 汉字的ascii码的对应关系
    dic = ttf.getBestCmap()

    new_dic = {}
    for k, v in dic.items():
        # v => li.index(v)
        new_dic[chr(k)] = li.index(v)

    return new_dic


# 获取页面内的数据信息
def page_inner_info(driver, font_dic):
    # find_elements 获取所有的li标签
    # time.sleep(20)
    li_list = driver.find_elements(By.XPATH, "//ul[@class='infos infos-card h-clearfix']/li")
    # print(li_list)

    car_data = []

    for li in li_list:
        try:
            car_id = li.get_attribute("data-entid")
            car_brand = li.find_element(By.XPATH, "div[@class='info--wrap']//span[@class='info_link']/font").text.strip()
            # brand = li.find_element(By.CLASS_NAME, "info_link").text.strip()
            car_title = li.find_element(By.XPATH, "div[@class='info--wrap']//span[@class='info_link']").text.strip()
            car_year_mile = li.find_element(By.XPATH, "div[@class='info--wrap']//div[@class='info_params']").text.strip()
            car_price = li.find_element(By.XPATH,
                                        "div[@class='info--wrap']//b[@class='info_price fontSecret']").text.strip()

            car_year = re.match("(\d+)", car_year_mile).group(1)
            car_mile = re.match("(.*?)·([\d\.]+)", car_year_mile).group(2)

            new_car_price = ''
            for i in car_price:
                if i == '.':
                    new_car_price += i
                else:
                    new_car_price += str(font_dic.get(i))

            # 价格的字体反爬解析

            print(car_id, car_brand, "# ", car_title, "# ", car_year, "# ", car_mile, "# ", car_price, '#', new_car_price)

            # 如果id不在car_id_list内 则做追加和加入data的操作
            if car_id not in car_id_list:
                car_id_list.append(car_id)
                car_data.append((car_id, car_brand,car_title, car_year, car_mile, new_car_price))
            # break
        except Exception as e:
            print(e)
            continue
    return car_data

# 获取全部的城市拼音称呼
def get_all_cities(driver):

    js = """document.getElementsByClassName('citySelectWrap')[0].style.display='block';"""
    driver.execute_script(js)

    time.sleep(5)

    city_list = []
    a_list = driver.find_elements(By.XPATH,"//div[@class='citySelectWrap']//a[@class='city-item']")
    for a in a_list:
        city_list.append(a.get_attribute("listname"))

    print(city_list)
    return city_list

if __name__ == '__main__':
    # 配置无头模式
    opt = Options()
    opt.add_argument("--headless")

    driver = webdriver.Edge(options=opt)
    conn = pymysql.connect(host='master', port=3306, user='root', password='123456')
    cur = conn.cursor()

    # 这个地址只是用于获取所有的城市信息
    url = f'https://www.renrenche.com/hf/ershouche'
    driver.get(url)
    time.sleep(5)
    city_list = get_all_cities(driver)

    for city in city_list:
        time.sleep(5)
        print(city)
        url = f'https://www.renrenche.com/{city}/ershouche'
        driver.get(url)

        # 获取字体解析的信息
        font_dic = font_analysis(driver)
        # 将驱动传入函数内  在函数内部去获取页面的详细信息
        car_data = page_inner_info(driver, font_dic)
        # 数据写入mysql
        mysql_insert(conn, cur, car_data)
        print(city)

    # 变换网页的时候出现了问题 导致后续网页被反爬了
    # for i in range(1,3):
    #     time.sleep(5)
    #     # url = f'https://www.renrenche.com/hf/ershouche/pn{i}/?reentries=%7B%22reentry_id%22%3A%22a661f062-9c0e-4290-8625-ca1c50003187%22%7D'
    #     url = f'https://www.renrenche.com/hf/ershouche'
    #     driver.get(url)
    #
    #     # 获取字体解析的信息
    #     font_dic = font_analysis(driver)
    #     # 将驱动传入函数内  在函数内部去获取页面的详细信息
    #     car_data = page_inner_info(driver, font_dic)
    #     # 数据写入mysql
    #     mysql_insert(conn, cur, car_data)
    driver.close()
    cur.close()
    conn.close()
