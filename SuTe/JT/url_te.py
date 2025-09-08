import requests
url='https://www.jtsprockets.com/catalogue/model/s909/'
re=requests.get(url)
print(re.status_code)
print(re.encoding)
print(re.text)