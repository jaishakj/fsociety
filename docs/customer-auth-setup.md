# Customer accounts

Customer accounts use the API's existing email/password authentication, Argon2 password hashing, short-lived access tokens, rotating refresh tokens, and revocable database-backed sessions. Customer registration creates a standard `user` role; it does not grant administrator access.

Shipping phone and address live in `customer_profiles`, linked to the account UUID. Each signed-in customer can read or change only their own profile. The customer directory remains restricted to API administrators and the configured `CUSTOMER_DATA_OWNER_EMAIL`.

## Vercel configuration

The web app uses `VITE_API_URL` when configured and otherwise defaults to the production API URL. Set the web Preview value to the API Preview URL for branch deployments. The API requires:

- `DATABASE_URL` — the database connection for that deployment environment.
- `JWT_SECRET_KEY` — an existing strong, random secret, at least 32 bytes.
- `FRONTEND_URL` — the exact storefront origin allowed by API CORS.
- `CUSTOMER_DATA_OWNER_EMAIL` — the administrator email allowed to access the customer directory.

Do not copy Preview values into Production. Apply Alembic migrations through `0006` to the database before enabling account signup in a deployment.

## Account recovery

The app currently supports registration, sign-in, sign-out, and session refresh. It does not send email verification or password reset messages. Customers who lose access to a password need the store operator to provide a recovery process before public launch.
