# div class를 이용해 안에 있는 모든 내용 추출


import json
import os
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

def is_login_page(response):
    """로그인 페이지인지 확인하는 함수"""
    # 로그인 페이지를 식별할 수 있는 특정 요소를 찾아서 판단
    login_indicators = ["login", "sign in", "username", "password"]  # 로그인 페이지를 식별할 수 있는 단어들
    if any(indicator in response.text.lower() for indicator in login_indicators):
        return True
    return False

def extract_data_from_webpage(url):
    """웹 페이지에서 데이터를 추출합니다."""

    try:
        response = requests.get(url, allow_redirects=True)
        response.raise_for_status()  # 요청이 성공했는지 확인
        
        # 최종 URL이 로그인 페이지인지 확인
        if "login" in response.url.lower():
            print(f"로그인 페이지로 리디렉션됨: {response.url}")
            return None

        # 페이지 내용으로 로그인 페이지인지 확인
        if is_login_page(response):
            print(f"로그인 페이지 발견: {url}")
            return None
        
    except requests.HTTPError as e:
        if response.status_code == 404:
            print(f"404 에러 발생: {url} 페이지를 찾을 수 없습니다.")
        else:
            print(f"HTTP 에러 발생: {e}")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(chrome_options)
    driver.get(url)
    driver.maximize_window()
    sleep(2)
    html = driver.page_source
    #response = requests.get(url)
    soup = BeautifulSoup(html, 'html.parser')


    #username = soup.find(attrs= {"style": "text-align: center"})
    username = soup.select("#myBroadcomLogin > div > div")[0].get_text()
    #//*[@id="js-mainContentBox"]/content/app-init/form/div/label[1]
    #myBroadcomLogin > div > div
    print(username)

    if username == "Username":
        print("login page")
        return None
    
    # class="example"인 모든 <div> 태그를 찾습니다.
    div_tags = soup.find_all('div', {"class": "card-body"})
    title = soup.find("p", {"class": "ecx-page-title-default undefined mb-0"}).decode_contents()
    solution_id_tag = soup.find_all("p", {"class": "edit-solution-text"})
    solution_id = solution_id_tag[1].decode_contents()
    print(solution_id,"\n\n\n\n")
    print("zzz", title,"\n\n\n\n")


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
        "div_tags": extract_content(div_tags)
    }

    return data

url = "https://support.broadcom.com/web/ecx/support-content-notification/-/external/content/legal-notices/0/22527"
#url = "https://access.broadcom.com/default/ui/v1/signin/"

data = extract_data_from_webpage(url)

print(data)




