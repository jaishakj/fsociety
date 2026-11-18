# E-commerce transformation progress

This document tracks implementation against `writing-block (4).md`. That specification covers the storefront, commerce API, payments, operations, and launch readiness; it directs work to proceed in deployable stages when the full scope cannot fit into one change. The transformation is still in progress.

## Waiting for owner input

- **May I make the isolated Preview API publicly reachable by changing only its Preview deployment protection, so the storefront can call it without a Vercel SSO session?** This would expose the Preview API URL and public catalogue/auth endpoints; account and cart routes still require app authentication, and they use the isolated Preview database. Production protection and data would remain untouched. I have not changed this access setting.
- The owner approved correcting only the Preview API `FRONTEND_URL`. I set it to the active Preview web origin, kept it sensitive and scoped to `codex/publish-sizes-to-main`, then rebuilt the API Preview from commit `be2813e`.
- The API Preview build is `READY`, and the public categories endpoint returns data through Vercel's authenticated fetch. The browser storefront still shows catalogue loading. A direct unauthenticated request to the API branch alias receives Vercel's HTML access page instead of JSON; an `OPTIONS` preflight also returns without CORS headers. Opening the API URL directly in the signed-in browser returns JSON. This points to Vercel Preview SSO intercepting cross-origin requests; changing CORS alone cannot bypass that gate.
- The authenticated cart round trip remains unverified. No test account was created and no cart data was written.

## Running notes

- The original attachment path is unavailable in this session. The prior audited roadmap and the spec's staged-work instruction are preserved here; implementation is continuing from the recorded next step without expanding the plan.
- Decision: the merchandise quote is public because it exposes only current public catalogue prices, has no personal data or purchase side effects, and is rate-limited to 30 requests per minute. No stock is reserved, so it cannot authorize an order.
- On 2026-11-18, the owner approved applying migration `0007_customer_carts` to the isolated Neon Preview branch `fsociety-codex-publish-sizes-preview`. The migration was applied transactionally from the generated Alembic SQL; the Preview version is `0007`, both cart tables and constraints are present, and Production remains at `0006`.

## Current increment

- Removed the client-generated UPI payment link and QR code. A configured VPA alone cannot prove that a payment was received, and this app currently has no order creation or payment verification endpoint.
- Checkout now explains that secure payment is unavailable, no order has been placed, and no payment has been taken. The customer's bag remains available for later.
- Before the checkout quote integration, the summary used a browser-calculated estimate. Checkout now displays the server-calculated merchandise subtotal, while the final payable total remains unavailable.
- Removed the UPI settings from the web environment example; checkout no longer consumes them.
- Corrected the registration rate-limit test to expect the API's existing `409 Conflict` response for a duplicate account.

## Storefront filter state stage

- The shop page now reads category, search query, minimum and maximum price, sort order, and page number from the URL. Filter changes update the URL, so shared links, refreshes, and browser Back/Forward restore the selected state.
- Invalid query values fall back to safe defaults, unrelated query parameters are preserved, and default values are omitted when serializing. Price input edits replace the current history entry; category, sort, and pagination changes create navigable entries. Sorting resets pagination, and a minimum price of zero can be cleared.
- The search modal now has a “View all” link after its eight suggestions. It opens the shop with the current query using the existing filter serializer, so shoppers can continue through the full result set.
- Verification on 2026-11-18: web tests `11 passed`; TypeScript build passed; Vite production build passed. The existing large-chunk warning remains. Web lint is unavailable because ESLint is not installed in the web package.

## Commerce foundation stage 1

- Added `POST /api/v1/cart/merchandise-quote`. It accepts product IDs and quantities, looks up published products, calculates decimal prices on the server, checks aggregate quantities against current product-level stock, rejects mixed currencies, and limits the public endpoint to 30 requests per minute.
- The endpoint is read-only: it does not reserve stock, persist a cart, create an order, or include shipping, tax, or discounts. Its result is a merchandise subtotal, not a final checkout amount.
- This stage adds no database tables or production migration. Product variants and size-specific inventory remain unsupported by the API.
- Verification: API suite `20 passed`; Ruff passed for the commerce module and its tests. One existing Pydantic deprecation warning remains in the products schema.

## Commerce foundation stage 2

- Added authenticated `GET /api/v1/cart`, `PUT /api/v1/cart`, and `DELETE /api/v1/cart` endpoints. Cart data is scoped by the verified user ID; update and clear operations are rate-limited, and replacement is atomic.
- Cart lines store product, quantity, and selected size. The API validates clothing sizes against category (XS only for dresses; S–XXL for other apparel; no size for footwear), checks aggregate product stock, merges duplicate product/size lines, and marks previously saved products unavailable when their current status or stock no longer permits them.
- Added additive migration `0007_customer_carts`. Its downgrade refuses to drop tables when saved cart data exists. Migration SQL was generated offline for review; no database was modified.
- Verification: full API suite `28 passed`; Ruff passed for commerce code and migration; Alembic offline upgrade generated both cart tables and constraints. The existing product-schema Pydantic deprecation warning remains.

## Checkout stage 1

