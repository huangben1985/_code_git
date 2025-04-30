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