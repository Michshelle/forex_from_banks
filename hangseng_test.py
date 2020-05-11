import urllib3
import json


with open('bank_api_info.json') as json_file:
    js_bank = json.load(json_file)

hangseng_info=js_bank["HangSeng_Info"]["API_Key"]
hangseng_url = js_bank["HangSeng_Info"]["URLs"]["Base_URL"] + js_bank["HangSeng_Info"]["URLs"]["Path_URL"]["Forex_Info"]

https = urllib3.PoolManager()

r = https.request('GET', 
                   hangseng_url,
                   headers=hangseng_info
                )
data = json.loads(r.data.decode('utf-8'))  # 此行是为了查看返回的文件内容是否准确
print(type(data))
#print(json.dumps(data, indent=4))  #Indent 4 可美化输出

#with open('hangseng_forex.json', 'w') as json_file:
#     json.dumps(data, indent=4)