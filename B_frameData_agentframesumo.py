import traci
import sys
import json
import traci.constants as tc
import datetime
import time
import config
from kafka import KafkaProducer

class SUMO:
    def __init__(self, agentids):
        self.agentids = agentids
        self.frame = 0
        #self.record_file = open(config.subids[0]+'.txt', 'a', encoding='utf-8')     #不往kafka写，写在文件
        self.producer = KafkaProducer(bootstrap_servers=[config.kafkahost])
        self.start = time.perf_counter()

    def simulation(self):
        #traci.start(['sumo-gui', '-c', './scenario/sumodata/shihuxilu_add.sumocfg', '--start'])
        traci.init(8813)
        traci.setOrder(2)

        for junctionID in self.agentids:
            traci.junction.subscribeContext(                   #位置、           角度、          类型、        车长、          颜色、         速度
                junctionID, tc.CMD_GET_VEHICLE_VARIABLE, 1500, [tc.VAR_POSITION, tc.VAR_ANGLE, tc.VAR_TYPE, tc.VAR_LENGTH, tc.VAR_COLOR, tc.VAR_SPEED])

        #traci.inductionloop.subscribeContext("d_1", tc.CMD_GET_INDUCTIONLOOP_VARIABLE, 0, [tc.VAR_LANE_ID, tc.LAST_STEP_VEHICLE_NUMBER])
        traci.lane.subscribeContext("lane1_0", tc.CMD_GET_LANE_VARIABLE, -1, [tc.LAST_STEP_MEAN_SPEED, tc.LAST_STEP_VEHICLE_NUMBER])

        while traci.simulation.getMinExpectedNumber() > 0:
            # print("size : ", len(traci.vehicle.getIDList()))
            # for vec_id in traci.vehicle.getIDList():
            #     # 订阅车辆信息：坐标，角度，车辆类型，颜色，速度
            #     traci.vehicle.subscribe(str(vec_id),
            #                             (tc.VAR_POSITION, tc.VAR_ANGLE, tc.VAR_TYPE, tc.VAR_COLOR, tc.VAR_SPEED))
            traci.simulationStep()    ##整合在一起时，只需要一个切帧
            self.frame += 1
            # n = traci.inductionloop.getLastStepVehicleNumber("d_2")
            # print("getLastStepVehicleNumber = ", n)
            dict_sub = traci.lane.getContextSubscriptionResults("lane1_0")
            #print("lane dict = ", dict_sub)
            self.process_vehpos_v17()      #函数用生成帧数据
            #self.process_vehpos()
            #帧间休眠
            sleeping = config.steplength*self.frame - \
                (time.perf_counter() - self.start)
            # print(sleeping)
            if sleeping > 0:
                time.sleep(sleeping)

        sys.stdout.flush()
        traci.close()
        #self.record_file.close()
        self.producer.close()
        exit(0)



    def process_vehpos_v17(self):
        """
        0        1           2          3       4        5      6      7
        [车辆id,   经度,       纬度,      角度,     对象类型, 颜色,    ,   速度]
        ['198', 121.519851, 31.243368, 172.797378, 6,       2,    5.0, 21.822069]
        """
        for junctionID in config.subids:
            dict_sub = traci.junction.getContextSubscriptionResults(junctionID)       #得到车辆订阅信息，字典
            print("dict_sub = ", dict_sub)
            #初始化帧数据信息
            framedict = dict()
            framedict['gbid'] = junctionID
            dtime = datetime.datetime.now().timestamp()
            framedict['dataId'] = str(dtime).replace('.', '')
            framedict['sourceType'] = 10
            framedict['timestamp'] = int(dtime * 1000)
            framedict['objList'] = list()

            if dict_sub == None:
                #print(framedict)
                framejson = json.dumps(framedict)
                self.producer.send(config.frametopic, bytes(framejson, 'utf-8'))
                # self.record_file.write(framejson + '\n')
                continue

            vehicleids = list(dict_sub.keys())
            #print("vehicleids = ", vehicleids)
            if len(vehicleids) == 0:
                framejson = json.dumps(framedict)
                print(framejson)
                self.producer.send(config.frametopic,bytes(framejson, 'utf-8'))
                # self.record_file.write(framejson + '\n')
                continue

            for v in vehicleids:
                vdict = dict()
                tempV = dict_sub[v]
                #print("tempV = " , tempV)
                vdict['ObjID'] = str(v)
                x, y = tempV[66]
                lon, lat = traci.simulation.convertGeo(x, y)
                vdict['Longitude'] = lon
                vdict['Lattitude'] = lat
                vdict['ObjAngle'] = tempV[67]
                vdict['ObjType'] = str(self.convertLength(tempV[68]))
                vdict['VehBodyColor'] = str(self.convertColor(tempV[69]))
                vdict['ObjSpeed'] = str(tempV[64])
                framedict['objList'].append(vdict)
                #print("vdict = ", vdict)
            framejson = json.dumps(framedict)
            #print("framejson = ", framejson)
            # self.record_file.write(framejson+'\n')
            self.producer.send(config.frametopic, bytes(framejson, 'utf-8'))
            #self.producer.send(config.frametopic, bytes(framejson, 'utf-8'), partition=int(junctionID) % 3)   ##partition=int(junctionID) % 3： kafka的分区参数

    def process_vehpos(self):
        """
           0        1           2          3       4        5      6      7
        [车辆id,   经度,       纬度,      角度,     对象类型, 颜色,    ,   速度]
        ['198', 121.519851, 31.243368, 172.797378, 6,       2,    5.0, 21.822069]
        """
        for junctionID in config.subids:
            dict_sub = traci.junction.getContextSubscriptionResults(junctionID)
            print("dict_sub = ", dict_sub)

            framedict = dict()
            framedict['gbid'] = junctionID
            dtime = datetime.datetime.now().timestamp()
            framedict['dataId'] = str(dtime).replace('.', '')
            framedict['sourceType'] = 10
            framedict['timestamp'] = int(dtime * 1000)
            framedict['objList'] = list()

            if dict_sub == None:
                print(framedict)
                framejson = json.dumps(framedict)
                self.producer.send(config.frametopic, bytes(framejson, 'utf-8'))
                # self.record_file.write(framejson + '\n')
                continue

            vehicleids = list(dict_sub.keys())
            if len(vehicleids) == 0:
                framejson = json.dumps(framedict)
                self.producer.send(config.frametopic,bytes(framejson, 'utf-8'))
                # self.record_file.write(framejson + '\n')
                continue


            vehiclestr = ','.join(vehicleids)
            vehicles = traci.vehicle.getMPositionList(
                junctionID+","+vehiclestr)
            vehList = json.loads("["+vehicles+"]")
            # print(type(vehList[0][0]))
            for v in vehList:
                vdict = dict()
                vdict['ObjType'] = v[4]
                vdict['ObjID'] = v[0]
                vdict['Longitude'] = v[1]
                vdict['Lattitude'] = v[2]
                vdict['ObjSpeed'] = v[7]
                vdict['ObjAngle'] = v[3]
                vdict['VehPlate'] = v[0]
                # vdict['PltClr'] =
                vdict['VehBodyColor'] = v[5]
                # vdict['VehLogo'] =
                framedict['objList'].append(vdict)
            print(framedict)
            framejson = json.dumps(framedict)
            #self.record_file.write(framejson+'\n')
            #self.producer.send(config.frametopic, bytes(framejson, 'utf-8'))
            self.producer.send(config.frametopic, bytes(framejson, 'utf-8'), partition=int(junctionID) % 3)   ##partition=int(junctionID) % 3： kafka的分区参数



    def convertLength(self, vLength):
        nSize = 0
        if vLength < 4.5:
            nSize = 4
        elif vLength < 6:
            nSize = 6
        elif vLength < 8:
            nSize = 7
        else:
            nSize = 8
        return nSize

    def convertColor(self, colorTuple):
        nColor = 0
        r,g,b,q = colorTuple
        print(r, g, b)
        if r == 255 and g == 0 and b == 0:
            nColor = 1
        elif r == 255 and g == 255 and b == 0:
            nColor = 2
        elif r == 0 and g == 0 and b == 255:
            nColor = 3
        elif r == 0 and g == 255 and b == 0:
            nColor = 4
        elif r == 255 and g == 165 and b == 0:
            nColor = 5
        elif r == 255 and g == 0 and b == 255:
            nColor = 6
        elif r == 0 and g == 0 and b == 0:
            nColor = 7
        elif r == 255 and g == 255 and b == 255:
            nColor = 8
        elif r == g and g == b:
            nColor = 0
        else:
            nColor = 0
        return nColor

if __name__ == '__main__':
    junctions = ['10001', '10002', '10003', '10004',
                 '10005', '10006', '10007', '10008', '10009', '10010']
    sumo = SUMO(junctions)
    sumo.simulation()
    pass
