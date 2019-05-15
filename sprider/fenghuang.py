# -*- coding: utf-8 -*-
import configparser
import redis
import requests
import json
import jsonpath
import time

# @File  : fenghuang.py
# @Author: Li
# @Date  : 2019/5/14
# @Desc  : 凤凰房产
class FengHuang():
    pool = None
    url = "https://cd.house.ifeng.com/news/wap"
    headers = {
        "Cookie":"TEMP_USER_ID=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1aWQiOiI1Y2Q5NmNmZDM3NzIwIiwidGltZSI6MTU1Nzc1MzA4NX0.bC7tWfWBI4EZnfyrruTHQtIBh7U-wQ5mhpN-qxO5VaU; userid=1557752814463_335ita9276; ifh_site=21057%2Ccd; city_redirected=12; ifengRotator_iis3_c=7; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2216ab14d7fdd1-00569b86bd20bd-76212462-1440000-16ab14d7fe0ba%22%2C%22%24device_id%22%3A%2216ab14d7fdd1-00569b86bd20bd-76212462-1440000-16ab14d7fe0ba%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%7D; Hm_lvt_2618c9646a4a7be2e5f93653be3d5429=1557752814,1557833624; Hm_lpvt_2618c9646a4a7be2e5f93653be3d5429=1557834105"
        ,"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.4098.3 Safari/537.36"
       }

    def __init__(self):
        # 获取配置
        cfg = configparser.ConfigParser()
        cfg.read("../config.ini")
        # redis 初始化连接池
        self.pool = redis.ConnectionPool(host='127.0.0.1')  # 实现一个连接池

    def init_url_data(self):
        '''
        初始化新闻数据
        :return:
        '''
        # post
        i = 1
        post_data = {
            "pageid": i
            , "siteid": 21057
            , "type": 2
        }
        sum = 0
        while True:
            datas = self.get_url_data(post_data)
            # 判断下页是否有数据 若连续3次出现无数据则视为页面数据已爬完
            if not datas:
                sum = sum + 1
            if sum > 2:
                break
            r = redis.Redis(connection_pool=self.pool)
            r.set("url_data",datas)
            i = i + 1
            post_data["pageid"] = i
            # 每次请求间隔300毫秒
            time.sleep(0.3)
            print("----------------------------------加载数据成功-------------------------------------------")
            print(datas)
        print("url数据初始化完成")
    def get_url_data(self,post_data):
        '''
        分析获取数据
        :return:
        '''
        req = requests.session().post(url=self.url,data=post_data,headers=self.headers)
        data = json.loads(req.text)
        data_end = jsonpath.jsonpath(data,"data.newslist.*")
        return data_end
if __name__ == '__main__':
    FengHuang().init_url_data()