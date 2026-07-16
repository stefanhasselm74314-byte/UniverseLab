export class CellularAutomaton {
  constructor(size = 120) { this.N=size; this.cells=new Uint8Array(size*size); this.next=new Uint8Array(size*size); this.generation=0; }
  setSize(n){n=Math.max(40,Math.min(260,n));if(n===this.N)return;const old=this.cells,oldN=this.N;this.N=n;this.cells=new Uint8Array(n*n);this.next=new Uint8Array(n*n);for(let y=0;y<n;y++)for(let x=0;x<n;x++)this.cells[y*n+x]=old[Math.min(oldN-1,Math.floor(y*oldN/n))*oldN+Math.min(oldN-1,Math.floor(x*oldN/n))]}
  clear(){this.cells.fill(0);this.generation=0}
  seed(kind,density,rng){this.clear();const p=density/100,N=this.N;if(kind==='random'){for(let i=0;i<this.cells.length;i++)this.cells[i]=rng()<p}else if(kind==='bigbang'){const r=N*.055,cx=N/2,cy=N/2;for(let y=0;y<N;y++)for(let x=0;x<N;x++)if((x-cx)**2+(y-cy)**2<r*r)this.cells[y*N+x]=rng()<.58}else if(kind==='symmetry'){for(let y=10;y<N/2;y++)for(let x=10;x<N/2;x++)if(rng()<p){this.cells[y*N+x]=1;this.cells[y*N+N-1-x]=1;this.cells[(N-1-y)*N+x]=1;this.cells[(N-1-y)*N+N-1-x]=1}}else{for(let k=0;k<36;k++){const x=5+Math.floor(rng()*(N-10)),y=5+Math.floor(rng()*(N-10));for(const[dx,dy]of[[1,0],[2,1],[0,2],[1,2],[2,2]])this.cells[(y+dy)*N+x+dx]=1}}}
  step(ruleText,noise,rng){const [b,s]=ruleText.split('/'),born=new Set([...b.slice(1)].map(Number)),survive=new Set([...s.slice(1)].map(Number)),N=this.N,q=noise/100000;for(let y=0;y<N;y++)for(let x=0;x<N;x++){let n=0;for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++)if(dx||dy)n+=this.cells[((y+dy+N)%N)*N+(x+dx+N)%N];const i=y*N+x;this.next[i]=((this.cells[i]?survive.has(n):born.has(n))||rng()<q)?1:0}[this.cells,this.next]=[this.next,this.cells];this.generation++}
  liveCount(){return this.cells.reduce((a,b)=>a+b,0)}
  paint(x,y){if(x>=0&&y>=0&&x<this.N&&y<this.N)this.cells[y*this.N+x]=1}
  serialize(){return{N:this.N,generation:this.generation,cells:[...this.cells]}}
  restore(d){this.N=d.N;this.generation=d.generation||0;this.cells=Uint8Array.from(d.cells||[]);this.next=new Uint8Array(this.N*this.N)}
}
