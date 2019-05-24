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

'''

@author: Mr.Chen
@file: wangyi_house.py
@time: 2019/5/17 9:49

'''
class WangyiHouse():
    pool = None
    config = None
    # 默认等待时间
    sleep_time = 0.3
    # 评论接口模板
    discuss_url_temp = "http://xf.house.163.com/cd/comment/%s.html"
    # 初始url
    index_url = "http://xf.house.163.com/cd/es/searchProducts?district=0&plate=0&metro=0&metro_station=0&price=0&total_price=0&huxing=0&property=0&base_kpsj=0&base_lpts=0&buystatus=0&base_hxwz=0&param_zxqk=0&orderby=1&use_priority_str=buystatus&pageSize=10&pageno=%s"
    headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.4098.3 Safari/537.36"
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

    def __init__(self,redis_con):
        '''

        :param threadID: 线程id
        :param name: 线程名
        '''
        # 初始化redis连接
        # 初始化数据库连接
        # try:
        #     db_host = self.config.get("db", "host")
        #     db_port = int(self.config.get("db", "port"))
        #     db_user = self.config.get("db", "user")
        #     db_pass = self.config.get("db", "password")
        #     db_db = self.config.get("db", "db")
        #     db_charset = self.config.get("db", "charset")
        #     self.db = pymysql.connect(host=db_host, port=db_port, user=db_user, passwd=db_pass, db=db_db,
        #                               charset=db_charset)
        #     self.db_cursor = self.db.cursor()
        # except Exception as err:
        #     print("请检查数据库配置")
        #     sys.exit()

        # 初始化redis连接
        self.redis_con = redis_con


    def get_loupan_pinglun(self):
        '''
        获取楼盘评论
        :return:
        '''
        # 遍历所有队列中所有值
        while int(self.redis_con.llen("user_queue")) != 0:
            name_url = str(self.redis_con.rpop("loupan_pinjia_url_queue").decode('utf-8'))
            print("正在处理:" + name_url)
            # 处理新闻页面信息
            try:
                resp = requests.session().get(name_url,headers=self.headers,timeout=5)
                BS = BeautifulSoup(resp.text, "html.parser")
                lis = BS.find_all('div',class_='cr-con')
                if len(lis) > 1:
                    print("a")
                for li in lis:
                    text = li.text
            except Exception as e:
                print("异常的url:" + name_url)
            # 设置user-agent
            self.set_random_ua()
            # 减缓爬虫速度
            time.sleep(self.sleep_time)

    def index_data(self):
        '''
        获取首页基础
        :return:
        '''
        # 获取到响应数据处理获取url到redis队列
        # 每次请求10条请求约269页
        for i in range(1, 270):
            # 初始化后的url
            url = self.index_url%i
            # 判断是否已抓取
            if not self.redis_con.hexists('loupan_already_get_index_url', url):
                self.redis_con.hset('loupan_already_get_index_url', url, 1)
                print("添加链接 " + url + "到队列")
                try:
                    resp = requests.session().get(url=url, headers=self.headers,timeout=5)
                    if not resp:
                        print("未获取到首页数据，请检查网络或接口地址")
                        break
                    # 基础信息list，地址 -> lpts -> rzsj -> yd
                    json_obj = json.loads(resp.text)
                    datas = jsonpath.jsonpath(json_obj, "$.dataList")
                    for data in datas:
                        # 分析首页数据
                        self.ex_data(data)
                    time.sleep(0.5)
                except Exception as e:
                    print("连接超时 url:" + url)
                    continue

    def ex_data(self,json_data):
        '''
        分析首页获取数据 获取评论数据
        :return:
        '''
        # 基础信息list，buystatus 购买状态 -> district 地区 -> name名称 -> price价格  -> productid评论id -> property房产类型
        # 详情信息 , base_dz 地址 -> base_ebusiness_begindate 开盘时间  -> base_ebusiness_date 交房时间
        # json格式保存首页数据
        for data in json_data:
            text = ""

            # 楼盘评价url
            pingjia_url = self.discuss_url_temp%data['productid']
            # 保存楼盘评价数据
            # 判断是否已抓取
            if not self.redis_con.hexists('loupan_pinjia_already', pingjia_url):
                self.redis_con.hset('loupan_pinjia_already', pingjia_url, 1)
                print("添加链接 " + pingjia_url + "到队列")
                # 处理新闻页面信息
                try:
                    resp = requests.session().get(pingjia_url,timeout=5,headers=self.headers)
                    BS = BeautifulSoup(resp.text, "html.parser")
                    context_pingluns = BS.find_all('div', class_='cr-con')
                    for li in context_pingluns:
                        text = text + li.text
                except Exception as e:
                    print("异常的url:" + pingjia_url)
                # 设置user-agent
                self.set_random_ua()
            data = dict(data)
            data['pinglun'] = text
            self.redis_con.lpush("loupan_data", str(data))

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

    def get_discuss(self, cmt_id):
        '''
        获取评论以及回复
        :return: json key is pinglun or huifu
        '''
        resp = requests.session().get(self.discuss_url_temp % cmt_id, headers=self.headers,timeout=5)
        # resp = requests.session().get(self.discuss_url_temp % "2300201266", headers=self.headers)
        json_data = json.loads(resp.text)
        return {"pinlun": jsonpath.jsonpath(json_data,"$.data.oriCommList")[0], "huifu": jsonpath.jsonpath(json_data, "$.data.repCommList.*.*")}

    def run(self):
        self.index_data()

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