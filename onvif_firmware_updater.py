from concurrent import futures
import logging
import grpc
import onvif_firmware_update_pb2
import onvif_firmware_update_pb2_grpc
import os, subprocess, time

START_CAMERA_SCRIPT_PATH = "/tmp/mock-onvif/debug-start-onvif-camera.sh"
# FirmwareUpdater provides an implementation of the methods of the RouteGuide service.
class FirmwareUpdateServicer(onvif_firmware_update_pb2_grpc.FirmwareUpdateServicer):

    def UpdateFirmware(self, request, context):
        requested_version = request.version
        timeout = request.reboot_time_secs
        print("UpdateFirmware - called with version {} and timeout {}".format(requested_version, timeout))
        if os.path.exists(START_CAMERA_SCRIPT_PATH):
            print("exists")
            # Needs to be sudo
            # rc = subprocess.check_call([START_CAMERA_SCRIPT_PATH, "eno1"])
            os.system("sudo {} {} {}".format(START_CAMERA_SCRIPT_PATH, "eno1", requested_version))
        else: 
            print("ERROR script file DNE")
            # TODO: pull file
        return onvif_firmware_update_pb2.UpdateFirmwareReply(version = requested_version)


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