import selenium
from selenium import webdriver
import time
import bs4
import requests
import urllib.request
from selenium.webdriver.remote.webelement import WebElement, By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from itertools import chain
from collections import defaultdict
import pandas as pd
import openpyxl
import csv
import json
import os
import re
import urllib
import chromedriver_autoinstaller
from urllib.parse import urlparse, parse_qs
import ast
import numpy as np


url_list = [
    'https://smartstore.naver.com/hanbando/products/416050801?NaPm=ct%3Dkvwb0brs%7Cci%3Dd6cc9c53383c9eafe7dfa0d3ddcb57ddc4bce2f5%7Ctr%3Dslsl%7Csn%3D193128%7Chk%3Dac4533ab11d8bc618f079d226907c91cc1132db5'
]

def get_driver(url, is_true):
    options = webdriver.ChromeOptions()

    if is_true:
        options.add_argument('headless')
    options.add_argument("--start-maximized")

    path = chromedriver_autoinstaller.install()
    driver = webdriver.Chrome(path, options=options)
    driver.get(url)
    return driver

def GetNetworkResources(driver):
    Resources = driver.execute_script("return window.performance.getEntries();")

    return_list = {}
    for resource in Resources:

        if 'https://m.land.naver.com/cluster/clusterList' in resource['name']:
            list_values = list(parse_qs(urlparse(resource['name']).query).values())
            list_keys = list(parse_qs(urlparse(resource['name']).query).keys())

            for key, value in enumerate(list_keys):
                return_list[value] = "".join(list_values[key])

    return return_list

def get_sellerlist(infor_group):
    info_sort = infor_group['info_sort']
    info_pagingIndex_s = infor_group['info_pagingIndex_s']
    info_pagingIndex_e = infor_group['info_pagingIndex_e']
    info_pagingSize = infor_group['info_pagingSize']
    info_viewType = infor_group['info_viewType']
    info_productSet = infor_group['info_productSet']
    info_frm = infor_group['info_frm']
    info_query = infor_group['info_query']
    info_origQuery = infor_group['info_origQuery']
    info_output = infor_group['output_file']

    item_info = []
    index = 1
    while True:
        print('page : ', index)
        url = 'https://search.shopping.naver.com/api/search/all?sort={}&pagingIndex={}&pagingSize={}&viewType={}&productSet={}&deliveryFee=&deliveryTypeValue=&frm={}&query={}&origQuery={}&iq=&eq=&xq='
        url = url.format(info_sort, str(index), info_pagingSize, info_viewType, info_productSet, info_frm, info_query, info_origQuery)
        print(url)

        req = requests.get(url)
        items = req.json()

        if len(items) < 8 or (infor_group['info_pagingIndex_e'] != '' and index > int( infor_group['info_pagingIndex_e'])): break
        for key, value in enumerate(items['shoppingResult']['products']):
            if 'smartstore.naver' not in items['shoppingResult']['products'][key]['mallPcUrl']:
                continue;

            mall_url = items['shoppingResult']['products'][key]['mallPcUrl'] + '/profile?cp=1'
            info_mallProdMblUrl = items['shoppingResult']['products'][key]['mallProdMblUrl'].strip()
            info_mallName = items['shoppingResult']['products'][key]['mallName'].strip()

            check = False
            for i in item_info:
                if info_mallName in i[0]:
                    check = True
                    break

            if not check:
                item_info.append([info_mallName, mall_url, info_mallProdMblUrl])
        index = index + 1

    list_pandas = pd.DataFrame(item_info, columns=['mallName','sellerUrl','mallProdUrl'])
    list_pandas = list_pandas.drop_duplicates()
    # print(list_pandas.info())
    print(info_output)
    list_pandas.to_excel(info_output)
    print(item_info)
    return item_info

def get_sellerinformation(infor_group):
    global result_info
    excel_url = infor_group['output_file']
    excel_detail_url = infor_group['output_file_detail']
    df_sheet_index = pd.read_excel(excel_url, engine='openpyxl')

    driver = get_driver('https://www.naver.com/', False)
    result_list = []
    for key in range(0, len(df_sheet_index)):
        info_product_url = df_sheet_index['mallProdUrl'][key]
        info_url = df_sheet_index['sellerUrl'][key]
        info_mallName = df_sheet_index['mallName'][key]

        print("---start : ", info_url, info_mallName)

        driver.get(info_url)
        time.sleep(2)


        soup = bs4.BeautifulSoup(driver.page_source, "html.parser")
        body = soup.select_one('div.oSdeQo13Wd > div')

        seller_boss = body.select_one('div:nth-child(1) > div:nth-child(2) > div._2PXb_kpdRh').text
        temp = body.select_one('div:nth-child(1) > div:nth-child(3) > div._2PXb_kpdRh > div')
        [x.extract() for x in temp.findAll('span')]
        seller_call = temp.text
        seller_mail = body.select_one('div:nth-child(2) > div:nth-last-child(1) > div._2PXb_kpdRh').text

        result_info = [
            info_mallName,
            seller_boss,
            seller_call,
            seller_mail,
            info_product_url
        ]

        print(result_info)
        result_list.append(result_info)

    # 판매자/이메일/통신판매업신고번호/사업장소재지/연락처/사업자번호/고객센터연락처
    list_pandas = pd.DataFrame(result_list, columns=['판매 사이트명', '대표자 이름', '고객 센터', '이메일', '사이트 주소'])
    list_pandas = list_pandas.drop_duplicates()
    list_pandas.to_excel(excel_detail_url)

    return result_list


infor_group = {}
keyword = ''
list_result = []
infor_group['info_sort'] = 'rel'
infor_group['info_pagingSize'] = '40'
infor_group['info_viewType'] = 'list'
infor_group['info_productSet'] = 'total'
infor_group['info_frm'] = 'NVSHATC'
infor_group['info_pagingIndex_s'] = 1
infor_group['info_pagingIndex_e'] =''

def getDatas():
    get_sellerlist(infor_group)
    list = get_sellerinformation(infor_group)
    return list


