# Controller

Open-source ChatGPT that interacts with all your third party applications!

## Super quick demo
https://github.com/user-attachments/assets/3f384bc9-90c9-4101-a9aa-7d473cb45859

## Getting Started locally

1. Follow the README instructions in the [`frontend`](./frontend/README.md) and [`backend`](./backend/README.md) folders (You have to set up a few environment variables)

2. Build the docker container to start the project

```bash
docker compose up --build
```

3. Go to `localhost:3000` to start Controller!

- **IMPORTANT**: If you find yourself stuck at the loading screen, try refreshing the page. This is a known issue as our code is not bundling optimally (we are figuring out a fix for it right now!)

## Self-Hosting

We recommend hosting `frontend` on Vercel and `backend` on AWS!

### Useful commands for Development (Not necessary unless you want to contribute)

Copy the existing environment template file
```bash
# Create .env file (by copying from .env.example)
cp .env.example .env
```



