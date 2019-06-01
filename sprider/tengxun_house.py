# -*- coding: utf-8 -*-
import requests
import json
import jsonpath
import time
import random
import re
from bs4 import BeautifulSoup


'''
 @File  : tengxun_house.py
 @Author: Li
 @Date  : 2019/5/14
 @Desc  : 房产
'''
class TengxunHouse():
    pool = None
    config = None
    # 默认等待时间
    sleep_time = 0.3
    header_url = "https://cd.house.qq.com"
    # 评论数接口模板
    discuss_num_url_temp = "https://coral.qq.com/article/%s/commentnum"
    # 评论接口模板
    discuss_url_temp = "https://coral.qq.com/article/%s/comment/v2?orinum=30&pageflag=0&orirepnum=500"
    # 初始url
    index_url = [
            #   全国热点
            "https://cd.house.qq.com/c/qgrd_%s.htm",
            #   房产新闻
           "https://cd.house.qq.com/c/firstnewslist_%s.htm",
            #   楼市政策
           "http://cd.house.qq.com/c/lszc_%s.htm",
            #   土地市场
           "http://cd.house.qq.com/c/tdsc_%s.htm",
            #   数据调查
           "http://cd.house.qq.com/c/sjdc_%s.htm",
            #   置业宝典
           "http://cd.house.qq.com/c/zybd_%s.htm"
       ]
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

    # 被抓取新闻计数
    counter = 0

    def __init__(self,redis_con):
        '''

        :param threadID: 线程id
        :param name: 线程名
        '''
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
        #     print(err)
        #     sys.exit()

        # 初始化redis连接
        self.redis_con = redis_con


    def index_data(self):
        '''
        获取首页
        :return:
        '''
        for url in self.index_url:
            # 获取前14页
            for i in range(1,15):
                # 获取到响应数据处理获取url到redis队列
                try:
                    resp = requests.session().get(url=url%str(i),headers=self.headers,timeout=5)
                    # 减缓速度
                except Exception as e:
                    print("链接超时")
                time.sleep(self.sleep_time)
                self.url_data(resp.text)




    def url_data(self,index_html):
        '''
        分析获取数据
        :return:
        '''
        if not index_html:
            return
        BS = BeautifulSoup(index_html, "html.parser")
        user_a = BS.find_all("a")
        for a in user_a:
            if a:
                href = a.get('href')
                # test = href[(href.rindex('/')) + 1:]
                self.add_wait_user(self.header_url + href)
            else:
                print("获取初始页面 a 标签失败，跳过")
                continue

    # 加入待抓取用户队列，先用redis判断是否已被抓取过
    def add_wait_user(self, name_url):
        # 判断是否已抓取
        if not self.redis_con.hexists('already_get_index_url', name_url):
            self.counter += 1
            print(name_url + " 加入队列")
            self.redis_con.hset('already_get_index_url', name_url, 1)
            self.redis_con.lpush('user_queue', name_url)
        else:
            print("链接已获取过")

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
        json_data = {}
        resp = requests.session().get(url,headers=self.headers,timeout=5)
        try:
            BS = BeautifulSoup(resp.text, "html.parser")
            # 获取所有P标签内的内容
            P = BS.find_all("p")

            context = ""
            for p in P:
                context += p.text
            json_data['context'] = self.format_str(str(P))
            # 获取标题
            title = BS.find("title").text
            json_data['title'] = title
            # 获取时间
            pub_time = BS.find("span", class_="a_time")

            # 若pub_time为空则按新版数据格式匹配
            if not pub_time:
                pub_time = BS.find("span", class_="article-time")
            # 若pub_time为空则更新版数据格式匹配
            if not pub_time:
                pub_time = BS.find("span", class_="pubTime")
            pub_time = pub_time.text
            json_data['pub_time'] = pub_time
            # 正则获取页面js中的cmt参数值
            cmt_id = re.findall("cmt_id = (.+?);", resp.text)
            if cmt_id:
                cmt_id = cmt_id[0]
            # 获取评论数
            discuss_num = int(self.get_discuss_number(cmt_id)) if cmt_id else 0
            json_data['discuss_num'] = discuss_num
            # 获取评论以及回复内容 (评论内容腾讯设置一次请求最多拿30条，鉴于代码复杂度，每条新闻最多取30条评论)
            discuss_re = self.get_discuss(cmt_id) if cmt_id else ["",""]
            json_data['discuss'] = ""
            json_data['huifu'] = ""
            if discuss_re[0]:
                json_data['discuss'] = discuss_re[0]
            if discuss_re[1]:
                json_data['huifu'] = discuss_re[1]
            self.redis_con.lpush("tengxun_news",str(json_data))
        except Exception as e:
            print(e)
        # my_uuid = str(uuid.uuid4())
        # 保存数据
        # self.save_data(my_uuid,cmt_id,title,pub_time,discuss_num, context,discuss_re)

    def _sget_new_data(self,url):
        json_data = {}
        resp = requests.session().get(url,headers=self.headers,timeout=5)
        try:
            BS = BeautifulSoup(resp.text, "html.parser")
            P = BS.find_all("p")

            context = ""
            for p in P:
                context += p.text
            json_data['context'] = self.format_str(str(P))
            title = BS.find("title").text
            json_data['title'] = title
            pub_time = BS.find("span", class_="a_time")

            if not pub_time:
                pub_time = BS.find("span", class_="article-time")
            if not pub_time:
                pub_time = BS.find("span", class_="pubTime")
            pub_time = pub_time.text
            json_data['pub_time'] = pub_time
            cmt_id = re.findall("cmt_id = (.+?);", resp.text)
            if cmt_id:
                cmt_id = cmt_id[0]
            discuss_num = int(self.get_discuss_number(cmt_id)) if cmt_id else 0
            json_data['discuss_num'] = discuss_num
            discuss_re = self.get_discuss(cmt_id) if cmt_id else ["",""]
            json_data['discuss'] = ""
            json_data['huifu'] = ""
            if discuss_re[0]:
                json_data['discuss'] = discuss_re[0]
            if discuss_re[1]:
                json_data['huifu'] = discuss_re[1]
            self.redis_con.lpush("tengxun_news",str(json_data))
        except Exception as e:
            print(e)
        # my_uuid = str(uuid.uuid4())
        # 保存数据
        # self.save_data(my_uuid,cmt_id,title,pub_time,discuss_num, context,discuss_re)
    def _save_data(self, uuid,cmt_id, title, pub_time, discuss_num, new_context,discuss_redis):
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
        try:
            resp = requests.session().get(self.discuss_num_url_temp%cmt_id,headers=self.headers,timeout=5)
            json_data = json.loads(resp.text)
        except Exception as e:
            print(e)
        return jsonpath.jsonpath(json_data,"$.data.commentnum")[0]

    def get_discuss(self, cmt_id):
        '''
        获取评论以及恢复
        :return: json key is pinglun or huifu
        '''
        content = []
        try:
            resp = requests.session().get(self.discuss_url_temp % cmt_id, headers=self.headers,timeout=5)
            json_data = json.loads(resp.text)
        except Exception as e:
            print(e)
        content.append(jsonpath.jsonpath(json_data, "$.data.oriCommList[*].content"))
        content.append(jsonpath.jsonpath(json_data, "$.data.repCommList.*[*].content"))
        return content

    def format_str(self,content):
        content_str = ''
        for i in content:
            if self.is_chinese(i):
                content_str = content_str + i
        return content_str

    def is_chinese(self,uchar):
        """判断一个unicode是否是汉字"""
        if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
            return True
        else:
            return False

    def manage(self):
        '''
        方法入口
        :return:
        '''
        self.index_data()
        # 出队列获取用户name_url redis取出的是byte，要decode成utf-8
        # name_url = str(self.redis_con.rpop("user_queue").decode('utf-8'))
        # 遍历所有队列中所有值
        while int(self.redis_con.llen("user_queue"))!=0:
            name_url = str(self.redis_con.rpop("user_queue").decode('utf-8'))
            print("正在处理:" + name_url)
            # 处理新闻页面信息
            try:
                # if self.redis_con.llen("tengxun_news")>800:
                #     break
                self.get_new_data(name_url)
            except Exception as e:
                print("异常的url:"+name_url)
            # 设置user-agent
            self.set_random_ua()
            # 减缓爬虫速度
            time.sleep(self.sleep_time)

    def run(self):
        print(self.name + " is running")
        self.manage()