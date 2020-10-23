
from B_frameData_agentframesumo import SUMO
from B_frameData_kafkaopts import updateSubIDs  # , frameProducer
import threading
import config

class Main:
    def __init__(self):
        self.sumo = SUMO(config.B_frameData_junctions)

    def start_sumo(self):
        self.sumo.simulation()
if __name__ == '__main__':
    main = Main()
    # threads = []
    # updateSubIDs_thread = threading.Thread(target=updateSubIDs)
    # threads.append(updateSubIDs_thread)

    # for thread in threads:
    #     thread.start()
    main.start_sumo()
