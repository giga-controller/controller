# Frontend

## Getting Started

Make sure your terminal is at the root of frontend

Copy the existing environment template file

```bash
# Create .env file (by copying from .env.example)
cp .env.example .env
```

Set up Clerk environment variables in the `.env` file

1. Navigate to [Clerk](https://clerk.com/docs/quickstarts/nextjs#set-your-environment-variables) and complete step 2 in the instruction manual  
   ![Set Clerk Environment Variables](./images/clerk_environment_variables.png)

2. Your `.env` (NOT `.env.local`) file should have the `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` and `CLERK_SECRET_KEY` variables populated with **no inverted commas**

### Useful commands for Development (Not necessary unless you're a Chad and want to contribute)

Install the dependencies at the root of `frontend`

```bash
npm i
```

Run the development server at the root of `frontend`

```bash
npm run dev
```

Use local tunnel to test certain authentication flows

```
npm install -g localtunnel
lt --port 3000
```
