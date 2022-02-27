from concurrent import futures
import argparse
import logging
import grpc
import threading
import time
import proto.onvif_firmware_update_pb2 as onvif_firmware_update_pb2, proto.onvif_firmware_update_pb2_grpc as onvif_firmware_update_pb2_grpc
import os, time

STOP_CAMERA_SCRIPT_NAME = "scripts/stop-onvif-camera.sh"
START_CAMERA_SCRIPT_NAME = "scripts/start-onvif-camera.sh"

# FirmwareUpdater provides an implementation of the methods of the RouteGuide service.
class FirmwareUpdateServicer(onvif_firmware_update_pb2_grpc.FirmwareUpdateServicer):

    def UpdateFirmware(self, request, context):
        print("UpdateFirmware - called")
        directory = get_directory()
        print("Using resources in directory {}".format(directory))
        requested_version = request.version
        timeout = request.reboot_time_secs
        print("UpdateFirmware - called with version {} and timeout {}".format(requested_version, timeout))
        t1 = threading.Thread(target=stop_sleep_start, args=(requested_version, int(timeout),directory))
        t1.start()
        return onvif_firmware_update_pb2.UpdateFirmwareReply(version = requested_version)

def stop_sleep_start(version, timeout, script_directory):
    start_camera_script_path = os.path.join(script_directory, START_CAMERA_SCRIPT_NAME)
    stop_camera_script_path = os.path.join(script_directory, STOP_CAMERA_SCRIPT_NAME)
    if not (os.path.exists(start_camera_script_path) and os.path.exists(stop_camera_script_path)):
        print("ERROR script files DNE")
        raise ValueError("ERROR script files DNE at {} and {}".format(start_camera_script_path, stop_camera_script_path))
    print("Requested interface is {}".format(network_interface))
    os.system("sudo {}".format(stop_camera_script_path))
    print("Sleeping for {} seconds requested before restarting camera".format(timeout))
    time.sleep(timeout)
    os.system("sudo {} {} {} {}".format(start_camera_script_path, network_interface, script_directory, version))

def get_directory():
    if not os.path.exists(resources_directory):
        raise ValueError("Directory {} does not exist".format(resources_directory))
    return resources_directory

def serve():
    print("Serving FirmwareUpdateServicer")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    onvif_firmware_update_pb2_grpc.add_FirmwareUpdateServicer_to_server(
        FirmwareUpdateServicer(), server)
    server.add_insecure_port('[::]:6052')
    server.start()
    server.wait_for_termination()

def main():
    print("Starting Upgrade Service")
    logging.basicConfig()
    global resources_directory
    global network_interface
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start-camera', action='store_true',
                        help='Specifies whether the mock camera should be served (in the case it is not already running)')
    parser.add_argument('-d', '--resources-directory', default='~/onvif-camera-mocking',
                        help='Directory where mock camera resources are located (mock ONVIF server `onvif_srvd`, discovery service `wsdd`, and stop and start scripts are located. Default: ~/onvif-camera-mocking')
    # TODO: have script query the machine for this information instead of requiring user input
    parser.add_argument('-n', '--network-interface', required=True,
                        help='[Required] Defines the network interface of the machine that is running this program (ie `eno1, `eth0, `eth1`, etc)')
    args = parser.parse_args()

    print('Starting camera? ' + str(args.start_camera) )
    print('Resources directory: ' + args.resources_directory)
    resources_directory = args.resources_directory
    print('Network interface ' + args.network_interface)
    network_interface = args.network_interface

    if args.start_camera :
        print("Starting Camera with initial version 1.0")
        # Terminate any previously running cameras and start the camera without a timeout
        stop_sleep_start("1.0", 0, get_directory())
    serve()

main()