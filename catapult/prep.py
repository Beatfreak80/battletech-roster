# copy Catapult.svg, adding each circle path (the LRM tube rings) as a closed polyline so the line-art pipeline can use it
import re, math
src=open('../../Fancy Gary Record Sheets/Catapult.svg').read()
def circles(d):
    # each path is "m x,y a r r 0 0 1 ... z m dx,dy a R R ..." : two concentric-ish rings, the arc start is the circle's rightmost point
    out=[];x=y=0.0
    for m in re.finditer(r'm\s*([-\d.]+),([-\d.]+)\s*a\s*([-\d.]+),([-\d.]+)',d):
        x+=float(m.group(1));y+=float(m.group(2));r=float(m.group(3));out.append((x-r,y,r))
    return out
extra=[]
for g in re.finditer(r'<g[^>]*transform="([^"]+)"[^>]*>(.*?)</g>',src,re.S):
    t=g.group(1);n=[float(v) for v in re.findall(r'[-\d.]+',t)]
    if t.startswith('translate'):a,b,c,d,e,f=1,0,0,1,n[0],n[1]
    else:a,b,c,d,e,f=n
    for p in re.findall(r'\sd="([^"]+)"',g.group(2)):
        for cx,cy,r in circles(p):
            pts=[(cx+r*math.cos(2*math.pi*i/24),cy+r*math.sin(2*math.pi*i/24)) for i in range(25)]
            pts=[(a*x+c*y+e,b*x+d*y+f) for x,y in pts]
            extra.append('<polyline points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in pts)+'"/>')
extra=list(dict.fromkeys(extra))   # the drawing repeats some rings
out=src.replace('</svg>','\n'.join(extra)+'\n</svg>')
open('Catapult.svg','w').write(out);print(len(extra),'rings added')
