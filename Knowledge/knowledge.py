# div class를 이용해 안에 있는 모든 내용 추출


import requests
from bs4 import BeautifulSoup
import json
import os
from time import sleep
from datetime import datetime

def escape_string(value):
    """이스케이프 문자를 처리하는 함수."""
    escape_chars = {
        '\\': '\\\\',
        '"': '\\"',
        '\b': '\\b',
        '\f': '\\f',
        '\n': '\\n',
        '\r': '\\r',
        '\t': '\\t'
    }
    return ''.join(escape_chars.get(char, char) for char in value)

def dict_to_json(data):
    """딕셔너리를 JSON 문자열로 변환합니다."""
    json_items = []
    for key, value in data.items():
        if isinstance(value, dict):
            json_value = dict_to_json(value)
        elif isinstance(value, list):
            json_value = list_to_json(value)
        elif isinstance(value, str):
            json_value = f'"{escape_string(value)}"'  # 이스케이프 문자 처리
        elif value is None:
            json_value = "null"
        elif value is True:
            json_value = "true"
        elif value is False:
            json_value = "false"
        else:
            json_value = str(value)
        json_items.append(f'"{escape_string(key)}": {json_value}')  # 키도 이스케이프 문자 처리
    return "{" + ", ".join(json_items) + "}"

def list_to_json(lst):
    """리스트를 JSON 문자열로 변환합니다."""
    json_items = []
    for item in lst:
        if isinstance(item, dict):
            json_items.append(dict_to_json(item))
        elif isinstance(item, list):
            json_items.append(list_to_json(item))
        elif isinstance(item, str):
            json_items.append(f'"{escape_string(item)}"')  # 이스케이프 문자 처리
        elif item is None:
            json_items.append("null")
        elif item is True:
            json_items.append("true")
        elif item is False:
            json_items.append("false")
        else:
            json_items.append(str(item))
    return "[" + ", ".join(json_items) + "]"


    


def extract_data_from_webpage(url, date):
    """웹 페이지에서 데이터를 추출합니다."""
    try:
        response = requests.get(url)
        #sleep(2)
        response.raise_for_status()
    except requests.HTTPError as e:
        if response.status_code == 404:
            print("Page not found")
        else:
            print(f"HTTP 에러 발생: {e}")
        return None
    soup = BeautifulSoup(response.content, 'html.parser')

    
    
    # class="example"인 모든 <div> 태그를 찾습니다.
    div_tags = soup.find_all('div', class_='article-detail-card-content wolken-h5')
    div_titles = soup.find_all('div', class_= 'article-detail-card-header')
    div_products = soup.find_all('span', class_= 'product-chip')

    title = soup.find("h3", {"class": "wolken-h3"}).decode_contents()
    article_id = soup.find("h4", {"class": "wolken-h4"}).decode_contents()
    #update_date = soup.find("span", {"id":"date_time"})
    update_date = date.strftime('%Y-%m-%d')
    #update_date = soup.find_all("h4", {"class": "wolken-h4"})[1].find("span", {"id": "date_time"})


    # 각 <div> 태그 안의 모든 내용을 추출합니다.
    def extract_content(div_elements):
        content_list = []
        for div_tag in div_elements:
            content = div_tag.decode_contents()  # 태그 자체를 포함하여 내용 모두 추출
            content_list.append({"content": content})
        return content_list
    
    data = {
        "title": title,
        "article_id": article_id,
        "update_date": update_date,
        "div_tags": extract_content(div_tags),
        "div_titles": extract_content(div_titles),
        "products": extract_content(div_products)

    }

    return data

url = "https://knowledge.broadcom.com/external/article?articleNumber=294488" #404 page not found
date_str = "2024-06-04"
date = datetime.strptime(date_str, "%Y-%m-%d")
data = extract_data_from_webpage(url, date)






