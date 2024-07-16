import json
import selenium
from datetime import datetime, timedelta, date, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from time import sleep
from func_module import *
import os


def startCrawls(baseUrl, start_date_str, end_date_str, serverUrl):
    """Selenium을 사용하여 주어진 날짜 범위 내의 게시물 URL을 크롤링"""
    print("-----------------------------------------")
    print("주어진 범위 내의 크롤링을 시작합니다. \n\n\n")
    # 시간 범위를 지정하는 경우에만 활용.
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    end_date = end_date.replace(hour=23, minute=59, second=59)
    if start_date == end_date:
        end_date = start_date + timedelta(days=1) - timedelta(seconds=1)
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 브라우저 창을 띄우지 않음
    # chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(baseUrl)
    driver.maximize_window()
    sleep(1)
    posts_urls = crawlPostsWithinDate(driver, start_date, end_date)
    print("크롤링할 게시물은 총 ", len(posts_urls), "개 입니다.")
    all_posts_details = []
    errors = []
    i = 1
    for post in posts_urls:
        print("-----------------------------------------")
        print(
            "각 게시글의 상세내역을 크롤링합니다. 현재 페이지는: ",
            i,
            "번째 페이지입니다.",
            " \n\n\n",
        )

        url = post.get("url")
        date = post.get("date")
        post_type = post.get("type")
        id = post.get("id")

        flag = None
        if post_type == "KB":
            flag = True
        elif post_type == "PN":
            flag = False

        if flag:
            data = extractDataKB(url, date, post_type, serverUrl)
            if data is not None:
                all_posts_details.append(data)
            else:
                print("이 페이지는 없거나 리다이렉션된 페이지입니다.(KB)", url)
                print("오류가 발생한 페이지의 id: ", post.get("id"))
                print("오류가 발생한 페이지의 날짜: ", date)
                errors.append(url)
                continue
        else:
            data = extractDataPN(url, date, post_type, id, serverUrl)
            if data is not None:
                all_posts_details.append(data)
            else:
                print("이 페이지는 없거나 리다이렉션된 페이지입니다.(PN)", url)
                print("오류가 발생한 페이지의 id: ", post.get("id"))
                print("오류가 발생한 페이지의 날짜: ", date)
                errors.append(url)
                continue

        print(
            "각 게시글의 상세내역 크롤링이 끝났습니다. 끝난 페이지는",
            i,
            "번째 페이지입니다.",
        )
        print("---------------------------------------------------------\n\n\n")
        i += 1
    print("크롤링한 게시글의 수는 총 ", i - 1, "개 입니다.")
    print("오류난 페이지: ", errors)
    print("오류난 페이지는 총 ", len(errors), "개입니다.")
    driver.quit()
    print("주어진 범위 내의 모든 크롤링을 끝마쳤습니다. 데이터를 반환합니다.")
    print("-------------------------------------------------------\n\n\n")

    return all_posts_details


def startCrawlsToday(baseUrl, serverUrl):
    """Selenium을 사용하여 주어진 날짜 범위 내의 게시물 URL을 크롤링"""
    print("---------------------------------------------------------")
    print("오늘 날짜의 크롤링을 시작합니다. \n\n\n")

    today = datetime.today().date()
    start_date = datetime.combine(today, time.min)
    end_date = datetime.combine(today, time.max)

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 브라우저 창을 띄우지 않음
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(baseUrl)
    driver.maximize_window()
    sleep(1)
    posts_urls = crawlPostsWithinDate(driver, start_date, end_date)
    print("크롤링할 게시물은 총 ", len(posts_urls), "개 입니다.")
    all_posts_details = []
    i = 1
    errors = []
    for post in posts_urls:
        print("-------------------------------------------------------")
        print(
            "각 게시글의 상세내역을 크롤링합니다. 현재 페이지는: ",
            i,
            "번째 페이지입니다.",
            " \n\n\n",
        )
        url = post.get("url")
        date = post.get("date")
        post_type = post.get("type")
        id = post.get("id")
        flag = None
        if post_type == "KB":
            flag = True
        elif post_type == "PN":
            flag = False

        if flag:
            data = extractDataKB(url, date, post_type, serverUrl)
            if data is not None:
                all_posts_details.append(data)
            else:
                print("이 페이지는 없거나 리다이렉션된 페이지입니다.(KB)", url)
                print("오류가 발생한 페이지의 id: ", post.get("id"))
                print("오류가 발생한 페이지의 날짜: ", date)
                errors.append(url)
                continue
        else:
            data = extractDataPN(url, date, post_type, id, serverUrl)
            if data is not None:
                all_posts_details.append(data)
            else:
                print("이 페이지는 없거나 리다이렉션된 페이지입니다.(PN)", url)
                print("오류가 발생한 페이지의 id: ", post.get("id"))
                print("오류가 발생한 페이지의 날짜: ", date)
                errors.append(url)
                continue

        print(
            "각 게시글의 상세내역 크롤링이 끝났습니다. 끝난 페이지는",
            i,
            "번째 페이지입니다.",
        )
        print("----------------------------------------------------------\n\n\n")
        i += 1
    print("크롤링한 게시글의 수는 총 ", i - 1, "개 입니다.")
    print("오류난 페이지: ", errors)
    print("오류난 페이지는 총 ", len(errors), "개입니다.")
    driver.quit()
    print("오늘 날짜의 모든 크롤링을 끝마쳤습니다. 데이터를 반환합니다.")
    print("---------------------------------------------------\n\n\n")
    return all_posts_details


