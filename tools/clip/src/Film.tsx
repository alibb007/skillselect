import React from "react";
import { AbsoluteFill, getInputProps, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "./theme";
import data from "./data.json";

// Everything on screen comes from data.json, which tools/clip/make_data.py writes from the saved session.
const C = theme.colors;
const FLAT = Boolean((getInputProps() as any).flat);
export const SECONDS = 48;

// scene starts, in seconds
const T = { grid: 0.6, job: 6.0, type: 6.5, scan: 8.8, fitTitle: 11.2, cards: 14.0, hub: 21.0, rows: 21.9, pick: 30.5, cmd: 31.9, nums: 38.5, end: 44.5 };

const PAD = 96, W = 1920 - PAD * 2, TOP = 316;
const COLS = 10, GAP = 16, TW = (W - GAP * (COLS - 1)) / COLS, TH = 118;
const CW = (W - 24 * 4) / 5, CH = 380;

type Ctx = { f: number; fps: number };
const sec = (c: Ctx, s: number) => Math.round(s * c.fps);
const sp = (c: Ctx, at: number, cfg: any = theme.spring.smooth) => spring({ frame: c.f - sec(c, at), fps: c.fps, config: cfg });
const clampOpt = { extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const };
const tw = (c: Ctx, a: number, b: number, from: number, to: number, ease = theme.ease.out) => interpolate(c.f, [sec(c, a), sec(c, b)], [from, to], { ...clampOpt, easing: ease });
const out = (c: Ctx, at: number, dur = 0.32) => tw(c, at, at + dur, 1, 0, theme.ease.in);
const mix = (a: number, b: number, p: number) => a + (b - a) * p;
const fmt = (n: number) => Math.round(n).toLocaleString("en-US");
const soft = (s: string) => s.replace(/-/g, "-​");

const BgMesh: React.FC<{ c: Ctx }> = ({ c }) => {
  const d1 = FLAT ? 0 : Math.sin(c.f / 70) * 60, d2 = FLAT ? 0 : Math.cos(c.f / 90) * 50;
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <div style={{ position: "absolute", width: 1300, height: 1300, borderRadius: "50%", top: -620, left: -380 + d1, filter: "blur(60px)", background: `radial-gradient(circle, ${C.hero}1F, transparent 62%)` }} />
      <div style={{ position: "absolute", width: 1100, height: 1100, borderRadius: "50%", bottom: -560, right: -320 - d2, filter: "blur(70px)", background: `radial-gradient(circle, ${C.star}24, transparent 64%)` }} />
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

// One headline at a time. `hi` is the one number or word the eye should land on.
const Headline: React.FC<{ c: Ctx; from: number; to: number; pre: string; hi: string; post: string }> = ({ c, from, to, pre, hi, post }) => {
  if (c.f < sec(c, from) - 2 || c.f > sec(c, to) + 14) return null;
  const words = [...pre.split(" ").filter(Boolean).map((w) => ({ w, hi: false })), { w: hi, hi: true }, ...post.split(" ").filter(Boolean).map((w) => ({ w, hi: false }))];
  const o = out(c, to);
  return (
    <div style={{ position: "absolute", left: PAD, top: 70, display: "flex", flexWrap: "wrap", gap: 22, fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 92, letterSpacing: "-0.035em", lineHeight: 1.05, color: C.ink, opacity: o, transform: `translateY(${(1 - o) * -26}px)` }}>
      {words.map((x, i) => {
        const p = sp(c, from + i * 0.09, theme.spring.snappy);
        return <span key={i} style={{ display: "inline-block", opacity: p, transform: `translateY(${mix(34, 0, p)}px) scale(${mix(0.96, 1, p)})`, color: x.hi ? C.hero : C.ink }}>{x.w}</span>;
      })}
    </div>
  );
};

// The job the person typed, and the three steps lighting up as the film reaches them.
const JobRow: React.FC<{ c: Ctx }> = ({ c }) => {
  const p = sp(c, T.job), o = out(c, T.end - 0.4);
  const n = Math.round(tw(c, T.type, T.type + 1.9, 0, data.ask.length, theme.ease.inOut));
  const steps = [{ at: T.fitTitle, t: `${data.fits.length} you have` }, { at: T.rows + 2.2, t: `${data.github.length} on GitHub` }, { at: T.cmd + 1.6, t: "how to use it" }];
  return (
    <div style={{ position: "absolute", left: PAD, top: 206, width: W, height: 76, display: "flex", alignItems: "center", gap: 18, opacity: p * o, transform: `translateY(${mix(-22, 0, p)}px)` }}>
      <div style={{ flex: "0 0 auto", height: 76, padding: "0 30px", borderRadius: 38, background: C.surface, border: `2px solid ${C.line}`, boxShadow: `0 14px 34px -18px ${C.shadow}`, display: "flex", alignItems: "center", gap: 16 }}>
        <span style={{ fontFamily: theme.fonts.mono, fontWeight: 700, fontSize: 19, letterSpacing: "0.08em", color: C.faint }}>YOUR JOB</span>
        <span style={{ fontFamily: theme.fonts.body, fontWeight: 600, fontSize: 31, color: C.ink, minWidth: 560 }}>{data.ask.slice(0, n)}{n < data.ask.length ? <span style={{ display: "inline-block", width: 3, height: 32, background: C.hero, marginLeft: 3, verticalAlign: -5 }} /> : null}</span>
      </div>
      <div style={{ flex: 1 }} />
      {steps.map((s, i) => {
        const q = sp(c, s.at, theme.spring.bouncy);
        return (
          <div key={i} style={{ height: 60, padding: "0 22px 0 10px", borderRadius: 30, display: "flex", alignItems: "center", gap: 12, background: q > 0.5 ? C.ink : "transparent", border: `2px solid ${q > 0.5 ? C.ink : C.line}`, transform: `scale(${mix(0.94, 1, q)})` }}>
            <span style={{ width: 40, height: 40, borderRadius: 20, display: "grid", placeItems: "center", fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 22, background: q > 0.5 ? C.surface : C.line, color: q > 0.5 ? C.ink : C.dim }}>{i + 1}</span>
            <span style={{ fontFamily: theme.fonts.body, fontWeight: 600, fontSize: 24, color: q > 0.5 ? C.surface : C.faint }}>{s.t}</span>
          </div>
        );
      })}
    </div>
  );
};

const tilePos = (i: number) => ({ x: PAD + (i % COLS) * (TW + GAP), y: TOP + Math.floor(i / COLS) * (TH + GAP) });

const Grid: React.FC<{ c: Ctx }> = ({ c }) => {
  const fitNames = data.fits.map((x) => x.name);
  return (
    <>
      {data.installed.map((name, i) => {
        const { x, y } = tilePos(i), col = i % COLS;
        const k = fitNames.indexOf(name), fit = k >= 0;
        const pop = sp(c, T.grid + i * 0.05, theme.spring.snappy);
        const hit = sp(c, T.scan + col * 0.2 + 0.12, fit ? theme.spring.bouncy : theme.spring.smooth);
        if (!fit) {
          const gone = out(c, T.cards - 0.25 + (i % 7) * 0.02, 0.3);
          if (gone <= 0) return null;
          return (
            <div key={name} style={{ position: "absolute", left: x, top: y, width: TW, height: TH, borderRadius: 18, background: C.surface, border: `2px solid ${C.line}`, display: "flex", alignItems: "center", justifyContent: "center", padding: 12, textAlign: "center", fontFamily: theme.fonts.body, fontWeight: 600, fontSize: 18, lineHeight: 1.22, color: C.ink,
              opacity: pop * mix(1, 0.26, hit) * gone, transform: `translateY(${mix(26, 0, pop) + (1 - gone) * 18}px) scale(${mix(0.86, 1, pop) * mix(1, 0.95, hit)})` }}>{soft(name)}</div>
          );
        }
        // a skill that fits: lights up in place, then grows into its card
        const fly = sp(c, T.cards + k * 0.13), gone = out(c, T.hub - 0.2 + k * 0.05, 0.3);
        if (gone <= 0) return null;
        const tx = PAD + k * (CW + 24), ty = TOP + 6, info = sp(c, T.cards + 0.75 + k * 0.16);
        const bob = Math.sin((c.f + k * 17) / 26) * 3 * fly;
        return (
          <div key={name} style={{ position: "absolute", left: mix(x, tx, fly), top: mix(y, ty, fly) + bob - (1 - gone) * 30, width: mix(TW, CW, fly), height: mix(TH, CH, fly), borderRadius: mix(18, 28, fly), overflow: "hidden", zIndex: 5,
            background: `rgb(${mix(255, 255, 1)},255,255)`, border: `${mix(2, 3, hit)}px solid ${hit > 0.4 ? C.hero : C.line}`, boxShadow: `0 ${mix(10, 34, fly)}px ${mix(24, 60, fly)}px -22px ${hit > 0.4 ? C.hero + "66" : C.shadow}`,
            opacity: pop * gone, transform: `translateY(${mix(26, 0, pop)}px) scale(${mix(0.86, 1, pop) * mix(1, 1.07, hit * (1 - fly))})` }}>
            <div style={{ position: "absolute", inset: 0, background: C.hero, opacity: hit * (1 - fly) }} />
            <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", padding: 12, textAlign: "center", fontFamily: theme.fonts.body, fontWeight: 700, fontSize: 18, lineHeight: 1.22, color: hit > 0.4 ? C.surface : C.ink, opacity: 1 - Math.min(1, fly * 2.2) }}>{soft(name)}</div>
            <div style={{ position: "absolute", inset: 0, padding: 30, display: "flex", flexDirection: "column", opacity: Math.max(0, fly * 1.6 - 0.6) }}>
              <div style={{ width: 56, height: 56, borderRadius: 16, background: C.heroSoft, display: "grid", placeItems: "center", fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 28, color: C.hero }}>{k + 1}</div>
              <div style={{ marginTop: 22, fontFamily: theme.fonts.display, fontWeight: 800, fontSize: name.length > 16 ? 31 : 38, letterSpacing: "-0.02em", lineHeight: 1.05, color: C.ink }}>{soft(name)}</div>
              <div style={{ marginTop: 14, fontFamily: theme.fonts.body, fontWeight: 500, fontSize: 23, lineHeight: 1.32, color: C.dim, opacity: info, transform: `translateY(${mix(14, 0, info)}px)` }}>{data.fits[k].use}</div>
              <div style={{ flex: 1 }} />
              <div style={{ alignSelf: "flex-start", fontFamily: theme.fonts.mono, fontWeight: 700, fontSize: 18, letterSpacing: "0.04em", color: C.hero, background: C.heroSoft, borderRadius: 10, padding: "7px 12px", opacity: info }}>ALREADY INSTALLED</div>
            </div>
          </div>
        );
      })}
      <Sweep c={c} />
    </>
  );
};

// The soft bar that reads the grid, one column at a time.
const Sweep: React.FC<{ c: Ctx }> = ({ c }) => {
  const a = T.scan, b = T.scan + COLS * 0.2 + 0.2;
  if (c.f < sec(c, a) || c.f > sec(c, b) + 8) return null;
  const x = tw(c, a, b, PAD - 60, PAD + W + 10, theme.ease.inOut), o = Math.min(tw(c, a, a + 0.25, 0, 1), tw(c, b - 0.15, b + 0.2, 1, 0));
  return <div style={{ position: "absolute", left: x, top: TOP - 22, width: 90, height: 5 * (TH + GAP) + 28, borderRadius: 45, background: `linear-gradient(90deg, transparent, ${C.hero}3D, transparent)`, opacity: o, zIndex: 6 }} />;
};

const Rows: React.FC<{ c: Ctx }> = ({ c }) => {
  if (c.f < sec(c, T.hub) || c.f > sec(c, T.pick) + 14) return null;
  const max = Math.max(...data.github.map((g) => g.stars)), RH = 118;
  return (
    <>
      {data.github.map((g, i) => {
        const at = T.rows + i * 0.5, p = sp(c, at), bar = sp(c, at + 0.25, theme.spring.slow), o = out(c, T.pick - 0.25 + i * 0.04, 0.28);
        return (
          <div key={g.skill + g.repo} style={{ position: "absolute", left: PAD, top: TOP + i * (RH + 14), width: W, height: RH, borderRadius: 24, background: C.surface, border: `2px solid ${C.line}`, boxShadow: `0 18px 40px -26px ${C.shadow}`, display: "flex", alignItems: "center", padding: "0 30px", gap: 26,
            opacity: p * o, transform: `translateX(${mix(70, 0, p)}px) scale(${mix(0.97, 1, p)})` }}>
            <div style={{ width: 56, height: 56, borderRadius: 28, background: C.bg, display: "grid", placeItems: "center", fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 28, color: C.ink, flex: "0 0 auto" }}>{i + 1}</div>
            <div style={{ width: 520, flex: "0 0 auto" }}>
              <div style={{ fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 34, letterSpacing: "-0.02em", color: C.ink, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{g.skill}</div>
              <div style={{ fontFamily: theme.fonts.mono, fontWeight: 500, fontSize: 20, color: C.dim, marginTop: 2, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{g.repo}</div>
            </div>
            <div style={{ flex: 1, height: 20, borderRadius: 10, background: C.bg, overflow: "hidden" }}>
              <div style={{ width: `${(g.stars / max) * 100 * bar}%`, height: "100%", borderRadius: 10, background: i === 0 ? C.hero : C.ink }} />
            </div>
            <div style={{ width: 210, flex: "0 0 auto", textAlign: "right", fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 38, letterSpacing: "-0.02em", color: C.ink, fontVariantNumeric: "tabular-nums" }}>{fmt(g.stars * bar)}<span style={{ color: C.star, fontSize: 30, marginLeft: 8 }}>★</span></div>
            <div style={{ width: 170, flex: "0 0 auto", textAlign: "center", fontFamily: theme.fonts.mono, fontWeight: 700, fontSize: 19, color: C.dim, border: `2px solid ${C.line}`, borderRadius: 12, padding: "8px 0" }}>{g.license}</div>
          </div>
        );
      })}
    </>
  );
};

const Check: React.FC<{ c: Ctx; at: number; children: React.ReactNode }> = ({ c, at, children }) => {
  const p = sp(c, at, theme.spring.snappy);
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 14, opacity: p, transform: `translateY(${mix(16, 0, p)}px)`, fontFamily: theme.fonts.body, fontWeight: 600, fontSize: 28, color: C.ink }}>
      <svg width="34" height="34" viewBox="0 0 34 34"><circle cx="17" cy="17" r="17" fill={C.ink} /><path d="M9.5 17.5l5 5 10-11" fill="none" stroke={C.surface} strokeWidth="3.4" strokeLinecap="round" strokeLinejoin="round" /></svg>
      {children}
    </div>
  );
};

const Pick: React.FC<{ c: Ctx }> = ({ c }) => {
  if (c.f < sec(c, T.pick) || c.f > sec(c, T.nums) + 14) return null;
  const p = sp(c, T.pick + 0.5), o = out(c, T.nums - 0.3), k = data.pick;
  const n = Math.round(tw(c, T.cmd, T.cmd + 1.5, 0, k.call.length, theme.ease.inOut));
  const bob = Math.sin(c.f / 28) * 3;
  return (
    <div style={{ position: "absolute", left: PAD, top: TOP + bob, width: W, height: 600, borderRadius: 36, display: "flex", flexDirection: "column", background: C.surface, border: `2px solid ${C.line}`, boxShadow: `0 40px 90px -40px ${C.shadow}`, padding: "50px 60px", opacity: p * o, transform: `translateY(${mix(46, 0, p) + (1 - o) * -30}px) scale(${mix(0.95, 1, p)})` }}>
      <div style={{ fontFamily: theme.fonts.mono, fontWeight: 700, fontSize: 22, letterSpacing: "0.1em", color: C.dim }}>RECOMMENDED · {k.where.toUpperCase()}</div>
      <div style={{ marginTop: 10, fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 104, letterSpacing: "-0.04em", lineHeight: 1, color: C.ink }}>{k.name}</div>
      <div style={{ marginTop: 34, height: 118, borderRadius: 26, background: C.ink, display: "flex", alignItems: "center", padding: "0 38px", fontFamily: theme.fonts.mono, fontWeight: 700, fontSize: 52, color: C.surface, boxShadow: `0 0 0 6px ${C.heroSoft}` }}>
        <span style={{ color: "#8FA8FF" }}>{k.call.slice(0, n).split(" ")[0]}</span>
        <span style={{ whiteSpace: "pre", color: C.faint }}>{k.call.slice(0, n).includes(" ") ? " " + k.call.slice(0, n).split(" ").slice(1).join(" ") : ""}</span>
        {c.f < sec(c, T.cmd + 2.2) || Math.floor(c.f / 15) % 2 === 0 ? <span style={{ width: 5, height: 56, background: C.hero, marginLeft: 6 }} /> : null}
      </div>
      <div style={{ marginTop: 26, fontFamily: theme.fonts.body, fontWeight: 500, fontSize: 30, color: C.dim, opacity: sp(c, T.cmd + 1.4) }}>or just ask in your own words. Claude loads it when the request fits.</div>
      <div style={{ flex: 1 }} />
      <div style={{ display: "flex", gap: 54, borderTop: `2px solid ${C.line}`, paddingTop: 30 }}>
        <Check c={c} at={T.cmd + 2.0}>{k.why}</Check>
        <Check c={c} at={T.cmd + 2.6}>{k.needs}</Check>
        <Check c={c} at={T.cmd + 3.2}>the plugin installs nothing</Check>
      </div>
    </div>
  );
};

const Numbers: React.FC<{ c: Ctx }> = ({ c }) => {
  if (c.f < sec(c, T.nums) || c.f > sec(c, T.end) + 14) return null;
  const r = data.run, pl = data.plain, o = out(c, T.end - 0.3);
  const cards = [
    { big: (pl.tokens / r.tokens).toFixed(1) + "×", small: "fewer tokens", a: pl.tokens, b: r.tokens, u: (v: number) => fmt(v) },
    { big: (pl.sec / r.sec).toFixed(1) + "×", small: "faster", a: pl.sec, b: r.sec, u: (v: number) => Math.round(v) + " s" },
    { big: r.steps + (r.steps === 1 ? " step" : " steps"), small: "instead of " + pl.steps, a: pl.steps, b: r.steps, u: (v: number) => String(Math.round(v)) },
  ];
  const cw = (W - 28 * 2) / 3;
  return (
    <>
      {cards.map((k, i) => {
        const at = T.nums + 0.6 + i * 0.9, p = sp(c, at), g = sp(c, at + 0.3, theme.spring.slow), bob = Math.sin((c.f + i * 21) / 27) * 3;
        return (
          <div key={i} style={{ position: "absolute", left: PAD + i * (cw + 28), top: TOP + bob, width: cw, height: 520, borderRadius: 34, background: C.surface, border: `2px solid ${C.line}`, boxShadow: `0 34px 80px -40px ${C.shadow}`, padding: "44px 46px", opacity: p * o, transform: `translateY(${mix(50, 0, p)}px) scale(${mix(0.94, 1, p)})` }}>
            <div style={{ fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 132, letterSpacing: "-0.05em", lineHeight: 0.95, color: i === 0 ? C.hero : C.ink }}>{k.big}</div>
            <div style={{ marginTop: 8, fontFamily: theme.fonts.display, fontWeight: 700, fontSize: 40, letterSpacing: "-0.02em", color: C.ink }}>{k.small}</div>
            <div style={{ marginTop: 44 }}>
              {[{ l: "Without", v: k.a, col: C.faint }, { l: "With the plugin", v: k.b, col: C.ink }].map((b, j) => (
                <div key={j} style={{ marginBottom: 22 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", fontFamily: theme.fonts.body, fontWeight: 600, fontSize: 24, color: C.dim }}><span>{b.l}</span><span style={{ color: C.ink, fontVariantNumeric: "tabular-nums" }}>{k.u(b.v * g)}</span></div>
                  <div style={{ marginTop: 8, height: 18, borderRadius: 9, background: C.bg, overflow: "hidden" }}><div style={{ width: `${Math.max(2, (b.v / Math.max(k.a, k.b)) * 100) * g}%`, height: "100%", borderRadius: 9, background: b.col }} /></div>
                </div>
              ))}
            </div>
          </div>
        );
      })}
      <div style={{ position: "absolute", left: PAD, top: TOP + 556, width: W, textAlign: "center", fontFamily: theme.fonts.body, fontWeight: 500, fontSize: 26, color: C.dim, opacity: sp(c, T.nums + 3.4) * o }}>This request, asked once without the plugin and once with it. Claude Opus.</div>
    </>
  );
};

const End: React.FC<{ c: Ctx }> = ({ c }) => {
  if (c.f < sec(c, T.end)) return null;
  const p = sp(c, T.end + 0.2), q = sp(c, T.end + 0.7), u = sp(c, T.end + 1.2, theme.spring.bouncy), bob = Math.sin(c.f / 26) * 3;
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 26 }}>
      <div style={{ fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 176, letterSpacing: "-0.05em", lineHeight: 1, color: C.ink, opacity: p, transform: `translateY(${mix(40, 0, p) + bob}px) scale(${mix(0.94, 1, p)})` }}>Straight Answer</div>
      <div style={{ fontFamily: theme.fonts.body, fontWeight: 500, fontSize: 44, color: C.dim, opacity: q, transform: `translateY(${mix(24, 0, q)}px)` }}>Which skill to use, and how. Short answers, too.</div>
      <div style={{ marginTop: 18, fontFamily: theme.fonts.mono, fontWeight: 700, fontSize: 34, color: C.surface, background: C.hero, borderRadius: 22, padding: "20px 34px", boxShadow: `0 0 60px ${C.hero}55`, opacity: u, transform: `scale(${mix(0.9, 1, u)})` }}>github.com/alibb007/straight-answer</div>
    </AbsoluteFill>
  );
};

export const Film: React.FC = () => {
  const f = useCurrentFrame(), { fps } = useVideoConfig(), c: Ctx = { f, fps };
  const n = data.installed.length;
  const count = Math.round(interpolate(spring({ frame: f - sec(c, T.grid), fps, config: theme.spring.slow, durationInFrames: sec(c, 2.9) }), [0, 1], [0, n]));
  return (
    <AbsoluteFill>
      <BgMesh c={c} />
      <Headline c={c} from={0.25} to={T.job + 4.9} pre="You have" hi={String(count)} post="skills." />
      <Headline c={c} from={T.fitTitle} to={T.cards - 0.2} pre="" hi={String(data.fits.length)} post="of them fit this job." />
      <Headline c={c} from={T.cards + 0.1} to={T.hub - 0.3} pre="You already have" hi={String(data.fits.length)} post="that fit." />
      <Headline c={c} from={T.hub + 0.2} to={T.pick - 0.3} pre="And" hi={String(data.github.length)} post="more on GitHub you don't have." />
      <Headline c={c} from={T.pick + 0.2} to={T.nums - 0.3} pre="Start with the one" hi="you have." post="" />
      <Headline c={c} from={T.nums + 0.2} to={T.end - 0.3} pre="One command," hi="not" post={`${data.plain.steps} steps.`} />
      <JobRow c={c} />
      <Grid c={c} />
      <Rows c={c} />
      <Pick c={c} />
      <Numbers c={c} />
      <End c={c} />
      <Finish c={c} />
    </AbsoluteFill>
  );
};
