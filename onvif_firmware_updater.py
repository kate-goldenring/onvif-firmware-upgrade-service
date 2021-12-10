from concurrent import futures
import logging
import grpc
import threading
import time
import onvif_firmware_update_pb2
import onvif_firmware_update_pb2_grpc
import os, subprocess, time

RESOURCES_DIRECTORY_ENV_VAR = "RESOURCES_DIRECTORY"
DEFAULT_RESOURCES_DIRECTORY ="/tmp/mock-onvif"
STOP_CAMERA_SCRIPT_NAME = "stop-onvif-camera.sh"
START_CAMERA_SCRIPT_NAME = "start-onvif-camera.sh"
NETWORK_INTERFACE_ENV_VAR = "NETWORK_INTERFACE"

# FirmwareUpdater provides an implementation of the methods of the RouteGuide service.
class FirmwareUpdateServicer(onvif_firmware_update_pb2_grpc.FirmwareUpdateServicer):

    def UpdateFirmware(self, request, context):
        print("UpdateFirmware - called")
        directory = os.getenv(RESOURCES_DIRECTORY_ENV_VAR, default = DEFAULT_RESOURCES_DIRECTORY)
        if not os.path.exists(directory):
            raise ValueError("Directory {} does not exist".format(directory))
        print("Using resources in directory {}".format(directory))
        requested_version = request.version
        timeout = request.reboot_time_secs
        print("UpdateFirmware - called with version {} and timeout {}".format(requested_version, timeout))
        t1 = threading.Thread(target=update, args=(requested_version, int(timeout),directory))
        t1.start()
        return onvif_firmware_update_pb2.UpdateFirmwareReply(version = requested_version)

def update(version, timeout, script_directory):
    start_camera_script_path = os.path.join(script_directory, START_CAMERA_SCRIPT_NAME)
    stop_camera_script_path = os.path.join(script_directory, STOP_CAMERA_SCRIPT_NAME)
    if not (os.path.exists(start_camera_script_path) and os.path.exists(stop_camera_script_path)):
        print("ERROR script files DNE")
        raise ValueError("ERROR script files DNE at {} and {}".format(start_camera_script_path, stop_camera_script_path))
    interface = os.environ[NETWORK_INTERFACE_ENV_VAR]
    print("Requested interface is {}".format(interface))
    os.system("sudo {}".format(stop_camera_script_path))
    print("Sleeping for {} seconds requested before restarting camera".format(timeout))
    time.sleep(timeout)
    os.system("sudo {} {} {}".format(start_camera_script_path, interface, version))


def serve():
    print("Serving FirmwareUpdateServicer")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    onvif_firmware_update_pb2_grpc.add_FirmwareUpdateServicer_to_server(
        FirmwareUpdateServicer(), server)
    server.add_insecure_port('[::]:6052')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    serve()