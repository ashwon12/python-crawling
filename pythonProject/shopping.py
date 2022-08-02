import requests
import json
from bs4 import BeautifulSoup

# 쇼핑몰 불러 오기 헤더
headers = {
    'authority': 'search.shopping.naver.com',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,de;q=0.6,de-CH;q=0.5,de-AT;q=0.4,de-LI;q=0.3,de-DE;q=0.2',
    # Requests sorts cookies= alphabetically
    # 'cookie': 'NNB=VVAWCK2HURNGE; ASID=797c83b20000018080dc37490000006a; autocomplete=use; AD_SHP_BID=32; NV_WETR_LAST_ACCESS_RGN_M="MDIyMTA1NTA="; NV_WETR_LOCATION_RGN_M="MDIyMTA1NTA="; NDARK=N; _fbp=fb.1.1655647576655.843765165; _ga=GA1.2.49519012.1655647577; nx_ssl=2; ncpa=537693|l66qo4qw|c940f7645a59d7e05442d03b1cb359e6d56a57eb|s_2c75418df4211|57fc12194033e41f3e08787148c7f1b8915102d3; page_uid=hXh2Fwp0YihssCZjb9Gssssst0o-361313; spage_uid=hXh2Fwp0YihssCZjb9Gssssst0o-361313; sus_val=jtoUBwCtie7RGNkZNoRCOxME',
    'logic': 'PART',
    'referer': 'https://search.shopping.naver.com/search/all?frm=NVSHTTL&origQuery=%EB%8B%B9%EA%B7%BC&pagingIndex=1&pagingSize=40&productSet=total&query=%EB%8B%B9%EA%B7%BC&sort=price_asc&timestamp=&viewType=list',
    'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
}

# 판매처 정보 불러 오기 헤더
sellerHeaders = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}


def getMalls(keyword, start, end):
    index = 1
    if start != '':
        index = int(start)
    mall_list = []
    while True:
        params = {
            'sort': 'rel',
            'pagingIndex': index,
            'pagingSize': '40',
            'viewType': 'list',
            'productSet': 'total',
            'deliveryFee': '',
            'deliveryTypeValue': '',
            'query': keyword,
            'origQuery': keyword,
            'iq': '',
            'eq': '',
            'xq': '',
            'window': '',
        }
        response = requests.get('https://search.shopping.naver.com/api/search/all', params=params, headers=headers)
        item_list = json.loads(response.text)
        if len(item_list) < 8 or (end != '' and index > int(end)): break
        for item in item_list['shoppingResult']['products']:
            mall_url = item['mallPcUrl'] + '/profile?cp=1'
            mall_list.append(mall_url)
        index = index + 1
    datas = [a for a in mall_list if "smartstore" in a]
    return getSellerInfo(list(set(datas)))


def getSellerInfo(mall_List):
    result = []
    for mall in mall_List:
        data = requests.get(mall, headers=sellerHeaders)
        soup = BeautifulSoup(data.text, 'html.parser')
        body = soup.select_one('div.oSdeQo13Wd > div')

        seller_name = soup.select_one('._6P7lESLavN > strong').text
        seller_boss = body.select_one('div:nth-child(1) > div:nth-child(2) > div._2PXb_kpdRh').text
        temp = body.select_one('div:nth-child(1) > div:nth-child(3) > div._2PXb_kpdRh > div')
        [x.extract() for x in temp.findAll('span')]
        seller_call = temp.text
        seller_mail = body.select_one('div:nth-child(2) > div:nth-last-child(1) > div._2PXb_kpdRh').text

        mall_info = {
            '판매 사이트명': seller_name,
            '대표자 이름': seller_boss,
            '고객센터': seller_call,
            '이메일': seller_mail
        }

        result.append(mall_info)
    return result
