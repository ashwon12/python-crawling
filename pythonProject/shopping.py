import requests
import json
from bs4 import BeautifulSoup
import time
import random

# Tk progress를 update 해주기 위한 변수
_CurrentProgress = None
_ProgressBar = None

# 쇼핑몰 불러 오기 헤더
headers = {
    'authority': 'search.shopping.naver.com',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,de;q=0.6,de-CH;q=0.5,de-AT;q=0.4,de-LI;q=0.3,de-DE;q=0.2',
    'logic': 'PART',
    'referer': 'https://search.shopping.naver.com/search/all?frm=NVSHTTL&origQuery=%EB%8B%B9%EA%B7%BC&pagingIndex=1&pagingSize=40&productSet=total&query=%EB%8B%B9%EA%B7%BC&sort=price_asc&timestamp=&viewType=list',
    'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
}

# 판매처 정보 불러 오기 헤더


def getMalls(keyword, start, end):
    ''' Progress bar 값 변경 '''
    if (_CurrentProgress != None) and (_ProgressBar != None):
        _CurrentProgress.set( 10 )
        _ProgressBar.update()

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
        time.sleep( 0.5 )
        item_list = json.loads(response.text)
        if len(item_list) < 8 or (end != '' and index > int(end)): break
        for item in item_list['shoppingResult']['products']:
            mall_url = item['mallPcUrl'] + '/profile?cp=1'
            mall_list.append(mall_url)
        index = index + 1
    datas = [a for a in mall_list if "smartstore" in a]
    return getSellerInfo(list(set(datas)))


def getSellerInfo(mall_List):
    global data
    result = []
    statusCode = 0
    mall_idx = 0
    while mall_idx < len(mall_List) :
        mall = mall_List[mall_idx]
        ''' Progress bar 값 변경 '''
        if (_CurrentProgress != None) and (_ProgressBar != None):
            _CurrentProgress.set(((mall_idx / len(mall_List)) * 100) + 10)
            _ProgressBar.update()

        device = [
            ("macOS", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.141 Whale/3.15.136.29 Safari/537.36", '"Whale";v="3", " Not;A Brand";v="99", "Chromium";v="102"'),
            ("Windows", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36", '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"'),
            ("Windows", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.77", "\" Not;A Brand\";v=\"99\", \"Microsoft Edge\";v=\"103\", \"Chromium\";v=\"103\"" )
        ]
        pc_info = device[random.randint(0,len(device)-1)]
        sellerHeaders = {
            "Host": "smartstore.naver.com",
            "Connection": "keep-alive",
            "sec-ch-ua":pc_info[2],
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"{0}"'.format(pc_info[0]),
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": pc_info[1],
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Referer": mall,
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "ko,en;q=0.9,en-US;q=0.8"
        }
        
        params = {
            'cp': '1',
        }

        ''' 503 에러 및 requests.get 작동 에러발생 시 보완하는 구간 '''
        try:
            #time.sleep( random.randint(7,12) )   #  5~10sec, 7~12sec은 block 당함
            time.sleep( random.randint(10,15) )   #  (503 에러 방지)
            data = requests.get(mall, headers=sellerHeaders, 
                                params = params)     # DDoS 유발 가능성 존재
            print( "[SEND][{0}/{1}] STATUS: {2}, {3}".format(mall_idx, len(mall_List), data.status_code, mall))
            if data.status_code != 200:
                print( '[*] wait.. 60sec' )
                time.sleep( 60  )    # request 시 에러가 발생할 경우, 30초 대기...
                continue
        except Exception as e:
            print( '[*] wait.. 70sec' )
            time.sleep( 70 )  # request 시 에러가 발생할 경우, 30초 대기...
            continue
        ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        
        soup = BeautifulSoup(data.text, 'html.parser')
        body = soup.select_one('div.oSdeQo13Wd > div')

        seller_name = soup.select_one('div._3MuEQCqxSb > div._2i91yA8LnF > div._34hhYZytTs > div > strong').text
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
        mall_idx = mall_idx+1
        result.append(mall_info)
    print("[FINISH]")
    return result, statusCode
