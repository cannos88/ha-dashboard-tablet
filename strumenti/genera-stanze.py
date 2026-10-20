"""Genera la vista Stanze della dashboard Tablet e i popup delle stanze.

Un'unica tabella (STANZE, qui sotto) descrive ogni stanza: cosa conta la
tessera (luci, alim/alimDa, media, clima, sonde: la stessa mappatura della
dashboard Mobile) e cosa mostra il popup (luci con nome e icona, interruttori,
media, dati d'ambiente). Lo script scrive:
    tablet/vista-stanze.yaml       la griglia delle tessere
    tablet/popup-<id>.yaml         il contenuto del popup di ogni stanza
I popup sono costruiti con i template del tablet (sezione, luce_riga,
clima_quadrante, dato_stanza): stesso stile del resto della dashboard.
I file generati non vanno modificati a mano: si cambia qui e si rilancia.

Uso:
    python genera-stanze.py [cartella-tablet]
cartella-tablet di default: ../dashboards/tablet.
Prima di scrivere controlla via API che ogni entita' esista (serve il token nel file
HA_TOKEN_FILE, default ha_token.txt; URL in HA_URL); con --senza-verifica salta il controllo.
"""
import json
import os
import sys
import urllib.request

import yaml

QUI = os.path.dirname(os.path.abspath(__file__))
argomenti = [a for a in sys.argv[1:] if not a.startswith('--')]
USCITA = argomenti[0] if argomenti else os.path.join(QUI, '..', 'dashboards', 'tablet')
HA = os.environ.get('HA_URL', 'http://homeassistant.local:8123')
TOKEN = os.environ.get('HA_TOKEN_FILE', 'ha_token.txt')

# Icone (markup interno di un <svg> 24x24) delle tessere.
CUCINA = '<path d="M4 4h16v6H4zM7 14v6M12 14v6M17 14v6"/>'
DIVANO = '<rect x="3" y="10" width="18" height="8" rx="2"/><path d="M6 10V7a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v3"/>'
VASCA = '<path d="M4 12h16v3a4 4 0 0 1-4 4H8a4 4 0 0 1-4-4zM7 12V6a2 2 0 0 1 4 0"/>'
FOGLIA = '<path d="M12 20v-7M12 13c-4 0-6-3-6-6 4 0 6 2 6 6zM12 13c4 0 6-3 6-6-4 0-6 2-6 6z"/>'
LETTO = '<path d="M3 18v-9M3 13h18v5M7 10h4v3H7z"/>'
PERSONA = '<circle cx="12" cy="8" r="4"/><path d="M5 21c1-4 4-6 7-6s6 2 7 6"/>'
PORTA = '<path d="M6 21V4a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v17M4 21h16"/><circle cx="14.6" cy="12.4" r=".9"/>'
TETTO = '<path d="M12 3l9 8h-3v10H6V11H3zM10 21v-6h4v6"/>'
SCATOLA = ('<polyline points="21 8 21 21 3 21 3 8"/><rect x="1" y="3" width="22" height="5"/>'
           '<line x1="10" y1="12" x2="14" y2="12"/>')

PLAFONIERA = 'mdi:ceiling-light-outline'

