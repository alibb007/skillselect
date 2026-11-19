import React from "react";
import { AbsoluteFill, getInputProps, interpolate, random, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "./theme";
import data from "./data.json";

// Everything on screen comes from data.json, which tools/clip/make_data.py writes from the saved sessions.
const C = theme.colors;
const FLAT = Boolean((getInputProps() as any).flat); // for the GIF: no moving grain, no drifting background
export const SECONDS = 65;

// when each beat starts, in seconds. Scenes with more to read get more time.
const T = {
  drop: 0.4,
  ask: 4.5, type: 5.0, mess: 7.3,
  lift: 11.0, buried: 12.4, noteA: 13.6,
  tidy: 18.0, sweep: 19.1,
  score: 22.5, rank: 25.6,
  cards: 29.0, card1: 30.6, cardStep: 1.9,
  hub: 40.5, row1: 41.4, rowStep: 1.7,
  chart: 50.5, bar1: 51.4, barStep: 2.0,
  end: 60.0,
};

const PAD = 96, W = 1920 - PAD * 2, TOP = 340;
const COLS = 10, GAP = 16, TW = (W - GAP * (COLS - 1)) / COLS, TH = 112;
const CW = (W - 24 * 4) / 5, CH = 560;

type Ctx = { f: number; fps: number };
const sec = (c: Ctx, s: number) => Math.round(s * c.fps);
const sp = (c: Ctx, at: number, cfg: any = theme.spring.smooth) => spring({ frame: c.f - sec(c, at), fps: c.fps, config: cfg });
const clampOpt = { extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const };
const tw = (c: Ctx, a: number, b: number, from: number, to: number, ease = theme.ease.out) => interpolate(c.f, [sec(c, a), sec(c, b)], [from, to], { ...clampOpt, easing: ease });
const out = (c: Ctx, at: number, dur = 0.32) => tw(c, at, at + dur, 1, 0, theme.ease.in);
const mix = (a: number, b: number, p: number) => a + (b - a) * p;
const fmt = (n: number) => Math.round(n).toLocaleString("en-US");
const soft = (s: string) => s.replace(/-/g, "-​");
const fitNames = data.fits.map((x) => x.name);
const maxScore = Math.max(...Object.values(data.scores as Record<string, number>), 1);

const BgMesh: React.FC<{ c: Ctx }> = ({ c }) => {
  const d1 = FLAT ? 0 : Math.sin(c.f / 70) * 60, d2 = FLAT ? 0 : Math.cos(c.f / 90) * 50;
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <div style={{ position: "absolute", width: 1300, height: 1300, borderRadius: "50%", top: -620, left: -380 + d1, filter: "blur(60px)", background: `radial-gradient(circle, ${C.hero}1F, transparent 62%)` }} />
      <div style={{ position: "absolute", width: 1100, height: 1100, borderRadius: "50%", bottom: -560, right: -320 - d2, filter: "blur(70px)", background: `radial-gradient(circle, ${C.warn}22, transparent 64%)` }} />
    </AbsoluteFill>
  );
};
const Finish: React.FC<{ c: Ctx }> = ({ c }) => {
  const noise = `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='220' height='220'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='220' height='220' filter='url(%23n)' opacity='0.5'/%3E%3C/svg%3E")`;
  return (
    <>
      <AbsoluteFill style={{ pointerEvents: "none", backgroundColor: C.hero, mixBlendMode: "soft-light", opacity: 0.06 }} />
      {FLAT ? null : <AbsoluteFill style={{ pointerEvents: "none", backgroundImage: noise, backgroundSize: "220px", backgroundPosition: `${(c.f * 7) % 220}px ${(c.f * 13) % 220}px`, opacity: 0.05, mixBlendMode: "multiply" }} />}
      <AbsoluteFill style={{ pointerEvents: "none", background: "radial-gradient(ellipse at center, transparent 62%, rgba(20,22,27,0.10) 100%)" }} />
    </>
  );
};

