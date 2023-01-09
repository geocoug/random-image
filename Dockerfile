# ~~~~~~~~~~~
# Build stage
# ~~~~~~~~~~~
FROM python:3.10-slim as staging
WORKDIR /usr/local/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update -y

RUN pip install --no-cache-dir --upgrade pip==22.3.1

COPY ./requirements.txt .

RUN pip wheel --no-cache-dir --wheel-dir /usr/local/app/wheels -r requirements.txt


# ~~~~~~~~~~~
# Build final
# ~~~~~~~~~~~
FROM python:3.10-slim

ENV HOME=/usr/local/app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p $HOME

WORKDIR $HOME

RUN addgroup --system app && \
    adduser --system --group app

RUN apt-get update && \
    rm -rf /var/lib/apt/lists/*

COPY --from=staging /usr/local/app/wheels /wheels

# hadolint ignore=DL3013
RUN pip install --no-cache-dir --upgrade pip==22.3.1 && \
    pip install --no-cache-dir /wheels/*

# COPY . $HOME

RUN chown -R app:app $HOME

USER app

# CMD ["python", "unsplash_image.py", "-v", "./images/"]
