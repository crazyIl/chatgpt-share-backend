#!/bin/bash
set -x
# 设置一个项目名变量
project_name="chatgpt-share-backend"
docker rm -f $project_name
docker build . -t crazyl/${project_name}:latest
# 启动容器
docker run -d --restart always -p 13013:5000 --name $project_name \
-e TZ=Asia/Shanghai \
-e DB_HOST=172.17.0.1 \
-e DB_PORT=3306 \
-e DB_USER=chatgpt_share \
-e DB_PASSWORD=chatgpt123 \
-e DB_NAME=chatgpt_share \
-e SITE_PASSWORD=Ib4HBeJs2T1GMaY3 \
-e FUCLAUDE_BASE_URL=http://10.18.2.110:13015 \
--log-opt loki-pipeline-stages=$'- multiline:\n    firstline: \'^^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}\'\n    max_wait_time: 5s' \
crazyl/${project_name}:latest


docker run -d --restart always -p 13013:5000 --name chatgpt-share-backend \
-e TZ=Asia/Shanghai \
-e FUCLAUDE_BASE_URL=http://10.18.2.110:13015 \
-e DB_HOST=172.17.0.1 \
-e DB_PORT=3306 \
-e DB_USER=chatgpt_share \
-e DB_PASSWORD=chatgpt123 \
-e DB_NAME=chatgpt_share \
-e SITE_PASSWORD=Ib4HBeJs2T1GMaY3 \
crazyl/chatgpt-share-backend:latest


docker run -d --restart always -p 13013:5000 --name chatgpt-share-backend \
-e TZ=Asia/Shanghai \
-e FUCLAUDE_BASE_URL=http://10.18.2.110:13015 \
-v /opt/chatgpt-share-backend/data:/app/data \
-e SITE_PASSWORD=Ib4HBeJs2T1GMaY3 \
crazyl/chatgpt-share-backend:latest


docker run -d --restart always -p 13013:5000 --name chatgpt-share-backend \
-e TZ=Asia/Shanghai \
-e FUCLAUDE_BASE_URL=http://10.18.2.110:13015 \
-e DB_HOST=172.17.0.1 \
-e DB_PORT=3306 \
-e DB_USER=chatgpt_share \
-e DB_PASSWORD=chatgpt123 \
-e DB_NAME=chatgpt_share \
-e SITE_PASSWORD=Ib4HBeJs2T1GMaY3 \
--log-opt loki-pipeline-stages=$'- multiline:\n    firstline: \'^^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}\'\n    max_wait_time: 5s' \
crazyl/chatgpt-share-backend:latest


DB_HOST=10.18.2.110 DB_PORT=3306 DB_USER=chatgpt_share DB_PASSWORD=chatgpt123 DB_NAME=chatgpt_share UCLAUDE_BASE_URL=http://10.18.2.110:135 PORT=13013 python3.9 main.py 
