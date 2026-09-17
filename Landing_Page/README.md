# Forma by Infra

The Infra landing page and early-access app for Forma: *See better. Design smarter.*

## Local setup

1. Copy `.env.example` to `.env.local` and fill in a Postgres `DATABASE_URL` and a long `AUTH_SECRET`.
2. Install dependencies and generate the Prisma client:

   ```bash
   pnpm install
   pnpm db:generate
   pnpm db:push
   ```

3. Start the app with `pnpm dev`.

## Production configuration

- `DATABASE_URL`: managed Postgres connection string (Neon, Supabase, Railway, or Vercel Postgres).
- `AUTH_SECRET`: a random 32+ character secret. Never expose it to the client.
- `SMTP_USER`: `admin.team.infra@gmail.com`.
- `SMTP_APP_PASSWORD`: a Google App Password for that account. Do not use the normal Gmail password.
- `ADMIN_EMAIL`: defaults to `admin.team.infra@gmail.com`.

Run `pnpm db:push` during the first deployment, then deploy with `pnpm build` and `pnpm start` (or use the standard Next.js deployment). The waitlist remains usable if email is not configured, but the admin notification is skipped and logged until `SMTP_APP_PASSWORD` is present.

For a production launch, also configure a custom domain, HTTPS, rate limiting/WAF, and a verified sending domain in Resend.
