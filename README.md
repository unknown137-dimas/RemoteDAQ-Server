# RemoteDAQ-Server
RemoteDAQ-Server is a server used to manage or control RemoteDAQ devices. RemoteDAQ devices is a device that can control and manage Data Acquisition (DAQ) device.


# How to Install
1. Create new ZeroTier account or login using Google Account [here](https://my.zerotier.com/login).
2. Create new network by click the 'Create A Network' button. Copy the Network ID. This ID is used to add a new device to the network.
3. Create API Token [here](https://my.zerotier.com/account) and click the 'New Token' button. Copy and save the API Token somewhere safe.
4. Go to your user's home directory and clone this repository.
    ```
    git clone https://github.com/unknown137-dimas/RemoteDAQ-Server
    ```
4. `cd` to inside the repository.
5. Change `setup.sh` script permission:
    ```
    chmod +x setup.sh
    ```
6. Run `setup.sh` command:
    ```
    sudo ./setup.sh
    ```
7. Fill the prompt accordingly.
8. Wait until finished.
