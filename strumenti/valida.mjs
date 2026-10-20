import fs from 'node:fs';
const token = fs.readFileSync(process.env.HA_TOKEN_FILE || 'ha_token.txt','utf8').trim();
const ws = new WebSocket((process.env.HA_URL || 'http://homeassistant.local:8123').replace(/^http/, 'ws') + '/api/websocket');
ws.onmessage = (e) => { const m = JSON.parse(e.data);
  if (m.type === 'auth_required') ws.send(JSON.stringify({type:'auth', access_token: token}));
  else if (m.type === 'auth_ok') ws.send(JSON.stringify({id:1, type:'lovelace/config', url_path: process.argv[2], force: true}));
  else if (m.id === 1) { console.log(m.success ? 'OK views=' + m.result.views.map(v => v.path + ':' + (v.cards || v.sections || []).length).join(' ') + ' templates=' + Object.keys(m.result.button_card_templates).length : 'ERRORE ' + JSON.stringify(m.error)); process.exit(0); } };
