import requests
import json
from bs4 import BeautifulSoup
import time

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
    idx = 0
    while idx < len(mall_List) :
        mall = mall_List[idx]
        ''' Progress bar 값 변경 '''
        if (_CurrentProgress != None) and (_ProgressBar != None):
            _CurrentProgress.set(((idx / len(mall_List)) * 100) + 10)
            _ProgressBar.update()

        '''
        sellerHeaders = {
            'authority': 'smartstore.naver.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            # Requests sorts cookies= alphabetically
            # 'cookie': 'NA_SAS=1; NA_SA=Y2k9MEF1MDAwMkdoY0R3RG9MUnZ2cEd8dD0xNjU5NTIyMjIxfHU9aHR0cHMlM0ElMkYlMkZzbWFydHN0b3JlLm5hdmVyLmNvbSUyRjYyMHBsdXMlMkZwcm9kdWN0cyUyRjQ3OTE0NzQ3MDklM0ZOYVBtJTNEY3QlMjUzRGw2ZGdvazRnJTI1N0NjaSUyNTNEMEF1MDAwMkdoY0R3RG9MUnZ2cEclMjU3Q3RyJTI1M0RwbGElMjU3Q2hrJTI1M0RiOTE2ODAzNDYwM2U2MTEwMWJjOTQ4NjYxNzU3NGMyMGU3NTk1MDA5; NVADID=0Au0002GhcDwDoLRvvpG; NA_CO=ct%3Dl6dgok4g%7Cci%3D0Au0002GhcDwDoLRvvpG%7Ctr%3Dpla%7Chk%3Db9168034603e61101bc9486617574c20e7595009%7Ctrx%3Dundefined; wcs_bt=s_2df61f61724d1:1659550445; NNB=LMHFYRWF5KRGE; _ga=GA1.2.1536591858.1655134812; _ga_7VKFYR6RV1=GS1.1.1655134811.1.1.1655135041.60; page_uid=hXpKOwp0JXVssPUAQohssssssBN-362210; nx_ssl=2; ASID=797c83b200000182633ae56e00000052; BMR=s=1659549564094&r=https%3A%2F%2Fm.blog.naver.com%2FPostView.naver%3FisHttpsRedirect%3Dtrue%26blogId%3Dbinsoore%26logNo%3D221204112042&r2=https%3A%2F%2Fwww.google.com%2F',
            'referer': mall,
            'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        }
        '''
        # del sellerHeaders
        sellerHeaders = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
        }

        params = {
            'cp': '1',
        }

        ''' 503 에러 및 requests.get 작동 에러발생 시 보완하는 구간 '''
        status_chk_count = 0
        status_chk_flag = False
        while status_chk_flag != True:
            if status_chk_count > 3:  # 해당 카운트가 3 이상이면 다음 mall 정보를 요청하기위해 while 문을 멈춘다.
                break
            try:
                time.sleep(10)  # request 하기 전에 0.5초의 딜레이를 준다. (503 에러 방지)
                data = requests.get(mall, headers=sellerHeaders,
                                    params=params)  # DDoS 유발 가능성 존재. if Status == 503: sleep.until(ServerOpen)
                print("[SEND] {0}".format(mall))
                status_chk_flag = True  # request가 정상적으로 이루어졌을 경우, 이 값을 True로 변경
            except Exception as e:
                status_chk_count += 1  # requests.get 이 정상적으로 수행되지 않았을 경우, 해당 카운트를 1 증가한다.
                time.sleep(70)  # request 시 에러가 발생할 경우, 30초 대기...
                continue

        ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        statusCode = data.status_code
        if data.status_code != 200:
            print(">> Occurd not 200: {0} ({1})".format(mall,data.status_code))  # 위 로직에서 status_chk_count가 3번 이상 발생했을 경우, 이 조건문을 수행함
            time.sleep(60)  # request 시 에러가 발생할 경우, 30초 대기...
            continue

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
        idx = idx+1
        result.append(mall_info)

    print("[FINISH]")
    return result, statusCode
