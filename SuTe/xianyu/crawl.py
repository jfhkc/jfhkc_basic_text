from headers import headers
import requests
from lxml import etree
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

def create_session():
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    return session


def crawl(oem):
    post_url = 'https://cloyes.mycarparts.net/search_pn'

    data = {'search_pn': str(oem), 'commit': 'Search'}

    try:
        session = create_session()
        response = session.post(
            url=post_url,
            headers=headers,
            data=data,
            timeout=5
        )
        response.raise_for_status()

        tree = etree.HTML(response.text)
        # 更精确的XPath选择器
        url = tree.xpath('//@href')
        if url:
            clean_url = url[0].replace('\\', '').replace('\"', '')
            return clean_url
        return 0
    except (requests.RequestException, IndexError) as e:
        print(f"Error crawling {oem}: {str(e)}")


def detail_crawl(detail_url):
    full_url = f'https://cloyes.mycarparts.net{detail_url}'

    try:
        session = create_session()
        response = session.get(full_url, headers=headers, timeout=10)
        response.raise_for_status()

        tree = etree.HTML(response.text)
        tooth_quantity = tree.xpath('''
            //table[@class="table"]//td[
                contains(.,"Tooth Quantity")
            ]/following-sibling::th[1]/text()
        ''')
        if tooth_quantity:
            return tooth_quantity[0].strip()
        return 0

    except (requests.RequestException, IndexError) as e:
        print(f"Error parsing {detail_url}: {str(e)}")

