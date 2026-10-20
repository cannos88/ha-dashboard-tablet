import { spawn } from 'node:child_process';
import fs from 'node:fs';
const token = fs.readFileSync(process.env.HA_TOKEN_FILE || 'ha_token.txt','utf8').trim();
const views = process.argv.slice(2).length ? process.argv.slice(2) : ['salotto','accessi','energia','stanze','media'];
const HA = process.env.HA_URL || 'http://homeassistant.local:8123';
const chrome = spawn(process.env.CHROME || 'C:/Program Files/Google/Chrome/Application/chrome.exe',
  ['--headless=new','--remote-debugging-port=9333','--user-data-dir='+process.cwd()+'/prof','--window-size=1280,800','--hide-scrollbars','about:blank']);
await new Promise(r=>setTimeout(r,2500));
const tabs = await (await fetch('http://127.0.0.1:9333/json')).json();
const ws = new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
await new Promise(r=>ws.onopen=r);
let id=0; const pend={};
ws.onmessage=e=>{const m=JSON.parse(e.data); if(m.id&&pend[m.id]){pend[m.id](m.result); delete pend[m.id];}};
const send=(method,params={})=>new Promise(r=>{const i=++id;pend[i]=r;ws.send(JSON.stringify({id:i,method,params}));});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
await send('Emulation.setDeviceMetricsOverride',{width:1280,height:800,deviceScaleFactor:1,mobile:false});
await send('Page.navigate',{url:HA+'/'}); await sleep(3000);
const tok={access_token:token,token_type:'Bearer',expires_in:1e9,hassUrl:HA,clientId:HA+'/',expires:Date.now()+1e12,refresh_token:''};
await send('Runtime.evaluate',{expression:`localStorage.setItem('hassTokens',${JSON.stringify(JSON.stringify(tok))})`});
for (const v of views){
  await send('Page.navigate',{url:`${HA}/dashboard-tablet-yaml/${v}`.replace('dashboard-tablet-yaml', process.env.DASH||'dashboard-tablet')});
  await sleep(9000);
  const r=await send('Page.captureScreenshot',{format:'png'});
  fs.writeFileSync(`${v}.png`,Buffer.from(r.data,'base64'));
  console.log('saved',v);
}
chrome.kill(); process.exit(0);
