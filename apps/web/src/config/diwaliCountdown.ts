const SECOND = 1_000;

export interface CountdownParts {
  expired: boolean;
  days: number;
  hours: number;
  minutes: number;
  seconds: number;
}

export function getCountdown(endAt: string, now = Date.now()): CountdownParts | null {
  const target = Date.parse(endAt);
  if (!Number.isFinite(target)) return null;

  const remaining = Math.max(0, target - now);
  return {
    expired: remaining === 0,
    days: Math.floor(remaining / 86_400_000),
    hours: Math.floor((remaining % 86_400_000) / 3_600_000),
    minutes: Math.floor((remaining % 3_600_000) / 60_000),
    seconds: Math.floor((remaining % 60_000) / SECOND),
  };
}
