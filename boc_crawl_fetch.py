import json
import requests
from lxml import etree
from operator import itemgetter


class BOC_Data(object):

    def __init__(self):

        with open('bank_api_info.json','r',encoding='utf-8') as json_file:
            js_bank = json.load(json_file)  
        self.webpage = js_bank["BOC_Info"]["Forex_Webpage"]  
        self.list_keywords = js_bank["BOC_Info"]["Keyword"]
        self.list_validation_headers = js_bank["BOC_Info"]["Validation_Sequence"]

        req = requests.get(self.webpage)
        if req.encoding == 'ISO-8859-1':
            encodings = requests.utils.get_encodings_from_content(req.text)
            if encodings:
                encoding = encodings[0]
            else:
                encoding = req.apparent_encoding
            self.encoding = encoding
            encode_content = req.content.decode(self.encoding, 'replace') #如果设置为replace，则会用?取代非法字符；
        self.encode_content = encode_content
    
    def fetch(self):

        selector = etree.HTML(self.encode_content)
        headers = selector.xpath('//div[@class="publish"]/div/table//th/text()')
        if headers[:5] != self.list_validation_headers:  #确保中行没有更改列
            raise AssertionError

        row_cont = selector.xpath('//div[@class="publish"]/div/table//tr')
        self.list_currency_info = []
        for row in row_cont:
                row_byte = etree.tostring(row,encoding=self.encoding)
                row_str = row_byte.decode(self.encoding,'replace')
                for i in range(len(self.list_keywords)):
                    if self.list_keywords[i] in row_str:
                        row_selector = etree.HTML(row_str)
                        row_list = row_selector.xpath('//td/text()')
                        if len(row_list) != 8:
                            raise AssertionError
                        else:
                            self.list_currency_info.append(row_list)
        self.list_currency = self.__handle_data(self.list_currency_info)
        return self.list_currency
    
    def __handle_data(self,content_data=None):
        
        if content_data is None:
            raise AssertionError

        for i in range(len(content_data)):
            if content_data[i][0] == "英镑":
                content_data[i][0] = "CNY/GBP"
            elif content_data[i][0] == "美元":
                content_data[i][0] = "CNY/USD"
            elif content_data[i][0] == "港币":
                content_data[i][0] = "CNY/HKD"
            elif content_data[i][0] == "欧元":
                content_data[i][0] = "CNY/EUR"
            
            # 由["现汇买入价","现钞买入价","现汇卖出价","现钞卖出价"]，将变为，["现钞买入价","现钞卖出价","现汇买入价","现汇卖出价"]
            exc = content_data[i][2]
            content_data[i][2] = content_data[i][4]
            content_data[i][4] = content_data[i][3]
            content_data[i][3] = content_data[i][1]
            content_data[i][1] = exc

            #除以100，因为中国银行用外币100块做基数，这里向建行看齐
            for ii in range(1,5):
                content_data[i][ii] = str(round(float(content_data[i][ii]) / 100,7))
            content_data[i] = content_data[i][:5]  #时间不返回了
            
        content_data = sorted(content_data, key=itemgetter(0))
        return content_data 




                