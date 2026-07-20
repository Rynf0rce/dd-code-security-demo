# Datadog Code Security — IaC(docker) 룰 탐지 시연용 의도적 취약 Dockerfile

# docker-best-practices: 태그 미지정(latest) 베이스 이미지
FROM python:latest

# docker-best-practices: 컨테이너를 root로 실행 (USER 지시어 없음)
WORKDIR /app

COPY requirements.txt .

# docker-best-practices: apt 설치 후 캐시 정리 없음 / 버전 미고정
RUN apt-get update && apt-get install -y curl netcat-openbsd

RUN pip install --no-cache-dir -r requirements.txt

COPY app/ /app/

# docker-best-practices: 빌드 인자로 시크릿 전달
ARG DB_PASSWORD=Gs3ps!Prod#2024
ENV DB_PASSWORD=${DB_PASSWORD}

# docker-best-practices: ADD 대신 COPY 권장 / 원격 URL ADD
ADD https://raw.githubusercontent.com/Rynf0rce/dd-code-security-demo/main/README.md /app/README.md

EXPOSE 8080

CMD python main.py
