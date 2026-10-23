# Simplify a chassis's line art for the app: the record-sheet drawings arrive as thousands of short, densely sampled
# polylines. Drawn 4-6 units thick, most of those points make no visible difference. This
#   1. joins lines whose ends meet (only where exactly two ends meet, so junctions stay as they are),
#   2. drops points that sit within TOL units of the line through their neighbours (Ramer-Douglas-Peucker),
#   3. drops short pieces lying right on top of another line (every point within COVER x stroke width of it),
#   4. writes the result as one compact path: whole units, each point relative to the last.
# Checked against Chrome renders of the original: no visible change at record-sheet or thumbnail size.
import math,re
from collections import defaultdict

TOL=1.0      # units a point may sit off the line before it's kept
COVER=0.15   # a short piece is dropped only if every point lies within COVER x stroke width of another line
JOIN=0.6     # ends this close (units) count as meeting

def polylines(art):
    return [[tuple(map(float,p.split(','))) for p in m.split()] for m in re.findall(r'points="([^"]+)"',art)]

def dseg(p,a,b):
    ax,ay=a;dx,dy=b[0]-ax,b[1]-ay;L=dx*dx+dy*dy
    t=0 if L==0 else max(0,min(1,((p[0]-ax)*dx+(p[1]-ay)*dy)/L));return math.hypot(p[0]-ax-t*dx,p[1]-ay-t*dy)

def rdp(pts,tol=TOL):
    if len(pts)<3:return pts
    keep=[False]*len(pts);keep[0]=keep[-1]=True;st=[(0,len(pts)-1)]
    while st:
        a,b=st.pop();best,bi=-1,None
        for i in range(a+1,b):
            d=dseg(pts[i],pts[a],pts[b])   # to the segment, not the infinite line: a line that runs out and
            if d>best:best,bi=d,i          # doubles back must keep its turnaround point
        if bi is not None and best>tol:keep[bi]=True;st+=[(a,bi),(bi,b)]
    return [p for p,k in zip(pts,keep) if k]

def join(P,eps=JOIN):
    P=[list(p) for p in P if p];key=lambda e:(round(e[0]/eps),round(e[1]/eps))
    while True:
        ends=defaultdict(list)
        for i,p in enumerate(P):
            if len(p)<2 or math.dist(p[0],p[-1])<eps:continue   # dots and closed loops stay as they are
            ends[key(p[0])].append((i,0));ends[key(p[-1])].append((i,1))
        merged=False;used=set()
        for v in ends.values():
            if len(v)!=2:continue
            (i,ei),(j,ej)=v
            if i==j or i in used or j in used:continue
            a=P[i] if ei==1 else P[i][::-1];b=P[j] if ej==0 else P[j][::-1]
            P[i]=a+b[1:];P[j]=None;used|={i,j};merged=True
        P=[p for p in P if p]
        if not merged:return P

def uncovered(P,sw,frac=COVER):
    G=8.0;grid=defaultdict(list)
    segs=[(i,a,b) for i,p in enumerate(P) for a,b in (zip(p,p[1:]) if len(p)>1 else [(p[0],p[0])])]
    for s,(i,a,b) in enumerate(segs):
        for gx in range(int(min(a[0],b[0])//G)-1,int(max(a[0],b[0])//G)+2):
            for gy in range(int(min(a[1],b[1])//G)-1,int(max(a[1],b[1])//G)+2):grid[(gx,gy)].append(s)
    length=lambda p:sum(math.dist(a,b) for a,b in zip(p,p[1:]))
    lim=frac*sw;drop=set()
    for i in sorted(range(len(P)),key=lambda i:length(P[i])):
        p=P[i]
        if length(p)>3*sw:break
        smp=[p[0]]+[(a[0]+(b[0]-a[0])*t/4,a[1]+(b[1]-a[1])*t/4) for a,b in zip(p,p[1:]) for t in range(1,5)]
        if all(any(segs[s][0]!=i and segs[s][0] not in drop and dseg(q,segs[s][1],segs[s][2])<=lim
                   for s in grid[(int(q[0]//G),int(q[1]//G))]) for q in smp):drop.add(i)
    return [p for i,p in enumerate(P) if i not in drop]

def path_d(P):
    out=[]
    for p in P:
        r=[(round(x),round(y)) for x,y in p];s=[r[0]]
        for t in r[1:]:
            if t!=s[-1]:s.append(t)
        out.append(f"M{s[0][0]} {s[0][1]}"+('l'+' '.join(f"{x-px} {y-py}" for (px,py),(x,y) in zip(s,s[1:])) if len(s)>1 else 'l0 0'))
    return ''.join(out).replace(' -','-')

def simplify(data):
    """Returns the chassis data with its art replaced by a ready-made artPath (what the app's artOf() would build)."""
    sw=float(data.get('sw') or 6)
    P=uncovered([rdp(p) for p in join(polylines(data['art']))],sw)
    return {**data,'art':'','artPath':f'<path d="{path_d(P)}"/>'}