// One headline at a time. Words wrapped in *stars* are the ones the eye should land on.
const Headline: React.FC<{ c: Ctx; from: number; to: number; text: string; col?: string }> = ({ c, from, to, text, col = C.hero }) => {
  if (c.f < sec(c, from) - 2 || c.f > sec(c, to) + 14) return null;
  const words = text.split(" ").map((w) => ({ w: w.replace(/\*/g, ""), hi: w.includes("*") }));
  const o = out(c, to);
  return (
    <div style={{ position: "absolute", left: PAD, top: 64, width: W, display: "flex", flexWrap: "wrap", columnGap: 18, rowGap: 0, fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 68, letterSpacing: "-0.035em", lineHeight: 1.1, color: C.ink, opacity: o, transform: `translateY(${(1 - o) * -22}px)` }}>
      {words.map((x, i) => {
        const p = sp(c, from + i * 0.07, theme.spring.snappy);
        return <span key={i} style={{ display: "inline-block", opacity: p, transform: `translateY(${mix(30, 0, p)}px) scale(${mix(0.96, 1, p)})`, color: x.hi ? col : C.ink }}>{x.w}</span>;
      })}
    </div>
  );
};

const Note: React.FC<{ c: Ctx; from: number; to: number; children: React.ReactNode }> = ({ c, from, to, children }) => {
  if (c.f < sec(c, from) || c.f > sec(c, to) + 12) return null;
  const p = sp(c, from), o = out(c, to);
  return <div style={{ position: "absolute", left: PAD, top: 1002, width: W, textAlign: "center", fontFamily: theme.fonts.body, fontWeight: 500, fontSize: 25, color: C.dim, opacity: p * o, transform: `translateY(${mix(12, 0, p)}px)` }}>{children}</div>;
};

// What the person typed. It stays on screen from the moment they ask.
const JobRow: React.FC<{ c: Ctx }> = ({ c }) => {
  if (c.f < sec(c, T.ask)) return null;
  const p = sp(c, T.ask + 0.2), o = out(c, T.chart - 0.4);
  const n = Math.round(tw(c, T.type, T.type + 1.9, 0, data.ask.length, theme.ease.inOut));
  const withPlugin = sp(c, T.tidy, theme.spring.bouncy);
  return (
    <div style={{ position: "absolute", left: PAD, top: 236, height: 76, display: "flex", alignItems: "center", gap: 18, opacity: p * o, transform: `translateY(${mix(-20, 0, p)}px)` }}>
      <div style={{ height: 76, padding: "0 30px", borderRadius: 38, background: C.surface, border: `2px solid ${C.line}`, boxShadow: `0 14px 34px -18px ${C.shadow}`, display: "flex", alignItems: "center", gap: 16 }}>
        <span style={{ fontFamily: theme.fonts.mono, fontWeight: 700, fontSize: 19, letterSpacing: "0.08em", color: C.faint }}>YOU ASK</span>
        <span style={{ fontFamily: theme.fonts.body, fontWeight: 600, fontSize: 31, color: C.ink, minWidth: 560 }}>{data.ask.slice(0, n)}{n < data.ask.length ? <span style={{ display: "inline-block", width: 3, height: 32, background: C.ink, marginLeft: 3, verticalAlign: -5 }} /> : null}</span>
      </div>
      <div style={{ height: 60, padding: "0 24px", borderRadius: 30, background: C.hero, display: "flex", alignItems: "center", fontFamily: theme.fonts.body, fontWeight: 700, fontSize: 24, color: C.surface, opacity: withPlugin, transform: `scale(${mix(0.8, 1, withPlugin)})` }}>with Straight Answer</div>
    </div>
  );
};

const tilePos = (i: number) => ({ x: PAD + (i % COLS) * (TW + GAP), y: TOP + Math.floor(i / COLS) * (TH + GAP) });
// where each box ends up in the pile: fixed per box, so every render is the same
const messPos = (i: number) => ({ x: 960 - TW / 2 + (random("x" + i) - 0.5) * 1060, y: 640 + (random("y" + i) - 0.5) * 330, r: (random("r" + i) - 0.5) * 58 });

