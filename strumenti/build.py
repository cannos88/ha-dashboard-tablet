# Risolve gli !include come HA e scrive la config della dashboard in JSON.
import yaml, json, os, sys
class L(yaml.SafeLoader): pass
def inc(loader, node):
    p = os.path.join(os.path.dirname(loader.name), loader.construct_scalar(node))
    if not os.path.exists(p): return [] 
    with open(p, encoding='utf-8') as f:
        l = L(f); l.name = p
        try: return l.get_single_data()
        finally: l.dispose()
L.add_constructor('!include', inc)
src = sys.argv[1]
with open(src, encoding='utf-8') as f:
    l = L(f); l.name = src; cfg = l.get_single_data()
json.dump(cfg, open('config.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('views', [v['path'] for v in cfg['views']], 'cards', [len(v['cards']) for v in cfg['views']])
