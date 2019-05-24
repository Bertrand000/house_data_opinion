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
    for r in res:
        if r not in read_from_file("Kmeans_聚类切词_停用词.txt").split("\n"):
            new_word.append(r)
    return new_word
def get_all_vector():
    data_str = ["我，我是你爸爸爸爸爸","我儿子，是，是你啊，啊啊，"]
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
            tem_vector.append(doc.count(word)*1.0)
        docs_vsm.append(tem_vector)
    docs_matrix = np.array(docs_vsm)
    # TODO 列表构建词带空间
    print(docs_matrix)

if __name__ == '__main__':
    get_all_vector()