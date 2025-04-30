Here’s the general setup for Raspberry Pi Zero + Official Pi Camera Module:

1. Get Your Hardware Ready
Raspberry Pi Zero W (with built-in WiFi).
Camera: Official Pi Camera Module (either v1, v2, or HQ).
Camera cable for Pi Zero: It's a special smaller cable — standard camera cables don't fit!
(You need a "Raspberry Pi Zero Camera Cable" that adapts between the Pi Zero's small connector and the camera.)
Micro SD card (at least 8 GB, flashed with Raspberry Pi OS).
Power supply (5V, 2.5A recommended).
Mini HDMI adapter and USB OTG cable (for keyboard/mouse if setting up manually).

2. Prepare the Micro SD Card
Download Raspberry Pi Imager.
Flash Raspberry Pi OS onto the SD card.
Enable SSH and Wi-Fi (optional, for headless setup):
After flashing, place a blank file named ssh (no extension) in the SD card's boot partition.
--Create a wpa_supplicant.conf file to set up Wi-Fi credentials.(this now canbe setup in Raspberry Pi Imager)

3. Connect the Camera
Gently open the small black latch on the Pi Zero's camera connector.
Insert the small end of the camera cable with the blue side facing the HDMI port.
Connect the other end to the camera module.
Lock both sides.

4. Boot Up and Enable the Camera
Power up the Pi.
Log into it (either via monitor/keyboard or SSH).

--------------------
Run:
sudo raspi-config
Navigate to:
Interface Options -> Camera -> Enable

Reboot when prompted.
---------------depending on the system image version, camera is auto enabled----

5. Test the Camera
After reboot, try capturing an image:
raspistill -o test.jpg
If successful, it saves a test.jpg picture in your home directory!

On newer Raspberry Pi OS versions (Bullseye and later), the old raspistill is replaced by libcamera. The new test command is:
libcamera-still -o test.jpg

6. pull the program files from git hub

7. setup autorun camera app on startup.
    First, let's create a systemd service file:
    camera.service
---------------------------
[Unit]
Description=Camera Recording and Web Server
After=network.target

[Service]
Type=simple
User=ben
WorkingDirectory=/home/ben/code/camera2
ExecStart=/usr/bin/python3 /home/ben/code/camera2/run_all.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
----------------------------

Now, let's create a script to help you install and manage the service:

install_service.sh
----------------------------
#!/bin/bash

# Copy service file to systemd directory
sudo cp camera.service /etc/systemd/system/

# Reload systemd to recognize new service
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable camera.service

# Start the service
sudo systemctl start camera.service

# Check service status
sudo systemctl status camera.service
-----------------------------
Now let's make the installation script executable:
chmod +x install_service.sh

Now you can install the service by running:
sudo ./install_service.sh

This will:
    Copy the service file to the correct location
    Reload systemd to recognize the new service
    Enable the service to start on boot
    Start the service immediately
    Show you the service status
    The service will automatically start when your Raspberry Pi boots up. You can manage the service using these commands:
    Check status: sudo systemctl status camera.service
    Stop service: sudo systemctl stop camera.service
    Start service: sudo systemctl start camera.service
    Restart service: sudo systemctl restart camera.service
    View logs: sudo journalctl -u camera.service -f
