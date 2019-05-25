# -*- coding: utf-8 -*-
import jieba
import numpy as np
from collections import Counter

'''
 @File  : kmeans.py
 @Author: Li
 @Date  : 2019/5/25
 @Desc  : 聚类
'''
def read_from_file(file_name):
    with open(file_name,'r',encoding='utf-8') as fp:
        words = fp.read()
    return words

def del_stop_word(data_str):
    '''

    :param data_str:
    :return:
    '''
    res = jieba.lcut(data_str)
    new_word = []
    read_file = read_from_file("Kmeans_聚类切词_停用词.txt").split("\n")
    for r in res:
        if r not in read_file:
            new_word.append(r)
    return new_word
def get_all_vector(data_str):
    # 去停用词
    # word_set = set()
    doc = del_stop_word(data_str)
    # word_set |= set(doc)
    # word_set = list(word_set)
    # docs_vsm = []
    # tem_vector=[]
    # for word in word_set:
    #     tem_vector.append(int(doc.count(word)))
    # docs_vsm.append(tem_vector)
    # 词频统计
    count_map = Counter(doc)
    return count_map

def func02(kjz1,k):    #k个均值分k份

    kjz1=np.sort(kjz1);#正序
    wb2=kjz1.copy();
    #初始均匀分组wb1
    xlb=[];a=round(len(wb2)/(k));b=len(wb2)%(k);
    for j in range(1,k+1):
        xlb.append(j*a)
        if j==k:
            xlb[j-1]=xlb[j-1]+b;
    j=0;wb1=[];
    for j in range(0,k):
        wb1.append([])
    i=0;j=0;
    while(i<=len(wb2)-1):
        wb1[j].append(wb2[i]);
        if i>=xlb[j]-1:
            j=j+1;
        i=i+1;
    kj1=means(wb1);#初始分组均值

    bj=1;
    while(True):
        wb2=kjz1.copy().tolist();
        if bj!=1:
            kj1=kj2.copy();

        wb3=[];
        for j in range(0,k-1):
            wb3.append([])
        for j in range(0,k-1):
            i=-1;
            while(True):
                if wb2[i]<=kj1[j]:
                    wb3[j].append(wb2.pop(i));
                else:
                    i=i+1;
                if i>=len(wb2):
                    break
        wb3.append(wb2)

        kj2=means(wb3);#过程均值
        if bj==2:
            if kj1==kj2:
                break
        bj=2;
    return wb3

def means(lb1):    #计算均值

    mean1=[];mean2=[];std1=[];
    for j in lb1:
        mean1.append(np.mean(j).tolist())
    for j in range(1,len(mean1)):
        mean2.append(np.mean([mean1[j-1],mean1[j]])) #分组均值使用各组的均值
    print(mean2)
    return mean2
def format_str(content):
    content_str = ''
    for i in content:
        if is_chinese(i):
            content_str = content_str + i
    return content_str

def is_chinese(uchar):
    """判断一个unicode是否是汉字"""
    if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
        return True
    else:
        return False
def run(data_str):
    # chinese_word = format_str(data_str)
    kjz1 = get_all_vector(data_str)
    keys = list(kjz1.keys())
    values = list(kjz1.values())
    # 默认k=3
    k=3
    kjz3=func02(values,k)    #k个均值分k份
    for index,j in enumerate(kjz3):
        for indexv,i in enumerate(j):
            local_index = values.index(i)
            values.pop(local_index)
            kjz3[index][indexv] = {keys.pop(local_index):i}
    return kjz3

