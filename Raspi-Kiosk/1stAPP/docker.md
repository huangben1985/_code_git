docker save -o todolist-arm64.tar todolist-arm64:latest

docker run -d -p 5001:5000 todolist:latest

docker build -t todolist-arm64 .

docker load -i todolist-arm64.tar

scp "C:\Users\huang\OneDrive\_code_personalOneDrive\_code_git\Raspi-Kiosk\1stAPP\todolist-arm64.tar" ben@raspberrypi:/home/ben/app
<!-- run this in window command line to copy files to raspi -->

<!-- for moveing everything in the folder run this in powershell -->
<!-- browse to the right directory -->
PS C:\Users\huang\OneDrive\_code_personalOneDrive\_code_git\Raspi-Kiosk> 
<!-- run following command in powershell -->
scp -r "./1stAPP/*" ben@raspberrypi:/home/ben/app/1stWeb


docker build --platform linux/arm64 -t todolist-arm64 .


To use buildx specifically, you can install it using:
docker buildx create --name mybuilder --driver docker-container --bootstrap
docker buildx use mybuilder


docker run -d --restart=unless-stopped --name todolist -p 5001:5000 todolist-arm:latest