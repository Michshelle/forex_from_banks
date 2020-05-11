import requests
import json
from operator import itemgetter


class HangSeng_Data(object):

    def __init__(self):
      
        with open('bank_api_info.json','r',encoding='utf-8') as json_file:
            js_bank = json.load(json_file)
        self.hangseng_client = js_bank["HangSeng_Info"]["API_Key"]
        self.hangseng_url  = js_bank["HangSeng_Info"]["URLs"]["Base_URL"] + js_bank["HangSeng_Info"]["URLs"]["Path_URL"]["Forex_Info"]
        self.keywords = js_bank["HangSeng_Info"]["Keyword"]
        self.res = requests.request('GET', 
                   self.hangseng_url,
                   headers=self.hangseng_client
              )


    def fetch(self):
        
        dict_info = json.loads(self.res.text.encode('utf8'))
        list_currency = self.__handle_data(content_data=dict_info)
        return list_currency
        


    def __handle_data(self,content_data=None):
        
        if content_data is None:
            raise AssertionError
            
        list_all_banknote = content_data["data"][0]["Brand"][0]["ExchangeRateType"][0]["ExchangeRate"][0]["ExchangeRateTierBand"]
        list_all_tt = content_data["data"][0]["Brand"][0]["ExchangeRateType"][1]["ExchangeRate"][0]["ExchangeRateTierBand"]

        list_target=[]  #这个里面放所有想观察的货币banknote 和 tt

        banknote_i = len(list_all_banknote)
        tt_i = len(list_all_tt)
        for i in range(banknote_i):
            if list_all_banknote[i]["CurrencyCode"] in self.keywords:
                list_target.append(list_all_banknote[i])
        for i in range(tt_i):
            if list_all_tt[i]["CurrencyCode"] in self.keywords:
                list_target.append(list_all_tt[i])

        #注意以上形式整理的list_target就必定出现banknote在先，tt在后。
        len_i = len(list_target)
        len_k = len(self.keywords)
        content_data = [] #这里里面放对齐boc和ccb格式的list_target，它是个list of lists

        for k in range(len_k):
            list_item = [] #用来放list_data里面不同货币的子list
            for i in range(len_i):
                if list_target[i]["CurrencyCode"] == self.keywords[k]:
                    if self.keywords[k] != "CNY":
                        if list_item == []: #现钞的生成
                            list_item.append("HKD/" + self.keywords[k])
                            list_item.append(list_target[i]["BankBuyRate"])
                            list_item.append(list_target[i]["BankSellRate"])
                        else: #现汇的生成
                            list_item.append(list_target[i]["BankBuyRate"])
                            list_item.append(list_target[i]["BankSellRate"])
                    elif self.keywords[k] == "CNY":
                        if list_item == []: #现钞的生成
                            list_item.append(self.keywords[k] + "/HKD")
                            list_item.append(str(round(1 / float(list_target[i]["BankSellRate"]),6)))
                            list_item.append(str(round(1 / float(list_target[i]["BankBuyRate"]),6)))
                        else: #现汇的生成
                            list_item.append(str(round(1 / float(list_target[i]["BankSellRate"]),6)))  
                            list_item.append(str(round(1 / float(list_target[i]["BankBuyRate"]),6)))                  

                    else:
                        raise AssertionError

            if len(list_item) == 5:
                content_data.append(list_item)
            else:
                raise AssertionError
            
        content_data=sorted(content_data, key=itemgetter(0))              
        return content_data
