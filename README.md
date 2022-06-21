# The Romanian Diaspora Map Kit

This project is created by [DCB](https://diasporacivica.berlin) and aims to facilitate the creation of community maps by and for Romanian diaspora communities across the globe.
The Map Kit allows members of these communities to create their own map based application to manage and share POIs around a certain region. Its goal is to provide clear information on places of interest and services in demand among the Romanian diaspora in the city and its surroundings.

## Set up for development

### Requirements

* docker-compose
* poetry

### First steps

* Clone the repo.
* Source the required env variables: `source .env`
* Make sure you have Docker and Docker Compose installed.
* Run all the required containers with `docker-compose up`.
* Apply the migrations if you're setting up for the first time: `docker exec -t map-kit-api python src/manage.py migrate`
* You're good to go! Any changes will be reflected in the containers as well, thanks to Docker volumes. The app is available under port `8000`.

### Setting up authentication

We use token based auth and authenticate users with OIDC via Auth0. To set up auth, you need access to Auth0 and you need to set a bunch of env variables so that get picked up by docker-compose and get injected into the app container. If you look in the docker-compose config, you'll find all of them, it's the variables prefixed with `OIDC_`.

The backend just uses tokens that it receives, it does not do anything else (issuing, refreshing tokens etc.). The frontend will have to prompt the user to start the social login flow via Auth0, get a token, and then use that token in any subsequent requests to the backend.

We use Auth0 because it makes managing multiple authentication providers (Google, Facebook etc.) much easier. We can add new ones or remove one without touching the application configuration.

### Running tests

The most convenient way of running the tests is inside the container of the app:

```bash
docker exec -it map-kit-api pytest src/tests/
```

You can still profit from full interactivity with the debugger in this testing setup, if needed.

### Quality checks

Currently there are two quality checks, both enforced by a GitHub Actions workflow: Autoformatting with `black` and testing. Please make sure that you have your code formatted properly and that the tests are running before committing and pushing, so that you avoid unnecessary long feedback loops after checking in code that doesn't pass the checks. In the future we will add pre-commit hooks to simplify this.
