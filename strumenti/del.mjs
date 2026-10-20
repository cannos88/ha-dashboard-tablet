import fs from 'node:fs';
const token = fs.readFileSync(process.env.HA_TOKEN_FILE || 'ha_token.txt','utf8').trim();
const ws = new WebSocket((process.env.HA_URL || 'http://homeassistant.local:8123').replace(/^http/, 'ws') + '/api/websocket');
ws.onmessage = (e) => { const m = JSON.parse(e.data);
  if (m.type === 'auth_required') ws.send(JSON.stringify({type:'auth', access_token: token}));
  else if (m.type === 'auth_ok') ws.send(JSON.stringify({id:1, type:'lovelace/dashboards/list'}));
  else if (m.id === 1) { const d = m.result.find(x => x.url_path === (process.env.URLP || 'tablet-anteprima'));
    ws.send(JSON.stringify({id:2, type:'lovelace/dashboards/delete', dashboard_id: d.id})); }
  else if (m.id === 2) { console.log('delete', m.success); process.exit(0); } };
