export function AmbientGlow() {
  return (
    <>
      <div
        className="pointer-events-none absolute -top-20 left-1/4 h-[420px] w-[420px] rounded-full blur-3xl"
        style={{ background: "var(--color-signal-dim)", opacity: 0.35 }}
      />
      <div
        className="pointer-events-none absolute right-1/4 top-1/2 h-[320px] w-[320px] rounded-full blur-3xl"
        style={{ background: "var(--color-signal-dim)", opacity: 0.25 }}
      />
    </>
  );
}
