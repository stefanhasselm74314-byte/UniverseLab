import { chromium } from 'playwright';

const BASE=process.env.UNIVERSELAB_BASE_URL||'http://127.0.0.1:8000/';
const browser=await chromium.launch({headless:true});
try{
  const page=await browser.newPage({viewport:{width:1280,height:900},locale:'de-DE'});
  const errors=[];
  page.on('pageerror',error=>errors.push(String(error)));
  page.on('console',message=>{if(message.type()==='error')errors.push(`console: ${message.text()}`);});

  const url=new URL('compare-safe.html',BASE);
  url.searchParams.set('formula_refresh_audit',String(Date.now()));
  const response=await page.goto(url.href,{waitUntil:'networkidle',timeout:45000});
  if(!response?.ok())throw new Error(`HTTP ${response?.status()} ${url.href}`);
  await page.waitForFunction(()=>window.UniverseLabCompareSafe?.snapshot().revision>=1,{timeout:20000});

  const result=await page.evaluate(async()=>{
    const A=window.UniverseLabCompareSafe;
    const C=window.UniverseLabCosmology;
    const formula=document.getElementById('formula');
    const output=document.getElementById('fResult');
    const parse=text=>Number(String(text).replace(/\./g,'').replace(',','.').replace(/[^0-9eE+\-.]/g,''));
    const changeInput=async(id,value)=>{
      const before=A.snapshot().revision;
      const node=document.getElementById(id);
      node.value=String(value);
      node.dispatchEvent(new Event('input',{bubbles:true}));
      const deadline=performance.now()+10000;
      while(A.snapshot().revision<=before&&performance.now()<deadline){await new Promise(resolve=>setTimeout(resolve,20));}
      if(A.snapshot().revision<=before)throw new Error(`revision did not advance for ${id}`);
    };

    A.setView('formulas');
    formula.value='dh';
    formula.dispatchEvent(new Event('change',{bubbles:true}));
    const dhBefore=parse(output.textContent);
    await changeInput('beta',0.10);
    const dhAfter=parse(output.textContent);
    const s1=A.snapshot();
    const dhExpected=C.E(1,s1.params,'bridge')/C.E(1,s1.params,'lcdm')-1;

    formula.value='qeff';
    formula.dispatchEvent(new Event('change',{bubbles:true}));
    const qBefore=parse(output.textContent);
    await changeInput('Om',0.40);
    const qAfter=parse(output.textContent);
    const s2=A.snapshot();
    const qExpected=C.q(0,s2.params,'bridge');

    return {
      dhBefore,dhAfter,dhExpected,
      qBefore,qAfter,qExpected,
      status:s2.status,
      revisions:[s1.revision,s2.revision]
    };
  });

  const close=(a,b,tol=1e-6)=>Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<=tol;
  if(result.status!=='PASS')throw new Error(`unexpected status ${result.status}`);
  if(close(result.dhBefore,result.dhAfter,1e-9))throw new Error('dh formula did not refresh after beta update');
  if(!close(result.dhAfter,result.dhExpected,1e-6))throw new Error(`dh mismatch: ${JSON.stringify(result)}`);
  if(close(result.qBefore,result.qAfter,1e-9))throw new Error('qeff formula did not refresh after Om update');
  if(!close(result.qAfter,result.qExpected,1e-6))throw new Error(`qeff mismatch: ${JSON.stringify(result)}`);
  if(errors.length)throw new Error(`browser errors: ${JSON.stringify(errors)}`);

  console.log(JSON.stringify({schema:'universelab.compare-safe-formula-refresh-audit.v1',status:'PASS',...result},null,2));
}finally{
  await browser.close();
}
