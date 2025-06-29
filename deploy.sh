#!/bin/bash

# Docker 이미지 가져오기
docker pull koesnam/blog-to-book:latest

# 기존 컨테이너 중지 및 제거 (존재하는 경우)
if [ $(docker ps -q -f name=blog-to-book) ]; then
    docker stop blog-to-book
fi
if [ $(docker ps -aq -f status=exited -f name=blog-to-book) ]; then
    docker rm blog-to-book
fi

# 새 컨테이너 실행
docker run -d --name blog-to-book -p 8000:8000 koesnam/blog-to-book:latest

# 사용하지 않는 Docker 이미지 정리 (선택 사항)
docker image prune -f
