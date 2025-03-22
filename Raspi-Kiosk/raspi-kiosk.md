

<!-- setting up raspi connection -->

sudo apt update

<!-- Then update your installed packages: -->
sudo apt full-upgrade

<!-- Then we will install Pi Connect with: -->
sudo apt install rpi-connect

<!-- enable it, enter into a terminal: -->
systemctl --user enable rpi-connect

<!-- And we will also enable it's required VNC with: -->
systemctl --user enable rpi-connect-wayvnc

<!-- Reboot your Pi, and you should see it now! -->

<!--  -- or just enable SSH  user@ ip address -->


<!-- Now we will head to the configuration window with: -->
sudo raspi-config
-> system Options > Boot / Auto Login, select B4 Desktop Autologin

<!-- #A shell script is a series of lines we can write to make the Pi execute commands. We can create a new shell script by first opening a command terminal and typing in: -->

nano run_kiosk.sh
----------------------------------------------
#!/bin/sh

# Ensure Wayland session environment
export DISPLAY=:0
export WAYLAND_DISPLAY=wayland-0

# Kill existing Chromium instances (if any)
pkill -f chromium-browser

# Wait for the Wayland session to be ready
sleep 5

# Start Chromium in kiosk mode
/usr/bin/chromium-browser --kiosk --ozone-platform=wayland --start-maximized \
  --noerrdialogs --disable-infobars --enable-features=OverlayScrollbar \
  https://time.is/ &

# Keep the script running (prevent systemd from thinking it failed)
tail -f /dev/null
--------------------------------------------------

<!-- #make it executable so we can run it. To do so, in the terminal enter: -->
sudo chmod +x run_kiosk.sh

 
<!-- #Auto-start at Boot (Wayland-Compatible) -->
<!-- If you want to auto-start the kiosk mode when your system boots, add the script to your autostart file. -->

<!-- Option 1: LXDE Autostart
If using LXDE (Raspberry Pi OS Desktop), edit: -->

sudo nano /etc/xdg/lxsession/LXDE-pi/autostart

<!-- Add this at the end: -->
@/home/ben/run_kiosk.sh

<!-- Option 2: Systemd (Recommended) -->
<!-- If you prefer a systemd service: -->

<!-- Create a new service file: -->
sudo nano /etc/systemd/system/kiosk.service

--------------------------------------------------------
[Unit]
Description=Chromium Kiosk Mode
After=graphical.target
Wants=graphical.target

[Service]
User=ben
Group=ben
Environment=DISPLAY=:0
Environment=WAYLAND_DISPLAY=wayland-0
ExecStart=/home/ben/run_kiosk.sh
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=graphical.target
---------------------------------------------------------

<!-- Save and enable the service: -->
sudo systemctl enable kiosk.service
sudo systemctl start kiosk.service

<!-- Check if it service fails: -->
systemctl status kiosk.service

<!-- After making changes, reload systemd: -->
sudo systemctl daemon-reload
sudo systemctl enable kiosk.service
sudo systemctl restart kiosk.service


<!-- Hiding the Cursor in Wayland -->
<!-- need to install both ydotool and ydotoold -->
sudo apt install ydotool
sudo apt install ydotoold

<!-- create new service file for ydotoold -->

sudo nano /etc/systemd/system/ydotoold.service

<!-- Replace /usr/local/bin/ydotoold with the correct path (from Step 1).-->
which ydotoold
<!-- For example, if which ydotoold shows /usr/bin/ydotoold, update the file:  -->

--------------------------------
[Unit]
Description=ydotool Daemon
After=multi-user.target

[Service]
ExecStart=/usr/bin/ydotoold
Restart=always
RestartSec=5
User=root

[Install]
WantedBy=multi-user.target
--------------------------------

<!-- Then, ensure the ydotool service is enabled: -->
sudo systemctl enable ydotoold
sudo systemctl start ydotoold

<!-- Check if it service fails: -->
systemctl status ydotoold.service


<!-- Then create a new script with: -->
nano hide_cursor.sh

<!-- And in there paste: -->

sleep 8
sudo ydotool mousemove --delay 1000 10000 10000