# Ogni stanza:
#   tessera: entity (entita' principale), luci/alim/alimDa/media/clima/sonde come
#            nella Mobile (sono cio' che la tessera conta), extra_trigger
#   popup:   popup_luci [(entita', nome, icona, opzioni)], popup_media,
#            ambiente [(entita', nome, tipo)]
STANZE = [
    dict(id='cucina', nome='Cucina', icona=CUCINA, colore='#FF9F5A',
         entity='light.luci_interne_cucina',
         luci=['light.luci_interne_cucina', 'light.luci_tavolo_cucina'],
         media=['media_player.cucina_2'], sonde=['sensor.aqaracucina_temperature'],
         popup_luci=[('light.luci_interne_cucina', 'Luci interne', PLAFONIERA, {}),
                     ('light.luci_tavolo_cucina', 'Luce tavolo', 'mdi:lamp-outline', {}),
                     ('light.ledcucina', 'LED cucina', 'mdi:led-strip-variant', {})],
         popup_media=['media_player.cucina_2'],
         ambiente=[('sensor.aqaracucina_temperature', 'Temperatura', 'temperatura'),
                   ('sensor.aqaracucina_humidity', 'Umidità', 'umidita'),
                   ('sensor.aqaracucina_battery', 'Batteria sonda', 'batteria')]),
    dict(id='salotto', nome='Salotto', icona=DIVANO, colore='#F5B53D',
         entity='climate.condizionatore_salotto',
         luci=['light.luci_salotto', 'light.shellyplus1_80646fc7eaec_switch_0',
               'light.luce_tavolo_salotto', 'light.led_salotto', 'light.led_divano_2',
               'light.led_tv_salotto'],
         media=['media_player.salotto_2'],
         sonde=['sensor.aqarasalotto_temperature', 'sensor.netatmo_salotto_temperature'],
         clima='climate.condizionatore_salotto',
         popup_luci=[('light.luci_salotto', 'Luci salotto', 'mdi:ceiling-light', {}),
                     ('light.led_tv_salotto', 'LED TV', 'mdi:television-ambient-light', {}),
                     ('light.led_divano_2', 'LED divano', 'mdi:sofa-outline', {}),
                     ('light.luce_tavolo_salotto', 'Luce tavolo', 'mdi:floor-lamp', {}),
                     ('light.led_salotto', 'LED perimetro', 'mdi:led-strip', {}),
                     ('light.shellyplus1_80646fc7eaec_switch_0', 'Faretti', 'mdi:spotlight-beam', {})],
         popup_media=['media_player.salotto_2'],
         ambiente=[('sensor.aqarasalotto_temperature', 'Temperatura', 'temperatura'),
                   ('sensor.aqarasalotto_humidity', 'Umidità', 'umidita'),
                   ('sensor.netatmo_salotto_temperature', 'Netatmo', 'temperatura'),
                   ('sensor.netatmo_salotto_co2', 'CO₂', 'co2')]),
    dict(id='bagno-giu', nome='Bagno di sotto', icona=VASCA, colore='#5CC8FF',
         entity='light.luce_bagno_giu', luci=['light.luce_bagno_giu'],
         sonde=['sensor.aqarabagnogiu_temperature'],
         popup_luci=[('light.luce_bagno_giu', 'Luce', PLAFONIERA, {}),
                     ('input_boolean.automazione_luci_bagno_giu', 'Accensione automatica',
                      'mdi:motion-sensor', {'testo_on': 'Attiva', 'testo_off': 'Disattivata'})],
         ambiente=[('sensor.aqarabagnogiu_temperature', 'Temperatura', 'temperatura'),
                   ('sensor.aqarabagnogiu_humidity', 'Umidità', 'umidita'),
                   ('binary_sensor.movimentobagnogiu_presence', 'Presenza', 'presenza'),
                   ('sensor.movimentobagnogiu_illuminance', 'Luminosità', 'luce'),
                   ('sensor.aqarabagnogiu_battery', 'Batteria sonda', 'batteria'),
                   ('sensor.movimentobagnogiu_battery', 'Batteria sensore', 'batteria')]),
    dict(id='giardino', nome='Giardino', icona=FOGLIA, colore='#6FD39B',
         entity='switch.shelly_lucibbq_channel_1',
         # La zanzariera non e' una luce: sta nel popup ma non nel conteggio
         # (allineato alla Mobile il 5/10/2026).
         luci=['switch.shelly_lucibbq_channel_1'],
         extra_trigger=['switch.presazanzareporticato'],
         media=['media_player.casse_giardino_2'],
         sonde=['sensor.casa_rotondo_salotto_esterno_temperature'],
         popup_luci=[('switch.shelly_lucibbq_channel_1', 'Luci BBQ', 'mdi:string-lights', {}),
                     ('switch.presazanzareporticato', 'Zanzariera porticato', 'mdi:bug-outline', {})],
         popup_media=['media_player.casse_giardino_2'],
         ambiente=[('sensor.casa_rotondo_salotto_esterno_temperature', 'Temperatura esterna',
                    'temperatura')]),
    dict(id='matrimoniale', nome='Camera matrimoniale', icona=LETTO, colore='#B79CFF',
         entity='climate.condizionatore_matrimoniale',
         luci=['light.luce_letto_anna', 'light.luce_letto_marco',
               'light.camera_matrimoniale_luce_matrimoniale_luce_matrimoniale'],
         media=['media_player.decoder_camera'],
         sonde=['sensor.aqaracameramatrimoniale_temperature', 'sensor.netatmo_camera_temperature',
                'sensor.valvolatermostaticamatrimoniale_local_temperature'],
         clima='climate.condizionatore_matrimoniale',
         popup_luci=[('light.camera_matrimoniale_luce_matrimoniale_luce_matrimoniale',
                      'Luce principale', PLAFONIERA, {}),
                     ('light.luce_letto_anna', 'Letto Anna', 'mdi:lamp-outline', {}),
                     ('light.luce_letto_marco', 'Letto Marco', 'mdi:lamp-outline', {})],
         popup_media=['media_player.decoder_camera'],
         ambiente=[('sensor.aqaracameramatrimoniale_temperature', 'Temperatura', 'temperatura'),
                   ('sensor.aqaracameramatrimoniale_humidity', 'Umidità', 'umidita'),
                   ('sensor.netatmo_camera_temperature', 'Netatmo', 'temperatura'),
                   ('sensor.netatmo_camera_co2', 'CO₂', 'co2')]),
    dict(id='camera-luca', nome='Camera Luca', icona=PERSONA, colore='#FF7EB6',
         entity='climate.condizionatore_luca',
         luci=['light.nspanel_luca_relay_1', 'light.razzonotteluca'],
         alim=['light.luci_luca'], alimDa='light.nspanel_luca_relay_1',
         sonde=['sensor.aqaracameraluca_temperature', 'sensor.nspanel_luca_temperature'],
         clima='climate.condizionatore_luca',
         popup_luci=[('light.nspanel_luca_relay_1', 'Corrente', 'mdi:power-plug-outline', {}),
                     ('light.luci_luca', 'Lampadine', 'mdi:lightbulb-group-outline',
                      {'alimDa': 'light.nspanel_luca_relay_1'}),
                     ('light.razzonotteluca', 'Razzo notte', 'mdi:rocket-launch-outline', {})],
         ambiente=[('sensor.aqaracameraluca_temperature', 'Temperatura', 'temperatura'),
                   ('sensor.aqaracameraluca_humidity', 'Umidità', 'umidita'),
                   ('binary_sensor.balconeluca_contact', 'Balcone', 'apertura'),
                   ('sensor.nspanel_luca_temperature', 'NSPanel', 'temperatura'),
                   ('sensor.aqaracameraluca_battery', 'Batteria sonda', 'batteria'),
                   ('sensor.telecomandocameraluca_battery', 'Batteria telecomando', 'batteria')]),
    dict(id='camera-sofia', nome='Camera Sofia', icona=PERSONA, colore='#7DB4FF',
         entity='climate.condizionatore_sofia',
         luci=['light.luce_sofia', 'light.lucinottesofia_l1', 'light.lucinottesofia_l2'],
         sonde=['sensor.aqarasofia_temperature'], clima='climate.condizionatore_sofia',
         popup_luci=[('light.luce_sofia', 'Luce principale', PLAFONIERA, {}),
                     ('light.lucinottesofia_l1', 'Luna', 'mdi:moon-waning-crescent', {}),
                     ('light.lucinottesofia_l2', 'Nuvola', 'mdi:cloud-outline', {})],
         ambiente=[('sensor.aqarasofia_temperature', 'Temperatura', 'temperatura'),
                   ('sensor.aqarasofia_humidity', 'Umidità', 'umidita'),
                   ('binary_sensor.espkyogate_persiana_sofia', 'Persiana', 'apertura'),
                   ('sensor.aqarasofia_battery', 'Batteria sonda', 'batteria'),
                   ('sensor.tastilucinottesofia_battery', 'Batteria tasti', 'batteria')]),
    dict(id='bagno-su', nome='Bagno di sopra', icona=VASCA, colore='#5CC8FF',
         entity='light.luce_bagno_su', luci=['light.luce_bagno_su'],
         sonde=['sensor.aqarabagnosu_temperature'],
         popup_luci=[('light.luce_bagno_su', 'Luce', PLAFONIERA, {})],
         ambiente=[('sensor.aqarabagnosu_temperature', 'Temperatura', 'temperatura'),
                   ('sensor.aqarabagnosu_humidity', 'Umidità', 'umidita'),
                   ('binary_sensor.movimentobagnosu_presence', 'Presenza', 'presenza'),
                   ('sensor.movimentobagnosu_illuminance', 'Luminosità', 'luce'),
                   ('sensor.aqarabagnosu_battery', 'Batteria sonda', 'batteria'),
                   ('sensor.movimentobagnosu_battery', 'Batteria sensore', 'batteria')]),
    dict(id='corridoio', nome='Corridoio', icona=PORTA, colore='#A0AEC0',
         entity='light.corridoio_su_luce_corridoiosu_luce_corridoiosu',
         luci=['light.corridoio_su_luce_corridoiosu_luce_corridoiosu'],
         popup_luci=[('light.corridoio_su_luce_corridoiosu_luce_corridoiosu', 'Luce', PLAFONIERA, {})]),
    dict(id='sottotetto', nome='Sottotetto', icona=TETTO, colore='#4FD1C5',
         entity='climate.condizionatore_sottotetto',
         luci=['light.wled_triangoli', 'light.lucisottotetto'],
         media=['media_player.sottotetto'], sonde=['sensor.xiaomisottotetto_temperature'],
         clima='climate.condizionatore_sottotetto',
         popup_luci=[('light.lucisottotetto', 'Luci sottotetto', PLAFONIERA, {}),
                     ('light.wled_triangoli', 'Triangoli', 'mdi:triangle-outline', {})],
         popup_media=['media_player.sottotetto'],
         ambiente=[('sensor.xiaomisottotetto_temperature', 'Temperatura', 'temperatura'),
                   ('sensor.xiaomisottotetto_humidity', 'Umidità', 'umidita'),
                   ('sensor.xiaomisottotetto_battery', 'Batteria sonda', 'batteria')]),
    dict(id='ripostiglio', nome='Ripostiglio', icona=SCATOLA, colore='#A0AEC0',
         entity='light.luce_ripostiglio', luci=['light.luce_ripostiglio'],
         extra_trigger=['binary_sensor.portaripostiglio_contact'],
         popup_luci=[('light.luce_ripostiglio', 'Luce', PLAFONIERA, {})],
         ambiente=[('binary_sensor.portaripostiglio_contact', 'Porta', 'porta')]),
]

