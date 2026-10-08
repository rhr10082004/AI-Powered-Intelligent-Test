# Production Deployment

The web client is a Vercel Next.js project. The API and PostgreSQL database are separate Render services; Vercel does not host this FastAPI application as a long-running ASGI server.

## Vercel

1. Import this Git repository into Vercel and set **Root Directory** to `apps/web`.
2. Leave the framework as Next.js. `apps/web/vercel.json` installs dependencies from the npm workspace root and builds the web workspace.
3. Set `NEXT_PUBLIC_API_URL` in Production, Preview, and Development environments to the public API URL including `/api`, for example `https://your-api.onrender.com/api`.
4. Deploy. The Vercel build intentionally fails if a production API URL is missing.

## API and database on Render

1. Create a Render Blueprint from this repository using `render.yaml`.
2. Set the requested `CORS_ORIGINS` environment variable to a JSON string array containing the exact Vercel origin(s), for example `["https://your-project.vercel.app"]`. Add the production custom domain when configured.
3. Set `OPENAI_API_KEY` to enable model-backed tutoring. The tutor has local study guidance when it is unset.
4. Render provisions PostgreSQL, generates `JWT_SECRET_KEY` and `ADMIN_API_KEY`, runs Alembic migrations and idempotent starter seeding before deploy, then serves `/health`.
5. Copy the deployed API base URL plus `/api` into Vercel's `NEXT_PUBLIC_API_URL` and redeploy the web project.

## Required production settings

- `ENVIRONMENT=production`
- `DATABASE_URL` from the managed PostgreSQL service
- `JWT_SECRET_KEY` generated and at least 32 characters
- `ADMIN_API_KEY` generated; needed only for content-authoring endpoints
- `CORS_ORIGINS` as a JSON array; localhost origins are rejected in production
- `NEXT_PUBLIC_API_URL` as the public API origin ending in `/api`

Never commit production tokens, passwords, database URLs, or provider keys. Deploying the services still requires the repository to be connected to your Vercel and Render accounts; this workspace does not contain those account credentials.