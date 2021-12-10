import logging
import grpc
import onvif_firmware_update_pb2
import onvif_firmware_update_pb2_grpc
import os

CAMERA_IP_ENV_VAR = "ONVIF_DEVICE_IP_ADDRESS"
DESIRED_FIRMWARE_VERSION_ENV_VAR = "DESIRED_FIRMWARE_VERSION"
STATE_FILE_PATH = "AKRI_JOB_STATE_FILE_PATH"

def run():
    print("-------------- Running --------------")
    ip = os.getenv(CAMERA_IP_ENV_VAR, default = "localhost")
    with grpc.insecure_channel(ip + ":6052") as channel:
        stub = onvif_firmware_update_pb2_grpc.FirmwareUpdateStub(channel)
        print("-------------- UpdateFirmware --------------")
        version = os.environ[DESIRED_FIRMWARE_VERSION_ENV_VAR]
        print("Version requested is {}".format(version))
        request = onvif_firmware_update_pb2.UpdateFirmwareRequest(version=version, reboot_time_secs=30)
        response = stub.UpdateFirmware(request)
        print("Response is {}".format(response))


if __name__ == '__main__':
    print("Starting client")
    logging.basicConfig()
    run()