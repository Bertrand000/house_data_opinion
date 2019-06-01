#-*- coding: utf-8 -*-
import os
from matplotlib import pyplot as plt

def cre_bing(labels,sizes,path=False):
    '''
    分析文档
    :return:
    '''
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.figure(figsize=(6, 9))  # 调节图形大小
    # colors = ['red','#F0F8FF',"yellow"] #每块颜色定义
    colors = ['#F5F5DC', 'yellowgreen', '#F0F8FF', 'yellow']  # 每块颜色定义
    explode = [0 for l in labels]
    plt.pie(sizes,
            explode=explode,
            labels=labels,
            colors=colors,
            autopct='%3.2f%%',  # 数值保留固定小数位
            shadow=False,  # 无阴影设置
            startangle=90,  # 逆时针起始角度设置
            pctdistance=0.6)  # 数值距圆心半径倍数距离
    # patches饼图的返回值，texts1饼图外label的文本，texts2饼图内部的文本
    # x，y轴刻度设置一致，保证饼图为圆形
    plt.axis('equal')
    # 获取当前目录绝对路径
    if path:
        plt.savefig(path)
    else:
        plt.show()
