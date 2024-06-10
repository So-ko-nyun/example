# div class를 이용해 안에 있는 모든 내용 추출


import json
import selenium
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from time import sleep
import requests


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

def extract_data_from_webpage(url):
    """웹 페이지에서 데이터를 추출합니다."""
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(chrome_options)
    driver.get(url)
    driver.maximize_window()
    sleep(2)
    html = driver.page_source
    #response = requests.get(url)
    soup = BeautifulSoup(html, 'html.parser')

    
    # class="example"인 모든 <div> 태그를 찾습니다.
    div_tags = soup.find_all('div', {"class": "card-body"})
    div_subheads = soup.find_all('h2', class_= 'font-weight-bold')
    div_titles = soup.find_all('p', class_= 'ecx-page-title-white undefined mb-0')

    solution_id = soup.find("span", {"class": "badge-item badge-item-expand"}).decode_contents()
    title = soup.find("p", class_= "ecx-page-title-white undefined mb-0").decode_contents() #.find("p", class_= "ecx-page-title-white undefined mb-0")
    

    # 각 <div> 태그 안의 모든 내용을 추출합니다.
    def extract_content(div_elements):
        content_list = []
        for div_tag in div_elements:
            content = div_tag.decode_contents()  # 태그 자체를 포함하여 내용 모두 추출
            content_list.append({"content": content})
        return content_list
    
    data = {
        "title": title,
        "solution_id": solution_id,
        "div_tags": extract_content(div_tags),
        "div_titles": extract_content(div_titles),
        "subhead": extract_content(div_subheads)
    }

    return data





