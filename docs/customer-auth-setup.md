# Customer accounts (Clerk)

Customer sign-in uses Clerk. Shipping phone numbers and addresses are stored in the API's configured PostgreSQL database (`DATABASE_URL`), linked by Clerk's stable user ID. A customer API token can only read or update the profile belonging to its verified Clerk subject. Shipping addresses are not stored in Clerk public or unsafe metadata. The customer directory endpoint also requires the existing API admin role and a matching `CUSTOMER_DATA_OWNER_EMAIL`.

## Clerk Dashboard

1. Create or select the Clerk application for FSOCIETY.
2. In **User & authentication**, enable email sign-up and email verification. For a free production setup, use email verification codes as the account verification method. Email is the sign-in identifier; users provide their mobile number as a shipping contact after sign-up. Clerk phone/SMS authentication requires a paid production plan.
3. Do not make phone number a required authentication identifier. The app collects it with the shipping address after the verified email sign-up.
4. Add the deployed storefront origin and local development origin to Clerk's allowed origins / authorized parties.
5. Obtain the application's publishable key and the instance's Frontend API issuer URL / JWKS URL from Clerk.

## Deployment settings

Set these in the deployment environments (never commit keys into source):

**Web app**

- `VITE_CLERK_PUBLISHABLE_KEY` — Clerk publishable key, set on the Vercel project serving `apps/web` for Preview and Production.
- The frontend requires Node.js 20.9.0 or newer (declared in `apps/web/package.json`).

**API**

- `CLERK_ISSUER` — exact HTTPS issuer URL from the Clerk instance's default session token.
- `CLERK_JWKS_URL` — that instance's `/.well-known/jwks.json` URL.
- `CLERK_AUTHORIZED_PARTIES` — comma-separated storefront origins, e.g. local development and the production storefront origin.
- `CUSTOMER_DATA_OWNER_EMAIL` — email address on the existing local API admin account that alone can read the customer directory.
- Keep the API's existing `DATABASE_URL` pointed at the intended PostgreSQL/Neon database and keep the production `JWT_SECRET_KEY` configured for the existing admin login.

## Database rollout

Apply the new Alembic migration (`0005_customer_profiles`) to the target database as part of the API release. It adds a private `customer_profiles` table; it does not alter existing account rows or change the legacy admin login. Do not enable sign-up publicly until Clerk keys are set and the migration has completed.

The account page supports editing saved delivery details. Requests to access or delete a customer's details should be verified and handled by the store owner through the authorized customer directory / database process. The store currently does not save completed orders or verify UPI payments.
