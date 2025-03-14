import numpy as np
from sklearn import manifold
import math
import copy
import hashlib
from routes.overviewdb.data_process.tf_idf import tfidf, participle


def flow_kew_words(ids, ori_data, topic):
    months_topic_keywords = {}
    months_texts_topic = {}
    for id in ids:
        for i in ori_data:
            if id == i[0]:
                created_time = int(copy.deepcopy(i[7]).split("-")[1])
                if created_time not in months_texts_topic.keys():
                    months_texts_topic[created_time] = {}
                if topic[id]['topic'] not in months_texts_topic[created_time].keys():
                    months_texts_topic[created_time][topic[id]['topic']] = []
                months_texts_topic[created_time][topic[id]['topic']].append(copy.deepcopy(i[2]))
                break
    for mo in months_texts_topic:
        months_topic_keywords[mo] = {}
        for to in months_texts_topic[mo]:
            sentences = participle(copy.deepcopy(months_texts_topic[mo][to]))
            if len(sentences) > 1:
                months_topic_keywords[mo][to] = tfidf(sentences)
    return months_topic_keywords


class Overview:
    """
    用于生成overview数据

    传入参数类简介：
    ori_data:list

    users_info:dict,

    time:dict

    topic:dict,

    返回参数简介：
    self.map2time:dict,
                    键值为地点（用户信息中的provence），
                    值类型list，
                    存储微博发布时间，微博内容id

    self.time2topic:dict
                    键值为时间，
                    值类型dict，
                    存储每个主题下微博数量和对应id
    """

    def __init__(self):
        self.map2time = {}
        self.time2topic = {}

    def creat(self, ori_data, users_info, time, topic):
        temp = []
        for i in range(len(ori_data)):
            temp.append([ori_data[i][0], users_info[ori_data[i][1]]["province"], time[ori_data[i][0]].split(" ")[0]])
        for i in temp:
            if i[1] not in self.map2time.keys():
                self.map2time[i[1]] = []
            self.map2time[i[1]].append([i[-1], i[0]])

        temp = []
        temp_dict = {}
        for i in range(len(ori_data)):
            temp.append([ori_data[i][0], time[ori_data[i][0]].split(" ")[0], topic[ori_data[i][0]]["topic"]])
        for i in temp:
            if i[1] not in temp_dict.keys():
                temp_dict[i[1]] = {}
            if i[2] not in temp_dict[i[1]].keys():
                temp_dict[i[1]][i[2]] = {"num": 0, "id": []}
            temp_dict[i[1]][i[2]]["num"] += 1
            temp_dict[i[1]][i[2]]["id"].append(i[0])

        for i in temp_dict:
            self.time2topic[i] = {"date": i, "topic": []}
            for j in temp_dict[i]:
                self.time2topic[i]["topic"].append({"name": j,
                                                    "num": temp_dict[i][j]["num"],
                                                    "id": temp_dict[i][j]["id"]
                                                    })

        print("Overview ready!!")
        return self.map2time, self.time2topic



class NewCommunicationMap(object):
    """
    传入参数简介：
        介绍略，参考其他地方

    返回参数简介：
        self.info:dict,
                键值为微博内容id,
                内容为id，内容，发表时间，用户信息，情感信息，评论信息
    """

    def __init__(self):
        self.info = {}

    def creat(self, ori_data, time, users_info, emotion, fc2020, commentusers, forward_users_info, fcemotion):
        for i in ori_data:
            self.info[i[0]] = {
                "content_id": i[0],
                "content": i[-1],
                "created_at": time[i[0]],
                "user_info": users_info[i[1]],
                "emotion": emotion[i[0]],
                "data": []}
            for j in fc2020:
                if j[0] == i[0] and (j[1] in commentusers.keys() or j[1] in forward_users_info.keys()):
                    self.info[i[0]]["data"].append(
                        {"fc_user": commentusers[j[1]] if j[1] in commentusers.keys() else forward_users_info[j[1]],
                         "content": j[2], "created_at": j[3], "like_num": j[4], "C_F": j[5],
                         "emotion": fcemotion[j[6]]})
        return self.info


class DataDimensionReduction(object):
    """
    计算谣言的降维坐标

    传入参数简介：
        ori_data:list
        users_info:dict

    返回参数简介：
        self.high_dimensional_info:list
            存储谣言高维特征依次分别为：发布用户粉丝数，发布用户关注数，发布用户微博数，发布用户信息完整度，微博转发数，微博评论数，微博点赞数，
            微博长度，微博内容含有图片或视频链接数量
        self.low_dimensional_coordinate:dict
                键值为微博内容id,
                内容为低维坐标
    """

    def __init__(self):
        self.high_dimensional_info = []
        self.low_dimensional_coordinate = {}

    def calculate(self, ori_data, users_info):

        for i in ori_data:
            count = 0
            self.high_dimensional_info.append([int(users_info[i[1]]['fans_num']), int(users_info[i[1]]['follows_num']),
                                               int(users_info[i[1]]['tweets_num'])])
            for j in users_info[i[1]]:
                if users_info[i[1]][j] is not None:
                    count += 1
            self.high_dimensional_info[-1].append(count)
            self.high_dimensional_info[-1].append(int(i[5]))
            self.high_dimensional_info[-1].append(int(i[3]))
            self.high_dimensional_info[-1].append(int(i[4]))
            self.high_dimensional_info[-1].append(len(i[2]))
            if i[8] is not None and i[9] is not None:
                self.high_dimensional_info[-1].append(2)
            elif i[8] is not None or i[9] is not None:
                self.high_dimensional_info[-1].append(1)
            else:
                self.high_dimensional_info[-1].append(0)

        tsne = manifold.TSNE(n_components=2, init='pca', random_state=0)
        X_tsne = tsne.fit_transform(np.array(self.high_dimensional_info))

        for i in range(len(self.high_dimensional_info)):
            self.low_dimensional_coordinate[ori_data[i][0]] = [str(X_tsne[i][0]), str(X_tsne[i][1])]
        return self.low_dimensional_coordinate


