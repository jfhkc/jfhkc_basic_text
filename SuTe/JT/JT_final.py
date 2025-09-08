import random
import time

import fake_useragent
import pymysql
import requests
from fake_useragent import UserAgent
from lxml import etree

# 出现InsecureRequestWarning，采集无影响但使用urllib3.disable_warnings()可以消除
import urllib3

urllib3.disable_warnings()


car_shape_fail = []


def mysql_insert(conn, cur, car_shape_all):
    '''
    todo mysql建表语句
    1.JT_Gears
    create table if not exists JT_Gears(
    car_shape varchar(100) primary key
    ,car_brand varchar(20)
    ,car_years varchar(100)
    ,car_year_initial varchar(10)
    ,jf_number varchar(10)
    ,teeth varchar(120)
    ,availableSizes varchar(120)
);

    2.JT_number_fail
    create table if not exists JT_number_fail(
    s_num bigint primary key
    ,url varchar(255)
);

    '''

    try:
        insert_sql_JT_Gears = 'insert into zinnia.JT_Gears(car_shape, car_brand, car_years, car_year_initial, jf_number, teeth, availableSizes) values(%s,%s,%s,%s,%s,%s,%s)'
        cur.executemany(insert_sql_JT_Gears, car_shape_all)
        


    except Exception as e:
        print(e)
        print("failure")
    else:
        conn.commit()
        print("Success")


def page_inner_info(url):
    '''
        todo http连接过多-关闭SSH认证，verify参数设置为False
    '''
    car_shape_all = []
    response = session.get(url, headers=headers, timeout=10, stream=True, verify=False)
    # response = requests.get(url, headers=headers, stream=True, verify=Falset=(5,5))
    print(f"正在抓取 {url} | 状态码: {response.status_code}")

    if response.status_code != 200:
        print(f"异常状态码，跳过当前页面")
        # continue  # 跳过错误页面
        return

    # HTML解析文本
    html = etree.HTML(response.text)

    # 元素不存在抛异常
    try:
        car_shape = html.xpath("//div[@class='model']/h2/text()")[0].strip()
        car_brand = car_shape.split()[0]
        car_years = html.xpath("//div[@class='yeartext']/text()")[0].strip()
        car_year_initial = car_years.split()[0]
        # print(f"车型: {car_shape}, 年份: {car_years}")
        # print(car_brand)
        # print(f"{car_shape},{car_years}")
    except IndexError:
        print(f"定位不到s{i}界面")
        car_shape_fail.append(i)
        # continue
        return

    # 链轮编号
    jt_3p = html.xpath("//div[@class='model']/div[@class='parts']")
    for jt_p in jt_3p[:2]:
        jt_shapes = jt_p.xpath(".//div[@class='part']")
        for jf_shape in jt_shapes:
            try:
                # 清理数据-strip
                jf_number = jf_shape.xpath(".//div[1]/p[1]/a/text()")[0].strip()
                teeth = jf_shape.xpath(".//div[1]/p[2]/text()")[0].strip()
                availableSizes = jf_shape.xpath(".//div[1]/p[3]/text()")[0].strip()
                pic_url=jf_shape.xpath(".//div[1]/a[2]/img/text()")[0]
                # print(f"链轮编号: {jf_number}")
                # print(f"链轮齿数: {teeth}")
                # print(f"链轮齿数: {pic_url}")
                print(pic_url)
                car_shape_all.append(
                    (car_shape, car_brand, car_years, car_year_initial, jf_number, teeth, availableSizes))
            except (IndexError, AttributeError) as e:
                print(f"链轮号获取失败: {str(e)}")
            break

    time.sleep(random.uniform(0.3, 2.5))
    return car_shape_all


if __name__ == '__main__':
    conn = pymysql.connect(host='localhost', port=3306, user='root', password='123456')
    cur = conn.cursor()
    session = requests.Session()
    ua = UserAgent()
    headers = {
        "User-Agent": fake_useragent.UserAgent().random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.jtsprockets.com/",
        "Connection": "close"
    }
    for i in range(3,4):
        # for i in [42, 48, 58, 59, 61, 64, 68, 69, 72, 74]:
        try:
            url = f'https://www.jtsprockets.com/catalogue/model/s{i}/'
            # page_inner_info(url)
            # session发送请求
            car_shape_all = page_inner_info(url)
            mysql_insert(conn, cur, car_shape_all)
            mysql_insert(conn, cur, car_shape_fail)
        # 页面请求失败，终止
        except requests.exceptions.RequestException as e:
            print(f"请求异常: {str(e)},正在跳过继续")
            car_shape_fail.append(i)
            i=i-1;
            time.sleep(random.uniform(9, 17))
            continue
        except Exception as e:
            print(f"未知错误: {str(e)}")
            continue  # 跳过当前页面继续执行
        print(car_shape_all)

    insert_sql_JT_number_fail='insert into zinnia.JT_number_fail(s_num) values(%s)'
    cur.executemany(insert_sql_JT_number_fail,car_shape_fail)
    print(car_shape_fail)

    cur.close()
    conn.close()
