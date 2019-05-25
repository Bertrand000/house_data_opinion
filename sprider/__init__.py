# TODO 临时写到这里测试完模块删除
import jieba
import numpy as np

def read_from_file(file_name):
    with open(file_name,'r',encoding='utf-8') as fp:
        words = fp.read()
    return words

def del_stop_word(data_str):
    res = jieba.lcut(data_str)
    new_word = []
    read_file = read_from_file("Kmeans_聚类切词_停用词.txt").split("\n")
    for r in res:
        if r not in read_file:
            new_word.append(r)
    return new_word
def get_all_vector(data_str):
    word_set = set()
    docs = []
    for data in data_str:
        doc = del_stop_word(data)
        docs.append(doc)
        word_set |= set(doc)
    word_set = list(word_set)
    docs_vsm = []
    for doc in docs:
        tem_vector=[]
        for word in word_set:
            tem_vector.append(int(doc.count(word)))
        docs_vsm.append(tem_vector)
    return dict(map(lambda x,y:[x,y],word_set,docs_vsm[0]))
if __name__ == '__main__':
    get_all_vector()