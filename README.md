# RemoteDAQ-Server
RemoteDAQ-Server is a server used to manage or control RemoteDAQ devices. RemoteDAQ devices is a device that can control and manage Data Acquisition (DAQ) device.


# How to Install
1. Go to web browser and visit ZeroTier website [here](https://my.zerotier.com/login).
2. Create new ZeroTier account or login using Google Account.
3. Create new network by click the `Create A Network` button. Copy the Network ID. This ID is used to add a new device to the network.
4. Create API Token [here](https://my.zerotier.com/account) and click the `New Token` button. Copy and save the API Token somewhere safe.
5. Go to your user's home directory and clone this repository.
    ```
    git clone https://github.com/unknown137-dimas/RemoteDAQ-Server
    ```
6. `cd` to inside the repository.
7. Change `setup.sh` script permission:
    ```
    chmod +x setup.sh
    ```
8. Run `setup.sh` command:
    ```
    sudo ./setup.sh
    ```
9. Fill the prompt accordingly.
10. Wait until finished.

# Configure DNS & Proxy for Easy Access
## Create a Domain using DuckDNS
1. Go to web browser and visit DuckDNS website [here](https://www.duckdns.org).
2. Create new DuckDNS account or login using Google Account.
3. Add subdomain of your choice.
4. In `Current IP` Column, insert your server IP assigned by ZeroTier and click `Update IP`.
## Configure Proxy
1. Go to web browser and visit your nginx proxy server UI using IP assigned by ZeroTier.
    ```
    http://SERVER-IP:81
    ```
2. Login using username `admin@example.com` and password `changeme`.
3. Update login credential by changing username and password.
4. Go to `SSL Certificates` tab, click `Add SSL Certificate`.
5. Input your main domain name (e.g. rdaq.duckdns.org), as well as the wildcard record for all the subdomains (e.g. *.rdaq.duckdns.org).
6. Click on `Use a DNS Challenge` and select `DuckDNS` from the list of providers.
7. Go back to DuckDNS and copy your API token. Paste the token into the `Credentials File Contents` textbox.
8. Additionally, you might want to set the `Propagation Seconds` parameter to 120 seconds. The default value is 30 sec., however, sometimes this is not enough for the DNS changes to propagate.
9. Finally, agree to Let's Encrypt Terms of Service and click on `Save`.
## Add New Proxy Entry
1. In the top menu bar, click on Hosts > Proxy Hosts, and then click on `Add a Proxy Host`. Use the following parameters:

    For the dashboard:
    ```
    Domain Names            : dashboard.rdaq.duckdns.org
    Scheme                  : http
    Forward Hostname / IP   : remotedaq_ui
    Forward Port            : 2023
    ```
    For the database:
    ```
    Domain Names            : db.rdaq.duckdns.org
    Scheme                  : http
    Forward Hostname / IP   : remotedaq_db
    Forward Port            : 8086
    ```
2. Go to `SSL` tab, click the SSL certificate.
3. Select `Force SSL` and `HTTP/2 Support` options, and click `Save`.
## How to Access
You can access the server from several ways:
1. Using IP address and port.
2. Using domain from Nginx Proxy Manager with DuckDNS service.