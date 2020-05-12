import json
from lxml import etree
from datetime import datetime
import mysql.connector

from hangseng_api_fetch import HangSeng_Data
from bochk_api_fetch import BOCHK_Data
from ccb_crawl_fetch import CCB_Data
from boc_crawl_fetch import BOC_Data

def all_banks_fetch():
    dict_all_banks = dict()
    res_HangSeng = HangSeng_Data()
    res_BOCHK = BOCHK_Data()
    res_BOC = BOC_Data()
    res_CCB = CCB_Data()
    dict_all_banks["hangseng"] = res_HangSeng.fetch()
    dict_all_banks["bochk"] = res_BOCHK.fetch()
    dict_all_banks["boc"] = res_BOC.fetch()
    dict_all_banks["ccb"] = res_CCB.fetch()
    return dict_all_banks

def xml_update(dict_banks=None):
    if dict_banks is None:
        raise AssertionError
    html = etree.parse('schema.html', etree.XMLParser())
    for bank in dict_banks.keys():
        list_currencypair = dict_banks[bank]
        currency_pairs = len(list_currencypair)
        for i in range(currency_pairs):
            int_types = len(list_currencypair[i])
            for k in range(int_types):
                if k == 1:
                    id_k = "buycash"
                elif k == 2:
                    id_k = "sellcash"
                elif k == 3:
                    id_k = "buytt"
                elif k == 4:
                    id_k = "selltt"
                else:
                    continue
                if id_k != "":
                    str_content = './/td[@class="{}"][@name="{}"][@id="{}"]'.format(bank,list_currencypair[i][0],id_k)
                    id_k = ""
                else:
                    raise AssertionError
                td_content = html.find(str_content)
                td_content.text = list_currencypair[i][k]
    str_err=""
    try:
        html.write('output.xml')
    except:
        str_err = "Oops!  File cannot be saved.  Try again..."
    return str_err

def db_update():
    dict_all = all_banks_fetch()
    if xml_update(dict_banks=dict_all) == "":
        f = open("output.xml", "r")
        sql_content = f.read()
        f.close()
        time_cue = "*Update on {}".format(datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
        sql_content = sql_content + '\n' + time_cue 
        print(sql_content)
    else:
        raise AssertionError

if __name__ == "__main__":
    db_update()