def is_before_start_date(date, start_date):
    return date < start_date


def is_within_date_range(post_date, start_date, end_date):
    """주어진 날짜가 시작 날짜와 끝 날짜 범위 내에 있는지 확인"""
    return start_date <= post_date <= end_date


def crawlPostsWithinDate(driver, start_date, end_date):
    """페이지를 순회하며 주어진 날짜 범위 내의 게시물 URL을 추출"""
    posts_urls = []
    current_page = 1

    while True:
        # 현재 페이지 HTML 콘텐츠 파싱
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, "html.parser")
        # 모든 게시물 요약 찾기
        posts = soup.find_all(
            "div",
            {
                "class": "su__list-items su__bg-white su__sm-shadow su__radius-1 su__position-relative su__mb-3 su__p-3 su__content_tile_padding"
            },
        )
        # posts는 한 게시물의 미리보기뷰를 포함하는 div태그이며 그 태그들의 집합임
        if not posts:
            break

        for post in posts:
            # 제목과 값을 모두 포함하고 있는 div태그
            div_id_date = post.find_all(
                "div", class_="su__d-flex su__flex-wrap custom-metadata"
            )
            title_tag = post.find("h2")
            ttype = post.find("div", class_="customdata-view")
            post_type = ttype.span.next_sibling.get_text().strip()
            if post_type == "Knowledge Articles":
                post_type = "KB"
            elif post_type == "Product News":
                post_type = "PN"
            else:
                print("type 오류 발생")
            if title_tag:
                a_tag = post.find(
                    "span",
                    class_="su__viewed-results su__noclicked-title su__text-truncate1 su__text_align",
                ).find("a")
                title = title_tag.get_text()
                href = a_tag.get("href") if a_tag else None
                # ID와 업데이트 시간의 제목 부분
                try:
                    post_title_id = div_id_date[0].find(
                        "span",
                        class_="metaDataKey su__font-bold su__color-blue su__mr-2 su__rtlmr-0 su__rtlml-2 su__font-12",
                    )
                    post_title_date = div_id_date[3].find(
                        "span",
                        class_="metaDataKey su__font-bold su__color-blue su__mr-2 su__rtlmr-0 su__rtlml-2 su__font-12",
                    )
                except:
                    continue
                # 제목의 옆노드로, next_sibling을 사용하여 불러옴
                id_check = post_title_id.find_next_sibling("span")
                if id_check:
                    post_id = id_check.get_text(strip=True)
                    date_check_tag = post_title_date.find_next_sibling("span")
                    if date_check_tag:
                        post_date_time = date_check_tag.get_text(strip=True)
                        try:
                            post_date = datetime.strptime(
                                post_date_time, "%m/%d/%Y %I:%M %p"
                            )
                            if is_within_date_range(post_date, start_date, end_date):
                                posts_urls.append(
                                    {
                                        "url": href,
                                        "id": post_id,
                                        "date": post_date,
                                        "title": title,
                                        "type": post_type,
                                    }
                                )

                            if is_before_start_date(post_date, start_date):
                                driver.quit()
                        except ValueError as ve:
                            print(f"Date parsing error: {ve}")
                    else:
                        print("update-date span not found")
                else:
                    print("post-id span not found")
        try:
            next_button = None
            possible_buttons = driver.find_elements(
                By.XPATH, '//*[contains(text(), "Next")]'
            )
            print("current", current_page)
            for button in possible_buttons:
                if (
                    button.is_displayed()
                    and button.is_enabled()
                    and button.text.strip().lower() == "next"
                ):
                    next_button = button
                    break

            if next_button:
                driver.execute_script("arguments[0].click();", next_button)
                current_page += 1
                sleep(2)
            else:
                print(f"Could not find next button for page {current_page + 1}")
                break

        except Exception as e:
            print(f"Could not find next button for page {current_page + 1}: {e}")
            break

    return posts_urls


def save_json_to_file(data, path, filename):
    """딕셔너리 데이터를 JSON 파일로 저장합니다."""
    if not os.path.exists(path):
        os.makedirs(path)
    json_string = list_to_json(data)
    file_path = os.path.join(path, filename)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(json_string)


'''
def load_json_from_file(path, filename):
    """JSON 파일에서 데이터를 로드합니다."""
    file_path = os.path.join(path, filename)
    if not os.path.exists(file_path):
        return []  # 파일이 없으면 빈 리스트 반환
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
        return data if isinstance(data, list) else []


def merge_data(existing_data, new_data, duplicates):
    """기존 데이터와 새로운 데이터를 병합합니다."""
    existing_ids = {item["id"] for item in existing_data if isinstance(item, dict)}
    if new_data["id"] in existing_ids:
        print("여기서 중복이 발생하였습니다.", new_data["id"])
        duplicates += 1
    else:
        existing_data.append(new_data)
    return existing_data, duplicates
'''
