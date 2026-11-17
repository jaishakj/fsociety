# E-commerce transformation progress

This document tracks implementation against `writing-block (4).md`. That specification covers the storefront, commerce API, payments, operations, and launch readiness; it directs work to proceed in deployable stages when the full scope cannot fit into one change. This commit delivers the first safety-focused increment and does not claim the full transformation is complete.

## Current increment

- Removed the client-generated UPI payment link and QR code. A configured VPA alone cannot prove that a payment was received, and this app currently has no order creation or payment verification endpoint.
- Checkout now explains that secure payment is unavailable, no order has been placed, and no payment has been taken. The customer's bag remains available for later.
- The checkout summary labels its browser-calculated amount as an estimate; it is not a server-authoritative quote.
- Removed the UPI settings from the web environment example; checkout no longer consumes them.
- Corrected the registration rate-limit test to expect the API's existing `409 Conflict` response for a duplicate account.

## Existing foundation observed during audit

- React/Vite storefront with product browsing, categories, product detail, local cart and wishlist, customer registration/sign-in, and shipping profiles.
- FastAPI/PostgreSQL API with product/category reads, admin product/category APIs, customer authentication, and shipping-profile access controls.
- Alembic history through migration `0006_customer_accounts`.

These existing features have not been independently re-certified by this increment. In particular, the cart and totals are still client-side, and the admin APIs do not amount to a complete admin dashboard.

## Remaining implementation

1. **Commerce foundation:** server-owned cart/quote, product variants and SKU-level inventory, stock reservations, shipping/tax calculation, coupon rules, order and line-item snapshots, idempotent order placement, and customer order history.
2. **Verified payment:** integrate a real provider in test mode, create payment intents/orders on the API, verify signatures and webhooks server-side, handle idempotency/refunds, and only mark orders paid from verified provider events. No payment provider credentials are currently configured for this app.
3. **Customer operations:** order status, cancellation/return eligibility and requests, shipment/tracking data, transactional email, support contact flow, and account recovery/verification.
4. **Store operations:** protected admin UI for products, inventory, orders, customers, promotions, content, and settings, backed by role-checked API operations and audit history.
5. **Storefront completeness:** persistent consent-based newsletter and unsubscribe, product reviews, robust search/filter URL state, accurate merchandising/bestsellers, policy/trust content, and product structured data/sitemap/metadata.
6. **Launch verification:** automated API and browser tests for registration, catalogue, inventory races, checkout, provider callbacks, refunds, and admin permissions; accessibility/performance checks; staging deployment verification.

## Owner-provided launch inputs

Before enabling payments or promising delivery, the store owner must choose a supported payment provider and provide its test credentials, webhook configuration, and later production credentials. The business must also define supported delivery regions/rates, tax treatment, refund/return policy, support contact, and transactional email sender. These values are intentionally not invented or committed here. Production environment variables and database migrations were not changed by this increment.

## Next safe stage

Build the server-side commerce schema and quote/order API behind tests, then connect checkout to a provider's test environment. Do not re-enable direct client-to-VPA payment as a substitute for verified order/payment state.
