FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    calibre \
    xdg-utils \
    wget \
    xz-utils \
    && rm -rf /var/lib/apt/lists/*
    
# PDF 변환을 위한 환경변수 설정
ENV XDG_RUNTIME_DIR=/tmp/runtime-root
ENV QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox --disable-dev-shm-usage --disable-gpu"

# 런타임 디렉토리 생성
RUN mkdir -p /tmp/runtime-root

# Poetry 설치 (버전 고정)
RUN pip install poetry==1.6.1

# Poetry 설정: 가상 환경 생성하지 않음
RUN poetry config virtualenvs.create false

# 의존성 파일 복사 및 설치
COPY pyproject.toml poetry.lock* ./
RUN poetry install --without dev --no-interaction --no-ansi

# 애플리케이션 코드 복사
COPY app app/

# 서버 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]