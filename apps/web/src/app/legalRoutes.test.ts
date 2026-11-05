import assert from "node:assert/strict";
import test from "node:test";

import { legalRoutes } from "./legalRoutes.ts";

test("legal pages use the public privacy and terms routes", () => {
  assert.deepEqual(legalRoutes, {
    privacy: "/privacy-policy",
    terms: "/terms-of-service",
  });
});
