import {advanceAdaptive,E,fractions,deceleration,dominantComponent,equalityPoints} from './numerics.js';
export class CosmologyController{
  constructor(){this.a=1e-3;this.tau=0;this.last={accepted:0,rejected:0};this.error=''}
  reset(){this.a=1e-3;this.tau=0;this.last={accepted:0,rejected:0};this.error=''}
  advance(deltaTau,p){const r=advanceAdaptive(this.a,deltaTau,p,{rtol:1e-8,atol:1e-11,initialStep:Math.min(deltaTau,1e-4)});this.last={accepted:r.accepted,rejected:r.rejected};if(!r.ok){this.error=r.reason;return false}this.a=r.a;this.tau+=deltaTau;this.error='';return true}
  snapshot(p){const f=fractions(this.a,p),q=deceleration(this.a,p),d=dominantComponent(this.a,p);return{a:this.a,tau:this.tau,E:E(this.a,p),fractions:f,q,dominant:d,equalities:equalityPoints(p),accepted:this.last.accepted,rejected:this.last.rejected,error:this.error}}
  serialize(){return{a:this.a,tau:this.tau,last:this.last,error:this.error}}
  restore(d){this.a=d.a??1e-3;this.tau=d.tau??0;this.last=d.last??{accepted:0,rejected:0};this.error=d.error??''}
}