# Aspetto dei popup browser_mod: fondo, raggio e font della dashboard. Il popup
# vive fuori dalla vista e non eredita il tema tablet_bento.
STILE_POPUP = ("--popup-background-color: #0E1116; --popup-border-radius: 28px; "
               "--mdc-theme-surface: #0E1116; --primary-background-color: #0E1116; "
               "--ha-font-family-body: 'Plus Jakarta Sans', system-ui, sans-serif; "
               "--mdc-typography-font-family: 'Plus Jakarta Sans', system-ui, sans-serif; "
               "--mdc-typography-headline6-font-family: 'Plus Jakarta Sans', system-ui, sans-serif; "
               "--mdc-typography-headline6-font-weight: 800; --ha-font-weight-medium: 800; "
               "font-family: 'Plus Jakarta Sans', system-ui, sans-serif;")

INTESTAZIONE_VISTA = """\
# ===========================================================================
# VISTA "Stanze" - dashboard Tablet
# GENERATO da genera-stanze.py: non modificare qui, cambia la tabella STANZE
# nello script e rilancialo.
#
# Undici stanze in quattro colonne sotto un'intestazione che fa da riepilogo.
# I parametri della tessera (luci, clima, sonde, alim/alimDa) sono gli stessi
# della dashboard Mobile. Al tocco si apre il popup della stanza (browser_mod),
# costruito con i template del tablet.
# ===========================================================================
"""