const Tiles: React.FC<{ c: Ctx }> = ({ c }) => {
  const used = data.plain.used[0];
  return (
    <>
      {data.installed.map((name, i) => {
        const g = tilePos(i), m = messPos(i), col = i % COLS;
        const k = fitNames.indexOf(name), fit = k >= 0, isUsed = name === used;
        const drop = sp(c, T.drop + i * 0.055, theme.spring.bouncy);
        const toMess = sp(c, T.mess + random("d" + i) * 0.9, theme.spring.smooth), back = sp(c, T.tidy + (i % 10) * 0.03 + Math.floor(i / 10) * 0.05, theme.spring.snappy);
        const mess = toMess * (1 - back);
        const rummage = mess * Math.sin(c.f / 7 + i) * 5 * (c.f < sec(c, T.lift) ? 1 : 0.25);
        const lift = isUsed ? sp(c, T.lift + 0.3, theme.spring.bouncy) * (1 - back) : 0;
        const glow = fit && !isUsed ? Math.min(tw(c, T.buried, T.buried + 0.5, 0, 1), tw(c, T.tidy - 0.2, T.tidy, 1, 0)) : 0;
        const score = sp(c, T.score + 0.3 + col * 0.08 + Math.floor(i / COLS) * 0.05, theme.spring.slow);
        const s = (data.scores as Record<string, number>)[name] || 0;
        const ranked = sp(c, T.rank + (fit ? k * 0.14 : 0), fit ? theme.spring.bouncy : theme.spring.smooth);
        let x = mix(g.x, m.x, mess) + rummage, y = mix(g.y, m.y, mess), rot = m.r * mess, scale = mix(0.7, 1, drop), z = fit ? 3 : 1;
        if (lift > 0) { x = mix(x, 960 - TW / 2, lift); y = mix(y, TOP + 20, lift); rot *= 1 - lift; scale *= mix(1, 1.9, lift); z = 9; }
        const dropY = mix(-420 - (i % COLS) * 30, 0, drop);
        if (!fit) {
          const gone = out(c, T.cards - 0.25 + (i % 7) * 0.02, 0.3);
          if (gone <= 0) return null;
          return (
            <div key={name} style={{ position: "absolute", left: x, top: y + dropY + (1 - gone) * 18, width: TW, height: TH, borderRadius: 18, background: C.surface, border: `2px solid ${C.line}`, boxShadow: mess > 0.05 ? `0 10px 24px -14px ${C.shadow}` : "none", overflow: "hidden", zIndex: z,
              opacity: Math.min(1, drop * 1.4) * mix(1, 0.3, ranked) * gone, transform: `rotate(${rot}deg) scale(${scale * mix(1, 0.96, ranked)})` }}>
              <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", padding: 12, textAlign: "center", fontFamily: theme.fonts.body, fontWeight: 600, fontSize: 18, lineHeight: 1.22, color: C.ink }}>{soft(name)}</div>
              <div style={{ position: "absolute", left: 12, right: 12, bottom: 9, height: 6, borderRadius: 3, background: C.bg, opacity: score }}><div style={{ width: `${(s / maxScore) * 100 * score}%`, height: "100%", borderRadius: 3, background: C.faint }} /></div>
            </div>
          );
        }
        // a skill that fits the request
        const fly = sp(c, T.cards + k * 0.13), gone = out(c, T.hub - 0.2 + k * 0.05, 0.3);
        if (gone <= 0) return null;
        const tx = PAD + k * (CW + 24), ty = TOP, at = T.card1 + k * T.cardStep, info = sp(c, at), active = c.f >= sec(c, at) && c.f < sec(c, at + T.cardStep);
        const hot = ranked > 0.4 || lift > 0.4, blue = ranked > 0.4;
        return (
          <div key={name} style={{ position: "absolute", left: mix(x, tx, fly), top: mix(y + dropY, ty, fly) - (1 - gone) * 30, width: mix(TW, CW, fly), height: mix(TH, CH, fly), borderRadius: mix(18, 28, fly), overflow: "hidden", zIndex: lift > 0 ? 9 : 5,
            background: C.surface, border: `${glow > 0.1 || hot ? 3 : 2}px ${glow > 0.1 && !hot ? "dashed" : "solid"} ${fly > 0.5 ? (active ? C.hero : C.line) : blue ? C.hero : lift > 0.4 ? C.ink : glow > 0.1 ? C.warn : C.line}`,
            boxShadow: `0 ${mix(10, 34, fly)}px ${mix(24, 60, fly)}px -22px ${active ? C.hero + "88" : C.shadow}`, opacity: Math.min(1, drop * 1.4) * gone, transform: `rotate(${rot * (1 - fly)}deg) scale(${scale * mix(1, 1.07, ranked * (1 - fly))})` }}>
            <div style={{ position: "absolute", inset: 0, background: blue ? C.hero : C.ink, opacity: (blue ? ranked : lift) * (1 - fly) }} />
            <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", padding: 12, textAlign: "center", fontFamily: theme.fonts.body, fontWeight: 700, fontSize: 18, lineHeight: 1.22, color: hot ? C.surface : C.ink, opacity: 1 - Math.min(1, fly * 2.2) }}>{soft(name)}</div>
            <div style={{ position: "absolute", left: 12, right: 12, bottom: 9, height: 6, borderRadius: 3, background: hot ? "rgba(255,255,255,0.3)" : C.bg, opacity: score * (1 - fly) }}><div style={{ width: `${(s / maxScore) * 100 * score}%`, height: "100%", borderRadius: 3, background: hot ? C.surface : C.hero }} /></div>
            <div style={{ position: "absolute", inset: 0, padding: 28, display: "flex", flexDirection: "column", opacity: Math.max(0, fly * 1.6 - 0.6) }}>
              <div style={{ width: 54, height: 54, borderRadius: 16, background: active ? C.hero : C.heroSoft, display: "grid", placeItems: "center", fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 28, color: active ? C.surface : C.hero }}>{k + 1}</div>
              <div style={{ marginTop: 20, fontFamily: theme.fonts.display, fontWeight: 800, fontSize: name.length > 16 ? 31 : 38, letterSpacing: "-0.02em", lineHeight: 1.05, color: C.ink }}>{soft(name)}</div>
              <div style={{ marginTop: 20, fontFamily: theme.fonts.mono, fontWeight: 700, fontSize: 16, letterSpacing: "0.08em", color: C.faint, opacity: info }}>WHEN</div>
              <div style={{ marginTop: 6, fontFamily: theme.fonts.body, fontWeight: 500, fontSize: 24, lineHeight: 1.3, color: C.ink, opacity: info, transform: `translateY(${mix(14, 0, info)}px)` }}>{data.fits[k].when.charAt(0).toUpperCase() + data.fits[k].when.slice(1)}</div>
              <div style={{ flex: 1 }} />
              <div style={{ fontFamily: theme.fonts.mono, fontWeight: 700, fontSize: 16, letterSpacing: "0.08em", color: C.faint, opacity: info }}>HOW</div>
              <div style={{ marginTop: 8, fontFamily: theme.fonts.mono, fontWeight: 700, fontSize: data.fits[k].call.length > 18 ? 16 : 23, color: C.surface, background: C.ink, borderRadius: 12, padding: "12px 14px", whiteSpace: "nowrap", overflow: "hidden", opacity: info, transform: `translateY(${mix(14, 0, info)}px)` }}>{data.fits[k].call}</div>
            </div>
          </div>
        );
      })}
      <Tags c={c} />
      <Sweep c={c} />
    </>
  );
};

