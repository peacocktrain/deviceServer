
import devicesServer
import missionPlannerServer
import threading


deviceServerThread = threading.Thread(target=devicesServer.deviceServer)
deviceServerThread.start()

missionServerThread = threading.Thread(target=missionPlannerServer.missionPlannerServer)
missionServerThread.start()
