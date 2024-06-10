# -*- coding: utf-8 -*-
'''
Equal Plus
@author: Hye-Churn Jang
'''

#===============================================================================
# Import
#===============================================================================
import requests

#===============================================================================
# Abstract
#===============================================================================
class VMwareCrawlerAbs:
    
    def __init__(self, baseUrl=None, dataUri=None, authUri=None, username=None, password=None):
        self.baseUrl = baseUrl
        self.dataUri = dataUri
        self.authUri = authUri
        self.username = username
        self.password = password
    
    def sendToServer(self, data):
        if self.serverUrl:
            res = requests.post(f'{self.baseUrl}{self.dataUri}', headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }, json={
                'username': self.username,
                'password': self.password
            })
            res.raise_for_status()
            token = res.json()['token']
            
            res = requests.post(self.serverUrl, headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }, json=data)
            res.raise_for_status()
    
    def doCrawlingToday(self):
        # self.doCrawling(todayStartTime, todayEndTime)
        pass
    
    def doCrawling(self, startDate, endDate):
        # result = [{...}]
        # self.sendToServer(result)
        pass
