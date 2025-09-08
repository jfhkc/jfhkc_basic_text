from crawl import *
import pandas as pd
import os

read_path = r'C:\Users\31052\Desktop\read.xlsx'
save_path = r'C:\Users\31052\Desktop\save.xlsx'

def read_excel():
    df = pd.read_excel(read_path, usecols=['产品编码', 'OEM号码'])
    df1 = df.dropna()
    for _, row in df1.iterrows():
        yield row['产品编码'], row['OEM号码']

def save_excel(data):

    df_save = pd.DataFrame(data)
    df_save.to_excel(save_path, index=False)


def run():
    result = []
    for sumax, oem in read_excel():
        detail_url = crawl(oem)
        if not detail_url:
            item = {
                'sumax': sumax,
                'oem': oem,
                'detail_url': '',
                'tooth_quantity': ''
            }
            print(item)
            result.append(item)
            continue

        tooth_quantity = detail_crawl(detail_url)
        item = {
            'sumax': sumax,
            'oem': oem,
            'detail_url': detail_url,
            'tooth_quantity': tooth_quantity
        }
        print(item)
        result.append(item)
    save_excel(result)


if __name__ == '__main__':
    run()