NOTA_RIEPILOGO = """\
[[[
  var C = ['climate.condizionatore_luca', 'climate.condizionatore_sofia',
           'climate.condizionatore_matrimoniale', 'climate.condizionatore_salotto',
           'climate.condizionatore_sottotetto'];
  var a = 0;
  for (var i = 0; i < C.length; i++) {
    var s = states[C[i]];
    if (s && ['off', 'unavailable', 'unknown'].indexOf(s.state) < 0) a++;
  }
  var n = entity ? Number(entity.state) : 0;
  if (isNaN(n)) n = 0;
  return (n === 0 ? 'nessuna luce accesa' : (n === 1 ? '1 luce accesa' : n + ' luci accese')) +
    ' \\u00B7 ' + (a === 0 ? 'nessun clima acceso' : (a === 1 ? '1 clima acceso' : a + ' climi accesi'));
]]]"""


class Include(str):
    pass


class Scrivi(yaml.SafeDumper):
    pass


def _testo(dumper, dato):
    if '\n' in dato:
        return dumper.represent_scalar('tag:yaml.org,2002:str', dato, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', dato)


Scrivi.add_representer(str, _testo)
Scrivi.add_representer(Include, lambda d, v: d.represent_scalar('!include', str(v)))
Scrivi.ignore_aliases = lambda self, data: True


def dump(dato):
    return yaml.dump(dato, Dumper=Scrivi, allow_unicode=True, sort_keys=False, width=1000)


def stile_zona():
    """Il card_mod delle zone audio della vista Media: un solo posto per lo stile del player."""
    class L(yaml.SafeLoader):
        pass
    L.add_constructor('!include', lambda l, n: None)
    with open(os.path.join(USCITA, 'vista-media.yaml'), encoding='utf-8') as f:
        media = yaml.load(f, Loader=L)
    for card in media:
        if isinstance(card, dict) and card.get('type') == 'vertical-stack':
            for c in card['cards']:
                if c.get('type') == 'grid':
                    return c['cards'][0]['card_mod']
    sys.exit('Stile delle zone non trovato in vista-media.yaml')


def sezione(titolo, nota=None, entity=None, trigger=None):
    c = {'type': 'custom:button-card', 'template': 'sezione'}
    if entity:
        c['entity'] = entity
    if trigger:
        c['triggers_update'] = trigger
    c['variables'] = {'titolo': titolo}
    if nota:
        c['variables']['nota'] = nota
    return c


def nota_luci(ids):
    lista = ', '.join("'%s'" % i for i in ids)
    return ('[[[\n  var L = [%s];\n  var n = 0;\n'
            "  for (var i = 0; i < L.length; i++) if (states[L[i]] && states[L[i]].state === 'on') n++;\n"
            "  return n === 0 ? 'tutto spento' : (n === 1 ? '1 accesa' : n + ' accese');\n]]]" % lista)


def popup(s, stile):
    sinistra, destra = [], []
    luci = s.get('popup_luci', [])
    if luci:
        ids = [l[0] for l in luci if l[0].split('.')[0] in ('light', 'switch')]
        sinistra.append(sezione('Luci', nota_luci(ids), ids[0], ids[1:]))
        righe = []
        for ent, nome, icona, opz in luci:
            var = {'nome': nome, 'icona': icona}
            var.update(opz)
            righe.append({'type': 'custom:button-card', 'template': 'luce_riga',
                          'entity': ent, 'variables': var})
        sinistra.append({'type': 'grid', 'columns': 2, 'square': False, 'cards': righe})
    if s.get('popup_media'):
        sinistra.append(sezione('Musica'))
        for m in s['popup_media']:
            sinistra.append({'type': 'custom:mini-media-player', 'entity': m, 'artwork': 'default',
                             'group': True, 'card_mod': stile})
    if s.get('clima'):
        destra.append(sezione('Clima'))
        destra.append({'type': 'custom:button-card', 'template': 'clima_quadrante',
                       'entity': s['clima'],
                       'variables': {'sonde': s.get('sonde', []), 'modi': True},
                       'styles': {'card': [{'height': '372px'}]}})
    if s.get('ambiente'):
        destra.append(sezione('Ambiente'))
        dati = [{'type': 'custom:button-card', 'template': 'dato_stanza', 'entity': e,
                 'variables': {'nome': n, 'tipo': t}} for e, n, t in s['ambiente']]
        destra.append({'type': 'grid', 'columns': 2, 'square': False, 'cards': dati})
    colonne = [c for c in (sinistra, destra) if c]
    return {'type': 'custom:layout-card', 'layout_type': 'custom:grid-layout',
            'layout': {'grid-template-columns': ' '.join(['minmax(0, 1fr)'] * len(colonne)),
                       'grid-gap': '20px', 'margin': '0', 'padding': '0 4px 8px'},
            'cards': [{'type': 'vertical-stack', 'cards': c} for c in colonne]}


def tessera(s):
    var = {'nome': s['nome'], 'icona': s['icona'], 'colore': s['colore'], 'apre': True}
    for k in ('luci', 'alim', 'alimDa', 'media', 'sonde', 'clima'):
        if s.get(k):
            var[k] = s[k]
    trigger = [e for k in ('luci', 'alim', 'media', 'sonde') for e in s.get(k, [])
               if e != s['entity']] + s.get('extra_trigger', [])
    if s.get('clima') and s['clima'] != s['entity']:
        trigger.append(s['clima'])
    c = {'type': 'custom:button-card', 'template': 'stanza_tablet', 'entity': s['entity']}
    if trigger:
        c['triggers_update'] = list(dict.fromkeys(trigger))
    c['tap_action'] = {'action': 'fire-dom-event', 'browser_mod': {
        'service': 'browser_mod.popup',
        'data': {'title': s['nome'], 'size': 'wide', 'style': STILE_POPUP,
                 'content': Include('popup-%s.yaml' % s['id'])}}}
    c['variables'] = var
    return c


def entita_usate():
    for s in STANZE:
        for k in ('entity', 'clima', 'alimDa'):
            if s.get(k):
                yield s[k]
        for k in ('luci', 'alim', 'media', 'sonde', 'popup_media', 'extra_trigger'):
            yield from s.get(k, [])
        for l in s.get('popup_luci', []):
            yield l[0]
            if l[3].get('alimDa'):
                yield l[3]['alimDa']
        for a in s.get('ambiente', []):
            yield a[0]


def verifica():
    token = open(TOKEN, encoding='utf-8').read().strip()
    req = urllib.request.Request(HA + '/api/states', headers={'Authorization': 'Bearer ' + token})
    esistenti = {s['entity_id'] for s in json.load(urllib.request.urlopen(req))}
    mancanti = sorted(set(entita_usate()) - esistenti)
    if mancanti:
        sys.exit('Entita\' inesistenti: ' + ', '.join(mancanti))


def main():
    if '--senza-verifica' not in sys.argv:
        verifica()
    stile = stile_zona()
    for s in STANZE:
        with open(os.path.join(USCITA, 'popup-%s.yaml' % s['id']), 'w', encoding='utf-8',
                  newline='\n') as f:
            f.write('# GENERATO da genera-stanze.py: popup della stanza "%s".\n'
                    '# Non modificare qui: cambia la tabella STANZE e rilancia lo script.\n'
                    % s['nome'] + dump(popup(s, stile)))
    vista = [Include('rail.yaml'), Include('testata.yaml'), {
        'type': 'vertical-stack',
        'view_layout': {'grid-column': '3 / span 12', 'grid-row': 3},
        'cards': [
            {'type': 'custom:button-card', 'template': 'sezione', 'entity': 'sensor.luci_accese',
             'triggers_update': ['climate.condizionatore_salotto', 'climate.condizionatore_luca',
                                 'climate.condizionatore_sofia', 'climate.condizionatore_matrimoniale',
                                 'climate.condizionatore_sottotetto'],
             'variables': {'titolo': 'Tutta la casa', 'nota': NOTA_RIEPILOGO}},
            {'type': 'grid', 'columns': 4, 'square': False, 'cards': [tessera(s) for s in STANZE]},
            # Alfred, il robot aspirapolvere: file scritto a mano, non generato.
            Include('alfred.yaml'),
        ]}]
    with open(os.path.join(USCITA, 'vista-stanze.yaml'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(INTESTAZIONE_VISTA + dump(vista))
    print('scritte %d stanze in %s' % (len(STANZE), USCITA))


if __name__ == '__main__':
    main()
