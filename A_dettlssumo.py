import time

import traci
import traci.constants as tc
import config
import A_queuedata
import copy

class SUMO:
    junctions = dict()    #这里存储的是所有关注路口的junction对象
    def __init__(self, sumoconfig):
        self.frame = 0;             #初始步长为0
        self.inductionloopid = '##'
        #traci.start(['sumo-gui', '--start', '-c', sumoconfig])
        traci.start(cmd=['sumo-gui', '--start', '-c', sumoconfig,
                         "--num-clients", "2"], port=8813, label="sim1")
        traci.setOrder(1)

        self.start = time.perf_counter()
        print("        3.2、启动sumo-gui,初始启动时间：", self.start)

    def subInductionloop(self, inductionloopid,lane, radius):
        """
        订阅感应线圈数据（以检测器inductionloopid为中心，半径radius）
        """
        self.inductionloopid = inductionloopid
        self.lane = lane
        traci.inductionloop.subscribeContext(
            inductionloopid, tc.CMD_GET_INDUCTIONLOOP_VARIABLE, radius)
        traci.lane.subscribeContext(
            lane, tc.CMD_GET_LANE_VARIABLE, radius)
        
        #traci.simulation.subscribe((tc.VAR_DEPARTED_VEHICLES_IDS,tc.VAR_LOADED_VEHICLES_IDS))
        # traci.inductionloop.subscribe(inductionloopid,tc.CMD_GET_INDUCTIONLOOP_VARIABLE,radius)

    def simulation(self):

        lastNumDict = {}           #记录上一帧各个检测器的状态
        passedNumDict = {}         #记录各个检测器累积的车辆数
        for k,v in config.junction_detectors.items():
            for det in v:
                passedNumDict[det] = 0
        print("passedNumDict = ", passedNumDict)
        while True:
            # for vec_id in traci.vehicle.getIDList():
            #
            #     #订阅车辆信息：坐标，角度，车辆类型，颜色，速度
            #     traci.vehicle.subscribe(str(vec_id),
            #                             (tc.VAR_POSITION, tc.VAR_ANGLE, tc.VAR_TYPE, tc.VAR_COLOR, tc.VAR_SPEED))
            traci.simulationStep()                 #开始切帧


            # loopdata = traci.inductionloop.getInductionLoopStat()
            # lanedata = traci.lane.getLaneStat()
            # cross_data = [loopdata, lanedata]
            # print(cross_data)
            # result = traci.inductionloop.getLastStepVehicleNumber(self.inductionloopid)
            # print("getLastStepVehicleNumber = ", result)

            self.frame+=1                             #步长+1
            if not self.inductionloopid == '##':
                temp = traci.inductionloop.getContextSubscriptionResults(self.inductionloopid)
                #print(temp)
                if self.frame > 1:
                    for k, v in temp.items():
                        currStatus = v[16]
                        preStatus = lastNumDict[k][16]
                        if currStatus - preStatus == 1:
                            passedNumDict[k] += 1

                if self.frame % int(20 / config.steplength) == 0:   ##时长达到1分钟，将数据推出去
                    passedNumDictDup = copy.deepcopy(passedNumDict)
                    A_queuedata.flow_queue.put(passedNumDictDup)         ##将1分钟流量数据，推送到flow队列中，用别的线程进行处理
                    for k, v in config.junction_detectors.items():
                        for det in v:
                            passedNumDict[det] = 0
                    # if not self.lane == '##':
                    #     temp1 = traci.lane.getContextSubscriptionResults(self.lane)
                    #     print(temp1)

                    #print("更新后的passedNumDict1 = ", passedNumDict)
                lastNumDict = temp
                A_queuedata.det_queue.put(temp)

                        #print(currStatus, preStatus)
                        #print(k)
                #print(passedNumDict)
                #print("当来车时：", temp)
                #print(temp)             ##此处打印检测器是否检测到车辆的信息

                # for vec_id in traci.vehicle.getIDList():
                #     dic = traci.vehicle.getSubscriptionResults(vec_id)
                #     print(dic)           ##这里打印的是之前车辆订阅的信息：坐标，角度，车辆类型，颜色，速度
                #     if dic:
                #         #print(dic[66])
                #         x,y = dic[66]
                #         lon, lat = traci.simulation.convertGeo(x,y)
                        #print(lon,lat)


            q_size = A_queuedata.ryg_queue.qsize()
            while q_size > 0:
                print("        5.4、当前ryg_queue.qsize：", q_size)
                tlsID, newryg = A_queuedata.ryg_queue.get()
                traci.trafficlight.setRedYellowGreenState(tlsID, newryg)
                traci.trafficlight.setPhaseDuration(tlsID,999)
                print("        5.5、向sumo仿真系统中设置灯色信息及其持续时间：", (tlsID, newryg))
                q_size -= 1
            logitTime = self.frame * config.steplength
            realTime = time.perf_counter() - self.start
            diff = logitTime - realTime
            if(diff > 0):
                time.sleep(diff)







