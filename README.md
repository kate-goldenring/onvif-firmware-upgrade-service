# ONVIF Firmware Upgrade Service
A gRPC interface definition for upgrading a mock ONVIF camera. Assumes the use of [this onvif-camera-mocking library](https://github.com/kate-goldenring/onvif-camera-mocking).
Includes:
1. A service that runs the [start script](https://github.com/kate-goldenring/onvif-camera-mocking#start-the-onvif-and-discovery-services) for the mock camera, passing in the requested firmware version. 
1. A client that can be used for testing the service.
1. A dockerfile for building the client

## Prerequisites
Install the necessary python requirements for a virtual environment:
```sh
sudo apt install python3-pip
pip install virtualenv
export PATH="$HOME/.local/bin:$PATH"
```
If using VS Code, follow [this guide](https://techinscribed.com/python-virtual-environment-in-vscode/) on how to select your virtual environment. 
Install gRPC tools for auto-generating the protobuf code.
```
pip3 install grpcio-tools
```
From the root of the project, generate the protobuf code:
```
python -m grpc_tools.protoc -I./ --python_out=. --grpc_python_out=. ./onvif_firmware_update.proto
```

## Running the client
The client takes in two environment variables:
`JOB_DESIRED_STATE`: defines the firmware version it should request (ie `2.0`)
`AKRI_JOB_STATE_FILE_PATH`: defines the directory at which it should write the version it successfully initiated an upgrade to (ie `/var/lib/akri/management/test`)
Full command: `JOB_DESIRED_STATE=2.0 AKRI_JOB_STATE_FILE_PATH=/var/lib/akri/management/test /home/kagold/.virtualenvs/venv/bin/python /home/kagold/onvif-firmware-update/client.py`

## Running the server
Ensure the mock onvif server binary is at `/tmp/mock-onvif/onvif_srvd/onvif_srvd_debug`
Ensure the mock onvif wsdd Discovery is at `/tmp/mock-onvif/wsdd/wsdd`
Ensure the start script is at `/tmp/mock-onvif/debug-start-onvif-camera.sh`
Run: `/home/kagold/.virtualenvs/venv/bin/python /home/kagold/onvif-firmware-update/onvif_firmware_updater.py`

> Note: `RECV.log`, `SENT.log`, `TEST.log`, and `wsdd.pid` files will be created in the root of the director each time the server is run. This is output from the `onvif_srvd` program.
