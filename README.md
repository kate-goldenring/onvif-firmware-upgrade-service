# ONVIF Firmware Upgrade Service
A gRPC interface definition for upgrading a mock ONVIF camera. Assumes the use of [this onvif-camera-mocking library](https://github.com/kate-goldenring/onvif-camera-mocking).
Includes:
1. A service that terminates any cameras with a [stop script](https://github.com/kate-goldenring/onvif-camera-mocking/blob/main/scripts/stop-onvif-camera.sh), pauses for given timeout (to simulate reboot), and runs the [start script](https://github.com/kate-goldenring/onvif-camera-mocking#start-the-onvif-and-discovery-services) for the mock camera, passing in the requested firmware version. 
1. A client that can be used for testing the service.
1. A dockerfile for building the client

## Prerequisites
### Mock camera services
Choose where to store th necessary resources for mocking an ONVIF camera. It should be in a global directory such as within the `/tmp` folder.
```sh
export RESOURCES_DIRECTORY = "/tmp/mock-onvif".
```

1. Follow these [steps](https://github.com/kate-goldenring/onvif-camera-mocking#get-the-onvif-server-and-ws-discovery-service) to get the `onvif_srvd` and `wsdd` services. Move the `onvif_srvd` and `wsdd` folders to the `$RESOURCES_DIRECTORY` directory.
1. Follow these [steps](https://github.com/kate-goldenring/onvif-camera-mocking#pass-an-rstp-feed-through-the-camera-onvif-service) to get the rtsp feed application that passes a fake stream through the camera. Move the `rtsp_feed.py` program to the `$RESOURCES_DIRECTORY` directory.
2. Get the start script, modifying the location of the wsdd and onvif_srvd executables and appending a line to start the rtsp feed script. Replace `\/tmp\/mock-onvif` with the value of `$RESOURCES_DIRECTORY` with each `/` converted to `\/`.
    ```sh
    curl https://raw.githubusercontent.com/kate-goldenring/onvif-camera-mocking/main/scripts/start-onvif-camera.sh | sed -E 's/.\/onvif_srvd\/onvif_srvd/\/tmp\/mock-onvif\/onvif_srvd\/onvif_srvd/g' |  sed -E 's/.\/wsdd\/wsdd/\/tmp\/mock-onvif\/wsdd\/wsdd/g' | sed -E '$a\nohup \/tmp\/mock-onvif\/rtsp-feed.py &' > $RESOURCES_DIRECTORY/start-onvif-camera.sh
    ```

    > TODO: Figure out how to set `$RESOURCES_DIRECTORY` via the `sed` command

    Make the script and python program executable:
    ```
    sudo chmod +x $RESOURCES_DIRECTORYstart-onvif-camera.sh
    sudo chmod +x $RESOURCES_DIRECTORY/rtsp_feed.py
    ```

3. Get the stop script and append a line to stop the `rtsp_feed` program.
    ``` 
    curl https://raw.githubusercontent.com/kate-goldenring/onvif-camera-mocking/main/scripts/stop-onvif-camera.sh | sed -E '$a\pkill -f rtsp-feed.py' > $RESOURCES_DIRECTORY/stop-onvif-camera.sh
    ```
        
    Make the script executable:
    ```
    sudo chmod +x $RESOURCES_DIRECTORY/stop-onvif-camera.sh
    ```
### Python requirements
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
python -m grpc_tools.protoc -I./proto --python_out=./proto --grpc_python_out=./proto ./proto/onvif_firmware_update.proto
```

## Running the client
The client takes in three environment variables:
`DESIRED_FIRMWARE_VERSION`: defines the firmware version it should request (ie `2.0`)
`ONVIF_DEVICE_IP_ADDRESS`: defines the IP address at which the camera update service lives (defaults to `localhost`)
Full command: `DESIRED_FIRMWARE_VERSION=2.0 $PWD/.virtualenvs/venv/bin/python $PWD/client.py`

## Running the server
Ensure the mock onvif server binary is at `$RESOURCES_DIRECTORY/onvif_srvd/onvif_srvd`
Ensure the mock onvif wsdd Discovery is at `$RESOURCES_DIRECTORY/wsdd/wsdd`
Ensure the rtsp feed program is at `$RESOURCES_DIRECTORY/rtsp_feed.py`
Ensure the start script is at `$RESOURCES_DIRECTORY/start-onvif-camera.sh`
Ensure the stop script is at `$RESOURCES_DIRECTORY/stop-onvif-camera.sh`
The server takes in two environment variable:
`NETWORK_INTERFACE`: defines the network interface of the machine that is running this program. It is the interface the camera will be served on. Run `ifconfig` or `ipconfig` to determine your network interface. Then, pass your interface (such as `eno1`, `eth0`, `eth1`, etc) to the script. The following assumes `eth0`.
`RESOURCES_DIRECTORY`: directory of both scripts and `onvif_srvd`, `wsdd`, and `rtsp_feed.py` binaries. Defaults to `/tmp/mock-onvif`.
Navigate to the directory of this README and run:
- if using a virtual environment at `$HOME/.virtualenvs`: `sudo NETWORK_INTERFACE=eth0 $HOME/.virtualenvs/venv/bin/python $PWD/onvif_firmware_updater.py`
- if using a standard Python environment: `sudo NETWORK_INTERFACE=eth0 onvif_firmware_updater.py`

> Note: `RECV.log`, `SENT.log`, `TEST.log`, and `wsdd.pid` files will be created in the root of the director each time the server is run. This is output from the `onvif_srvd` program.
