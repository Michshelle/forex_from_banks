import json
import requests
import xml.etree.ElementTree as ET
import time
from operator import itemgetter


class CCB_Data(object):

    def __init__(self):

        with open('bank_api_info.json','r',encoding='utf-8') as json_file:
            js_bank = json.load(json_file)  
        self.webpage = js_bank["CCB_Info"]["Forex_Xml"]  
        self.list_keywords = js_bank["CCB_Info"]["Keyword"]
        self.req = requests.get(self.webpage).text
        time.sleep(1)
        self.base =  js_bank["CCB_Info"]["Xpath"]["base"]
        self.currency =  js_bank["CCB_Info"]["Xpath"]["currency"]
        self.forex_buy_cash =js_bank["CCB_Info"]["Xpath"]["forex_buy_cash"]
        self.forex_sell_cash = js_bank["CCB_Info"]["Xpath"]["forex_sell_cash"]
        self.forex_buy_tt = js_bank["CCB_Info"]["Xpath"]["forex_buy_tt"]
        self.forex_sell_tt = js_bank["CCB_Info"]["Xpath"]["forex_sell_tt"]

    def fetch(self):

        tree = ET.fromstring(self.req)
        ele_tree = tree.findall(self.base)
        all_list=[]
        item_list=[]
        for child in ele_tree:
            grandchild = child.find("." + self.currency).text
            if grandchild in self.list_keywords:
                item_list.append(grandchild)
                item_list.append(child.find("." + self.forex_buy_cash).text)
                item_list.append(child.find("." + self.forex_sell_cash).text)
                item_list.append(child.find("." + self.forex_buy_tt).text)
                item_list.append(child.find("." + self.forex_sell_tt).text)
                if len(item_list) == 5:
                    all_list.append(item_list)
                    item_list = []
                else:
                    raise AssertionError            
        self.forex_list = self.__handle_data(content_data=all_list)
        return self.forex_list

    def __handle_data(self,content_data=None):
        
        if content_data is None:
            raise AssertionError

        for i in range(len(content_data)):
            if content_data[i][0] == "826":
                content_data[i][0] = "CNY/GBP"
            elif content_data[i][0] == "840":
                content_data[i][0] = "CNY/USD"
            elif content_data[i][0] == "344":
                content_data[i][0] = "CNY/HKD"
            elif content_data[i][0] == "978":
                content_data[i][0] = "CNY/EUR"

        content_data=sorted(content_data, key=itemgetter(0))
        return content_data