import assert from "node:assert/strict";
import test from "node:test";

import { getCountdown } from "./diwaliCountdown.ts";

test("calculates days, hours, minutes and seconds to the configured end", () => {
  const result = getCountdown("2026-11-06T01:01:01.000Z", Date.parse("2026-11-04T23:59:59.000Z"));

  assert.deepEqual(result, { expired: false, days: 1, hours: 1, minutes: 1, seconds: 2 });
});

test("marks a campaign expired at its end and clamps values to zero after it", () => {
  assert.deepEqual(getCountdown("2026-11-05T00:00:00.000Z", Date.parse("2026-11-05T00:00:00.000Z")), {
    expired: true,
    days: 0,
    hours: 0,
    minutes: 0,
    seconds: 0,
  });
  assert.deepEqual(getCountdown("2026-11-05T00:00:00.000Z", Date.parse("2026-11-05T00:01:00.000Z")), {
    expired: true,
    days: 0,
    hours: 0,
    minutes: 0,
    seconds: 0,
  });
});

test("returns null for an invalid campaign timestamp", () => {
  assert.equal(getCountdown("campaign date not set", 0), null);
});
