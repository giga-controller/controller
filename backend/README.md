# Backend

## Getting Started

Make sure your terminal is at the root of backend

### Using [Poetry](https://python-poetry.org/) for dependency management.

```bash
# Install Poetry (If using Windows, use WSL)
curl -sSL https://install.python-poetry.org | python3 -
```

You will need to set poetry in your `PATH` environment variable. See [Step 3](https://python-poetry.org/docs/#installing-with-the-official-installer).

Install all dependencies

```bash
# Install dependencies
poetry install
```

```bash
# Update/upgrade dependencies
poetry update
```

```bash
# Activate Python virtual environment
poetry shell
```

### Copy the existing environment template file

```bash
# Create .env file (by copying from .env.example)

# MacOS/Linux
cp .env.example .env

# Windows
copy .env.example .env
```

### Set up [Supabase](https://supabase.com/)

1. Create a project (Note down your project's password)  
  ![Create Project](./images/supabase_create_project.png)

2. Click on the `Connect` button (It might take 1-2mins for the button to appear as Supabase needs to create your DB)
  ![Connect to Supabase](./images/supabase_connect.png)

3. Set the mode from `transaction` to `session`  
  ![Set transaction mode](./images/supabase_transaction_mode.png)

4. Copy the URI (You will need it for step 5 and step 8)  
  ![Copy URI](./images/supabase_copy_uri.png)

5. Run `psql "<COPIED URI>"` (Remember to put the password in place of [YOUR PASSWORD] in the URI) in your terminal at the root of `backend`

```bash
psql "postgresql://postgres.jcmefqghesrtgvxzsvak:grae!bfSB@aws-0-us-west-7.pooler.supabase.com:5432/postgres"
```

**IMPORTANT: You MUST have the inverted commas around the URI. Do not include the square brackets around your password in the URI.**  

6. Run `\i ./supabase_schema.sql` in the same terminal instance at the root of `backend`
7. Close this terminal -> You are done!
8. Paste the copied URI (Remember to put the password in) into the DATABASE_URL `.env` variable. It should look like `DATABASE_URL=<COPIED URI>` with **no inverted commas** around the URI.
9. Replace the **prefix** of the copied URI from `postgresql://` to `postgresql+asyncpg://`

```bash
e.g. postgresql+asyncpg://postgres.jcmefqghesrtgvxzsvak:grae!bfSB@aws-0-us-west-7.pooler.supabase.com:5432/postgres
```

### Get your [OpenAI](https://platform.openai.com/api-keys) api key

1. Paste the api key into the OPENAI_API_KEY `.env` variable. It should look like `OPENAI_API_KEY=<COPIED API KEY>` with **no inverted commas** around the api key.

2. If you have a custom OpenAI compatible backend, you can change the default ```OPENAI_BASE_URL``` to use it.

### Useful commands for Development (Not necessary unless you're a Chad and want to contribute)

#### Start the server (locally)

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

#### Check style

Run the following command at the root of `backend`

```bash
# Style check
black .

# Import check
isort .
```
