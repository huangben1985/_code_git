sudo docker start -ai mictest_audio-app_1

sudo docker rm mictest_audio-app_1


sudo docker-compose down
sudo docker run -e -it mictest_audio-app_1

sudo docker-compose up --build -d

sudo docker stop mictest_audio-app_1
sudo docker start -ai mictest_audio-app_1 -- --device 3 --duration 15