// "used" on the one box Claude pulled out, "never used" under it for the four that fit and stayed in the pile
const Tags: React.FC<{ c: Ctx }> = ({ c }) => {
  if (c.f < sec(c, T.lift) || c.f > sec(c, T.tidy) + 10) return null;
  const a = sp(c, T.lift + 0.9, theme.spring.snappy), b = sp(c, T.buried + 0.5, theme.spring.snappy), o = out(c, T.tidy - 0.3, 0.25);
  const pill = (bg: string, col: string): React.CSSProperties => ({ fontFamily: theme.fonts.body, fontWeight: 700, fontSize: 26, color: col, background: bg, borderRadius: 22, padding: "8px 20px" });
  return (
    <>
      <div style={{ position: "absolute", left: 960 + TW * 1.05, top: TOP + 46, opacity: a * o, transform: `translateX(${mix(-16, 0, a)}px)`, zIndex: 10, ...pill(C.ink, C.surface) }}>1 skill used</div>
      <div style={{ position: "absolute", left: 0, width: 1920, top: 920, textAlign: "center", opacity: b * o, transform: `translateY(${mix(14, 0, b)}px)`, zIndex: 10 }}><span style={pill(C.warn, C.surface)}>{data.fits.length - 1} more that fit, never used</span></div>
    </>
  );
};

