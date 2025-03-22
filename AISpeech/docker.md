
<!-- for arm-64 To use buildx specifically, you can install it using: -->
docker buildx create --name mybuilder --driver docker-container --bootstrap
docker buildx use mybuilder

docker buildx build --platform linux/arm64 -t aispeech-arm64 . --load

docker save -o aispeech-arm64.tar aispeech-arm64:latest

<!-- for moveing everything in the folder run this in powershell -->
<!-- browse to the right directory -->
PS C:\Users\huang\OneDrive\_code_personalOneDrive\_code_git\aispeech\saveimage> 
<!-- run following command in powershell -->
scp -r aispeech-arm64.tar ben@raspberrypi:/home/ben/app/

docker load -i aispeech-arm64.tar 


docker run -d --restart=unless-stopped --name aispeech aispeech-arm64:latest