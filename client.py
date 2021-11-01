import logging
import grpc
import onvif_firmware_update_pb2
import onvif_firmware_update_pb2_grpc
import os

CAMERA_IP_ENV_VAR = "ONVIF_DEVICE_IP_ADDRESS"
DESIRED_VERSION_ENV_VAR = "JOB_DESIRED_STATE"
STATE_FILE_PATH = "AKRI_JOB_STATE_FILE_PATH"

def run():
    print("-------------- Running --------------")
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    ip = os.getenv(CAMERA_IP_ENV_VAR, default = "localhost")
    with grpc.insecure_channel(ip + ":6052") as channel:
        stub = onvif_firmware_update_pb2_grpc.FirmwareUpdateStub(channel)
        print("-------------- UpdateFirmware --------------")
        version = os.environ[DESIRED_VERSION_ENV_VAR]
        print("Version requested is {}".format(version))
        request = onvif_firmware_update_pb2.UpdateFirmwareRequest(version=version, reboot_time_secs=30)
        response = stub.UpdateFirmware(request)
        print("Response is {}".format(response))
        status_file = os.environ[STATE_FILE_PATH]
        f = open(status_file, "w")
        f.write(response.version)
        f.close()


if __name__ == '__main__':
    print("Starting client")
    logging.basicConfig()
    run()