# -*- coding: utf-8 -*-
"""
Equal Plus
@author: Hye-Churn Jang
"""

# ===============================================================================
# Import
# ===============================================================================
import requests
from func_module import *
from func_module_main import *
import time


# ===============================================================================
# Abstract
# ===============================================================================
class VMwareCrawlerAbs:

    def __init__(
        self, baseUrl=None, dataUri=None, authUri=None, username=None, password=None
    ):
        self.baseUrl = baseUrl
        self.dataUri = dataUri
        self.authUri = authUri
        self.username = username
        self.password = password

    def sendToServer(self, data):
        if self.serverUrl:
            res = requests.post(
                f"{self.baseUrl}{self.dataUri}",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                json={"username": self.username, "password": self.password},
            )
            res.raise_for_status()
            token = res.json()["token"]

            res = requests.post(
                self.serverUrl,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                json=data,
            )
            res.raise_for_status()

    def doCrawlingToday(self):
        # self.doCrawling(todayStartTime, todayEndTime)
        pass

    def doCrawling(self, startDate, endDate, serverUrl):
        # result = [{...}]
        # self.sendToServer(result)
        pass


class VMwareCrawler(VMwareCrawlerAbs):

    def __init__(
        self, baseUrl=None, dataUri=None, authUri=None, username=None, password=None
    ):
        VMwareCrawlerAbs().__init__(baseUrl, dataUri, authUri, username, password)

    def sendToServer(self, data):
        return VMwareCrawlerAbs().sendToServer(data)

    def doCrawlingToday(self):
        path = "/Users/chujiu/Coding/DataCrawling/BeautifulSouppp/for_test/test_KB"
        filename = "Crawling_class_siba.json"
        detail_data = startCrawlsToday(baseUrl)
        list_to_json(detail_data)
        save_json_to_file(detail_data, path, filename)
        print("success")

        return detail_data

    def doCrawling(self, startDate, endDate, serverUrl):
        path = "/Users/chujiu/Coding/DataCrawling/BeautifulSouppp/for_test/test_KB"
        filename = "example.json"
        detail_data = startCrawls(baseUrl, startDate, endDate, serverUrl)
        list_to_json(detail_data)
        save_json_to_file(detail_data, path, filename)

        return detail_data


baseUrl = "https://support.broadcom.com/web/ecx/search?searchString=&activeType=knowledge_articles_doc&from=0&sortby=post_time&orderBy=desc&pageNo=1&aggregations=%5B%7B%22type%22%3A%22_type%22%2C%22filter%22%3A%5B%22notification_docs%22%5D%7D%5D&uid=d042dbba-f8c4-11ea-beba-0242ac12000b&resultsPerPage=10&exactPhrase=&withOneOrMore=&withoutTheWords=&pageSize=10&language=en&state=5&suCaseCreate=false"
# baseUrl = "https://support.broadcom.com/web/ecx/search?searchString=&activeType=all&from=9950&sortby=post_time&orderBy=desc&pageNo=1&aggregations=%5B%7B%22type%22%3A%22productname%22%2C%22filter%22%3A%5B%22CLARITY+PPM+SAAS+FOR+ITG%22%2C%22clarity-client-automation%22%2C%22Clarity+PPM+On+Premise+-+Application%22%2C%22clarity-project-and-portfolio-management-ppm-on-premise%22%2C%22Clarity+SaaS%22%2C%22STARTER+PACK-CLARITY+PPM%22%2C%22Clarity+Business+Service+Insight%22%2C%22Clarity+PPM+SaaS%22%2C%22Clarity+PPM+SaaS+-+Application%22%2C%22Clarity%22%2C%22CLARITY+PPM+FEDERAL%22%2C%22CLARITY+PPM+FOR+ITG%22%2C%22Clarity+Project+and+Portfolio+Management+%28PPM%29+On+Premise%22%2C%22Clarity+Project+and+Portfolio+Management+%28PPM%29+On+Demand%22%2C%22Clarity+PPM+On+Premise%22%2C%22VMware%22%5D%7D%2C%7B%22type%22%3A%22post_time%22%2C%22filter%22%3A%5B%22All+Time%22%5D%7D%2C%7B%22type%22%3A%22_type%22%2C%22filter%22%3A%5B%22knowledge_articles_doc%22%2C%22notification_docs%22%5D%7D%5D&uid=d042dbba-f8c4-11ea-beba-0242ac12000b&resultsPerPage=50&exactPhrase=&withOneOrMore=&withoutTheWords=&pageSize=50&language=en&state=1&suCaseCreate=false"
dataUri = "/external/article?articleNumber="
authUri = "/external/article?articleNumber="
username = "chuchu"
password = "kiki"
startDate = "2024-7-05"
endDate = "2024-07-10"


start_time = time.time()
hi = VMwareCrawler(baseUrl, dataUri, authUri, username, password)
serverUrl = "http://localhost:9200/"
toto = hi.doCrawling(startDate, endDate, serverUrl)
end_time = time.time()
final_time = end_time - start_time
print("코드 실행시간: ", final_time)

print(len(toto))

"""
for 날짜범위:
    vm.doCrawling(같은 날짜, 같은 날짜)
    
하루를 기준으로 계속 반복. 다만 뒤로갈 수록 느려지는 경향이 있음. 
"""
