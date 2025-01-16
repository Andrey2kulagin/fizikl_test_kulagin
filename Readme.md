1. Устанавливаем docker  и даем ему права sudo
```
curl -fsSL https://get.docker.com -o get-docker.sh 
sudo sh get-docker.sh 
sudo usermod -aG docker $USER 
su - $USER 
```

2. устанавливаем зеркала для докера
```
sudo nano /etc/docker/daemon.json
```
```
{  
  "registry-mirrors": [  
    "https://dockerhub1.beget.com", 
    "https://mirror.gcr.io"  
  ]  
}
```
```
sudo systemctl restart docker
```
3. Устанавливаем docker-compose
```
sudo apt install docker-compose
```
4. Копируем .env
```
cp .env_example .env
```
5. Собираем контейнер
```
docker-compose up --build
```
6. Открываем документацию
```
http://127.0.0.1:8000/swagger/
```