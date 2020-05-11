import requests
import json
import time
from operator import itemgetter

class BOCHK_Data(object):

    def __init__(self):
        with open('bank_api_info.json','r',encoding='utf-8') as json_file:
            js_bank = json.load(json_file)
        self.auth = js_bank["BOCHK_Info"]["Auth_Door"]["production"]
        self.keywords =  js_bank["BOCHK_Info"]["Keyword"]

        self.bn_api_key  = js_bank["BOCHK_Info"]["API_Key"]["Banknote_HKD" + "_Key"]
        self.bn_api_secret = js_bank["BOCHK_Info"]["API_Secret"]["Banknote_HKD" + "_Secret"]
        self.bn_api_url = js_bank["BOCHK_Info"]["API_Url"]["Banknote_HKD"]

        self.tt_api_key  = js_bank["BOCHK_Info"]["API_Key"]["TT_HKD" + "_Key"]
        self.tt_api_secret = js_bank["BOCHK_Info"]["API_Secret"]["TT_HKD" + "_Secret"]
        self.tt_api_url = js_bank["BOCHK_Info"]["API_Url"]["TT_HKD"]

        headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'cache-control': 'no-cache'
            }
        self.bn_payload = 'grant_type=client_credentials&client_id=' + self.bn_api_key + '&client_secret=' + self.bn_api_secret
        self.tt_payload = 'grant_type=client_credentials&client_id=' + self.tt_api_key + '&client_secret=' + self.tt_api_secret

        bn_response = requests.request("POST",self.auth, headers=headers, data=self.bn_payload)
        tt_response = requests.request("POST",self.auth, headers=headers, data=self.tt_payload)

        bn_info = json.loads(bn_response.text.encode('utf8'))  #turn text to json
        tt_info = json.loads(tt_response.text.encode('utf8'))  #turn text to json

        self.bn_token = bn_info['access_token']  #get the token
        self.tt_token = tt_info['access_token']

    def fetch(self):
        bn_headers = {
              'cache-control': 'no-cache',
              'Authorization': 'Bearer ' + self.bn_token
        }
        tt_headers = {
              'cache-control': 'no-cache',
              'Authorization': 'Bearer ' + self.tt_token
        }

        bn_response = requests.request('POST', 
                   self.bn_api_url,
                   headers=bn_headers
                )
        time.sleep(1)
        tt_response = requests.request('POST', 
                   self.tt_api_url,
                   headers=tt_headers
                )        
        bn_dict_info = json.loads(bn_response.text.encode('utf8'))
        tt_dict_info = json.loads(tt_response.text.encode('utf8'))

        list_all = []
        list_bn = bn_dict_info["products"]
        list_tt = tt_dict_info["products"]
        list_all.append(list_bn)
        list_all.append(list_tt)
        list_currency = self.__handle_data(list_all=list_all)
        return list_currency        

    def __handle_data(self,list_all=None):

        if len(list_all) != 2:
            raise AssertionError
        content_data = [] #这里里面放对齐boc和ccb格式的list_target，它是个list of lists
        bn_list = list_all[0]
        tt_list = list_all[1]
        for k in range(len(self.keywords)):
            list_item=[]
            for b in range(len(bn_list)):
                if bn_list[b]["Currency"] in self.keywords[k]:
                    list_item=[]
                    if bn_list[b]["Currency"] not in ["CNY","RMB"]:
                        list_item.append("HKD/" + bn_list[b]["Currency"])
                        list_item.append(str(float(bn_list[b]["BankBuy"])/100.0))
                        list_item.append(str(float(bn_list[b]["BankSell"])/100.0))
                        for t in range(len(tt_list)):
                            if tt_list[t]["Currency"] == bn_list[b]["Currency"]:
                                list_item.append(str(float(tt_list[t]["BankBuy"])/100.0))
                                list_item.append(str(float(tt_list[t]["BankSell"])/100.0))

                            else:
                                continue
                    else:
                        list_item.append("CNY/HKD")
                        list_item.append(str(round(float(bn_list[b]["BankSell"])/100,6)))
                        list_item.append(str(round(float(bn_list[b]["BankBuy"])/100,6)))
                        for t in range(len(tt_list)):
                            if tt_list[t]["Currency"] == "CNY":
                                list_item.append(str(round(float(tt_list[t]["BankSell"])/100,6)))
                                list_item.append(str(round(float(tt_list[t]["BankBuy"])/100,6)))                           
                else:
                    continue
                if len(list_item) == 5:
                    content_data.append(list_item)
                else:
                    raise AssertionError 
        content_data=sorted(content_data, key=itemgetter(0))              
        return content_data
        #return 1