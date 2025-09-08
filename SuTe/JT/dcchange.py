import fake_useragent
import requests
from lxml import etree
from fake_useragent import UserAgent
from urllib3.util.retry import Retry
import time
import random

session = requests.Session()
ua = UserAgent()

headers = {
    "User-Agent": fake_useragent.UserAgent().random,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.jtsprockets.com/",
    "Connection": "keep-alive"
}

car_shape_all=[]
car_shape_fail=[]
for i in range(1,3):
    try:
        url = f'https://www.jtsprockets.com/catalogue/model/s{i}/'

        # session发送请求
        response = session.get(url, headers=headers, timeout=10)
        print(f"正在抓取 {url} | 状态码: {response.status_code}")

        if response.status_code != 200:
            print(f"异常状态码，跳过当前页面")
            continue  # 跳过错误页面

        # HTML解析文本
        html = etree.HTML(response.text)

        # 元素不存在抛异常
        try:
            car_shape = html.xpath("//div[@class='model']/h2/text()")[0].strip()
            car_brand=car_shape.split()[0]
            car_years = html.xpath("//div[@class='yeartext']/text()")[0].strip()
            print(f"车型: {car_shape}, 年份: {car_years}")
            print(car_brand)
            print(f"{car_shape},{car_years}")
        except IndexError:
            print(f"定位不到s{i}界面")
            car_shape_fail.append(i)
            continue

        # 链轮编号
        jt_3p = html.xpath("//div[@class='model']/div[@class='parts']")
        for jt_p in jt_3p[:2]: 
            jt_shapes = jt_p.xpath(".//div[@class='part']")
            for jf_shape in jt_shapes:
                try:
                    # 清理数据-strip
                    jf_number = jf_shape.xpath(".//div[1]/p[1]/a/text()")[0].strip()
                    teeth = jf_shape.xpath(".//div[1]/p[2]/text()")[0].strip()
                    print(f"链轮编号: {jf_number}")
                    print(f"链轮齿数: {teeth}")
                    car_shape_all.append((car_shape,car_years,jf_number,teeth))
                except (IndexError, AttributeError) as e:
                    print(f"链轮号获取失败: {str(e)}")
                break 

        time.sleep(random.uniform(3,8))

    #页面请求失败，终止
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {str(e)}")
        time.sleep(15)
        continue  
    except Exception as e:
        print(f"未知错误: {str(e)}")
        continue  # 跳过当前页面继续执行