<!-- This will delay for 8 seconds and then simulate a mouse movement to the bottom right of 10,000 pixels in the x and y direction, which should be plenty enough to move it to the edge of the screen. Note: the --delay 1000 is to allow enough time for this input to be registered, ydotool and Wayland have a complicated relationship. -->

<!-- Now make it an executable with: -->

sudo chmod +x hide_cursor.sh

<!-- And in the same location as your kiosk script, you should be able to find and launch it to test that the mouse moves as intended. -->


<!-- LXDE Autostart -->
sudo nano /etc/xdg/lxsession/LXDE-pi/autostart

<!-- Add this line at the bottom: -->

@/home/ben/hide_cursor.sh

<!-- Save and reboot: -->
sudo reboot

<!-- if still not working check  -->
ls -l /dev/uinput
crw------- 1 root root 10, 223 Mar 10 16:24 /dev/uinput
<!-- Your /dev/uinput device is only accessible by root (crw------- 1 root root), 
which means non-root users (including your regular user account) cannot access it. This is why ydotool is failing. -->
<!-- Create a new udev rule: -->
echo 'KERNEL=="uinput", GROUP="input", MODE="0660"' | sudo tee /etc/udev/rules.d/99-ydotool.rules
<!-- Reload udev rules and restart services: -->
sudo udevadm control --reload-rules
sudo udevadm trigger
sudo systemctl restart ydotoold
<!-- Reboot to apply changes: -->
sudo reboot




<!-- Check Logs for Errors -->
journalctl -u ydotool.service --no-pager --lines=50

<!-- set auto dim screen
Using lightdm Configuration (For Raspberry Pi OS with Desktop)
If you use lightdm as your display manager, you can configure auto-dimming by editing its configuration file. -->

<!-- Edit the lightdm.conf file: -->
sudo nano /etc/lightdm/lightdm.conf
<!-- Find the [Seat:*] section and add (or modify) the following line: -->
xserver-command=X -s 300 -dpms
<!-- Save the file (CTRL+X, Y, Enter), then restart the system: -->
sudo reboot


<!-- install docker -->
<!-- Step 1: Update Your System
Before installing Docker, update your Raspberry Pi OS: -->

sudo apt update && sudo apt upgrade -y

<!-- Step 2: Install Docker
Run the following command to install Docker using the official convenience script: -->

curl -fsSL https://get.docker.com | sudo bash
<!-- This script detects your OS and architecture automatically and installs the correct version of Docker. -->

<!-- Step 3: Add Your User to the Docker Group
To allow running Docker commands without sudo, add your user to the Docker group: -->
sudo usermod -aG docker $USER

<!-- Then, log out and back in or run: -->
newgrp docker

<!-- Step 4: Verify Docker Installation
Check if Docker is installed correctly by running: -->

docker --version
<!-- You should see output like:
Docker version XX.XX.XX, build XXXXXX -->

<!-- Step 5 (Optional): Enable Docker to Start on Boot
To ensure Docker starts automatically on reboot, enable its service: -->
sudo systemctl enable docker
sudo systemctl start docker

<!-- Step 6 (Optional): Install Docker Compose
Docker Compose makes it easier to manage multi-container applications. Install it with: -->
sudo apt install -y docker-compose

<!-- Verify installation: -->
docker-compose --version



scp "C:\Users\huang\OneDrive\_code_personalOneDrive\_code_git\Raspi-Kiosk\1stAPP\todolist-arm64.tar" ben@raspberrypi:/home/ben/app
<!-- run this in window command line to copy files to raspi -->

<!-- for moveing everything in the folder run this in powershell -->
<!-- browse to the right directory -->
PS C:\Users\huang\OneDrive\_code_personalOneDrive\_code_git\Raspi-Kiosk> 
<!-- run following command in powershell -->
scp -r "./1stAPP/*" ben@raspberrypi:/home/ben/app/1stWeb

<!-- check screen brightness -->
cat /sys/class/backlight/11-0045/brightness
<!-- adjust the brightness --0 to 255  -->
echo 80 | sudo tee /sys/class/backlight/11-0045/brightness

https://www.industrialshields.com/blog/raspberry-pi-for-industry-26/touch-screen-configuration-kiosk-mode-virtual-keyboard-setup-249


