(function(root,factory){
  'use strict';
  const api=factory();
  if(typeof module==='object'&&module.exports) module.exports=api;
  if(root) root.UniverseLabCosmology=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const VERSION='1.0.0';
  const REVISION='1.0.2';
  const C_KM_S=299792.458;
  const HUBBLE_TIME_100_GYR=9.77813;
  const DEFAULT_OR=9.2e-5;
  const DEFAULT_RD_MPC=147.1;

  class CosmologyError extends Error{
    constructor(code,message,detail={}){
      super(message);
      this.name='CosmologyError';
      this.code=code;
      this.detail=detail;
    }
  }

  const finite=(x,name)=>{
    const value=Number(x);
    if(!Number.isFinite(value)) throw new CosmologyError('NONFINITE_PARAMETER',`${name} must be finite`,{name,value:x});
    return value;
  };

  function normalizeParams(input={}){
    const p={
      H0:finite(input.H0??67.4,'H0'),
      Om:finite(input.Om??0.315,'Om'),
      Ode:finite(input.Ode??input.Ol??0.684908,'Ode'),
      Or:finite(input.Or??DEFAULT_OR,'Or'),
      w:finite(input.w??-1,'w'),
      sigma8:finite(input.sigma8??input.s8??0.811,'sigma8'),
      betaTau:finite(input.betaTau??input.beta??input.b??0,'betaTau'),
      IB:finite(input.IB??input.ib??0,'IB'),
      Rchi:finite(input.Rchi??input.rchi??input.r??1,'Rchi'),
      ac:input.ac==null?null:finite(input.ac,'ac')
    };
    p.Ok=finite(input.Ok??(1-p.Or-p.Om-p.Ode),'Ok');
    if(!(p.H0>0)) throw new CosmologyError('INVALID_H0','H0 must be positive',{H0:p.H0});
    if(!(p.sigma8>=0)) throw new CosmologyError('INVALID_SIGMA8','sigma8 must be non-negative',{sigma8:p.sigma8});
    if(!(p.Rchi>0)) throw new CosmologyError('INVALID_RCHI','Rchi must be positive',{Rchi:p.Rchi});
    if(p.ac!=null&&!(p.ac>0)) throw new CosmologyError('INVALID_AC','ac must be positive',{ac:p.ac});
    return Object.freeze(p);
  }

  function normalizeModel(model='lcdm'){
    const key=String(model).toLowerCase();
    if(key==='lcdm'||key==='l') return 'lcdm';
    if(key==='wcdm'||key==='w') return 'wcdm';
    if(key==='bridge'||key==='b') return 'bridge';
    throw new CosmologyError('UNKNOWN_MODEL',`Unknown model: ${model}`,{model});
  }

  function validateZ(z){
    const value=finite(z,'z');
    if(value<0) throw new CosmologyError('NEGATIVE_REDSHIFT','This engine contract currently requires z >= 0',{z:value});
    return value;
  }

  function aOfZ(z){return 1/(1+validateZ(z));}
  function zOfA(a){
    const value=finite(a,'a');
    if(!(value>0&&value<=1)) throw new CosmologyError('INVALID_SCALE_FACTOR','This engine contract requires 0 < a <= 1',{a:value});
    return 1/value-1;
  }

  function bridgeScale(p){return p.ac??p.Rchi/(p.Rchi+2.5);}
  function bridgeDeltaFromA(a,p){
    const ac=bridgeScale(p);
    return p.betaTau*p.IB*Math.exp(-Math.pow(a/ac,2));
  }

  function backgroundTermsFromA(a,p,model){
    const key=normalizeModel(model);
    const aa=finite(a,'a');
    if(!(aa>0&&aa<=1)) throw new CosmologyError('INVALID_SCALE_FACTOR','This engine contract requires 0 < a <= 1',{a:aa});
    const r=p.Or/aa**4;
    const m=p.Om/aa**3;
    const k=p.Ok/aa**2;
    const de=key==='wcdm'?p.Ode*aa**(-3*(1+p.w)):p.Ode;
    const base=r+m+k+de;
    if(key!=='bridge') return {r,m,k,de,base,e2:base,delta:0,onePlusDelta:1};
    const delta=bridgeDeltaFromA(aa,p);
    const onePlusDelta=1+delta;
    return {r,m,k,de,base,e2:base*onePlusDelta,delta,onePlusDelta};
  }

  function e2FromA(a,input={},model='lcdm'){
    const p=normalizeParams(input);
    return backgroundTermsFromA(a,p,model).e2;
  }

  function e2(z,input={},model='lcdm'){
    return e2FromA(aOfZ(z),input,model);
  }

  function assertPhysicalE2(value,detail={}){
    if(!Number.isFinite(value)) throw new CosmologyError('NONFINITE_E2','E^2 is non-finite',detail);
    if(!(value>0)) throw new CosmologyError('INVALID_BACKGROUND_DOMAIN','E^2 must remain strictly positive',Object.assign({e2:value},detail));
    return value;
  }

  function E(z,input={},model='lcdm'){
    const zz=validateZ(z);
    const p=normalizeParams(input);
    const key=normalizeModel(model);
    const terms=backgroundTermsFromA(1/(1+zz),p,key);
    if(key==='bridge'&&!(terms.onePlusDelta>0)){
      throw new CosmologyError('INVALID_BRIDGE_DOMAIN','1 + Delta(a) must be strictly positive',{z:zz,delta:terms.delta,onePlusDelta:terms.onePlusDelta});
    }
    return Math.sqrt(assertPhysicalE2(terms.e2,{z:zz,model:key,params:p}));
  }

  function dE2dXFromA(a,p,model){
    const key=normalizeModel(model);
    const t=backgroundTermsFromA(a,p,key);
    const deDerivative=key==='wcdm'?-3*(1+p.w)*t.de:0;
    const baseDerivative=-4*t.r-3*t.m-2*t.k+deDerivative;
    if(key!=='bridge') return baseDerivative;
    const u=Math.pow(a/bridgeScale(p),2);
    const deltaDerivative=-2*u*t.delta;
    return baseDerivative*t.onePlusDelta+t.base*deltaDerivative;
  }

  function dLnHdLnA(a,input={},model='lcdm'){
    const p=normalizeParams(input);
    const key=normalizeModel(model);
    const t=backgroundTermsFromA(a,p,key);
    assertPhysicalE2(t.e2,{a,model:key,params:p});
    return 0.5*dE2dXFromA(a,p,key)/t.e2;
  }

  function q(z,input={},model='lcdm'){
    const zz=validateZ(z);
    const p=normalizeParams(input);
    const key=normalizeModel(model);
    const a=1/(1+zz);
    const t=backgroundTermsFromA(a,p,key);
    assertPhysicalE2(t.e2,{z:zz,model:key,params:p});
    return -1-dE2dXFromA(a,p,key)/(2*t.e2);
  }

  function omegaM(z,input={},model='lcdm'){
    const zz=validateZ(z);
    const p=normalizeParams(input);
    const key=normalizeModel(model);
    const a=1/(1+zz);
    const t=backgroundTermsFromA(a,p,key);
    assertPhysicalE2(t.e2,{z:zz,model:key,params:p});
    return t.m/t.e2;
  }

  function validateBackgroundDomain(input={},model='lcdm',options={}){
    const p=normalizeParams(input);
    const key=normalizeModel(model);
    const zMin=finite(options.zMin??0,'zMin');
    const zMax=finite(options.zMax??5,'zMax');
    const samples=Math.max(16,Math.trunc(finite(options.samples??4096,'samples')));
    if(zMin<0||zMax<zMin) throw new CosmologyError('INVALID_DOMAIN_INTERVAL','Require 0 <= zMin <= zMax',{zMin,zMax});
    let minE2=Infinity,minZ=zMin;
    for(let i=0;i<=samples;i++){
      const z=zMin+(zMax-zMin)*i/samples;
      const a=1/(1+z);
      const terms=backgroundTermsFromA(a,p,key);
      if(terms.e2<minE2){minE2=terms.e2;minZ=z;}
      if(!Number.isFinite(terms.e2)||terms.e2<=0||(key==='bridge'&&terms.onePlusDelta<=0)){
        return {ok:false,code:key==='bridge'&&terms.onePlusDelta<=0?'INVALID_BRIDGE_DOMAIN':'INVALID_BACKGROUND_DOMAIN',model:key,z,minE2,minZ,e2:terms.e2,delta:terms.delta,onePlusDelta:terms.onePlusDelta,samples};
      }
    }
    return {ok:true,code:'PASS',model:key,zMin,zMax,minE2,minZ,samples};
  }

  function simpson(fn,a,b,n=1024){
    let N=Math.max(2,Math.trunc(finite(n,'n')));
    if(N%2)N++;
    if(!(b>=a)) throw new CosmologyError('INVALID_INTEGRATION_INTERVAL','Require b >= a',{a,b});
    if(a===b)return 0;
    const h=(b-a)/N;
    let s=fn(a)+fn(b);
    if(!Number.isFinite(s)) throw new CosmologyError('NONFINITE_INTEGRAND','Non-finite endpoint integrand',{a,b});
    for(let i=1;i<N;i++){
      const v=fn(a+i*h);
      if(!Number.isFinite(v)) throw new CosmologyError('NONFINITE_INTEGRAND','Non-finite integrand',{x:a+i*h});
      s+=(i%2?4:2)*v;
    }
    return s*h/3;
  }

  function hubbleDistance(input={}){return C_KM_S/normalizeParams(input).H0;}
  function hubbleTimeGyr(input={}){return HUBBLE_TIME_100_GYR/(normalizeParams(input).H0/100);}

  function radialComovingDistance(z,input={},model='lcdm',options={}){
    const zz=validateZ(z);
    const p=normalizeParams(input);
    const key=normalizeModel(model);
    const domain=validateBackgroundDomain(p,key,{zMin:0,zMax:zz,samples:options.domainSamples??Math.max(512,Math.ceil(512*zz))});
    if(!domain.ok) throw new CosmologyError(domain.code,'Invalid background domain encountered during distance integration',domain);
    const n=options.n??Math.max(512,Math.ceil(256*zz));
    return C_KM_S/p.H0*simpson(x=>1/E(x,p,key),0,zz,n);
  }

  function transverseComovingDistance(z,input={},model='lcdm',options={}){
    const p=normalizeParams(input);
    const dc=radialComovingDistance(z,p,model,options);
    const ok=p.Ok;
    if(Math.abs(ok)<1e-12)return dc;
    const dh=C_KM_S/p.H0;
    const chi=Math.sqrt(Math.abs(ok))*dc/dh;
    return ok>0?dh/Math.sqrt(ok)*Math.sinh(chi):dh/Math.sqrt(-ok)*Math.sin(chi);
  }

  function luminosityDistance(z,input={},model='lcdm',options={}){
    const zz=validateZ(z);
    return (1+zz)*transverseComovingDistance(zz,input,model,options);
  }

  function angularDiameterDistance(z,input={},model='lcdm',options={}){
    const zz=validateZ(z);
    return transverseComovingDistance(zz,input,model,options)/(1+zz);
  }

  function distanceModulus(z,input={},model='lcdm',options={}){
    const dl=luminosityDistance(z,input,model,options);
    if(!(dl>0)) throw new CosmologyError('INVALID_LUMINOSITY_DISTANCE','Luminosity distance must be positive',{z,dl});
    return 5*Math.log10(dl)+25;
  }

  function ageGyr(input={},model='lcdm',options={}){
    const p=normalizeParams(input);
    const key=normalizeModel(model);
    const aMin=finite(options.aMin??1e-8,'aMin');
    if(!(aMin>0&&aMin<1)) throw new CosmologyError('INVALID_AGE_AMIN','Require 0 < aMin < 1',{aMin});
    const zMax=1/aMin-1;
    const domain=validateBackgroundDomain(p,key,{zMin:0,zMax,samples:options.domainSamples??8192});
    if(!domain.ok) throw new CosmologyError(domain.code,'Invalid background domain encountered during age integration',domain);
    const n=options.n??4096;
    const integral=simpson(x=>{
      const a=Math.exp(x);
      return 1/E(1/a-1,p,key);
    },Math.log(aMin),0,n);
    return hubbleTimeGyr(p)*integral;
  }

  function lookbackTimeGyr(z,input={},model='lcdm',options={}){
    const zz=validateZ(z);
    const p=normalizeParams(input);
    const key=normalizeModel(model);
    const domain=validateBackgroundDomain(p,key,{zMin:0,zMax:zz,samples:options.domainSamples??Math.max(512,Math.ceil(512*zz))});
    if(!domain.ok) throw new CosmologyError(domain.code,'Invalid background domain encountered during lookback integration',domain);
    const n=options.n??Math.max(512,Math.ceil(256*zz));
    return hubbleTimeGyr(p)*simpson(x=>1/((1+x)*E(x,p,key)),0,zz,n);
  }

  function solveGrowth(input={},model='lcdm',options={}){
    const p=normalizeParams(input);
    const key=normalizeModel(model);
    if(key==='bridge') throw new CosmologyError('UNRELEASED_GROWTH_MAP','The effective bridge has no released perturbation/growth map',{model:key});
    const aEq=p.Om>0?p.Or/p.Om:0;
    const aInit=finite(options.aInit??Math.max(1e-3,10*aEq),'aInit');
    if(!(aInit>0&&aInit<1)) throw new CosmologyError('INVALID_GROWTH_AINIT','Require 0 < aInit < 1',{aInit});
    const steps=Math.max(400,Math.trunc(finite(options.steps??4000,'steps')));
    const x0=Math.log(aInit),nominalH=(0-x0)/steps;
    let x=x0,D=aInit,V=aInit;
    const rows=[];
    const rhs=(X,Y,W)=>{
      const a=Math.exp(X);
      const om=omegaM(Math.max(0,1/a-1),p,key);
      return [W,-(2+dLnHdLnA(a,p,key))*W+1.5*om*Y];
    };
    for(let i=0;i<=steps;i++){
      if(i===steps)x=0;
      rows.push({x,a:i===steps?1:Math.exp(x),D,V});
      if(i===steps)break;
      const nextX=i===steps-1?0:x+nominalH;
      const h=nextX-x;
      const k1=rhs(x,D,V);
      const k2=rhs(x+h/2,D+h*k1[0]/2,V+h*k1[1]/2);
      const k3=rhs(x+h/2,D+h*k2[0]/2,V+h*k2[1]/2);
      const k4=rhs(nextX,D+h*k3[0],V+h*k3[1]);
      D+=h*(k1[0]+2*k2[0]+2*k3[0]+k4[0])/6;
      V+=h*(k1[1]+2*k2[1]+2*k3[1]+k4[1])/6;
      x=nextX;
    }
    const norm=rows[rows.length-1].D;
    if(!(Number.isFinite(norm)&&norm>0)) throw new CosmologyError('INVALID_GROWTH_NORMALIZATION','Growth normalization is invalid',{norm});
    for(const row of rows){row.Dn=row.D/norm;row.f=row.V/row.D;}
    return Object.freeze({version:VERSION,revision:REVISION,model:key,params:p,aInit,steps,rows:Object.freeze(rows)});
  }

  function growthAtZ(z,solution){
    const zz=validateZ(z);
    if(!solution||!Array.isArray(solution.rows)) throw new CosmologyError('INVALID_GROWTH_SOLUTION','A solveGrowth result is required');
    const a=1/(1+zz),rows=solution.rows;
    if(a<rows[0].a) throw new CosmologyError('GROWTH_QUERY_BEFORE_INITIAL_EPOCH','Requested a is below growth initial scale factor',{a,aInit:rows[0].a});
    if(a>=1){const r=rows[rows.length-1];return {z:zz,a:1,D:1,f:r.f,fsigma8:r.f*solution.params.sigma8};}
    let lo=0,hi=rows.length-1;
    while(hi-lo>1){const mid=(lo+hi)>>1;if(rows[mid].a<a)lo=mid;else hi=mid;}
    const A=rows[lo],B=rows[hi];
    const u=(Math.log(a)-A.x)/(B.x-A.x);
    const D=A.Dn*(1-u)+B.Dn*u;
    const f=A.f*(1-u)+B.f*u;
    return {z:zz,a,D,f,fsigma8:f*solution.params.sigma8*D};
  }

  function S8(input={}){const p=normalizeParams(input);return p.sigma8*Math.sqrt(p.Om/0.3);}
  function baoDMOverRd(z,input={},model='lcdm',options={}){return transverseComovingDistance(z,input,model,options)/finite(options.rdMpc??DEFAULT_RD_MPC,'rdMpc');}
  function etheringtonRatio(z,input={},model='lcdm',options={}){
    const zz=validateZ(z);
    const dl=luminosityDistance(zz,input,model,options);
    const da=angularDiameterDistance(zz,input,model,options);
    return dl/((1+zz)**2*da);
  }

  return Object.freeze({
    VERSION,REVISION,C_KM_S,HUBBLE_TIME_100_GYR,DEFAULT_OR,DEFAULT_RD_MPC,CosmologyError,
    normalizeParams,normalizeModel,aOfZ,zOfA,bridgeScale,bridgeDeltaFromA,
    e2FromA,e2,E,dLnHdLnA,q,omegaM,validateBackgroundDomain,simpson,
    hubbleDistance,hubbleTimeGyr,radialComovingDistance,transverseComovingDistance,
    luminosityDistance,angularDiameterDistance,distanceModulus,ageGyr,lookbackTimeGyr,
    solveGrowth,growthAtZ,S8,baoDMOverRd,etheringtonRatio
  });
});
