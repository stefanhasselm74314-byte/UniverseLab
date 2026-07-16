'use strict';

/** UniverseLab MVP 0.5 numerical core.
 * Pure functions; no DOM access. All times use tau = H0 t.
 */

export function friedmannTerms(a, p) {
  if (!(a > 0) || !Number.isFinite(a)) throw new RangeError('a must be finite and > 0');
  const r = p.Or / a ** 4;
  const m = p.Om / a ** 3;
  const k = p.Ok / a ** 2;
  const l = p.Ol;
  return { r, m, k, l, sum: r + m + k + l };
}

export function E(a, p) {
  const s = friedmannTerms(a, p).sum;
  if (!(s > 0) || !Number.isFinite(s)) return NaN;
  return Math.sqrt(s);
}

export function fractions(a, p) {
  const t = friedmannTerms(a, p);
  if (!(t.sum > 0) || !Number.isFinite(t.sum)) return { r: NaN, m: NaN, k: NaN, l: NaN, closure: NaN };
  const r = t.r / t.sum, m = t.m / t.sum, k = t.k / t.sum, l = t.l / t.sum;
  return { r, m, k, l, closure: r + m + k + l - 1 };
}

export function deceleration(a, p) {
  const f = fractions(a, p);
  return f.r + 0.5 * f.m - f.l;
}

export function dominantComponent(a, p, transitionTolerance = 0.05) {
  const f = fractions(a, p);
  const entries = [['radiation', f.r], ['matter', f.m], ['curvature', f.k], ['lambda', f.l]]
    .filter(([, v]) => Number.isFinite(v))
    .sort((x, y) => y[1] - x[1]);
  if (!entries.length) return { dominant: 'invalid', transition: null };
  const [first, second] = entries;
  const denom = Math.abs(first[1]) + Math.abs(second[1]);
  const delta = denom > 0 ? Math.abs(first[1] - second[1]) / denom : 0;
  return { dominant: first[0], transition: delta < transitionTolerance ? `${first[0]}-${second[0]}` : null };
}

export function equalityPoints(p) {
  const rm = p.Or > 0 && p.Om > 0 ? p.Or / p.Om : NaN;
  const ml = p.Om > 0 && p.Ol > 0 ? (p.Om / p.Ol) ** (1 / 3) : NaN;
  return {
    radiationMatter: Number.isFinite(rm) ? { a: rm, z: 1 / rm - 1 } : null,
    matterLambda: Number.isFinite(ml) ? { a: ml, z: 1 / ml - 1 } : null,
    acceleration: findAccelerationTransition(p)
  };
}

export function findAccelerationTransition(p, aMin = 1e-8, aMax = 1e3, tolerance = 1e-12) {
  const f = a => 2 * p.Or + p.Om * a - 2 * p.Ol * a ** 4;
  let lo = aMin, hi = aMax, flo = f(lo), fhi = f(hi);
  if (!Number.isFinite(flo) || !Number.isFinite(fhi) || flo === 0) return flo === 0 ? { a: lo, z: 1 / lo - 1 } : null;
  if (flo * fhi > 0) return null;
  for (let i = 0; i < 200 && hi - lo > tolerance * Math.max(1, hi); i++) {
    const mid = 0.5 * (lo + hi), fm = f(mid);
    if (flo * fm <= 0) { hi = mid; fhi = fm; } else { lo = mid; flo = fm; }
  }
  const a = 0.5 * (lo + hi);
  return { a, z: 1 / a - 1 };
}

function rhs(a, p) {
  const e = E(a, p);
  return Number.isFinite(e) ? a * e : NaN;
}

/** Dormand-Prince 5(4) embedded step. */
export function rk45Step(a, h, p) {
  const f = x => rhs(x, p);
  const k1 = f(a);
  const k2 = f(a + h * k1 / 5);
  const k3 = f(a + h * (3 * k1 / 40 + 9 * k2 / 40));
  const k4 = f(a + h * (44 * k1 / 45 - 56 * k2 / 15 + 32 * k3 / 9));
  const k5 = f(a + h * (19372 * k1 / 6561 - 25360 * k2 / 2187 + 64448 * k3 / 6561 - 212 * k4 / 729));
  const k6 = f(a + h * (9017 * k1 / 3168 - 355 * k2 / 33 + 46732 * k3 / 5247 + 49 * k4 / 176 - 5103 * k5 / 18656));
  const y5 = a + h * (35 * k1 / 384 + 500 * k3 / 1113 + 125 * k4 / 192 - 2187 * k5 / 6784 + 11 * k6 / 84);
  const k7 = f(y5);
  const y4 = a + h * (5179 * k1 / 57600 + 7571 * k3 / 16695 + 393 * k4 / 640 - 92097 * k5 / 339200 + 187 * k6 / 2100 + k7 / 40);
  return { value: y5, error: Math.abs(y5 - y4) };
}

/** Advance by requested deltaTau using adaptive accepted substeps. */
export function advanceAdaptive(a0, deltaTau, p, options = {}) {
  const rtol = options.rtol ?? 1e-8;
  const atol = options.atol ?? 1e-11;
  const minStep = options.minStep ?? 1e-12;
  const maxSubsteps = options.maxSubsteps ?? 10000;
  let a = a0, elapsed = 0, h = Math.min(deltaTau, options.initialStep ?? deltaTau), accepted = 0, rejected = 0;
  while (elapsed < deltaTau && accepted + rejected < maxSubsteps) {
    h = Math.min(h, deltaTau - elapsed);
    const step = rk45Step(a, h, p);
    if (!(step.value > 0) || !Number.isFinite(step.value) || !Number.isFinite(step.error)) {
      h *= 0.2; rejected++;
      if (h < minStep) return { ok: false, reason: 'non-real Friedmann branch', a, elapsed, accepted, rejected, error: NaN };
      continue;
    }
    const scale = atol + rtol * Math.max(Math.abs(a), Math.abs(step.value));
    const ratio = step.error / scale;
    if (ratio <= 1) {
      a = step.value; elapsed += h; accepted++;
    } else rejected++;
    const factor = ratio === 0 ? 5 : Math.min(5, Math.max(0.2, 0.9 * ratio ** (-0.2)));
    h *= factor;
    if (h < minStep) return { ok: false, reason: 'minimum step reached', a, elapsed, accepted, rejected, error: step.error };
  }
  const ok = elapsed >= deltaTau;
  return { ok, reason: ok ? null : 'maximum substeps reached', a, elapsed, accepted, rejected, error: 0 };
}

/** Mulberry32 deterministic PRNG. */
export function seededRandom(seed) {
  let state = seed >>> 0;
  return function random() {
    state += 0x6D2B79F5;
    let t = state;
    t = Math.imul(t ^ t >>> 15, t | 1);
    t ^= t + Math.imul(t ^ t >>> 7, t | 61);
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}
