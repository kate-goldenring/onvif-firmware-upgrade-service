import argparse
import logging
import grpc
import proto.onvif_firmware_update_pb2 as onvif_firmware_update_pb2
import proto.onvif_firmware_update_pb2_grpc as onvif_firmware_update_pb2_grpc

def run():
    print("-------------- Running --------------")
    with grpc.insecure_channel(device_ip_address + ":6052") as channel:
        stub = onvif_firmware_update_pb2_grpc.FirmwareUpdateStub(channel)
        print("-------------- UpdateFirmware --------------")
        print("Version requested is {}".format(desired_firmware_version))
        request = onvif_firmware_update_pb2.UpdateFirmwareRequest(version=desired_firmware_version, reboot_time_secs=30)
        response = stub.UpdateFirmware(request)
        print("Response is {}".format(response))


def main():
    print("Starting client")
    logging.basicConfig()
    global device_ip_address
    global desired_firmware_version
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--firmware-version', default='2.0',
                        help='Defines the firmware version the client should request the camera be upgraded to (ie `2.0`). Default: 2.0')
    parser.add_argument('-i', '--device-ip-address', Required=True,
                        help='[Required] Defines the IP address at which the camera update service lives.')
    args = parser.parse_args()


    print('Desired firmware version ' + args.firmware_version )
    desired_firmware_version = args.firmware_version
    print('Device IP Address ' + args.device_ip_address)
    device_ip_address = args.device_ip_address
    run()

main()