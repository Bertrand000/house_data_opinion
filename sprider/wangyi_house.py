#!/usr/bin/env python
# encoding: utf-8

import configparser
import redis
import requests
import json
import jsonpath
import time
import sys
import threading
import random
import re
import pymysql
import uuid
from bs4 import BeautifulSoup

# 获取配置
cfg = configparser.ConfigParser()
cfg.read("../config.ini")
'''

@author: Mr.Chen
@file: wangyi_house.py
@time: 2019/5/17 9:49

'''
class WangyiHouse(threading.Thread):
    pool = None
    config = None
    # 默认等待时间
    sleep_time = 1
    header_url = "https://cd.house.qq.com"
    # 评论数接口模板
    discuss_num_url_temp = "https://coral.qq.com/article/%s/commentnum"
    # 评论接口模板
    discuss_url_temp = "https://coral.qq.com/article/%s/comment/v2?orinum=30&pageflag=0&orirepnum=500"
    # 初始url
    index_url = "http://xf.house.163.com/cd/es/searchProducts?district=0&plate=0&metro=0&metro_station=0&price=0&total_price=0&huxing=0&property=0&base_kpsj=0&base_lpts=0&buystatus=0&base_hxwz=0&param_zxqk=0&orderby=1&use_priority_str=buystatus&pageSize=10000&pageno=1"
    headers = {
        "Cookie":"TEMP_USER_ID=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1aWQiOiI1Y2Q5NmNmZDM3NzIwIiwidGltZSI6MTU1Nzc1MzA4NX0.bC7tWfWBI4EZnfyrruTHQtIBh7U-wQ5mhpN-qxO5VaU; userid=1557752814463_335ita9276; ifh_site=21057%2Ccd; city_redirected=12; ifengRotator_iis3_c=7; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2216ab14d7fdd1-00569b86bd20bd-76212462-1440000-16ab14d7fe0ba%22%2C%22%24device_id%22%3A%2216ab14d7fdd1-00569b86bd20bd-76212462-1440000-16ab14d7fe0ba%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%7D; Hm_lvt_2618c9646a4a7be2e5f93653be3d5429=1557752814,1557833624; Hm_lpvt_2618c9646a4a7be2e5f93653be3d5429=1557834105"
        ,"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.4098.3 Safari/537.36"
       }
    # ua池，随机取防止被查
    ua = (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)',
    )

    # 被抓取楼盘数计数
    counter = 0

    def __init__(self,threadID=1, name=''):
        '''

        :param threadID: 线程id
        :param name: 线程名
        '''
        # 初始化redis连接
        # 多线程
        print("线程" + str(threadID) + "初始化")
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.config = cfg
        try:
            print("线程" + str(threadID) + "初始化成功")
        except Exception as err:
            print(err)
            print("线程" + str(threadID) + "开启失败")

        self.threadLock = threading.Lock()
        # 初始化数据库连接
        try:
            db_host = self.config.get("db", "host")
            db_port = int(self.config.get("db", "port"))
            db_user = self.config.get("db", "user")
            db_pass = self.config.get("db", "password")
            db_db = self.config.get("db", "db")
            db_charset = self.config.get("db", "charset")
            self.db = pymysql.connect(host=db_host, port=db_port, user=db_user, passwd=db_pass, db=db_db,
                                      charset=db_charset)
            self.db_cursor = self.db.cursor()
        except Exception as err:
            print("请检查数据库配置")
            sys.exit()

        # 初始化redis连接
        try:
            redis_host = cfg.get("redis", "host")
            redis_port = cfg.get("redis", "port")
            self.redis_con = redis.Redis(host=redis_host, port=redis_port, db=0)
            # 刷新redis库
            # self.redis_con.flushdb()
        except Exception as err:
            print("请安装redis或检查redis连接配置")
            sys.exit()

        # 初始化系统设置
        self.max_queue_len = int(self.config.get("sys", "max_queue_len"))
        self.sleep_time = float(self.config.get("sys", "sleep_time"))

    def index_data(self):
        '''
        获取首页
        :return:
        '''
        # 获取到响应数据处理获取url到redis队列
        resp = requests.session().get(url=self.index_url, headers=self.headers)
        # 分析首页数据
        self.url_data(resp.text)

    def url_data(self,json_data):
        '''
        分析获取数据
        :return:
        '''
        if not json_data:
            print("未获取到首页数据，请检查网络或接口地址")
            return
        # 基础信息list，地址 -> lpts -> rzsj -> yd
        json_obj = json.loads(json_data)
        data = jsonpath.jsonpath(json_obj,"$.dataList[*].baseinfo.base_dz")
        print(data)
    # 加入待抓取用户队列，先用redis判断是否已被抓取过
    def add_wait_user(self, name_url):
        # 判断是否已抓取
        if not self.redis_con.hexists('already_get_index_url', name_url):
            self.counter += 1
            print(name_url + " 加入队列")
            self.redis_con.hset('already_get_index_url', name_url, 1)
            self.redis_con.lpush('user_queue', name_url)
            print("添加用户 " + name_url + "到队列")

    # 获取页面出错移出redis
    def del_already_user(self, name_url):
        self.threadLock.acquire()

        if not self.redis_con.hexists('already_get_index_url', name_url):
            self.counter -= 1
            self.redis_con.hdel('already_get_index_url', name_url)
        self.threadLock.release()

    def set_random_ua(self):
        '''
        随机设置ua值
        :return:
        '''
        length = len(self.ua)
        rand = random.randint(0, length - 1)
        self.headers['User-Agent'] = self.ua[rand]

    def get_new_data(self,url):
        '''
        获取新闻页信息
        :return:
        '''
        resp = requests.session().get(url,headers=self.headers)
        BS = BeautifulSoup(resp.text, "html.parser")
        # 获取所有P标签内的内容
        P = BS.find_all("p")

        context = ""
        for p in P:
            context += p.text
        # 获取标题
        title = BS.find("title").text
        # 获取时间
        pub_time = BS.find("span", class_="a_time")
        # 若pub_time为空则按新版数据格式匹配
        if not pub_time:
            pub_time = BS.find("span", class_="article-time")
        # 若pub_time为空则更新版数据格式匹配
        if not pub_time:
            pub_time = BS.find("span", class_="pubTime")
        pub_time = pub_time.text
        # 正则获取页面js中的cmt参数值
        cmt_id = re.findall("cmt_id = (.+?);", resp.text)
        if cmt_id:
            cmt_id = cmt_id[0]
        # 获取评论数
        discuss_num = int(self.get_discuss_number(cmt_id)) if cmt_id else 0
        # 获取评论以及回复内容 (评论内容腾讯设置一次请求最多拿30条，鉴于代码复杂度，每条新闻最多取30条评论)
        discuss_re = self.get_discuss(cmt_id) if cmt_id else ""
        my_uuid = str(uuid.uuid4())
        # 保存数据
        self.save_data(my_uuid,cmt_id,title,pub_time,discuss_num, context,discuss_re)

    def save_data(self, uuid,cmt_id, title, pub_time, discuss_num, new_context,discuss_redis):
        '''
        mysql保存数据
        :param title: 标题
        :param time: 时间
        :param discuss_num: 评论数
        :param discuss: 评论
        :param re_discuss: 评论回复
        :return:
        '''
        # 保存新闻
        news_sql = '''
        REPLACE INTO
                          news(cmt_id,title,pub_time,discuss_num,uuid,context)
                          VALUES(%s,%s,%s,%s,%s,%s)
        '''
        # 保存评论
        discuss_sql = '''
        REPLACE INTO
                          discuss(content,dis_time,pid,new_uuid)
                          VALUES(%s,%s,%s,%s)
        '''
        # 评论回复
        re_discuss_sql = '''
                REPLACE INTO
                                  re_discuss(content,redis_time,pid,new_uuid)
                                  VALUES(%s,%s,%s,%s)
                '''
        # 保存评论回复
        try:
            self.db_cursor.execute(news_sql,(cmt_id if cmt_id else "0", str(title), str(pub_time), discuss_num, uuid, str(new_context)))
            if discuss_num:
                if discuss_redis['pinlun']:
                    for discuss in discuss_redis['pinlun']:
                        self.db_cursor.execute(discuss_sql, (discuss['content'], discuss['time'], discuss['id'], uuid))
                if discuss_redis['huifu']:
                    for re_dis in discuss_redis['huifu']:
                        self.db_cursor.execute(re_discuss_sql,(re_dis['content'],re_dis['time'],re_dis['parent'],uuid))
            self.db.commit()
        except Exception as e:
            print(e)

    def get_discuss_number(self, cmt_id):
        '''
        获取评论数
        :return:
        '''
        resp = requests.session().get(self.discuss_num_url_temp%cmt_id,headers=self.headers)
        json_data = json.loads(resp.text)
        return jsonpath.jsonpath(json_data,"$.data.commentnum")[0]

    def get_discuss(self, cmt_id):
        '''
        获取评论以及恢复
        :return: json key is pinglun or huifu
        '''
        resp = requests.session().get(self.discuss_url_temp % cmt_id, headers=self.headers)
        # resp = requests.session().get(self.discuss_url_temp % "2300201266", headers=self.headers)
        json_data = json.loads(resp.text)
        return {"pinlun": jsonpath.jsonpath(json_data,"$.data.oriCommList")[0], "huifu": jsonpath.jsonpath(json_data, "$.data.repCommList.*.*")}

    def manage(self):
        '''
        方法入口
        :return:
        '''
        self.index_data()
        # # 判断是否取过首页信息
        # if not int(self.redis_con.hlen("already_get_index_url")) > 2000:
        #     self.index_data()
        # # 出队列获取用户name_url redis取出的是byte，要decode成utf-8
        # # name_url = str(self.redis_con.rpop("user_queue").decode('utf-8'))
        # # 遍历所有队列中所有值
        # while int(self.redis_con.llen("user_queue"))!=0:
        #     name_url = str(self.redis_con.rpop("user_queue").decode('utf-8'))
        #     print("正在处理:" + name_url)
        #     # 处理新闻页面信息
        #     try:
        #         self.get_new_data(name_url)
        #     except Exception as e:
        #         print("异常的url:"+name_url)
        #     # 设置user-agent
        #     self.set_random_ua()
        #     # 减缓爬虫速度
        #     time.sleep(self.sleep_time)

    def run(self):
        print(self.name + " is running")
        self.manage()

if __name__ == '__main__':
    '''
    多线程启动
    '''
    threads = []
    threads_num = int(cfg.get("sys", "thread_num"))
    for i in range(0, threads_num):
        m = WangyiHouse(i, "thread" + str(i))
        threads.append(m)

    for i in range(0, threads_num):
        threads[i].start()

    for i in range(0, threads_num):
        threads[i].join()