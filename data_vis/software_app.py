# -*- coding: utf-8 -*-

import tkinter as tk
import tkinter.messagebox
import redis
import time
import configparser
import json
import sys
import threading
from tkinter import ttk
from tkinter import *

from sprider import tengxun_house as txh
from sprider import wangyi_house as wyh
# from data_collection_ana import qg_ana

# 获取配置
cfg = configparser.ConfigParser()
cfg.read("./config.ini")

'''
 @File  : software_app.py
 @Author: Li
 @Date  : 2019/5/20
 @Desc  : GUI
'''
class softApp(threading.Thread):
    window = None
    new_name = None
    n = None
    x = None
    txh_obj = None
    wyh_obj = None
    redis_con = None
    sleep_time = None
    def __init__(self,window):
        try:
            redis_host = cfg.get("redis", "host")
            redis_port = cfg.get("redis", "port")
            self.redis_con = redis.Redis(host=redis_host, port=redis_port, db=0)
            # 刷新redis库
            # self.redis_con.flushdb()
        except Exception as err:
            print("请安装redis或检查redis连接配置")
            sys.exit()
        self.txh_obj = txh.TengxunHouse(self.redis_con)
        self.wyh_obj = wyh.WangyiHouse(self.redis_con)
        self.window = window
        self.main()
    def main(self):
        '''
        主界面
        :return:
        '''
        label = tk.Label(self.window,text='获取腾讯房产与网易房产数据', font=('Arial', 12), width=30, height=2)
        label.pack()
        # if not (int(self.txh_obj.redis_con.llen("loupan_data")) > 1 or int(self.txh_obj.redis_con.llen("tengxun_news")) > 1):
        #     b = tk.Button(self.window, text='开始获取', font=('Arial', 12), width=20, height=1, command=self.begin_get)
        # else:
        #     b = tk.Button(self.window, text='重新获取', font=('Arial', 12), width=20, height=1, command=self.re_get)
        b = tk.Button(self.window, text='爬虫管理', font=('Arial', 12), width=20, height=1, command=self.get_data_via)
        b2 = tk.Button(self.window, text='查看信息', font=('Arial', 12), width=20, height=1, command=self.news_table_show)
        b.pack()
        b2.pack()
        self.new_name = "主界面"


        self.ex_page()
    def dui_hua(self,kuang_name):
        '''
        对话框
        :return:
        '''
        return tkinter.messagebox.askokcancel('提示', kuang_name)
    def qg_table_show(self):
        '''
        评论情感界面
        :return:
        '''
        self.exit()
        label = tk.Label(self.window, text='情感分析信息列表(情感倾向分值越高,该条新闻越能被接受)', font=('Arial', 9), width=80, height=2)
        label.pack()

        # 获取数据
        result = self.txh_obj.redis_con.lrange("tengxun_news", 0, -1)
        # 定义一个空列表存储取出的元素
        reallyresult = []
        # 遍历取出的全部数据，实际上是列表类型的bytes数据类型
        for item in result:
            try:
                item = str(item, encoding='utf-8').replace("\"", "“").replace("'", "\"").replace("True",
                                                                                                 "true").replace(
                    "None", "null").replace("False", "false").replace("\\xa0", " ")
                item = json.loads(item)
                # 空列表追加数据
                reallyresult.append(item)
            except Exception as err:
                print(err)

        # table
        title = ['1', '2', '3', '4', '5', '6','7']
        tree = ttk.Treeview(self.window, columns=title, show='headings')  # 表格
        tree.column("1", width=20)
        tree.column("2", width=100)
        tree.column("3", width=100)
        tree.column("4", width=100)
        tree.column("5", width=100)
        tree.column("6", width=100)
        tree.column("7", width=100)

        tree.heading("1", text="情感倾向")
        tree.heading("2", text="标题")
        tree.heading("3", text="发布时间")
        tree.heading("4", text="评论数")
        tree.heading("5", text="评论")
        tree.heading("6", text="评论回复")
        tree.heading("7", text="新闻内容")
        for index, i in enumerate(reallyresult):
            qg_value = 0
            if i['discuss_num'] or "0":
                qg_res_value = qg_ana.sentiment_score(qg_ana.sentiment_score_list("".join(i['discuss']) + ',' + "".join(i['huifu'])))
                for value in qg_res_value:
                    qg_value = qg_value + value[0] - value[1]
            tree.insert("", 'end', values=(
            qg_value, i['title'], i['pub_time'], i['discuss_num'], i['discuss'], i['huifu'], i['context']))  # 插入数据，
        tree.pack()

        self.ex_page()

    def news_table_show(self):
        '''
        列表展示
        :return:
        '''
        # 销魂原界面
        self.exit()
        # 切换界面
        self.new_name = "信息列表"
        label = tk.Label(self.window, text='信息列表', font=('Arial', 12), width=30, height=2)
        label.pack()
        b = tk.Button(self.window, text='评论情感分析', font=('Arial', 12), width=20, height=1, command=self.qg_table_show)
        b.pack()
        # 获取数据
        result = self.txh_obj.redis_con.lrange("tengxun_news",0,-1)
        # 定义一个空列表存储取出的元素
        reallyresult = []
        # 遍历取出的全部数据，实际上是列表类型的bytes数据类型
        for item in result:
            try:
                item = str(item, encoding='utf-8').replace("\"", "“").replace("'", "\"").replace("True","true").replace(
                    "None", "null").replace("False", "false").replace("\\xa0", " ")
                item = json.loads(item)
                # 空列表追加数据
                reallyresult.append(item)
            except Exception as err:
                print(err)

        # table
        title=['1','2','3','4','5','6']
        tree = ttk.Treeview(self.window,columns=title,show='headings')  # 表格
        tree.column("1", width=100)
        tree.column("2", width=100)
        tree.column("3", width=100)
        tree.column("4", width=100)
        tree.column("5", width=100)
        tree.column("6", width=100)

        tree.heading("1", text="标题")  # 显示表头
        tree.heading("2", text="发布时间")
        tree.heading("3", text="评论数")
        tree.heading("4", text="评论")
        tree.heading("5", text="评论回复")
        tree.heading("6", text="新闻内容")
        for index,i in enumerate(reallyresult):
            tree.insert("",'end', values=(i['title'], i['pub_time'], i['discuss_num'] ,i['discuss'], i['huifu'],i['context']))  # 插入数据，
        tree.pack()

        self.ex_page()

    def get_data_via(self):
        '''
        获取数据页面
        :return:
        '''
        spri_manage = tk.Tk()
        b1 = None
        page_name = "爬虫管理"
        label = tk.Label(spri_manage, text='点击按钮运行爬虫')
        b1 = tk.Button(spri_manage, text='开始', font=('Arial', 12), width=20, height=1)
        if self.redis_con.llen('loupan_data') > 0 or self.redis_con.llen('tengxun_news') > 0:
            b1 = tk.Button(spri_manage, text='重新获取', font=('Arial', 12), width=20, height=1)
        b1.config(command=lambda: self.begin_get(b1, label))
        label.pack()
        b1.pack()
        screenwidth = spri_manage.winfo_screenwidth()
        screenheight = spri_manage.winfo_screenheight()
        size = '%dx%d+%d+%d' % (500, 300, (screenwidth - 500) / 2, (screenheight - 300) / 2)
        spri_manage.geometry(size)
        spri_manage.title(page_name)
        spri_manage.mainloop()

    def re_get(self):
        '''
        重新获取
        :return:
        '''


    def begin_get(self, b1, label):
        '''
        开始获取数据
        :return:
        '''
        b1.config(state=tk.DISABLED)
        # label = Enter(self.window, text = "")
        res_status = True
        if self.redis_con.llen('loupan_data') > 0 or self.redis_con.llen('tengxun_news') > 0:
            res_status = self.dui_hua("缓存中已有数据，重新获取会删除原数据，确认重新获取吗?")
        if res_status:
            self.txh_obj.redis_con.delete("already_get_index_url")
            self.txh_obj.redis_con.delete("loupan_already_get_index_url")
            self.txh_obj.redis_con.delete("loupan_data")
            self.txh_obj.redis_con.delete("loupan_pinjia_already")
            self.txh_obj.redis_con.delete("tengxun_news")
            self.txh_obj.redis_con.delete("user_queue")

        # # 启动爬虫
        thread1 = threading.Thread(target=self.run_spr)
        thread1.setDaemon(True)  # 线程守护，即主进程结束后，此线程也结束。否则主进程结束子进程不结束
        thread1.start()
        tkinter.messagebox.showinfo(title="来自爬虫的消息",message="爬虫已于后台启动，在爬虫完成提示框出现之前请勿关闭主界面")
        self.news_table_show()
    def run_spr(self):
        # 启动爬虫
        self.wyh_obj.index_data()
        self.txh_obj.manage()
        tkinter.messagebox.showinfo(title="来自爬虫的消息",message="数据加载完成，爬虫退出工作")

        # ------------------------------------------------------------------------------------------------------
        #                             进度条 sum_nub:总数据条数  new_nub:当前数据条数
        # ------------------------------------------------------------------------------------------------------
        # 创建主窗口
        # window = tk.Tk()
        # window.title('进度条')
        # window.geometry('630x150')
        #
        # # 设置下载进度条
        # tk.Label(window, text='爬取进度:', ).place(x=50, y=60)
        # canvas = tk.Canvas(window, width=456, height=22, bg="white")
        # canvas.place(x=110, y=60)
        # # 总数量
        # sum_nub = self.txh_obj.counter
        # # 当前剩余数量
        # new_nub = self.txh_obj.redis_con.llen("user_queue")
        # x = 456/sum_nub #每条数据完成爬取进度
        # y = new_nub*x #当前位置对应进度条
        # # 当前剩余链接状态
        # get_data_status = True
        #
        # # 显示下载进度
        # # 填充进度条
        # fill_line = canvas.create_rectangle(1.5, 1.5, 0, 23, width=0, fill="green")
        # while get_data_status:
        #     canvas.coords(fill_line, (0, 0, y, 60))
        #     window.update()
        #     if not self.txh_obj.redis_con.llen("user_queue"):
        #         window.exit()
        #         tk.messagebox.showinfo('提示', '数据爬取完成')
        #     time.sleep(1)
        #
        # self.exit()

    def read_black_load(self,fill_line,canvas,window):
        self.n = self.n + 1 / self.x

    def ex_page(self):
        '''
        打开界面
        :param new_name: 新界面名称
        :return:
        '''
        self.center_window(600, 400)
        self.window.title(self.new_name)
        self.window.mainloop()

    def center_window(self, width, height):
        screenwidth = self.window.winfo_screenwidth()
        screenheight = self.window.winfo_screenheight()
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.window.geometry(size)

    def exit(self):
        '''
        销毁
        :return:
        '''
        self.window.destroy()
        self.window = tk.Tk()

    def run(self):
        self.main()

if __name__ == '__main__':
    app = softApp(tk.Tk())