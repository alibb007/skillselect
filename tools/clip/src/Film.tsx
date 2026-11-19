import React from "react";
import { AbsoluteFill, getInputProps, interpolate, random, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "./theme";
import data from "./data.json";

// Everything on screen comes from data.json, which tools/clip/make_data.py writes from the saved sessions.
// The one exception is the counter in scene 1: it is a picture of "more and more", not a measurement.
const C = theme.colors;
const FLAT = Boolean((getInputProps() as any).flat); // for the GIF: no moving grain, no drifting background
export const SECONDS = 70;
const NAME = data.name;
// the product name is always gold and heavy, so the eye learns it
const Nm: React.FC = () => <b style={{ color: C.gold, fontWeight: 800 }}>{NAME}</b>;

// when each beat starts, in seconds. Scenes with more to read get more time.
const T = {
  count: 0.3, burst: 3.3,
  ask: 5.6, type: 6.1,
  pick: 9.6, lift: 12.4, miss: 13.9, noteA: 15.1,
  tidy: 19.1, sweep: 19.9,
  score: 23.5, rank: 25.7,
  cards: 28.7,
  what: 35.6,
  hub: 39.8, row1: 40.8, rowStep: 1.6,
  chart: 49.6, bar1: 50.8, barStep: 2.5,
  end: 62.0,
};

const PAD = 96, W = 1920 - PAD * 2, TOP = 350;
const COLS = 10, GAP = 16, TW = (W - GAP * (COLS - 1)) / COLS, TH = 108;
const K = data.fits.length, CW = (W - 24 * (K - 1)) / K, CH = 560;
const PILE = 960, SHIFT = 250; // the pile moves left in scene 3, so the list of what was missed has room

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
const scores = data.scores as Record<string, number>;
const maxScore = Math.max(...Object.values(scores), 1);
const USED = data.plain.used[0];
const clock = (s: number) => (s >= 60 ? `${Math.floor(s / 60)} min ${Math.round(s % 60)} s` : `${Math.round(s)} s`);

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

// One headline at a time, centred, dark ink. Words wrapped in *stars* are the ones the eye should land on.
const Headline: React.FC<{ c: Ctx; from: number; to: number; text: string; col?: string; sub?: string; top?: number; size?: number }> = ({ c, from, to, text, col = C.hero, sub, top = 56, size = 66 }) => {
  if (c.f < sec(c, from) - 2 || c.f > sec(c, to) + 14) return null;
  const words = text.split(" ").map((w) => ({ w: w.replace(/\*/g, ""), hi: w.includes("*") }));
  const o = out(c, to), s = sp(c, from + 0.7);
  return (
    <div style={{ position: "absolute", left: PAD, top, width: W, opacity: o, transform: `translateY(${(1 - o) * -22}px)`, zIndex: 20 }}>
      <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", columnGap: size * 0.27, rowGap: 0, fontFamily: theme.fonts.display, fontWeight: 800, fontSize: size, letterSpacing: "-0.035em", lineHeight: 1.1, color: C.ink }}>
        {words.map((x, i) => {
          const p = sp(c, from + i * 0.07, theme.spring.snappy);
          const isName = x.w.replace(/[^A-Za-z]/g, "") === NAME;
          return <span key={i} style={{ display: "inline-block", opacity: p, transform: `translateY(${mix(30, 0, p)}px) scale(${mix(0.96, 1, p) * (isName ? 1.05 : 1)})`, color: isName ? C.gold : x.hi ? col : C.ink, WebkitTextStroke: isName ? `1.2px ${C.gold}` : undefined }}>{x.w}</span>;
        })}
      </div>
      {sub ? <div style={{ marginTop: 6, textAlign: "center", fontFamily: theme.fonts.display, fontWeight: 800, fontSize: size * 0.62, letterSpacing: "-0.02em", color: col, opacity: s, transform: `scale(${mix(0.86, 1, s)})` }}>{sub}</div> : null}
    </div>
  );
};

const Note: React.FC<{ c: Ctx; from: number; to: number; children: React.ReactNode }> = ({ c, from, to, children }) => {
  if (c.f < sec(c, from) || c.f > sec(c, to) + 12) return null;
  const p = sp(c, from), o = out(c, to);
  return <div style={{ position: "absolute", left: PAD, top: 1008, width: W, textAlign: "center", fontFamily: theme.fonts.body, fontWeight: 600, fontSize: 25, color: C.note, opacity: p * o, transform: `translateY(${mix(12, 0, p)}px)`, zIndex: 20 }}>{children}</div>;
};

// Scene 1: a counter that runs away, then bursts into the boxes.
const Counter: React.FC<{ c: Ctx }> = ({ c }) => {
  if (c.f > sec(c, T.burst) + 16) return null;
  const p = interpolate(c.f, [sec(c, T.count), sec(c, T.burst)], [0, 1], clampOpt), n = Math.round(Math.pow(3, p * 7.2));
  const inn = sp(c, T.count, theme.spring.bouncy), pop = tw(c, T.burst, T.burst + 0.3, 0, 1), shake = FLAT ? 0 : Math.sin(c.f * 1.9) * 7 * p * p;
  const ring = tw(c, T.burst, T.burst + 0.7, 0, 1);
  return (
    <>
      <div style={{ position: "absolute", left: 0, width: 1920, top: 330, textAlign: "center", opacity: inn * (1 - pop), transform: `translate(${shake}px, ${-shake * 0.6}px) scale(${mix(0.7, 1.55, p) * mix(1, 1.9, pop)})` }}>
        <div style={{ fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 230, letterSpacing: "-0.05em", lineHeight: 1, color: p > 0.72 ? C.warn : C.hero, fontVariantNumeric: "tabular-nums" }}>{fmt(n)}</div>
        <div style={{ fontFamily: theme.fonts.body, fontWeight: 700, fontSize: 34, color: C.ink, marginTop: 4 }}>skills</div>
      </div>
      {ring > 0 && ring < 1 ? <div style={{ position: "absolute", left: 960 - 700 * ring, top: 560 - 700 * ring, width: 1400 * ring, height: 1400 * ring, borderRadius: "50%", border: `${mix(26, 2, ring)}px solid ${C.warn}`, opacity: 1 - ring }} /> : null}
    </>
  );
};

// What the person typed. It stays on screen from the moment they ask until the end title.
const JobRow: React.FC<{ c: Ctx }> = ({ c }) => {
  if (c.f < sec(c, T.ask)) return null;
  const p = sp(c, T.ask + 0.2), hide = Math.min(1, out(c, T.what - 0.3) + tw(c, T.hub, T.hub + 0.4, 0, 1)), o = out(c, T.end - 0.4);
  const n = Math.round(interpolate(c.f, [sec(c, T.type), sec(c, T.type + 0.9)], [0, data.ask.length], clampOpt)), blink = Math.floor(c.f / 8) % 2 === 0;
  const withPlugin = sp(c, T.tidy, theme.spring.bouncy);
  return (
    <div style={{ position: "absolute", left: 0, width: 1920, top: 232, height: 76, display: "flex", alignItems: "center", justifyContent: "center", gap: 18, opacity: p * o * hide, transform: `translateY(${mix(-20, 0, p)}px)`, zIndex: 18 }}>
      <div style={{ height: 76, padding: "0 30px", borderRadius: 38, background: C.surface, border: `3px solid ${C.ink}`, boxShadow: `0 14px 34px -18px ${C.shadow}`, display: "flex", alignItems: "center", gap: 16 }}>
        <span style={{ width: 50, height: 50, borderRadius: 15, border: `3px solid ${C.hero}`, background: C.heroSoft, display: "grid", placeItems: "center", marginLeft: -14 }}><svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke={C.hero} strokeWidth="2.8" strokeLinecap="round"><circle cx="11" cy="11" r="6.5" /><path d="M16 16l5 5" /></svg></span>
        <span style={{ fontFamily: theme.fonts.body, fontWeight: 700, fontSize: 32, color: C.ink, minWidth: 590 }}>{data.ask.slice(0, n)}{n < data.ask.length || (blink && c.f < sec(c, T.pick)) ? <span style={{ display: "inline-block", width: 3, height: 32, background: C.ink, marginLeft: 3, verticalAlign: -5 }} /> : null}</span>
      </div>
      <div style={{ height: 60, padding: "0 24px", borderRadius: 30, background: C.ink, display: withPlugin > 0.01 ? "flex" : "none", alignItems: "center", gap: 8, fontFamily: theme.fonts.body, fontWeight: 700, fontSize: 25, color: C.surface, opacity: withPlugin, transform: `scale(${mix(0.8, 1, withPlugin)})` }}>with <Nm /></div>
    </div>
  );
};

const tilePos = (i: number) => ({ x: PAD + (i % COLS) * (TW + GAP), y: TOP + Math.floor(i / COLS) * (TH + GAP) });
// where each box ends up in the pile: fixed per box, so every render is the same
const messPos = (i: number) => ({ x: PILE - TW / 2 + (random("x" + i) - 0.5) * 980, y: 650 + (random("y" + i) - 0.5) * 330, r: (random("r" + i) - 0.5) * 58 });
// the boxes Claude's eye stops on before it settles on one
const usedIdx = data.installed.indexOf(USED);
const HOPS = [7, 31, 18, 44, 12, 26].map((s) => (s === usedIdx ? s + 1 : s)).concat([usedIdx]);

const Tiles: React.FC<{ c: Ctx }> = ({ c }) => (
  <>
    {data.installed.map((name, i) => {
      const g = tilePos(i), m = messPos(i), col = i % COLS;
      const k = fitNames.indexOf(name), fit = k >= 0, isUsed = name === USED;
      const burst = sp(c, T.burst + random("b" + i) * 0.5, theme.spring.bouncy);
      if (burst <= 0.001) return null;
      const back = sp(c, T.tidy + (i % 10) * 0.03 + Math.floor(i / 10) * 0.05, theme.spring.snappy);
      const mess = 1 - back;
      const rummage = FLAT ? 0 : mess * Math.sin(c.f / 7 + i) * 5 * (c.f > sec(c, T.pick) && c.f < sec(c, T.lift) ? 1 : 0.2);
      const lift = isUsed ? sp(c, T.lift + 0.1, theme.spring.bouncy) * (1 - back) : 0;
      const glow = fit && !isUsed ? Math.min(tw(c, T.miss, T.miss + 0.5, 0, 1), tw(c, T.tidy - 0.2, T.tidy, 1, 0)) : 0;
      const score = sp(c, T.score + 0.3 + col * 0.08 + Math.floor(i / COLS) * 0.05, theme.spring.slow);
      const s = scores[name] || 0;
      const ranked = sp(c, T.rank + (fit ? k * 0.16 : 0), fit ? theme.spring.bouncy : theme.spring.smooth);
      const shift = sp(c, T.lift - 0.2) * mess * SHIFT;
      let x = mix(960 - TW / 2, mix(g.x, m.x, mess), burst) + rummage - shift, y = mix(560 - TH / 2, mix(g.y, m.y, mess), burst), rot = m.r * mess * burst + (1 - burst) * (random("q" + i) - 0.5) * 240, scale = mix(0.15, 1, burst), z = fit ? 3 : 1;
      if (lift > 0) { x = mix(x, PILE - SHIFT - TW / 2, lift); y = mix(y, TOP + 16, lift); rot *= 1 - lift; scale *= mix(1, 1.8, lift); z = 9; }
      if (!fit) {
        const gone = out(c, T.cards - 0.25 + (i % 7) * 0.02, 0.3);
        if (gone <= 0) return null;
        return (
          <div key={name} style={{ position: "absolute", left: x, top: y + (1 - gone) * 18, width: TW, height: TH, borderRadius: 18, background: C.surface, border: `2px solid ${C.line}`, boxShadow: mess > 0.05 ? `0 10px 24px -14px ${C.shadow}` : "none", overflow: "hidden", zIndex: z,
            opacity: Math.min(1, burst * 1.6) * mix(1, 0.3, ranked) * gone, transform: `rotate(${rot}deg) scale(${scale * mix(1, 0.96, ranked)})` }}>
            <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", padding: 12, textAlign: "center", fontFamily: theme.fonts.body, fontWeight: 600, fontSize: 18, lineHeight: 1.22, color: C.ink }}>{soft(name)}</div>
            <div style={{ position: "absolute", left: 12, right: 12, bottom: 9, height: 6, borderRadius: 3, background: C.bg, opacity: score }}><div style={{ width: `${(s / maxScore) * 100 * score}%`, height: "100%", borderRadius: 3, background: C.faint }} /></div>
          </div>
        );
      }
      // a skill the plugin kept
      const fly = sp(c, T.cards + k * 0.06), gone = out(c, T.what - 0.4 + k * 0.05, 0.3);
      if (gone <= 0) return null;
      const tx = PAD + k * (CW + 24), ty = TOP, info = sp(c, T.cards + 0.9), active = fly > 0.5;
      const hot = ranked > 0.4 || lift > 0.4, blue = ranked > 0.4, f0 = data.fits[k];
      const label: React.CSSProperties = { fontFamily: theme.fonts.mono, fontWeight: 700, fontSize: 28, letterSpacing: "0.08em", color: C.hero, opacity: info };
      return (
        <div key={name} style={{ position: "absolute", left: mix(x, tx, fly), top: mix(y, ty, fly) - (1 - gone) * 30, width: mix(TW, CW, fly), height: mix(TH, CH, fly), borderRadius: mix(18, 28, fly), overflow: "hidden", zIndex: lift > 0 ? 9 : 5,
          background: C.surface, border: `${glow > 0.1 || hot ? 4 : 2}px ${glow > 0.1 && !hot ? "dashed" : "solid"} ${fly > 0.5 ? (active ? C.hero : C.line) : blue ? C.hero : lift > 0.4 ? C.ink : glow > 0.1 ? C.warn : C.line}`,
          boxShadow: `0 ${mix(10, 34, fly)}px ${mix(24, 60, fly)}px -22px ${active ? C.hero + "88" : C.shadow}`, opacity: Math.min(1, burst * 1.6) * gone, transform: `rotate(${rot * (1 - fly)}deg) scale(${scale * mix(1, 1.08, ranked * (1 - fly))})` }}>
          <div style={{ position: "absolute", inset: 0, background: blue ? C.hero : C.ink, opacity: (blue ? ranked : lift) * (1 - fly) }} />
          <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", padding: 12, textAlign: "center", fontFamily: theme.fonts.body, fontWeight: 700, fontSize: 18, lineHeight: 1.22, color: hot ? C.surface : C.ink, opacity: 1 - Math.min(1, fly * 2.2) }}>{soft(name)}</div>
          <div style={{ position: "absolute", left: 12, right: 12, bottom: 9, height: 6, borderRadius: 3, background: hot ? "rgba(255,255,255,0.3)" : C.bg, opacity: score * (1 - fly) }}><div style={{ width: `${(s / maxScore) * 100 * score}%`, height: "100%", borderRadius: 3, background: hot ? C.surface : C.hero }} /></div>
          <div style={{ position: "absolute", inset: 0, padding: 28, display: "flex", flexDirection: "column", opacity: Math.max(0, fly * 1.6 - 0.6) }}>
            <div style={{ width: 54, height: 54, borderRadius: 16, background: active ? C.hero : C.heroSoft, display: "grid", placeItems: "center", fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 28, color: active ? C.surface : C.hero }}>{k + 1}</div>
            <div style={{ marginTop: 18, fontFamily: theme.fonts.display, fontWeight: 800, fontSize: name.length > 16 ? 33 : 40, letterSpacing: "-0.02em", lineHeight: 1.05, color: C.ink }}>{soft(name)}</div>
            <div style={{ marginTop: 26, ...label }}>WHEN</div>
            <div style={{ marginTop: 8, fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 37, letterSpacing: "-0.02em", lineHeight: 1.12, color: C.ink, opacity: info, transform: `translateY(${mix(14, 0, info)}px)` }}>{f0.short}</div>
            <div style={{ flex: 1 }} />
            {f0.needs ? <div style={{ marginBottom: 12, fontFamily: theme.fonts.body, fontWeight: 600, fontSize: 21, color: C.ink, opacity: info }}><span style={{ ...label, fontSize: 20, opacity: 1, marginRight: 10 }}>NEEDS</span>{f0.needs}</div> : null}
            <div style={{ ...label, fontSize: 22 }}>HOW</div>
            <div style={{ marginTop: 8, fontFamily: theme.fonts.mono, fontWeight: 700, fontSize: 20, lineHeight: 1.3, color: C.surface, background: C.ink, borderRadius: 12, padding: "12px 14px", opacity: info, transform: `translateY(${mix(14, 0, info)}px)` }}>{f0.how}</div>
          </div>
        </div>
      );
    })}
    <Picker c={c} />
    <Missed c={c} />
    <Sweep c={c} />
  </>
);

// Scene 3: a ring hops from box to box, the way Claude looks for one skill, and stops on the one it loads.
const Picker: React.FC<{ c: Ctx }> = ({ c }) => {
  if (c.f < sec(c, T.pick) || c.f > sec(c, T.lift) + 14) return null;
  const step = (T.lift - T.pick - 0.3) / HOPS.length, t = (c.f / c.fps - T.pick) / step, a = Math.max(0, Math.min(HOPS.length - 1, Math.floor(t))), b = Math.min(HOPS.length - 1, a + 1);
  const e = interpolate(t - Math.floor(t), [0.45, 1], [0, 1], { ...clampOpt, easing: theme.ease.inOut });
  const pa = messPos(HOPS[a]), pb = messPos(HOPS[b]), x = mix(pa.x, pb.x, t >= HOPS.length - 1 ? 0 : e), y = mix(pa.y, pb.y, t >= HOPS.length - 1 ? 0 : e);
  const inn = sp(c, T.pick, theme.spring.bouncy), o = out(c, T.lift + 0.1, 0.25), land = t >= HOPS.length - 1 ? 1 : 0;
  return <div style={{ position: "absolute", left: x - 22, top: y - 22, width: TW + 44, height: TH + 44, borderRadius: 34, border: `7px solid ${land ? C.ink : C.warn}`, boxShadow: `0 0 0 8px ${C.warn}22`, opacity: inn * o, transform: `scale(${mix(1.5, 1, inn)})`, zIndex: 12 }} />;
};

// Scene 3: what Claude used, and the skills that fit and were never opened.
const Missed: React.FC<{ c: Ctx }> = ({ c }) => {
  if (c.f < sec(c, T.lift) || c.f > sec(c, T.tidy) + 10) return null;
  const o = out(c, T.tidy - 0.3, 0.25), rows = [USED, ...fitNames.filter((n) => n !== USED)];
  return (
    <div style={{ position: "absolute", left: 1300, top: 380, width: 524, opacity: o, zIndex: 12 }}>
      {rows.map((n, i) => {
        const p = sp(c, i === 0 ? T.lift + 0.8 : T.miss + 0.5 + i * 0.45, theme.spring.snappy), ok = i === 0;
        return (
          <div key={n} style={{ display: "flex", alignItems: "center", gap: 16, height: 86, marginBottom: 14, padding: "0 20px", borderRadius: 22, background: C.surface, border: `3px solid ${ok ? C.ink : C.warn}`, boxShadow: `0 14px 30px -20px ${C.shadow}`, opacity: p, transform: `translateX(${mix(40, 0, p)}px)` }}>
            <div style={{ width: 46, height: 46, borderRadius: 23, background: ok ? C.ink : C.warn, color: C.surface, display: "grid", placeItems: "center", fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 28, flex: "0 0 auto" }}>{ok ? "✓" : "✕"}</div>
            <div style={{ minWidth: 0 }}>
              <div style={{ fontFamily: theme.fonts.display, fontWeight: 800, fontSize: n.length > 18 ? 25 : 29, letterSpacing: "-0.02em", color: C.ink, whiteSpace: "nowrap" }}>{n}</div>
              <div style={{ fontFamily: theme.fonts.body, fontWeight: 600, fontSize: 21, color: ok ? C.note : C.warn }}>{ok ? "Claude used this one" : "fits, never opened"}</div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

// Scene 3, second line: your sentence, with the two numbers big and coloured.
const Could: React.FC<{ c: Ctx }> = ({ c }) => {
  const from = T.miss, to = T.tidy - 0.3;
  if (c.f < sec(c, from) - 2 || c.f > sec(c, to) + 14) return null;
  const o = out(c, to), a = sp(c, from, theme.spring.snappy), n1 = sp(c, from + 0.5, theme.spring.bouncy), n2 = sp(c, from + 1.7, theme.spring.bouncy), b = sp(c, from + 1.2, theme.spring.snappy);
  const pulse = 1 + Math.sin(c.f / 6) * 0.03, num: React.CSSProperties = { display: "inline-block", fontSize: 128, lineHeight: 0.8, margin: "0 16px", verticalAlign: -14 };
  return (
    <div style={{ position: "absolute", left: PAD, top: 62, width: W, textAlign: "center", fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 66, letterSpacing: "-0.035em", lineHeight: 1.1, color: C.ink, opacity: o, zIndex: 20 }}>
      <span style={{ opacity: a }}>You could have used</span>
      <span style={{ ...num, color: C.hero, opacity: n1, transform: `scale(${mix(0.3, 1, n1) * pulse})` }}>{K}</span>
      <span style={{ opacity: a }}>skills,</span>{" "}
      <span style={{ opacity: b }}>but Claude used</span>
      <span style={{ ...num, color: C.warn, opacity: n2, transform: `translateY(${mix(-120, 0, n2)}px) scale(${mix(1.6, 1, n2)})` }}>{data.plain.used.length}</span>
    </div>
  );
};

const Sweep: React.FC<{ c: Ctx }> = ({ c }) => {
  const a = T.sweep, b = T.sweep + 2.4;
  if (c.f < sec(c, a) || c.f > sec(c, b) + 8) return null;
  const x = tw(c, a, b, PAD - 60, PAD + W + 10, theme.ease.inOut), o = Math.min(tw(c, a, a + 0.25, 0, 1), tw(c, b - 0.15, b + 0.2, 1, 0));
  return <div style={{ position: "absolute", left: x, top: TOP - 22, width: 90, height: 5 * (TH + GAP) + 28, borderRadius: 45, background: `linear-gradient(90deg, transparent, ${C.hero}3D, transparent)`, opacity: o, zIndex: 6 }} />;
};

// Scene 7 opens on the question alone.
const Question: React.FC<{ c: Ctx }> = ({ c }) => {
  if (c.f < sec(c, T.what) - 2 || c.f > sec(c, T.hub) + 14) return null;
  const q = sp(c, T.what, theme.spring.bouncy), o = out(c, T.hub - 0.35), words = "What if the best skill isn't installed yet?".split(" ");
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", opacity: o, zIndex: 20 }}>
      <div style={{ position: "absolute", fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 900, lineHeight: 1, color: C.warn, opacity: 0.13 * q, transform: `scale(${mix(0.6, 1, q)}) rotate(${mix(-14, 8, q)}deg)` }}>?</div>
      <div style={{ width: 1500, display: "flex", flexWrap: "wrap", justifyContent: "center", columnGap: 30, fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 118, letterSpacing: "-0.04em", lineHeight: 1.06, color: C.ink }}>
        {words.map((w, i) => { const p = sp(c, T.what + 0.15 + i * 0.09, theme.spring.snappy); return <span key={i} style={{ display: "inline-block", opacity: p, transform: `translateY(${mix(40, 0, p)}px)`, color: w === "best" || w === "installed" ? C.warn : C.ink }}>{w}</span>; })}
      </div>
    </AbsoluteFill>
  );
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
          <div key={g.skill + g.repo} style={{ position: "absolute", left: PAD, top: 332 + i * (RH + 12), width: W, height: RH, borderRadius: 24, background: C.surface, border: `${active ? 4 : 2}px solid ${active ? C.hero : C.line}`, boxShadow: `0 18px 40px -26px ${active ? C.hero + "88" : C.shadow}`, display: "flex", alignItems: "center", padding: "0 28px", gap: 24,
            opacity: p * o, transform: `translateX(${mix(70, 0, p)}px) scale(${mix(0.97, 1, p)})` }}>
            <div style={{ width: 54, height: 54, borderRadius: 27, background: active ? C.hero : C.bg, display: "grid", placeItems: "center", fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 27, color: active ? C.surface : C.ink, flex: "0 0 auto" }}>{i + 1}</div>
            <div style={{ width: 420, flex: "0 0 auto" }}>
              <div style={{ fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 32, letterSpacing: "-0.02em", color: C.ink, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{g.skill}</div>
              <div style={{ fontFamily: theme.fonts.mono, fontWeight: 500, fontSize: 19, color: C.note, marginTop: 2, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{g.repo} · {g.license}</div>
            </div>
            <div style={{ flex: 1, fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 31, letterSpacing: "-0.02em", lineHeight: 1.15, color: C.ink, opacity: sp(c, at + 0.3) }}><span style={{ fontFamily: theme.fonts.mono, fontWeight: 700, fontSize: 23, letterSpacing: "0.08em", color: C.hero, marginRight: 14 }}>WHEN</span>{g.short}</div>
            <div style={{ width: 250, flex: "0 0 auto" }}>
              <div style={{ textAlign: "right", fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 34, letterSpacing: "-0.02em", color: C.ink, fontVariantNumeric: "tabular-nums" }}>{fmt(g.stars * sp(c, at + 0.2, theme.spring.smooth))}<span style={{ color: C.star, fontSize: 27, marginLeft: 8 }}>★</span></div>
              <div style={{ marginTop: 6, height: 12, borderRadius: 6, background: C.bg, overflow: "hidden" }}><div style={{ width: `${Math.max(2, (g.stars / max) * 100) * bar}%`, height: "100%", borderRadius: 6, background: C.hero, marginLeft: "auto" }} /></div>
            </div>
          </div>
        );
      })}
    </>
  );
};

const Chart: React.FC<{ c: Ctx }> = ({ c }) => {
  if (c.f < sec(c, T.chart) || c.f > sec(c, T.end) + 14) return null;
  const b = data.before, a = data.after, o = out(c, T.end - 0.3), used = data.plain.used.length;
  const cut = (p: number, q: number) => `−${Math.round((1 - q / p) * 100)}%`;
  const rows = [
    { label: "Token Usage", bv: b.tokens, av: a.tokens, bt: fmt(b.tokens), at: fmt(a.tokens), big: cut(b.tokens, a.tokens), sub: "fewer tokens" },
    { label: "Time to get the answer", bv: b.sec, av: a.sec, bt: clock(b.sec), at: clock(a.sec), big: cut(b.sec, a.sec), sub: "less time" },
    { label: "Steps to find your skills", bv: b.steps, av: a.steps, bt: String(b.steps), at: String(a.steps), big: cut(b.steps, a.steps), sub: "fewer steps" },
    { label: "Useful skills found", bv: used, av: K, bt: `${used} of ${K}`, at: `${K} of ${K}`, big: `${Math.round(K / used)}×`, sub: "more" },
  ];
  const RH = 150;
  return (
    <>
      {rows.map((r, i) => {
        const at = T.bar1 + i * T.barStep, p = sp(c, at), g = sp(c, at + 0.25, theme.spring.slow), big = sp(c, at + 0.9, theme.spring.bouncy), m = Math.max(r.bv, r.av);
        const active = c.f >= sec(c, at) && c.f < sec(c, at + T.barStep);
        return (
          <div key={i} style={{ position: "absolute", left: PAD, top: 330 + i * (RH + 14), width: W, height: RH, borderRadius: 26, background: C.surface, border: `${active ? 4 : 2}px solid ${active ? C.hero : C.line}`, boxShadow: `0 18px 40px -26px ${C.shadow}`, display: "flex", alignItems: "center", padding: "0 34px", gap: 28, opacity: p * o, transform: `translateY(${mix(40, 0, p)}px) scale(${mix(0.97, 1, p)})` }}>
            <div style={{ width: 380, flex: "0 0 auto", fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 36, letterSpacing: "-0.02em", lineHeight: 1.08, color: C.ink }}>{r.label}</div>
            <div style={{ flex: 1 }}>
              {[{ v: r.bv, t: r.bt, col: C.warn, who: "Without" }, { v: r.av, t: r.at, col: C.hero, who: "With" }].map((k, j) => (
                <div key={j} style={{ display: "flex", alignItems: "center", gap: 16, marginTop: j ? 12 : 0 }}>
                  <div style={{ width: 232, flex: "0 0 auto", fontFamily: theme.fonts.body, fontWeight: 700, fontSize: 23, color: C.ink }}>{k.who} <Nm /></div>
                  <div style={{ flex: 1, height: 30, borderRadius: 15, background: C.bg, overflow: "hidden" }}><div style={{ width: `${Math.max(1.5, (k.v / m) * 100) * g}%`, height: "100%", borderRadius: 15, background: k.col }} /></div>
                  <div style={{ width: 190, textAlign: "right", fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 32, color: k.col, fontVariantNumeric: "tabular-nums", whiteSpace: "nowrap" }}>{k.t}</div>
                </div>
              ))}
            </div>
            <div style={{ width: 250, flex: "0 0 auto", textAlign: "right", opacity: big, transform: `scale(${mix(0.6, 1, big)})`, transformOrigin: "right center" }}>
              <div style={{ fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 84, letterSpacing: "-0.04em", lineHeight: 0.95, color: C.good }}>{r.big}</div>
              <div style={{ fontFamily: theme.fonts.body, fontWeight: 700, fontSize: 23, color: C.ink }}>{r.sub}</div>
            </div>
          </div>
        );
      })}
    </>
  );
};

const endPos = (i: number) => ({ x: 960 - 78 + (random("ex" + i) - 0.5) * 1560, y: 880 + (random("ey" + i) - 0.5) * 230, r: (random("er" + i) - 0.5) * 50 });
const End: React.FC<{ c: Ctx }> = ({ c }) => {
  if (c.f < sec(c, T.end)) return null;
  const p = sp(c, T.end + 1.5), q = sp(c, T.end + 2.4), u = sp(c, T.end + 3.0, theme.spring.bouncy), GW = 250;
  return (
    <AbsoluteFill>
      {data.installed.map((name, i) => {
        if (fitNames.includes(name)) return null;
        const m = endPos(i), d = sp(c, T.end + 0.05 + i * 0.012, theme.spring.snappy);
        return <div key={name} style={{ position: "absolute", left: m.x, top: m.y, width: 156, height: 84, borderRadius: 16, background: C.surface, border: `2px solid ${C.line}`, display: "grid", placeItems: "center", textAlign: "center", padding: 8, fontFamily: theme.fonts.body, fontWeight: 600, fontSize: 15, lineHeight: 1.2, color: C.faint, opacity: d * 0.7, transform: `rotate(${m.r}deg) scale(${mix(0.5, 1, d)})` }}>{soft(name)}</div>;
      })}
      {data.fits.map((f, k) => {
        const m = endPos(data.installed.indexOf(f.name)), rise = sp(c, T.end + 0.7 + k * 0.2, theme.spring.bouncy), float = FLAT ? 0 : Math.sin(c.f / 18 + k * 1.7) * 7;
        const tx = 960 - (K * GW - 30) / 2 + k * GW, ty = 150;
        return <div key={f.name} style={{ position: "absolute", left: mix(m.x, tx, rise), top: mix(m.y, ty, rise) + float * rise, width: mix(156, GW - 30, rise), height: mix(84, 112, rise), borderRadius: 20, background: C.hero, border: `5px solid ${C.gold}`, boxShadow: `0 26px 54px -18px ${C.hero}AA`, display: "grid", placeItems: "center", textAlign: "center", padding: 8, fontFamily: theme.fonts.display, fontWeight: 800, fontSize: mix(15, 23, rise), lineHeight: 1.12, color: C.surface, transform: `rotate(${m.r * (1 - rise)}deg)`, zIndex: 5 }}>{soft(f.name)}</div>;
      })}
      <div style={{ position: "absolute", left: 0, width: 1920, top: 330, textAlign: "center", fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 112, letterSpacing: "-0.045em", lineHeight: 1.02, color: C.ink, opacity: p, transform: `translateY(${mix(40, 0, p)}px) scale(${mix(0.94, 1, p)})` }}>Don't let your <span style={{ color: C.hero }}>best skill</span> sit unused.</div>
      <div style={{ position: "absolute", left: 0, width: 1920, top: 478, textAlign: "center", fontFamily: theme.fonts.body, fontWeight: 700, fontSize: 44, color: C.ink, opacity: q, transform: `translateY(${mix(24, 0, q)}px)` }}><span style={{ fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 56, color: C.gold, WebkitTextStroke: `1px ${C.gold}` }}>{NAME}</span>, a plugin for Claude Code</div>
      <div style={{ position: "absolute", left: 0, width: 1920, top: 590, display: "flex", justifyContent: "center", opacity: u, transform: `scale(${mix(0.9, 1, u)})` }}><div style={{ fontFamily: theme.fonts.mono, fontWeight: 700, fontSize: 30, color: C.surface, background: C.ink, borderRadius: 22, padding: "20px 34px" }}>/plugin install {data.slug} --marketplace alibb007/{data.slug}</div></div>
    </AbsoluteFill>
  );
};

export const Film: React.FC = () => {
  const f = useCurrentFrame(), { fps } = useVideoConfig(), c: Ctx = { f, fps };
  const g = data.github.length, pl = data.plain;
  return (
    <AbsoluteFill>
      <BgMesh c={c} />
      <Headline c={c} from={0.2} to={T.ask - 0.3} text="You keep *installing* skills." top={150} size={84} />
      <Counter c={c} />
      <Headline c={c} from={T.ask} to={T.pick - 0.3} text="Then you ask Claude to *build* something." />
      <Headline c={c} from={T.pick} to={T.miss - 0.3} text="Claude picks *one* skill and starts building." col={C.warn} />
      <Could c={c} />
      <Headline c={c} from={T.tidy} to={T.score - 0.3} text={`*${NAME}* reads *every* skill you have.`} />
      <Headline c={c} from={T.score} to={T.cards - 0.3} text="It *scores* each one against your request." />
      <Headline c={c} from={T.cards} to={T.what - 0.4} text={`${NAME} found the *${K}* most useful skills you *already* *have!*`} sub="No more guessing!" />
      <Question c={c} />
      <Headline c={c} from={T.hub} to={T.chart - 0.3} text={`${NAME} searches *GitHub* and brings back *${g}* that fit.`} />
      <Headline c={c} from={T.chart} to={T.end - 0.3} text={`Difference *with* and without ${NAME}`} />
      <JobRow c={c} />
      <Tiles c={c} />
      <Rows c={c} />
      <Chart c={c} />
      <Note c={c} from={T.noteA} to={T.tidy - 0.4}>Plain Claude, same request, {pl.runs} runs: it loaded 1 of these {K} skills in {pl.one} runs and 2 in {pl.more}.</Note>
      <Note c={c} from={T.rank + 0.6} to={T.cards - 0.4}>{data.passed} of {data.installed.length} passed the match rule. <Nm /> kept the {K} whose description does the job.</Note>
      <Note c={c} from={T.row1 + 1} to={T.chart - 0.4}>{data.gh.repos} repositories searched, {data.gh.files} skill files read, {data.gh.passed} matched, {g} kept. Nothing is installed for you.</Note>
      <Note c={c} from={T.bar1 + 5} to={T.end - 0.4}>Tokens, time, steps: Claude answering which skills to use, with <Nm /> (middle of 3 runs) and without (1 run). Claude Opus.</Note>
      <End c={c} />
      <Finish c={c} />
    </AbsoluteFill>
  );
};
