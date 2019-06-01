import numpy as np
import jieba
from data_collection_ana import qg_ana as qg

"""配置"""
SMOOTHNESS = 1e-8

START = 'start'  # 句始tag
NEG = 'negative' # 积极词
POS = 'positive' # 消极词
END = 'end' #句尾tag

"""数据预处理"""
words_list = []
dictionary_pos = open("../data_collection_ana/positive.txt", 'r', encoding='utf-8')
for word in dictionary_pos:
    list = []
    word = word.strip('\n')
    list.append(word)
    list.append(NEG)
    words_list.append(tuple(list))

dictionary_pas = open("../data_collection_ana/negative.txt", 'r', encoding='utf-8')
for word in dictionary_pas:
    list = []
    word = word.strip('\n')
    list.append(word)
    list.append(POS)
    words_list.append(tuple(list))
corpus = np.array(words_list)

words = sorted(set(corpus[:, 0]))
tags = sorted(set(corpus[:, 1]))

W = len(words)  # 词汇量
T = len(tags)  # 词性种类数

word2id = {words[i]: i for i in range(W)}
tag2id = {tags[i]: i for i in range(T)}
id2tag = {i: tags[i] for i in range(T)}

"""HMM训练"""
emit_p = np.zeros((T, W)) + SMOOTHNESS  # emission_probability
start_p = np.zeros(T) + SMOOTHNESS  # start_probability
trans_p = np.zeros((T, T)) + SMOOTHNESS  # transition_probability

prev_tag = START  # 前一个tag
for word, tag in corpus:
    wid, tid = word2id[word], tag2id[tag]
    emit_p[tid][wid] += 1
    if prev_tag == START:
        start_p[tid] += 1
    else:
        trans_p[tag2id[prev_tag]][tid] += 1
    prev_tag = START if tag == END else tag  # 句尾判断

# 频数 --> 概率对数
start_p = np.log(start_p / sum(start_p))
for i in range(T):
    test = emit_p[i] / sum(emit_p[i])
    emit_p[i] = np.log(emit_p[i] / sum(emit_p[i]))
    trans_p[i] = np.log(trans_p[i] / sum(trans_p[i]))


def viterbi(sentence):
    """维特比算法"""
    obs = []
    for w in jieba.lcut(sentence, cut_all=False):
        try:
            obs.append(word2id[w])
        except Exception as e:
            print("语料库未记录的词跳过。。。")
    le = len(obs)  # 序列长度

    # 动态规划矩阵
    dp = np.zeros((le, T))  # 记录节点最大概率对数
    path = np.zeros((le, T), dtype=int)  # 记录上个转移节点

    for j in range(T):
        dp[0][j] = start_p[j] + emit_p[j][obs[0]]

    for i in range(1, le):
        for j in range(T):
            dp[i][j], path[i][j] = max(
                (dp[i - 1][k] + trans_p[k][j] + emit_p[j][obs[i]], k)
                for k in range(T))

    # 隐序列
    states = [np.argmax(dp[le - 1])]
    # 从后到前的循环来依次求出每个单词的词性
    for i in range(le - 2, -1, -1):
        states.insert(0, path[i + 1][states[0]])

    res_list = []
    # 返回结果
    for word, tid in zip(sentence, states):
        list = []
        list.append(word)
        list.append(id2tag[tid])
        res_list.append(list)

    # 标记词性处理
    res_score = qg.sentiment_score(qg.sentiment_score_list(res_list))
    qg_value = 0.0
    for value in res_score:
        qg_value = qg_value + value[1] - value[0]
    return qg_value