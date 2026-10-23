# Check the build-time line-art simplification (simplify_art.py) against the original drawing, rendered by Chrome.
# usage (from the ChaosApp folder):  python compare_art.py                 every data_*.json
#                                    python compare_art.py data_lct.json   just these
# Writes art-compare/<name>.png (original | simplified | difference) and prints how much ink moved. Under about 1%
# is invisible by eye; look at the picture anyway. Needs Playwright (pip install playwright) and Google Chrome.
import sys,os,json,glob
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_dilation
from simplify_art import simplify,polylines
from playwright.sync_api import sync_playwright
OUT='art-compare';os.makedirs(OUT,exist_ok=True)
files=sys.argv[1:] or sorted(glob.glob('data_*.json'))

def original_d(art):
    return ''.join('M'+f"{p[0][0]:g} {p[0][1]:g}"+('L'+' '.join(f"{x:g} {y:g}" for x,y in p[1:]) if len(p)>1 else '') for p in polylines(art))
def svg(vb,sw,d,W,H):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{W}" height="{H}"><path d="{d}" fill="none" stroke="#000" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/></svg>'
K=np.ones((3,3),bool)
def moved(A,B):   # ink in one with no ink within 1 px in the other, as % of the original's ink
    return ((A&~binary_dilation(B,K)).sum()+(B&~binary_dilation(A,K)).sum())/max(1,A.sum())*100
try:font=ImageFont.truetype('arial.ttf',20)
except OSError:font=ImageFont.load_default()

with sync_playwright() as pw:
    b=pw.chromium.launch(channel='chrome');pg=b.new_page()
    for fn in files:
        D=json.load(open(fn,encoding='utf-8'));S=simplify(D);sw=float(D.get('sw') or 6);vb=D['viewBox']
        _,_,vw,vh=map(float,vb.split());ims={}
        for W in (900,180):   # record-sheet size and roster-thumbnail size
            H=round(W*vh/vw);pg.set_viewport_size({'width':W,'height':H})
            for tag,d in (('o',original_d(D['art'])),('s',S['artPath'][9:-3])):
                pg.set_content('<body style="margin:0;background:#fff">'+svg(vb,sw,d,W,H)+'</body>')
                pg.screenshot(path=f'{OUT}/_t.png',clip={'x':0,'y':0,'width':W,'height':H})
                ims[tag,W]=Image.open(f'{OUT}/_t.png').convert('L').copy()
        A,B=(np.array(ims[t,900])<128 for t in 'os');a,bb=(np.array(ims[t,180])<128 for t in 'os')
        n0,n1=len(polylines(D['art'])),S['artPath'].count('M');k0,k1=len(D['art'])//1024,len(S['artPath'])//1024
        ov=np.full(A.shape+(3,),255,np.uint8);ov[A&B]=(185,185,185);ov[A&~binary_dilation(B,K)]=(220,0,0);ov[B&~binary_dilation(A,K)]=(0,90,255)
        W,H=ims['o',900].size;out=Image.new('RGB',(W*3+40,H+40),'white');dr=ImageDraw.Draw(out);name=fn[5:-5]
        for i,(im,t) in enumerate([(ims['o',900],f'{name} original: {n0} lines, {k0} KB'),(ims['s',900],f'simplified: {n1} lines, {k1} KB'),
                                   (Image.fromarray(ov),'difference: red = only original, blue = only new')]):
            out.paste(im.convert('RGB'),(i*(W+20),40));dr.text((i*(W+20)+6,8),t,fill='black',font=font)
        out.save(f'{OUT}/{name}.png')
        print(f"{fn:16s} lines {n0:5d} -> {n1:5d}   {k0:4d} KB -> {k1:3d} KB   ink moved {moved(A,B):.2f}% (thumbnail {moved(a,bb):.2f}%)",flush=True)
    b.close()
os.remove(f'{OUT}/_t.png')