print(car_shape_fail)
print(car_shape_all)
'''
1th
fail=[5, 14, 15, 23, 27, 32, 33, 42, 48]
all_shape=[('Honda C50', '1970 to 1975', 'JTF253'), ('Honda C50', '1970 to 1975', 'JTR256'),
            ('Honda C50', '1975 to 1980', 'JTF253'), ('Honda C50', '1975 to 1980', 'JTR257'), 
            ('Honda C50 Z2,ZZ,L', '1980 to 1982', 'JTF253'), ('Honda C50 Z2,ZZ,L', '1980 to 1982', 'JTR257'), 
            ('Honda C50 C Cub', '1982 to 1984', 'JTF252'), ('Honda C50 C Cub', '1982 to 1984', 'JTR257'), 
            ('Honda C50 E Super Cub', '1984 to 1985', 'JTF252'), ('Honda C50 E Super Cub', '1984 to 1985', 'JTR257'), 
            ('Honda C50 LAC,LAE', '1982 to 1987', 'JTF253'), ('Honda C50 LAC,LAE', '1982 to 1987', 'JTR257'), 
            ('Honda C50 E,LAG', '1988', 'JTF253'), ('Honda C50 E,LAG', '1988', 'JTR257'), 
            ('Honda C50 GLX — Greece', '1991 to 1998', 'JTF252'), ('Honda C50 GLX — Greece', '1991 to 1998', 'JTR211'),
            ('Honda CB50 J', '1975 to 1982', 'JTF252'), ('Honda CB50 J', '1975 to 1982', 'JTR256'), 
            ('Honda CF50 Chaly', '1979 to 1996', 'JTF253'), ('Honda CF50 Chaly', '1979 to 1996', 'JTR256'), 
            ('Honda CY50 — Germany', '1977 to 1984', 'JTF253'), ('Honda CY50 — Germany', '1977 to 1984', 'JTR256'), 
            ('Honda CB50 J — Germany', '1977 to 1984', 'JTF252'), ('Honda CB50 J — Germany', '1977 to 1984', 'JTR256'), 
            ('Honda MB5 — USA', '1982', 'JTF253'), ('Honda MB5 — USA', '1982', 'JTR239'), 
            ('Honda MB50 SA', '1980 to 1982', 'JTF252'), ('Honda MB50 SA', '1980 to 1982', 'JTR239'), 
            ('Honda MB50 SA — Germany', '1979 to 1983', 'JTF252'), ('Honda MB50 SA — Germany', '1979 to 1983', 'JTR239'),
            ('Honda MBX50 SD,SF', '1984 to 1986', 'JTF252'), ('Honda MBX50 SD,SF', '1984 to 1986', 'JTR239'), 
            ('Honda MBX50 SDF (40 kmh)  — Germany', '1985', 'JTF253'), ('Honda MBX50 SDF (40 kmh)  — Germany', '1985', 'JTR239'), ('Honda MBX50 SDH ( 50 kmh)  — Germany', '1987', 'JTF253'), ('Honda MBX50 SDH ( 50 kmh)  — Germany', '1987', 'JTR239'), ('Honda MT50 S', '1980 to 1981', 'JTF253'), ('Honda MT50 S', '1980 to 1981', 'JTR239'), ('Honda MTX50 S-C,E', '1983 to 1985', 'JTF252'), ('Honda MTX50 S-C,E', '1983 to 1985', 'JTR239'), ('Honda MTX50  (AD05) — Germany', '1982 to 1984', 'JTF253'), ('Honda MTX50  (AD05) — Germany', '1982 to 1984', 'JTR239'), ('Honda MTX50 — France', '1985 to 1990', 'JTF251'), ('Honda MTX50 — France', '1985 to 1990', 'JTR239'), ('Honda NS50 F — USA', '1990', 'JTF253'), ('Honda NS50 F — USA', '1990', 'JTR239'), ('Honda NSR50 S-K', '1989 onwards', 'JTF253'), ('Honda NSR50 S-K', '1989 onwards', 'JTR216'), ('Honda NSR50  — France', '1989 to 1993', 'JTF251'), ('Honda NSR50  — France', '1989 to 1993', 'JTR216'), ('Honda NSR50 S-K — Germany', '1989 onwards', 'JTF253'), ('Honda NSR50 S-K — Germany', '1989 onwards', 'JTR216'), ('Honda SS50 Z-K1', '1978', 'JTF253'), ('Honda SS50 Z-K1', '1978', 'JTR256'), ('Honda SS50 Z-B1', '1979 to 1980', 'JTF253'), ('Honda SS50 Z-B1', '1979 to 1980', 'JTR256'), ('Honda ST50', '1978', 'JTF253'), ('Honda ST50', '1978', 'JTR256'), ('Honda ST50 J,K Dax', '1988 to 1989', 'JTF249'), ('Honda ST50 J,K Dax', '1988 to 1989', 'JTR256'), ('Honda ST50 L Dax', '1990', 'JTF249'), ('Honda ST50 L Dax', '1990', 'JTR256'), ('Honda ST50 G Dax  — Germany', '1974 to 1980', 'JTF253'), ('Honda ST50 G Dax  — Germany', '1974 to 1980', 'JTR256'), ('Honda ST50 J,K,L Dax  — Germany', '1987 to 1990', 'JTF249'), ('Honda ST50 J,K,L Dax  — Germany', '1987 to 1990', 'JTR256'), ('Honda Z50 A / J Monkey — Finland', '1982 to 1986', 'JTF252'), ('Honda Z50 A / J Monkey — Finland', '1982 to 1986', 'JTR255'), ('Honda Z50 A / J Monkey — Finland', '1987 to 1991', 'JTF252'), ('Honda Z50 A / J Monkey — Finland', '1987 to 1991', 'JTR255'), ('Honda Z50 A / J Monkey — Finland', '1992 to 1999', 'JTF252'), ('Honda Z50 A / J Monkey — Finland', '1992 to 1999', 'JTR255'), ('Honda Z50 — Australia', '1982 to 1994', 'JTF253'), ('Honda Z50 — Australia', '1982 to 1994', 'JTR255'), ('Honda ZB50 — USA', '1988', 'JTF252'), ('Honda ZB50 — USA', '1988', 'JTR256'), ('Honda ZB50 B Monkey — Germany', '1992 onwards', 'JTF253'), ('Honda ZB50 B Monkey — Germany', '1992 onwards', 'JTR256')]
'''
print("结束")