const Sweep: React.FC<{ c: Ctx }> = ({ c }) => {
  const a = T.sweep, b = T.sweep + 2.2;
  if (c.f < sec(c, a) || c.f > sec(c, b) + 8) return null;
  const x = tw(c, a, b, PAD - 60, PAD + W + 10, theme.ease.inOut), o = Math.min(tw(c, a, a + 0.25, 0, 1), tw(c, b - 0.15, b + 0.2, 1, 0));
  return <div style={{ position: "absolute", left: x, top: TOP - 22, width: 90, height: 5 * (TH + GAP) + 28, borderRadius: 45, background: `linear-gradient(90deg, transparent, ${C.hero}3D, transparent)`, opacity: o, zIndex: 6 }} />;
};

const Rows: React.FC<{ c: Ctx }> = ({ c }) => {
  if (c.f < sec(c, T.hub) || c.f > sec(c, T.chart) + 14) return null;
  const max = Math.max(...data.github.map((g) => g.stars)), RH = 122;
  return (
    <>
      {data.github.map((g, i) => {
        const at = T.row1 + i * T.rowStep, p = sp(c, at), bar = sp(c, at + 0.25, theme.spring.slow), o = out(c, T.chart - 0.25 + i * 0.04, 0.28);
        const active = c.f >= sec(c, at) && c.f < sec(c, at + T.rowStep);
        return (
          <div key={g.skill + g.repo} style={{ position: "absolute", left: PAD, top: TOP + i * (RH + 12), width: W, height: RH, borderRadius: 24, background: C.surface, border: `${active ? 3 : 2}px solid ${active ? C.hero : C.line}`, boxShadow: `0 18px 40px -26px ${active ? C.hero + "88" : C.shadow}`, display: "flex", alignItems: "center", padding: "0 28px", gap: 24,
            opacity: p * o, transform: `translateX(${mix(70, 0, p)}px) scale(${mix(0.97, 1, p)})` }}>
            <div style={{ width: 54, height: 54, borderRadius: 27, background: active ? C.hero : C.bg, display: "grid", placeItems: "center", fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 27, color: active ? C.surface : C.ink, flex: "0 0 auto" }}>{i + 1}</div>
            <div style={{ width: 400, flex: "0 0 auto" }}>
              <div style={{ fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 32, letterSpacing: "-0.02em", color: C.ink, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{g.skill}</div>
              <div style={{ fontFamily: theme.fonts.mono, fontWeight: 500, fontSize: 19, color: C.dim, marginTop: 2, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{g.repo} · {g.license}</div>
            </div>
            <div style={{ flex: 1, fontFamily: theme.fonts.body, fontWeight: 500, fontSize: 23, lineHeight: 1.28, color: C.ink, opacity: sp(c, at + 0.35) }}>{g.when}</div>
            <div style={{ width: 300, flex: "0 0 auto" }}>
              <div style={{ textAlign: "right", fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 34, letterSpacing: "-0.02em", color: C.ink, fontVariantNumeric: "tabular-nums" }}>{fmt(g.stars * bar)}<span style={{ color: C.star, fontSize: 27, marginLeft: 8 }}>★</span></div>
              <div style={{ marginTop: 6, height: 12, borderRadius: 6, background: C.bg, overflow: "hidden" }}><div style={{ width: `${(g.stars / max) * 100 * bar}%`, height: "100%", borderRadius: 6, background: C.hero, marginLeft: "auto" }} /></div>
            </div>
          </div>
        );
      })}
    </>
  );
};

const Chart: React.FC<{ c: Ctx }> = ({ c }) => {
  if (c.f < sec(c, T.chart) || c.f > sec(c, T.end) + 14) return null;
  const b = data.before, a = data.after, o = out(c, T.end - 0.3), n = data.fits.length;
  const x = (p: number, q: number) => (p / q).toFixed(1).replace(".0", "") + "×";
  const rows = [
    { label: "Fitting skills Claude shows you", bv: data.plain.used.length, av: n, bt: `${data.plain.used.length} of ${n}`, at: `${n} of ${n}`, big: `${n} of ${n}`, more: true },
    { label: "Steps", bv: b.steps, av: a.steps, bt: String(b.steps), at: String(a.steps), big: `${a.steps} step` },
    { label: "Seconds", bv: b.sec, av: a.sec, bt: String(Math.round(b.sec)), at: String(Math.round(a.sec)), big: x(b.sec, a.sec) + " faster" },
    { label: "Tokens", bv: b.tokens, av: a.tokens, bt: fmt(b.tokens), at: fmt(a.tokens), big: x(b.tokens, a.tokens) + " fewer" },
  ];
  const RH = 148, legend = sp(c, T.chart + 0.5);
  return (
    <>
      <div style={{ position: "absolute", left: PAD, top: 216, display: "flex", gap: 34, fontFamily: theme.fonts.body, fontWeight: 700, fontSize: 26, color: C.ink, opacity: legend * o }}>
        <span><span style={{ display: "inline-block", width: 22, height: 22, borderRadius: 6, background: C.warn, marginRight: 10, verticalAlign: -3 }} />Before, plain Claude</span>
        <span><span style={{ display: "inline-block", width: 22, height: 22, borderRadius: 6, background: C.hero, marginRight: 10, verticalAlign: -3 }} />After, with Straight Answer</span>
      </div>
      {rows.map((r, i) => {
        const at = T.bar1 + i * T.barStep, p = sp(c, at), g = sp(c, at + 0.25, theme.spring.slow), big = sp(c, at + 0.9, theme.spring.bouncy), m = Math.max(r.bv, r.av);
        const active = c.f >= sec(c, at) && c.f < sec(c, at + T.barStep);
        return (
          <div key={i} style={{ position: "absolute", left: PAD, top: TOP - 50 + i * (RH + 14), width: W, height: RH, borderRadius: 26, background: C.surface, border: `${active ? 3 : 2}px solid ${active ? C.hero : C.line}`, boxShadow: `0 18px 40px -26px ${C.shadow}`, display: "flex", alignItems: "center", padding: "0 34px", gap: 30, opacity: p * o, transform: `translateY(${mix(40, 0, p)}px) scale(${mix(0.97, 1, p)})` }}>
            <div style={{ width: 450, flex: "0 0 auto", fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 34, letterSpacing: "-0.02em", lineHeight: 1.08, color: C.ink }}>{r.label}</div>
            <div style={{ flex: 1 }}>
              {[{ v: r.bv, t: r.bt, col: C.warn }, { v: r.av, t: r.at, col: C.hero }].map((k, j) => (
                <div key={j} style={{ display: "flex", alignItems: "center", gap: 16, marginTop: j ? 12 : 0 }}>
                  <div style={{ flex: 1, height: 30, borderRadius: 15, background: C.bg, overflow: "hidden" }}><div style={{ width: `${Math.max(1.5, (k.v / m) * 100) * g}%`, height: "100%", borderRadius: 15, background: k.col }} /></div>
                  <div style={{ width: 150, fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 30, color: C.ink, fontVariantNumeric: "tabular-nums" }}>{k.t}</div>
                </div>
              ))}
            </div>
            <div style={{ width: 330, flex: "0 0 auto", textAlign: "right", fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 50, letterSpacing: "-0.03em", color: C.hero, opacity: big, transform: `scale(${mix(0.8, 1, big)})`, transformOrigin: "right center" }}>{r.big}</div>
          </div>
        );
      })}
    </>
  );
};

const End: React.FC<{ c: Ctx }> = ({ c }) => {
  if (c.f < sec(c, T.end)) return null;
  const p = sp(c, T.end + 0.9), q = sp(c, T.end + 1.5), u = sp(c, T.end + 2.1, theme.spring.bouncy), bob = Math.sin(c.f / 26) * 3;
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 24 }}>
      <div style={{ display: "grid", gridTemplateColumns: `repeat(${COLS}, 34px)`, gap: 10, marginBottom: 20 }}>
        {data.installed.map((name, i) => {
          const d = sp(c, T.end + 0.2 + i * 0.012, theme.spring.snappy), fit = fitNames.includes(name);
          return <div key={i} style={{ width: 34, height: 34, borderRadius: 9, background: fit ? C.hero : C.surface, border: `2px solid ${fit ? C.hero : C.line}`, opacity: d, transform: `scale(${mix(0.5, 1, d)})` }} />;
        })}
      </div>
      <div style={{ fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 124, letterSpacing: "-0.045em", lineHeight: 1, color: C.ink, opacity: p, transform: `translateY(${mix(40, 0, p) + bob}px) scale(${mix(0.94, 1, p)})` }}>{data.installed.length} skills. <span style={{ color: C.hero }}>Nothing buried.</span></div>
      <div style={{ fontFamily: theme.fonts.body, fontWeight: 600, fontSize: 40, color: C.dim, opacity: q, transform: `translateY(${mix(24, 0, q)}px)` }}>Straight Answer, a plugin for Claude Code</div>
      <div style={{ marginTop: 14, fontFamily: theme.fonts.mono, fontWeight: 700, fontSize: 32, color: C.surface, background: C.ink, borderRadius: 22, padding: "20px 34px", opacity: u, transform: `scale(${mix(0.9, 1, u)})` }}>/plugin marketplace add alibb007/straight-answer</div>
    </AbsoluteFill>
  );
};

export const Film: React.FC = () => {
  const f = useCurrentFrame(), { fps } = useVideoConfig(), c: Ctx = { f, fps };
  const n = data.installed.length, k = data.fits.length, g = data.github.length;
  const count = Math.round(interpolate(spring({ frame: f - sec(c, T.drop), fps, config: theme.spring.slow, durationInFrames: sec(c, 3.2) }), [0, 1], [0, n]));
  const cnt = sp(c, T.drop), cntOut = out(c, T.ask - 0.3);
  return (
    <AbsoluteFill>
      <BgMesh c={c} />
      <Headline c={c} from={0.2} to={T.ask - 0.3} text="You keep installing skills." />
      <div style={{ position: "absolute", left: PAD, top: 170, fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 96, letterSpacing: "-0.04em", color: C.hero, fontVariantNumeric: "tabular-nums", opacity: cnt * cntOut }}>{count}<span style={{ fontFamily: theme.fonts.body, fontWeight: 600, fontSize: 30, letterSpacing: 0, color: C.dim, marginLeft: 14 }}>installed</span></div>
      <Headline c={c} from={T.ask} to={T.lift - 0.3} text="Then you ask Claude to do something for you." />
      <Headline c={c} from={T.lift} to={T.tidy - 0.3} text="It pulls out *one* *skill.* Four more that fit stay *buried.*" col={C.warn} />
      <Headline c={c} from={T.tidy} to={T.score - 0.3} text={`Straight Answer reads *all* *${n}* for you.`} />
      <Headline c={c} from={T.score} to={T.cards - 0.3} text="It *scores* each one against your request." />
      <Headline c={c} from={T.cards} to={T.hub - 0.3} text={`*${k}* you already have, with *when* and *how* to use each.`} />
      <Headline c={c} from={T.hub} to={T.chart - 0.3} text={`The best one may not be installed yet. So it finds *${g}* *more* on GitHub.`} />
      <Headline c={c} from={T.chart} to={T.end - 0.3} text="Before and *after*" />
      <JobRow c={c} />
      <Tiles c={c} />
      <Rows c={c} />
      <Chart c={c} />
      <Note c={c} from={T.noteA} to={T.tidy - 0.4}>Plain Claude, same request, {data.plain.runs} runs: it loaded 1 of the {k} in {data.plain.one === 5 ? "five" : data.plain.one} runs and 2 in {data.plain.two === 1 ? "one" : data.plain.two}.</Note>
      <Note c={c} from={T.bar1 + 4.6} to={T.end - 0.4}>Steps, seconds and tokens: asking which skills to use and how, one run each side. Claude Opus.</Note>
      <End c={c} />
      <Finish c={c} />
    </AbsoluteFill>
  );
};
