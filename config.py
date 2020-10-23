# SUMO相关配置
sumocfg = './sumo/scenario/test.sumocfg'  # SUMO配置文件
steplength = 0.1  # 仿真步长 s


# kafka相关配置
#kafkahost = '10.68.2.27:9092'
#kafkahost = '10.68.2.131:19092'
kafkahost = '10.65.3.30:19092'
idtopic = "kiss-zhlk"  # 上报主体的订阅、取消订阅topic
#frametopic = "kedamap-ct-intellisense"  # 帧数据上报topic
frametopic = "wjh-test"  # 帧数据上报topic
#subids = list()
subids=["30002"]

B_frameData_junctions = ['30001', '30002']
#--------------------------------------------------------------


# SUMO相关配置
sumocfg = ''  # SUMO配置文件
steplength = 0.1  # 仿真步长 s
sumoterminals = "3"
cinductionloopid = ''  # 路网中心检测器id, 用于订阅检测器数据
radius = 0  # 订阅范围半径

# 接收信号灯数据的UDP端口
tlsport = 0

#######################################################
# 仿真路网相关信息
# 仅在.net.xml及.det.xml文件 改变时重新生成
######################################################
junctions = list()
# 路口及其包含车道id
junction_lanes = dict()
# 路口及其包含检测器id
junction_detectors = dict()

######################################################
# 仿真路口关联设备信息、通道配置
# sumo初始化时从 sumo\devices.csv 读入生成
######################################################
devices = dict()
devices2junction = dict()
addrs = dict()
junction_channels = dict()
channelsList = dict()
junction_linknum = dict()
junction_groupnum = dict()