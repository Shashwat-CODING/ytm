FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
	PYTHONUNBUFFERED=1 \
	PIP_NO_CACHE_DIR=1 \
	PORT=7860

# System deps and Python (Ubuntu 22.04 provides Python 3.10)
RUN apt-get update && apt-get install -y --no-install-recommends \
	ca-certificates \
	curl \
	python3 \
	python3-pip \
	python3-venv \
	&& update-ca-certificates \
	&& rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only requirements first for better layer caching
COPY requirements.txt /app/requirements.txt
RUN python3 -m pip install --upgrade pip \
	&& python3 -m pip install -r /app/requirements.txt

# Copy source
COPY . /app

# Non-root user
RUN useradd -m -u 1000 appuser
USER appuser

EXPOSE 7860

# Hugging Face Spaces provides $PORT
CMD ["sh", "-c", "waitress-serve --host=0.0.0.0 --port=${PORT:-7860} app:app"]
