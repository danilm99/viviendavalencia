# Une claves recogidas de cada página con va_all.json y actualiza los va-*.js (sin borrar claves existentes)
import json,subprocess,sys,os
SITE='/home/claude/pisos-turisticos'
src=open(SITE+'/va-informe.js').read(); TRAILER=src[src.index('};\n(function')+2:]
va=json.load(open('va_all.json'))
pages=[('index.html','va-inicio.js',None),('informe-vivienda-valencia.html','va-informe.js','steps_informe.js'),('pisos-turisticos-valencia.html','va-mapa.js','steps_mapa.js'),('elecciones-29n.html','va-elecciones.js',None)]
tot=0
for html,dj,steps in pages:
    out='k_tmp.json'; cmd=['node','harvest.js',SITE+'/'+html,out]+([steps] if steps else [])
    subprocess.run(cmd,check=True,capture_output=True)
    keys=[k for k,_ in json.load(open(out))['keys']]
    p=SITE+'/'+dj; d={}
    if os.path.exists(p):
        s=open(p).read(); pre='window.VA_DICT='; end=s.find('};\n(function'); d=json.loads(s[len(pre):end+1] if end>0 else s[len(pre):].rstrip().rstrip(';'))
    miss=[]
    for k in keys:
        if k in va:
            if va[k]!=k or k in d: d[k]=va[k]
        elif k not in d: miss.append(k)
    open(p,'w').write('window.VA_DICT='+json.dumps(d,ensure_ascii=False)+';'+TRAILER)
    print(dj,len(d),'faltan',len(miss)); [print('   ',repr(m[:120])) for m in miss[:30]]; tot+=len(miss)
print('total faltan',tot)