- Checkout now requests the merchandise quote from the API and displays server-returned product names, unit-derived line subtotals, and the merchandise subtotal. It checks that returned lines still match the bag before displaying prices.
- While the quote loads, checkout does not present browser-stored prices as current prices. If the request fails, it preserves the bag, explains the price/availability check failed, and offers a retry.
- Checkout still does not synchronize its local bag to the authenticated cart API. The payment action remains unavailable; shipping, tax, discounts, reservations, and final order totals are not yet calculated.
- Verification: TypeScript build passed; web tests `4 passed`; Vite production build passed with the existing large-chunk warning.

## Commerce foundation stage 3 — authenticated cart sync

- The web app now loads and saves the signed-in customer's cart through the authenticated API. Guest bag quantities win when the same product and size exist in both bags; server-only lines are appended, and current server product names, prices, and images refresh the display. Separate apparel sizes remain distinct.
- Account changes are isolated: the cart view waits for the active account's sync before showing items, an account's unsynced local bag is cached separately, and signing out clears its visible in-memory bag while preserving it for that account's next sign-in. Sync failures keep the local bag and expose a retry.
- Checkout waits for cart sync before showing the order summary or requesting server prices. The API DTO now includes category metadata needed to render persisted cart sizes correctly.
- Verification: web TypeScript build passed; web tests `8 passed`; API tests `28 passed`; targeted API Ruff checks passed; Vite production build passed. The production bundle still reports a chunk larger than 500 kB. The web lint script could not run because ESLint is not installed in the web package.
- Preview deployment verification on 2026-11-18: API and web deployments for commit `c22f1ec` are `READY`; API `/health` and `/openapi.json` returned `200`, the OpenAPI document lists the cart and auth routes, and public category data returned seven entries. The web homepage returned `200`, and its deployed JavaScript contains the branch-specific Preview API URL rather than the Production API URL.
- Browser verification is incomplete: the storefront displayed “Categories are temporarily unavailable” and “Couldn't load new arrivals.” The API data call succeeded through Vercel's authenticated fetch, but cross-origin browser requests are intercepted by Preview SSO. The authenticated cart GET/PUT flow has not been exercised.
- Follow-up on 2026-11-18: the owner approved a Preview-only `FRONTEND_URL` check/fix. It was set to the active Preview web origin and the API was redeployed from `be2813e` as `api-mhq6pgcrq-jaishak2003-gmailcoms-projects.vercel.app` (`READY`). Direct unauthenticated browser-origin requests to the API branch alias receive Vercel's HTML access page rather than catalogue JSON, while Vercel's authenticated fetch and the signed-in browser can read the JSON. This indicates Preview SSO is intercepting the cross-origin browser request. The storefront still cannot load its catalogue; no SSO setting was changed.
- Later read-only recheck: the API still has a `FRONTEND_URL` entry scoped to Preview branch `codex/publish-sizes-to-main`. Vercel redacts the sensitive value from reads, so I could not independently compare its exact origin with the active web deployment; I did not replace it blindly. Latest web and API Preview deployments for `5c57d9f` are `READY`; the cross-origin SSO/preflight issue remains unresolved.

## Existing foundation observed during audit

- React/Vite storefront with product browsing, categories, product detail, local cart and wishlist, customer registration/sign-in, and shipping profiles.
- FastAPI/PostgreSQL API with product/category reads, admin product/category APIs, customer authentication, and shipping-profile access controls.
- Alembic history through migration `0006_customer_accounts`.

These existing features have not been independently re-certified by this increment. In particular, the cart and totals are still client-side, and the admin APIs do not amount to a complete admin dashboard.

## Remaining implementation

1. **Commerce foundation:** persistent server-owned cart, product variants and SKU-level inventory, stock reservations, shipping/tax calculation, coupon rules, order and line-item snapshots, idempotent order placement, and customer order history. The merchandise-only quote endpoint is now used for checkout price display; local cart synchronization remains pending.
2. **Verified payment:** integrate a real provider in test mode, create payment intents/orders on the API, verify signatures and webhooks server-side, handle idempotency/refunds, and only mark orders paid from verified provider events. No payment provider credentials are currently configured for this app.
3. **Customer operations:** order status, cancellation/return eligibility and requests, shipment/tracking data, transactional email, support contact flow, and account recovery/verification.
4. **Store operations:** protected admin UI for products, inventory, orders, customers, promotions, content, and settings, backed by role-checked API operations and audit history.
5. **Storefront completeness:** persistent consent-based newsletter and unsubscribe, product reviews, robust search/filter URL state, accurate merchandising/bestsellers, policy/trust content, and product structured data/sitemap/metadata.
6. **Launch verification:** automated API and browser tests for registration, catalogue, inventory races, checkout, provider callbacks, refunds, and admin permissions; accessibility/performance checks; staging deployment verification.

## Owner-provided launch inputs

Before enabling payments or promising delivery, the store owner must choose a supported payment provider and provide its test credentials, webhook configuration, and later production credentials. The business must also define supported delivery regions/rates, tax treatment, refund/return policy, support contact, and transactional email sender. These values are intentionally not invented or committed here. Production environment variables and database migrations were not changed by this increment.

## Next safe stage

Resolve the Preview browser-to-API access/origin mismatch, then verify signed-in cart GET/PUT, account switching, and frontend-to-API behavior. After that, add the order/stock reservation model and verified payment-provider flow; keep purchase disabled until those steps and provider verification are complete.
