# Controller

**[Controller](https://usecontroller.com/)** is the Open-source ChatGPT that interacts with all your third-party applications! It serves as a Unified Platform across your tools such as Slack, Linear, Google Suite, etc.

1. You can talk to a single application (e.g. "Get me all linear tickets that are owned by Mike, and set me as the owner")

2. Talk across your applications (e.g. "Get me all emails sent by Mike that are about user feedback, and msg him on Slack and Discord about the feedback from users")

3. Integrate with multiple applications

## Super quick demo
https://github.com/user-attachments/assets/28894a96-19c3-4216-9f8e-a54c38567eee

## Getting Started locally

1. Follow the README instructions in the [`frontend`](./frontend/README.md) and [`backend`](./backend/README.md) folders (You have to set up a few environment variables)

2. Make sure [Docker Desktop](https://www.docker.com/products/docker-desktop/) is installed and running
3. Build the docker container to start the project

```bash
docker compose up --build
```

3. Go to `localhost:3000` to start Controller!

- **IMPORTANT**: If you find yourself stuck at the loading screen, try refreshing the page. This is a known issue as our code is not bundling optimally (we are figuring out a fix for it right now!)

## Self-Hosting

We recommend hosting `frontend` on Vercel and `backend` on AWS!

## Useful commands for Development (Not necessary unless you want to contribute)
Copy the existing environment template file
```bash
# Create .env file (by copying from .env.example)
cp .env.example .env
```
