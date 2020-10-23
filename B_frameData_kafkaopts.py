from kafka import KafkaConsumer
from kafka import KafkaProducer
from config import kafkahost, idtopic, frametopic
import config
import json


def updateSubIDs():
    consumer = KafkaConsumer(
        idtopic, bootstrap_servers=[kafkahost], auto_offset_reset='latest')

    for message in consumer:
        v = json.loads(message.value.decode())
        ids = {idstr.replace('asc:agentframe:','') for idstr in v['idList']}
        if v['type'] == 1:  # 订阅
            config.subids = list(
                set(config.subids).union(ids))
        elif v['type'] == 2:  # 取消订阅
            config.subids = list(
                set(config.subids).difference(ids))

        print(config.subids)



if __name__ == "__main__":
    # subids = list()
    # updateSubIDs(subids)

    # from queue import Queue
    # agentframe_queue = Queue()
    # framedict = {
    #     "dataId": "10008",
    #     "eventId": "1591939374585566",
    #     "eventType": 4,
    #     "ObjList": [
    #         {
    #             "ObjType": 6,
    #             "ObjID": "50",
    #             "Long": 121.519775,
    #             "Latt": 31.242853,
    #             "ObjSpeed": 0.0,
    #             "ObjAngle": 268.031662,
    #             "VehBodyColor": 2
    #         }
    #     ]
    # }
    # agentframe_queue.put(json.dumps(framedict))
    # frameProducer(agentframe_queue)

    # consumer = KafkaConsumer(
    #     idtopic, bootstrap_servers=[kafkahost], auto_offset_reset='latest')

    # for message in consumer:
    #     v = json.loads(message.value.decode())
    #     print(v)

    #     if v['type'] == 1:  # 订阅
    #         config.subids = list(
    #             set(config.subids).union(set(v['data']['idList'])))
    #     elif v['type'] == 2:  # 取消订阅
    #         config.subids = list(
    #             set(config.subids).difference(set(v['data']['idList'])))

    #     print(config.subids)
    updateSubIDs()
