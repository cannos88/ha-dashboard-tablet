import fs from 'node:fs';
const token = fs.readFileSync(process.env.HA_TOKEN_FILE || 'ha_token.txt','utf8').trim();
const URLP = process.env.URLP || 'tablet-anteprima';
const ws = new WebSocket((process.env.HA_URL || 'http://homeassistant.local:8123').replace(/^http/, 'ws') + '/api/websocket');
let id = 0; const pend = {};
const send = (msg) => new Promise(r => { const i = ++id; pend[i] = r; ws.send(JSON.stringify({id: i, ...msg})); });
ws.onmessage = async (e) => {
  const m = JSON.parse(e.data);
  if (m.type === 'auth_required') ws.send(JSON.stringify({type: 'auth', access_token: token}));
  else if (m.type === 'auth_ok') main();
  else if (m.id && pend[m.id]) { pend[m.id](m); delete pend[m.id]; }
};
async function main() {
  const list = await send({type: 'lovelace/dashboards/list'});
  if (!list.result.find(d => d.url_path === URLP)) {
    const c = await send({type: 'lovelace/dashboards/create', url_path: URLP, title: URLP,
      icon: 'mdi:tablet', mode: 'storage', require_admin: true, show_in_sidebar: false});
    console.log('create', c.success, c.error || '');
  }
  const cfg = JSON.parse(fs.readFileSync(process.env.CFG || 'config.json', 'utf8'));
  const s = await send({type: 'lovelace/config/save', url_path: URLP, config: cfg});
  console.log('save', s.success, s.error || '');
  ws.close(); process.exit(0);
}
