import json
import selenium
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from time import sleep
from test_solution import *
import os

def is_within_date_range(post_date, start_date, end_date):
    """주어진 날짜가 시작 날짜와 끝 날짜 범위 내에 있는지 확인"""
    return start_date <= post_date <= end_date

def get_posts_within_date_range(driver, start_date, end_date):
    """페이지를 순회하며 주어진 날짜 범위 내의 게시물 URL을 추출"""
    print("-----------------------------------------")
    print("get_posts_within_date_fange function is start~ \n\n\n")
    
    posts_urls = []
    current_page = 1
    
    while True:
        #현재 페이지 HTML 콘텐츠 파싱
        html_content = driver.page_source
        soup = BeautifulSoup(html_content,'html.parser')
        #모든 게시물 요약 찾기
        posts = soup.find_all("div", {"class": "su__list-items su__bg-white su__sm-shadow su__radius-1 su__position-relative su__mb-3 su__p-3 su__content_tile_padding"})
        #posts는 한 게시물의 미리보기뷰를 포함하는 div태그이며 그 태그들의 집합임
        if not posts:
            break 
        
        for post in posts:
            
            #제목과 값을 모두 포함하고 있는 div태그
            div_id_date = post.find_all('div', class_='su__d-flex su__flex-wrap custom-metadata')

            title_tag = post.find('h2')
            if title_tag:
                a_tag = post.find("span",class_="su__viewed-results su__noclicked-title su__text-truncate1 su__text_align").find("a")
                title = title_tag.get_text()
                href = a_tag.get('href') if a_tag else None
               
                #ID와 업데이트 시간의 제목 부분
                post_title_component = div_id_date[0].find('span', class_='metaDataKey su__font-bold su__color-blue su__mr-2 su__rtlmr-0 su__rtlml-2 su__font-12')
                post_title_release = div_id_date[1].find('span', class_='metaDataKey su__font-bold su__color-blue su__mr-2 su__rtlmr-0 su__rtlml-2 su__font-12')
                post_title_id = div_id_date[2].find('span', class_='metaDataKey su__font-bold su__color-blue su__mr-2 su__rtlmr-0 su__rtlml-2 su__font-12')
                post_title_date = div_id_date[5].find('span', class_='metaDataKey su__font-bold su__color-blue su__mr-2 su__rtlmr-0 su__rtlml-2 su__font-12')
                
                #제목의 옆노드로, next_sibling을 사용하여 불러옴    
                id_check = post_title_id.find_next_sibling('span')
                com_check = post_title_component.find_next_sibling('span')
                release_check = post_title_release.find_next_sibling('span')
                if id_check:
                    post_id = id_check.get_text(strip=True)
                    post_component = com_check.get_text(strip=True)
                    post_release = release_check.get_text(strip=True)

                    date_check_tag = post_title_date.find_next_sibling('span')
                    if date_check_tag:
                        post_date_time = date_check_tag.get_text(strip=True)
                        try:
                            post_date = datetime.strptime(post_date_time, "%m/%d/%Y %I:%M %p")
                            if is_within_date_range(post_date,start_date,end_date):
                                posts_urls.append({'url': href, "id": post_id, 'date': post_date, 'component': post_component, 'release': post_release})
                                
                        except ValueError as ve:
                            print(f"Date parsing error: {ve}")
                    else:
                        print("update-date span not found")
                else:
                    print("post-id span not found")

            
            
    
        try:
            next_button = None
    
            possible_buttons = driver.find_elements(By.XPATH, '//*[contains(text(), "Next")]')

            print("current", current_page)
            for button in possible_buttons:
                if button.is_displayed() and button.is_enabled() and button.text.strip().lower() == 'next':
                    next_button = button
                    break


            if next_button:   
                driver.execute_script("arguments[0].click();",next_button) 
                current_page += 1
                sleep(2)
            else:
                print(f"Could not find next button for page {current_page + 1}")
                break

        except Exception as e:
            print(f"Could not find next button for page {current_page + 1}: {e}")
            break

    print("All of posts_urls are here~~: ", posts_urls)
    print("-----------------------------------------")
    print("get_posts_within_date_fange function is end~ \n\n\n")


    return posts_urls

