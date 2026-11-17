# E-commerce transformation progress

This document tracks implementation against `writing-block (4).md`. That specification covers the storefront, commerce API, payments, operations, and launch readiness; it directs work to proceed in deployable stages when the full scope cannot fit into one change. This commit delivers the first safety-focused increment and does not claim the full transformation is complete.

## Running notes

- The original attachment path is unavailable in this session. The prior audited roadmap and the spec's staged-work instruction are preserved here; implementation is continuing from the recorded next step without expanding the plan.
- Decision: the merchandise quote is public because it exposes only current public catalogue prices, has no personal data or purchase side effects, and is rate-limited to 30 requests per minute. No stock is reserved, so it cannot authorize an order.

## Current increment

- Removed the client-generated UPI payment link and QR code. A configured VPA alone cannot prove that a payment was received, and this app currently has no order creation or payment verification endpoint.
- Checkout now explains that secure payment is unavailable, no order has been placed, and no payment has been taken. The customer's bag remains available for later.
- The checkout summary labels its browser-calculated amount as an estimate; it is not a server-authoritative quote.
- Removed the UPI settings from the web environment example; checkout no longer consumes them.
- Corrected the registration rate-limit test to expect the API's existing `409 Conflict` response for a duplicate account.

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

## Existing foundation observed during audit

- React/Vite storefront with product browsing, categories, product detail, local cart and wishlist, customer registration/sign-in, and shipping profiles.
- FastAPI/PostgreSQL API with product/category reads, admin product/category APIs, customer authentication, and shipping-profile access controls.
- Alembic history through migration `0006_customer_accounts`.

These existing features have not been independently re-certified by this increment. In particular, the cart and totals are still client-side, and the admin APIs do not amount to a complete admin dashboard.

## Remaining implementation

1. **Commerce foundation:** persistent server-owned cart, product variants and SKU-level inventory, stock reservations, shipping/tax calculation, coupon rules, order and line-item snapshots, idempotent order placement, and customer order history. The merchandise-only quote endpoint is now in place; the browser has not been switched to it yet.
2. **Verified payment:** integrate a real provider in test mode, create payment intents/orders on the API, verify signatures and webhooks server-side, handle idempotency/refunds, and only mark orders paid from verified provider events. No payment provider credentials are currently configured for this app.
3. **Customer operations:** order status, cancellation/return eligibility and requests, shipment/tracking data, transactional email, support contact flow, and account recovery/verification.
4. **Store operations:** protected admin UI for products, inventory, orders, customers, promotions, content, and settings, backed by role-checked API operations and audit history.
5. **Storefront completeness:** persistent consent-based newsletter and unsubscribe, product reviews, robust search/filter URL state, accurate merchandising/bestsellers, policy/trust content, and product structured data/sitemap/metadata.
6. **Launch verification:** automated API and browser tests for registration, catalogue, inventory races, checkout, provider callbacks, refunds, and admin permissions; accessibility/performance checks; staging deployment verification.

## Owner-provided launch inputs

Before enabling payments or promising delivery, the store owner must choose a supported payment provider and provide its test credentials, webhook configuration, and later production credentials. The business must also define supported delivery regions/rates, tax treatment, refund/return policy, support contact, and transactional email sender. These values are intentionally not invented or committed here. Production environment variables and database migrations were not changed by this increment.

## Next safe stage

Connect the authenticated cart and merchandise quote APIs to the existing checkout/cart UI, preserving local cart data during the move and leaving purchase disabled until an order/payment flow is verified. Apply migration `0007` only to a non-production preview database before testing those routes. Do not re-enable direct client-to-VPA payment as a substitute for verified order/payment state.
