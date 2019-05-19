# -*- coding: utf-8 -*-

import tkinter as tk
import tkinter.messagebox
import time
import threading
import configparser
import json
from  tkinter import ttk

from sprider import tengxun_house as txh
from sprider import wangyi_house as wyh
from data_collection_ana import qg_ana

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
    def __init__(self,window ):
        self.txh_obj = txh.TengxunHouse()
        self.wyh_obj = wyh.WangyiHouse()
        self.window = window
        threading.Thread.__init__(self)
        self.main()
    def main(self):
        '''
        主界面
        :return:
        '''
        label = tk.Label(self.window,text='获取腾讯房产与网易房产数据', font=('Arial', 12), width=30, height=2)
        label.pack()
        if not (int(self.txh_obj.redis_con.llen("loupan_data")) > 1 and int(self.txh_obj.redis_con.llen("tengxun_news")) > 1):
            b = tk.Button(self.window, text='开始获取', font=('Arial', 12), width=20, height=1, command=self.begin_get)
        else:
            b = tk.Button(self.window, text='已有数据,重新获取', font=('Arial', 12), width=20, height=1, command=self.re_get)
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
    def re_get(self):
        '''
        重新获取
        :return:
        '''
        res_status = self.dui_hua("缓存中已有数据，重新获取会删除原数据，确认重新获取吗?")
        if res_status:
            self.txh_obj.redis_con.delete("already_get_index_url")
            self.txh_obj.redis_con.delete("loupan_already_get_index_url")
            self.txh_obj.redis_con.delete("loupan_data")
            self.txh_obj.redis_con.delete("loupan_pinjia_already")
            self.txh_obj.redis_con.delete("tengxun_news")
            self.txh_obj.redis_con.delete("user_queue")
            self.begin_get()

    def begin_get(self):
        '''
        开始获取数据
        :return:
        '''
        self.exit()
        label = tk.Label(self.window, text='初次启动自动爬取数据，可能需要较长时间，数据加载完成会自动切换页面...', font=('Arial', 9), width=80, height=20)
        label.pack()
        self.new_name = "爬取数据"
        self.ex_page()
        # 启动爬虫
        threads = []
        threads_num = int(cfg.get("sys", "thread_num"))
        for i in range(0, threads_num):
            m = txh.TengxunHouse(i, "thread" + str(i))
            s = wyh.WangyiHouse(i, "thread" + str(i))
            threads.append(m)
            threads.append(s)
        for i in threads:
            i.start()
        for i in threads:
            i.join()
        self.news_table_show()


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