def crawl_posts(base_url, start_date_str, end_date_str):
    """Selenium을 사용하여 주어진 날짜 범위 내의 게시물 URL을 크롤링"""
    print("-----------------------------------------")
    print("Crawl_posts function is start~ \n\n\n")
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

    if start_date == end_date:
        end_date = start_date + timedelta(days=1) - timedelta(seconds=1)

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 브라우저 창을 띄우지 않음
    #chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(base_url)
    driver.maximize_window()    
    sleep(3)

    posts_urls = get_posts_within_date_range(driver, start_date, end_date)
    all_posts_details = []
    i=1
    for post in posts_urls:
        print("-----------------------------------------")
        print("get_post_details function is start~ and page is: ", i ," \n\n\n")
        #print(get_post_details(post.get('url')))
        all_posts_details.append(extract_data_from_webpage(post.get('url')))
        print("afdsafasd", post.get('date'))
        print("-----------------------------------------")
        print("get_post_details function page ",i," is end~  \n\n\n")
        i+=1
    print("크롤링한 게시글의 수는", i-1,"개 입니다.")
    driver.quit()
    print("-----------------------------------------")
    print("Crawl_posts function is end~ \n\n\n")

    return all_posts_details


def save_json_to_file(data, path, filename):
    """딕셔너리 데이터를 JSON 파일로 저장합니다."""
    if not os.path.exists(path):
        os.makedirs(path)
    json_string = list_to_json(data)
    file_path = os.path.join(path, filename)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(json_string)

def load_json_from_file(path, filename):
    """JSON 파일에서 데이터를 로드합니다."""
    file_path = os.path.join(path, filename)
    if not os.path.exists(file_path):
        return []  # 파일이 없으면 빈 리스트 반환
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data if isinstance(data, list) else []

def merge_data(existing_data, new_data, duplicates):
    """기존 데이터와 새로운 데이터를 병합합니다."""
    existing_ids = {item['solution_id'] for item in existing_data if isinstance(item, dict)}
    if new_data['solution_id'] in existing_ids:
        print("여기에서 중복되었습니다.: ", new_data['solution_id'])
        duplicates += 1
    else:    
        existing_data.append(new_data)
    return existing_data, duplicates


base_url = "https://support.broadcom.com/web/ecx/search?searchString=&activeType=all&from=0&sortby=post_time&orderBy=desc&pageNo=1&aggregations=%5B%7B%22type%22%3A%22productname%22%2C%22filter%22%3A%5B%22CLARITY+PPM+SAAS+FOR+ITG%22%2C%22clarity-client-automation%22%2C%22Clarity+PPM+On+Premise+-+Application%22%2C%22clarity-project-and-portfolio-management-ppm-on-premise%22%2C%22Clarity+SaaS%22%2C%22STARTER+PACK-CLARITY+PPM%22%2C%22Clarity+Business+Service+Insight%22%2C%22Clarity+PPM+SaaS%22%2C%22Clarity+PPM+SaaS+-+Application%22%2C%22Clarity%22%2C%22CLARITY+PPM+FEDERAL%22%2C%22CLARITY+PPM+FOR+ITG%22%2C%22Clarity+Project+and+Portfolio+Management+%28PPM%29+On+Premise%22%2C%22Clarity+Project+and+Portfolio+Management+%28PPM%29+On+Demand%22%2C%22Clarity+PPM+On+Premise%22%2C%22VMware+vSphere+ESXi%22%2C%22VMware%22%2C%22VMware+vCenter+Server%22%2C%22VMware+Aria+Suite%22%2C%22VMware+NSX+Networking%22%5D%7D%2C%7B%22type%22%3A%22post_time%22%2C%22filter%22%3A%5B%22All+Time%22%5D%7D%2C%7B%22type%22%3A%22_type%22%2C%22filter%22%3A%5B%22solutions_doc%22%5D%7D%5D&uid=d042dbba-f8c4-11ea-beba-0242ac12000b&resultsPerPage=50&exactPhrase=&withOneOrMore=&withoutTheWords=&pageSize=50&language=en&state=2&suCaseCreate=false"
start_date_str ='2010-05-1'
end_date_str ='2024-06-1'
#start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
#end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

filename = 'test_solution_May.json'
path = '/Users/chujiu/Coding/DataCrawling/BeautifulSouppp/for_Solutions/test_solution'
existing_data = load_json_from_file(path, filename)

detail_new_datas = crawl_posts(base_url,start_date_str,end_date_str)

duplicates = 0

for detail_new_data in detail_new_datas:
    update_data, duplicates = merge_data(existing_data, detail_new_data, duplicates)
    save_json_to_file(update_data, path, filename)


print(f"데이터가 {filename} 파일로 저장되었습니다.")
print(f"중복된 데이터 수: {duplicates}")

# 반복문을 이용하여 월별로 데이터 저장
