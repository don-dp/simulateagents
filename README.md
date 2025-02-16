# Setup guide

## Docker setup

[Docker with compose](https://docs.docker.com/engine/install/ubuntu/)

## Setup project

`git clone https://github.com/don-dp/simulateagents.git`

Set environment variables in `.env`

`touch .env`

These are for local testing.

```
DEBUG=True
SECRET_KEY="django-insecure-atfud-^dph4uj3tdzuth9rp@kpt*%rly8!30test"
ALLOWED_HOSTS=localhost,127.0.0.1
TURNSTILE_SECRET_KEY="1x0000000000000000000000000000000AA"
TURNSTILE_SITE_KEY="1x00000000000000000000AA"
OPENROUTER_API_KEY="your-key-here"
CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1

```

Edit `docker-compose.yml` to replace `Caddyfile.prod` with `Caddyfile.dev`.

You can replace `gunicorn` with the django development server for local testing in `entrypoint.sh`, comment out the gunicorn command and uncomment the django development server command.

`docker compose up`

In another terminal, create superuser:

`docker compose exec web python manage.py createsuperuser`
