import json,re,sys
src=json.load(open(sys.argv[1])); out=json.load(open(sys.argv[2]))
bad=0
for it in src:
    k=it['k']; v=out.get(k)
    if v is None: print('FALTA',k[:80]); bad+=1; continue
    ph=lambda s: sorted(re.findall(r'\{\d+\}',s)); tg=lambda s: sorted(re.findall(r'<[^>]+>',s))
    if ph(k)!=ph(v): print('MARCADORES',k[:60],'|',v[:60]); bad+=1
    if tg(k)!=tg(v): print('ETIQUETAS',k[:60],'|',v[:60]); bad+=1
extra=set(out)-set(i['k'] for i in src)
if extra: print('CLAVES DE MÁS',len(extra)); bad+=len(extra)
print('errores',bad,'de',len(src))
