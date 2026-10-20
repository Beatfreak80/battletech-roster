# Build the single-file app: inline each chassis's drawing data into template.html.
import json,re
t=open('template.html',encoding='utf-8').read()
for key,f in [('__DATA_KGC__','data_kgc.json'),('__DATA_SDR__','data_sdr.json'),('__DATA_BLR__','data_blr.json'),('__DATA_BJ__','data_bj.json'),('__DATA_CGR__','data_cgr.json'),('__DATA_DRG__','data_drg.json'),('__DATA_AS7__','data_as7.json'),('__DATA_CPLT__','data_cplt.json'),('__DATA_CN9__','data_cn.json'),('__DATA_CDA__','data_cda.json'),('__DATA_CP10__','data_cp.json'),('__DATA_FS9__','data_fs.json'),('__DATA_LCT__','data_lct.json'),('__DATA_WTH__','data_wth.json'),('__DATA_CRB__','data_crb.json'),('__DATA_ENF__','data_enf.json')]:
    t=t.replace(key,json.dumps(json.load(open(f,encoding='utf-8')),separators=(',',':')))
open('battletech-roster.html','w',encoding='utf-8',newline='\n').write(t)
open('index.html','w',encoding='utf-8',newline='\n').write(t)   # the page GitHub Pages serves
open('chk.js','w',encoding='utf-8',newline='\n').write(re.search(r'<script>(.*)</script>',t,re.S).group(1))
print('built; now run: node --check chk.js')
