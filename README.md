# The Romanian Diaspora Map Kit

This project is created by [DCB](https://diasporacivica.berlin) and aims to facilitate the creation of community maps by and for Romanian diaspora communities across the globe.

The Map Kit allows members of these communities to create their own map based application to manage and share POIs around a certain region. Its goal is to provide clear information on places of interest and services in demand among the Romanian diaspora in the city and its surroundings.

## Requirements

- [Poetry](https://python-poetry.org/docs/)
- [Docker](https://docs.docker.com/get-docker/)

## Install

1. Clone the repo
2. Create Docker containers

```bash
docker compose up
```

3. Apply the migrations if you're setting up for the first time

```bash
docker exec -t map-kit-api python src/manage.py migrate
```

## Run

Endpoints are reachable on port [8000](localhost:8000).

## Configure Django

### Create a superuser

```bash
docker exec -t map-kit-api python src/manage.py createsuperuser
```

:warning: Make sure the email for this user will not coincide with the mail of your google account from which you'll create your working user. (hint: <admin@example.com>). Otherwise, you'll get an error later when working with endpoints requiring a jwt.

Log into the [admin panel](http://localhost:8000/admin) with those credentials.

### Create working user

When you create a new username (google login, Auth0), make sure you set it to 'approved' in Django's admin section, otherwise none of the api endpoints that require a jwt token (i.e. /my-communities/*) will work.

## Authentication

We use token based auth and authenticate users with [OIDC](https://auth0.com/docs/authenticate/protocols/openid-connect-protocol) via [Auth0](https://auth0.com/).

The backend just uses tokens that it receives, it does not do anything else (issuing, refreshing tokens etc.). The frontend will have to prompt the user to start the social login flow via Auth0, get a token, and then use that token in any subsequent requests to the backend.

We use Auth0 because it makes managing multiple authentication providers (Google, Facebook etc.) much easier. We can add new ones or remove one without touching the application configuration.

### Set-up

1. Adjust Auth0 variables (prefixed `OIDC_`) in .env.
2. Build your containers again.

**TODO**

- [ ] Expand this section.

## Test

```bash
docker exec -it map-kit-api pytest src/tests/
```

You can still profit from full interactivity with the debugger in this testing setup, if needed.

## Lint

```bash
docker exec -it map-kit-api black src
```

In the future we will add pre-commit hooks to simplify this.

## Troubleshoot

### Django User Conflict

**Problem**
Admin and working user are the same.

**Solution**
Remove the user and registering it again. The 2 users with the same email will be merged.
