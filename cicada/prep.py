# copy Cicada.svg, baking the few transformed polylines into plain coordinates and turning the one <path> into a polyline
import re
src=open('../../Fancy Gary Record Sheets/Cicada.svg').read()
def mat(t):
    n=[float(v) for v in re.findall(r'[-\d.]+',t)]
    return (1,0,0,1,n[0],n[1]) if t.startswith('translate') else tuple(n)
def fix(m):
    el=m.group(0);t=re.search(r'transform="([^"]+)"',el)
    if not t:return el
    a,b,c,d,e,f=mat(t.group(1));n=[float(v) for v in re.search(r'points="([^"]+)"',el).group(1).replace(',',' ').split()]
    pts=' '.join(f'{a*x+c*y+e:.3f},{b*x+d*y+f:.3f}' for x,y in zip(n[0::2],n[1::2]))
    el=re.sub(r'points="[^"]+"',f'points="{pts}"',el);return re.sub(r'\s*transform="[^"]+"','',el)
out=re.sub(r'<polyline.*?/>',fix,src,flags=re.S)
# path648: "m 770.15094,522.40305 0.22329,44.65937" (relative line)
out=out.replace('</svg>','<polyline points="770.15094,522.40305 770.37423,567.06242"/>\n</svg>')
open('Cicada.svg','w').write(out);print('ok')
