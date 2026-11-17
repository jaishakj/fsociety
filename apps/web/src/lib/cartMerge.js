function keyFor(productId, size) {
  return size ? `${productId}:${size}` : productId;
}

function fromServer(item) {
  return {
    id: keyFor(item.product_id, item.size),
    productId: item.product_id,
    name: item.name,
    price: item.unit_price,
    currency: item.currency,
    image: item.image_url,
    quantity: item.quantity,
    categorySlug: item.category_slug,
    categoryName: item.category_name,
    size: item.size,
  };
}

/**
 * Keep local quantities for matching product/size lines and add server-only lines.
 * Server product data refreshes the display metadata without double-counting a bag
 * when a shopper signs in repeatedly on the same device.
 */
export function mergeCartItems(localItems, serverItems) {
  const merged = new Map();

  for (const item of localItems) {
    merged.set(keyFor(item.productId, item.size), { ...item });
  }

  for (const serverItem of serverItems) {
    const item = fromServer(serverItem);
    const previous = merged.get(item.id);
    merged.set(item.id, previous ? { ...item, quantity: previous.quantity } : item);
  }

  return [...merged.values()];
}

/** Keep the active local bag's quantity when restoring a cached account bag. */
export function mergeLocalCartItems(activeItems, cachedItems) {
  const merged = new Map();
  for (const item of cachedItems) merged.set(keyFor(item.productId, item.size), { ...item });
  for (const item of activeItems) merged.set(keyFor(item.productId, item.size), { ...item });
  return [...merged.values()];
}
