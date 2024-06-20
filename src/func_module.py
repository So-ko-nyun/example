# div class를 이용해 안에 있는 모든 내용 추출


import requests
from bs4 import BeautifulSoup
import os
from time import sleep
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

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


def extractDataPN(url, date, post_type, id, serverUrl):
    """웹 페이지에서 데이터를 추출합니다."""
    try:
        response = requests.get(url)
        if 'login' in response.url:
            return None
        response.raise_for_status()
        
    except requests.HTTPError as e:
        if response.status_code == 404:
            print("Page not found")
        else:
            print(f"HTTP 에러 발생: {e}")
        return None
    soup = BeautifulSoup(response.content, 'html.parser')
    
    try:
        
        div_tags = soup.find_all('div', {"class": "card-body"})
        if div_tags is None:
            print("div_tags가 존재하지않습니다.")
            return None
        title = soup.find("p", {"class": "ecx-page-title-default undefined mb-0"})
        if title is not None:
            title = title.get_text()
        else:
            title = None
        product = soup.find("p", class_="edit-solution-text")
        if product is not None:
            product = product.get_text()
        else:
            product = None
        update_date = date.strftime('%Y-%m-%d')
    except:
        print("해당 주소에서 오류 발생: ", url)
        return None

    # 각 <div> 태그 안의 모든 내용을 추출합니다.
    def extract_content(div_elements):
        content_list = []
        for div_tag in div_elements:
            content = div_tag.decode_contents()  # 태그 자체를 포함하여 내용 모두 추출
            if content is None:
                content = None
            content_list.append({
                "title": None,
                "text": content})
        return content_list
    
        
    data = {
        "title": title,
        "id": id,
        "type": post_type,
        "date": update_date,
        "products": [product],
        "contents": extract_content(div_tags)

    }
    
    
    #send구현
    #serverurl = "http://127.0.0.1:5500/for_test/page.html"
    response = requests.post(serverUrl, json=data)
    print(response.status_code)
    
    return data
    


def extractDataKB(url, date, post_type, serverUrl):
    """웹 페이지에서 데이터를 추출합니다."""
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.HTTPError as e:
        if response.status_code == 404:
            print("Page not found")
        else:
            print(f"HTTP 에러 발생: {e}")
        return None
    soup = BeautifulSoup(response.content, 'html.parser')

    
    try:
        title = soup.find("h3", {"class": "wolken-h3"}).decode_contents()
        if title is None:
            title = None
        article_id = soup.find("h4", {"class": "wolken-h4"}).decode_contents().strip("Article ID: ")
        if article_id is None:
            article_id = None
        update_date = date.strftime('%Y-%m-%d') 
        
        div_tags = soup.find_all('div', class_='article-detail-card-content wolken-h5')
        if div_tags is None:
            div_tags = None
        div_products = soup.find_all('span', class_= 'product-chip')
        if div_products is None:
            div_products = None
        div_titles = soup.find_all('div', class_="article-detail-card-header")
        if div_titles is None:
            div_titles = None
            
        products = []
        
        for div_product in div_products:
            product = div_product.get_text()
            products.append(product)

        contents = []

        del div_titles[0]

        for div_title,div_tag in zip(div_titles, div_tags):
            try:
                title = div_title.find('h4', class_="wolken-h4")
                if title is not None:
                    title = title.get_text()
                else:
                    title = "There is no title"
            except:
                title = None
                
            text = div_tag.decode_contents()
            if text is None:
                text = "None"
            contents.append({
                'title': title,
                'text': text
            })   
            
            
            
        download_links = soup.find_all('a', class_='attachment-download flex-row row-align-center-center', attrs={'data-uniquefileid': True, 'onclick': True})
        if not download_links:
            download_links = "There is no download files"
        else:
            download_folder = os.path.join(os.getcwd(), 'downloads')
            os.makedirs(download_folder, exist_ok=True)
            
            chrome_options = webdriver.ChromeOptions()
            prefs = {'download.default_directory': download_folder,
                    "download.prompt_for_download": False,
                    "download.directory_upgrade": True,
                    "safebrowsing.enabled": True
                    }
            chrome_options.add_experimental_option('prefs', prefs)
            #chrome_options.add_argument("--headless") 헤드리스사용시 오류 발생
            
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            driver.get(url)
            sleep(1)
            
            download_links = driver.find_elements(By.CSS_SELECTOR, "a[data-uniquefileid][onclick]")
            download_card = soup.find("div", class_="attachment-container")
            download_title = download_card.find("span", class_="attachment-name text-ellipsis")
            if download_title is None:
                download_title = "None"
            else:
                download_title = download_title.get_text()
                print(download_title)
                
            for link in download_links:
                initial_files = os.listdir(download_folder)
                # 클릭하여 파일 다운로드 시작
                link.click()

                # 다운로드 완료 대기
                download_complete = False
                while not download_complete:
                    sleep(1)  # 1초 간격으로 폴더 검사
                    current_files = os.listdir(download_folder)
                    new_files = set(current_files) - set(initial_files)
                    if new_files:
                        download_complete = True
                        downloaded_file = new_files.pop()
                        download_file_path = os.path.join(download_folder, downloaded_file)
                        
                        file_name, file_extension = os.path.splitext(downloaded_file)
                        dynamic_filename = f"{download_title.strip(".zip"".py"".txt")}{file_extension}"
                        new_file_path = os.path.join(download_folder, dynamic_filename)
                        os.rename(download_file_path, new_file_path)
                        
                        print(f"Downloaded: {new_file_path}")
                        
    
                        
                    contents.append({
                        "title": "Attachments",
                        "text": downloaded_file
                    })
                
            # 작업 완료 후 브라우저 종료
            driver.quit()

            print("id: ", article_id, ", ", download_title, ": files downloaded.", update_date)
            
            
    except:
        print("해당 주소에서 오류 발생: ", url)
        return None

    

    data = {
        "title": title,
        "id": article_id,
        "type": post_type,
        "date": update_date,
        "products": products,
        "contents": contents,
    }
    
    #serverurl = "http://127.0.0.1:8000"
    response = requests.post(serverUrl, json=data)
    print(response.status_code)
    
    return data


def save_json_to_file(data, path, filename):
    """딕셔너리 데이터를 JSON 파일로 저장합니다."""
    if not os.path.exists(path):
        os.makedirs(path)
    json_string = dict_to_json(data)
    file_path = os.path.join(path, filename)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(json_string)
