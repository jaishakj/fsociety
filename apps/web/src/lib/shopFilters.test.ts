import assert from "node:assert/strict";
import test from "node:test";

import { parseShopFilters, serializeShopFilters } from "./shopFilters.ts";

test("parses supported shop filters and ignores invalid values", () => {
  const filters = parseShopFilters(
    new URLSearchParams("page=3&category=saree&q=%20silk%20&min_price=0&max_price=2500&sort=price_desc"),
  );

  assert.deepEqual(filters, {
    page: 3,
    category: "saree",
    q: "silk",
    min_price: 0,
    max_price: 2500,
    sort: "price_desc",
  });

  assert.deepEqual(parseShopFilters(new URLSearchParams("page=0&q=x&min_price=-1&sort=popular")), {
    page: 1,
    sort: "newest",
  });
});

test("serializes filters while preserving unrelated query parameters", () => {
  const params = serializeShopFilters(
    { page: 1, category: "silk sarees", q: "silk + cotton", min_price: 0, sort: "newest" },
    new URLSearchParams("category=old&sort=price_asc&page=8&utm_source=mail&debug"),
  );

  assert.equal(params.get("category"), "silk sarees");
  assert.equal(params.get("q"), "silk + cotton");
  assert.equal(params.get("min_price"), "0");
  assert.equal(params.get("sort"), null);
  assert.equal(params.get("page"), null);
  assert.equal(params.get("utm_source"), "mail");
  assert.equal(params.has("debug"), true);
});

test("uses the first duplicate filter value and canonicalizes it when saved", () => {
  const current = new URLSearchParams("category=saree&category=dress&page=2&page=4");
  const filters = parseShopFilters(current);
  const saved = serializeShopFilters(filters, current);

  assert.equal(filters.category, "saree");
  assert.equal(filters.page, 2);
  assert.deepEqual(saved.getAll("category"), ["saree"]);
  assert.deepEqual(saved.getAll("page"), ["2"]);
});
