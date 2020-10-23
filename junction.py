# coding=utf-8

import json
import datetime
import config


class Junction:
    def __init__(self, junctionid):
        self.junctionid = junctionid            # 仿真路口ID
        self.deviceid = self.getDeviceID()      # 信号机ID
        self.tlLogicid = junctionid             # 仿真信号灯ID
        self.addr = self.getAddr()              # 信号机通信地址(IP:Port)
        self.lanes = self.getLanes()            # 仿真路口包含车道(进入路口)
        self.detectors = self.getDetectors()    # 仿真路口检测器
        self.channels = self.getChannels()      # 通道与路口车道(仿真链路)对应关系
        self.linksnum = self.getLinknum()       # 路口link数目(用于设置ryg)
        self.groupnum = self.getGroupnum()  # 路口仿真的通道数量

    def getDeviceID(self):
        deviceid = config.devices[self.junctionid]
        return deviceid

    def getAddr(self):
        addr = config.addrs[self.junctionid]
        return addr

    def getLanes(self):
        lanes = config.junction_lanes[self.junctionid]
        return lanes

    def getDetectors(self):
        detecors = config.junction_detectors[self.junctionid]
        return detecors

    def getGroupnum(self):
        return config.junction_groupnum[self.junctionid]

    def getChannels(self):
        channels = config.junction_channels[self.junctionid]
        return channels

    def getLinknum(self):
        linknum = config.junction_linknum[self.junctionid]
        return linknum

    def getCreateTime(self, frameno):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        now = now[:-3]
        simTime = frameno * config.steplength * 1000  # 毫秒数
        s, ms = divmod(simTime, 1000)
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        h %= 24
        strSimTime = ("%02d:%02d:%02d.%03d" % (h, m, s, ms))
        now = now[:10] + ' ' + strSimTime
        return now

    def getLocalTime(self):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        now = now[:-3]
        now = now[:10] + ' ' + now[11:]
        return now

    def getfsoinfo(self, detList, laneList, frame):
        """生成fso发送消息"""
        fsoDict = {
            'sourcetype': 'simu',
            'infotype': 'status/fso',
            'agentid': '27',
            'createtime': 'xxxx-xx-xx xx:xx:xx.xxx',
            'location': '',
            'data': []
        }
        dataList = []
        fsoDict['agentid'] = self.deviceid
        fsoDict['createtime'] = self.getLocalTime()
        #fsoDict['location'] = self.getLocation(self.agentid)
        for i in range(len(self.detectors)):
            dataDict = {'recordid': '', 'detectorid': 0,
                        'flow': 0, 'speed': 0.0, 'occupancy': 0.0}

            dataDict['recordid'] = str(self.deviceid) + '____' + self.getLocalTime() + '____' + str(i+1)
            dataDict['detectorid'] = i+1
            dataDict['flow'] = detList[4][self.detectors[i]] - \
                detList[0][self.detectors[i]]
            dataDict['speed'] = (laneList[0][self.lanes[i]][0] + laneList[1][self.lanes[i]][0] + laneList[2]
                                 [self.lanes[i]][0] + laneList[3][self.lanes[i]][0] + laneList[4][self.lanes[i]][0])/5.0
            dataDict['occupancy'] = (laneList[0][self.lanes[i]][1] + laneList[1][self.lanes[i]][1] + laneList[2]
                                     [self.lanes[i]][1] + laneList[3][self.lanes[i]][1] + laneList[4][self.lanes[i]][1])/5.0
            dataDict['queue'] = max(laneList[0][self.lanes[i]][2], laneList[1][self.lanes[i]][2], laneList[2]
                                    [self.lanes[i]][2], laneList[3][self.lanes[i]][2], laneList[4][self.lanes[i]][2])

            dataList.append(dataDict)

        fsoDict['data'] = dataList

        json_fso = json.dumps(fsoDict)
        return json_fso


if __name__ == "__main__":
    j1 = Junction('10001')
    d = j1.getLocalTime()
    print(type(d))
