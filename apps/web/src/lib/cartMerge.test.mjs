import assert from "node:assert/strict";
import test from "node:test";

import { mergeCartItems, mergeLocalCartItems } from "./cartMerge.js";

const serverItem = (overrides = {}) => ({
  id: "server-line-id",
  product_id: "dress-1",
  name: "Current cotton dress",
  slug: "cotton-dress",
  category_slug: "dresses",
  category_name: "Dresses",
  quantity: 2,
  size: "M",
  unit_price: "1800.00",
  currency: "INR",
  image_url: "/dress.jpg",
  is_available: true,
  ...overrides,
});

test("local quantities win for matching product sizes while server metadata refreshes", () => {
  const local = [{
    id: "dress-1:M",
    productId: "dress-1",
    name: "Old dress name",
    price: "1700.00",
    currency: "INR",
    image: null,
    quantity: 1,
    categorySlug: "dresses",
    categoryName: "Dresses",
    size: "M",
  }];

  assert.deepEqual(mergeCartItems(local, [serverItem()]), [{
    ...local[0],
    name: "Current cotton dress",
    price: "1800.00",
    image: "/dress.jpg",
  }]);
  assert.equal(local[0].name, "Old dress name");
});

test("server-only lines are appended and different sizes remain separate", () => {
  const local = [{
    id: "dress-1:S",
    productId: "dress-1",
    name: "Dress",
    price: "1800.00",
    currency: "INR",
    image: null,
    quantity: 1,
    categorySlug: "dresses",
    categoryName: "Dresses",
    size: "S",
  }];
  const remote = [serverItem({ size: "M" })];

  const merged = mergeCartItems(local, remote);

  assert.deepEqual(merged.map(({ id, quantity }) => ({ id, quantity })), [
    { id: "dress-1:S", quantity: 1 },
    { id: "dress-1:M", quantity: 2 },
  ]);
});

test("the server data is used when the local bag is empty", () => {
  const merged = mergeCartItems([], [serverItem()]);
  assert.equal(merged[0].id, "dress-1:M");
  assert.equal(merged[0].quantity, 2);
  assert.equal(merged[0].categorySlug, "dresses");
});

test("the active guest bag takes priority over a cached account bag for duplicate lines", () => {
  const cached = [{
    id: "dress-1:M",
    productId: "dress-1",
    name: "Cached dress",
    price: "1800.00",
    currency: "INR",
    image: null,
    quantity: 2,
    categorySlug: "dresses",
    categoryName: "Dresses",
    size: "M",
  }];
  const active = [{ ...cached[0], quantity: 1, name: "Guest dress" }];

  assert.deepEqual(mergeLocalCartItems(active, cached), active);
});
