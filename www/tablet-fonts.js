// ===========================================================================
// Carica Inter e JetBrains Mono per la dashboard Tablet.
//
// Perche' un modulo JS e non un @import dentro card-mod: le regole di
// card-mod finiscono negli shadow root delle card, e un @import CSS dentro
// uno shadow root e' inaffidabile. Le @font-face vanno dichiarate a livello
// di DOCUMENTO: da li' vengono ereditate da tutti gli shadow root, che e'
// esattamente quello che serve a una dashboard fatta di custom card.
//
// Il tema tablet_neumorphic_black dichiara 'Inter' e 'JetBrains Mono' come
// famiglie, ma nessuno caricava i file: il pannello rendeva tutto col font
// di sistema. Da qui la distanza dal mockup anche dove la struttura era
// corretta, visto che il mock usa pesi da 300 a 900.
//
// Registrato in configuration.yaml sotto frontend > extra_module_url.
// ===========================================================================
(function () {
  var ID = 'dashboard-tablet-fonts';
  if (document.getElementById(ID)) return;

  // Preconnect: taglia un round trip sul primo caricamento del pannello.
  [['preconnect', 'https://fonts.googleapis.com', false],
   ['preconnect', 'https://fonts.gstatic.com', true]].forEach(function (p) {
    var l = document.createElement('link');
    l.rel = p[0];
    l.href = p[1];
    if (p[2]) l.crossOrigin = 'anonymous';
    document.head.appendChild(l);
  });

  var link = document.createElement('link');
  link.id = ID;
  link.rel = 'stylesheet';
  link.href = 'https://fonts.googleapis.com/css2' +
    '?family=Inter:wght@300;400;500;600;700;800;900' +
    '&family=JetBrains+Mono:wght@400;500;600;700' +
    '&family=Plus+Jakarta+Sans:wght@400;500;600;700;800' +
    '&display=swap';
  document.head.appendChild(link);
})();

// ===========================================================================
// RITORNO ALLA PANORAMICA (5/10/2026)
// Il pannello a parete restava sull'ultima vista toccata. Dopo INATTIVITA
// senza tocchi torna a /dashboard-tablet/casa (la Panoramica) e chiude un
// eventuale popup browser_mod. Vale solo sulla dashboard Tablet e solo con
// input_boolean.kiosk_tablet acceso: con il kiosk spento si sta configurando
// e il pannello non deve scappare via.
// Sta in questo modulo perche' e' gia' caricato da frontend.extra_module_url:
// un modulo nuovo richiederebbe di riavviare HA.
// ===========================================================================
(function () {
  if (window.__ritornoTablet) return;
  window.__ritornoTablet = true;
  var INATTIVITA = 3 * 60 * 1000;
  var HOME = '/dashboard-tablet/casa';
  var ultimo = Date.now();
  ['pointerdown', 'touchstart', 'keydown', 'wheel'].forEach(function (ev) {
    window.addEventListener(ev, function () { ultimo = Date.now(); }, {capture: true, passive: true});
  });
  setInterval(function () {
    var p = location.pathname;
    if (p.indexOf('/dashboard-tablet') !== 0 || p === HOME) { ultimo = Date.now(); return; }
    if (Date.now() - ultimo < INATTIVITA) return;
    var ha = document.querySelector('home-assistant');
    var k = ha && ha.hass && ha.hass.states['input_boolean.kiosk_tablet'];
    if (!k || k.state !== 'on') { ultimo = Date.now(); return; }
    try {
      var pop = ha.shadowRoot && ha.shadowRoot.querySelector('browser-mod-popup');
      if (pop && typeof pop.closeDialog === 'function') pop.closeDialog();
    } catch (e) {}
    history.pushState(null, '', HOME);
    window.dispatchEvent(new CustomEvent('location-changed', {detail: {replace: false}}));
    ultimo = Date.now();
  }, 15000);
})();
