import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import fs from 'node:fs';
const require=createRequire(import.meta.url);
const C=require('../assets/2026-09-01_UniverseLab_CosmologyEngine_v1.0.js');

const report={schema:'universelab.cosmology-engine.validation.v1',engine_version:C.VERSION,status:'PASS',checks:[]};
function check(name,fn){
  try{const detail=fn()??{};report.checks.push({name,status:'PASS',detail});}
  catch(error){report.status='FAIL';report.checks.push({name,status:'FAIL',error:String(error?.stack||error)});}
}
function close(a,b,rtol=1e-10,atol=1e-12){assert.ok(Number.isFinite(a)&&Number.isFinite(b));assert.ok(Math.abs(a-b)<=atol+rtol*Math.max(Math.abs(a),Math.abs(b)),`${a} != ${b}`);}
const ref={H0:67.4,Om:.315,Ode:.684908,Or:9.2e-5,w:-1,sigma8:.811};

check('normalization_E0',()=>{close(C.E(0,ref,'lcdm'),1,1e-13);return{E0:C.E(0,ref,'lcdm')}});
check('flat_distance_identity',()=>{const dc=C.radialComovingDistance(1,ref);const dm=C.transverseComovingDistance(1,ref);close(dm,dc,1e-13);return{dc,dm}});
check('curvature_mapping_direction',()=>{
  const open={...ref,Om:.2,Ode:.5};
  const closed={...ref,Om:.5,Ode:.8};
  const dcOpen=C.radialComovingDistance(2.33,open),dmOpen=C.transverseComovingDistance(2.33,open);
  const dcClosed=C.radialComovingDistance(2.33,closed),dmClosed=C.transverseComovingDistance(2.33,closed);
  assert.ok(dmOpen>dcOpen,'open geometry must have DM > DC');
  assert.ok(dmClosed<dcClosed,'closed geometry must have DM < DC');
  return{open:{dc:dcOpen,dm:dmOpen},closed:{dc:dcClosed,dm:dmClosed}};
});
check('etherington_reciprocity',()=>{for(const z of [.01,.5,1,2.33])close(C.etheringtonRatio(z,ref),1,1e-12);return{tested_z:[.01,.5,1,2.33]}});
check('eds_age',()=>{const p={H0:70,Om:1,Ode:0,Or:0,w:-1,sigma8:.8};const age=C.ageGyr(p,'lcdm',{aMin:1e-10,n:8192});const expected=C.hubbleTimeGyr(p)*2/3;close(age,expected,2e-8);return{age,expected}});
check('invalid_background_fails_closed',()=>{
  const bad={H0:67.4,Om:.1,Ode:1.2,Or:9.2e-5,w:-1.5,sigma8:.811};
  const domain=C.validateBackgroundDomain(bad,'wcdm',{zMax:5,samples:20000});
  assert.equal(domain.ok,false);assert.equal(domain.code,'INVALID_BACKGROUND_DOMAIN');
  assert.throws(()=>C.radialComovingDistance(2,bad,'wcdm'),e=>e?.code==='INVALID_BACKGROUND_DOMAIN');
  return domain;
});
check('bridge_no_floor_and_domain_gate',()=>{
  const bad={...ref,betaTau:-3,IB:1,Rchi:1};
  const domain=C.validateBackgroundDomain(bad,'bridge',{zMax:5,samples:4096});
  assert.equal(domain.ok,false);assert.equal(domain.code,'INVALID_BRIDGE_DOMAIN');
  assert.throws(()=>C.E(domain.z,bad,'bridge'),e=>e?.code==='INVALID_BRIDGE_DOMAIN');
  return domain;
});
check('bridge_product_degeneracy',()=>{
  const p1={...ref,betaTau:.05,IB:.4,Rchi:1};
  const p2={...ref,betaTau:.1,IB:.2,Rchi:1};
  for(const z of [0,.5,1,3])close(C.E(z,p1,'bridge'),C.E(z,p2,'bridge'),1e-13);
  return{product:.02};
});
check('lcdm_growth_reference',()=>{
  const s=C.solveGrowth(ref,'lcdm',{steps:4000});
  const expected=new Map([[.5,.7689433284],[1,.6068047406],[2,.4172414795],[3,.3155380188]]);
  const rows=[];
  for(const [z,Dexp] of expected){const g=C.growthAtZ(z,s);close(g.D,Dexp,3e-9);rows.push({z,...g});}
  return{aInit:s.aInit,steps:s.steps,rows};
});
check('eds_growth_exact_limit',()=>{
  const p={H0:70,Om:1,Ode:0,Or:0,w:-1,sigma8:.8};
  const s=C.solveGrowth(p,'lcdm',{steps:2500,aInit:1e-3});
  for(const z of [0,.5,1,3,9]){const g=C.growthAtZ(z,s);close(g.D,1/(1+z),2e-6);close(g.f,1,2e-9);}
  return{tested_z:[0,.5,1,3,9]};
});
check('bridge_growth_firewall',()=>{assert.throws(()=>C.solveGrowth({...ref,betaTau:.05,IB:.4},'bridge'),e=>e?.code==='UNRELEASED_GROWTH_MAP');return{code:'UNRELEASED_GROWTH_MAP'}});
check('small_z_hubble_law',()=>{const z=1e-5;const dc=C.radialComovingDistance(z,ref);const approx=C.hubbleDistance(ref)*z;close(dc,approx,1e-5);return{z,dc,approx}});

fs.writeFileSync('canonical-cosmology-engine-report.json',JSON.stringify(report,null,2));
console.log(JSON.stringify(report,null,2));
if(report.status!=='PASS')process.exit(1);
