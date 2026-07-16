import assert from 'node:assert/strict';
import {
  E, fractions, deceleration, equalityPoints,
  advanceAdaptive, seededRandom
} from '../src/numerics.js';

const near = (actual, expected, tolerance, label) => {
  assert.ok(Math.abs(actual - expected) <= tolerance,
    `${label}: expected ${expected}, got ${actual}`);
};

// Closure identity.
{
  const p = { Or: 9.2e-5, Om: 0.315, Ok: 0, Ol: 0.684908 };
  for (const a of [1e-6, 1e-3, 0.1, 1, 10]) {
    near(fractions(a, p).closure, 0, 5e-15, `closure at a=${a}`);
  }
}

// Radiation-only exact solution: a(tau)^2 = a0^2 + 2 sqrt(Or) DeltaTau.
{
  const p = { Or: 1, Om: 0, Ok: 0, Ol: 0 };
  const a0 = 0.01, dt = 0.2;
  const exact = Math.sqrt(a0 * a0 + 2 * dt);
  const result = advanceAdaptive(a0, dt, p, { rtol: 1e-10, atol: 1e-13 });
  assert.equal(result.ok, true);
  near(result.a, exact, 2e-9, 'radiation solution');
}

// Matter-only exact solution: a(tau)^(3/2) = a0^(3/2) + 3 sqrt(Om) DeltaTau / 2.
{
  const p = { Or: 0, Om: 1, Ok: 0, Ol: 0 };
  const a0 = 0.01, dt = 0.2;
  const exact = (a0 ** 1.5 + 1.5 * dt) ** (2 / 3);
  const result = advanceAdaptive(a0, dt, p, { rtol: 1e-10, atol: 1e-13 });
  assert.equal(result.ok, true);
  near(result.a, exact, 2e-9, 'matter solution');
}

// de Sitter exact solution: a(tau) = a0 exp(sqrt(Ol) DeltaTau).
{
  const p = { Or: 0, Om: 0, Ok: 0, Ol: 1 };
  const a0 = 0.01, dt = 2;
  const exact = a0 * Math.exp(dt);
  const result = advanceAdaptive(a0, dt, p, { rtol: 1e-10, atol: 1e-13 });
  assert.equal(result.ok, true);
  near(result.a, exact, 2e-9, 'de Sitter solution');
}

// Standard epoch landmarks.
{
  const p = { Or: 9.2e-5, Om: 0.315, Ok: 0, Ol: 0.684908 };
  const points = equalityPoints(p);
  near(points.radiationMatter.a, 9.2e-5 / 0.315, 1e-15, 'radiation-matter equality');
  near(points.matterLambda.a, (0.315 / 0.684908) ** (1 / 3), 1e-14, 'matter-lambda equality');
  near(deceleration(points.acceleration.a, p), 0, 2e-10, 'acceleration transition');
  assert.ok(Number.isFinite(E(1, p)));
}

// Reproducible random stream.
{
  const a = seededRandom(123456), b = seededRandom(123456), c = seededRandom(654321);
  const xs = Array.from({ length: 8 }, () => a());
  const ys = Array.from({ length: 8 }, () => b());
  const zs = Array.from({ length: 8 }, () => c());
  assert.deepEqual(xs, ys);
  assert.notDeepEqual(xs, zs);
}

console.log('UniverseLab numerical validation: PASS');
