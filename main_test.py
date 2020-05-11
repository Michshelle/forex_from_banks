import json
from hangseng_api_fetch import HangSeng_Data
from bochk_api_fetch import BOCHK_Data
from ccb_crawl_fetch import CCB_Data
from boc_crawl_fetch import BOC_Data


res_HangSeng = HangSeng_Data()
print(res_HangSeng.fetch())

res_BOCHK = BOCHK_Data()
print(res_BOCHK.fetch())

res_BOC = BOC_Data()
print(res_BOC.fetch())

res_CCB = CCB_Data()
print(res_CCB.fetch())
