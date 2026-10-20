import re
from PIL import Image, ImageDraw
src=open('Locust.svg').read()
im=Image.new('L',(1920,1080),255);d=ImageDraw.Draw(im)
xs=[];ys=[]
for p in re.findall(r'points="([^"]+)"',src):
    n=[float(v) for v in p.replace(',',' ').split()]
    pts=list(zip(n[0::2],n[1::2]));xs+=n[0::2];ys+=n[1::2]
    if len(pts)==1:pts=pts*2
    d.line(pts,fill=0,width=6,joint='curve')
    for x,y in (pts[0],pts[-1]):d.ellipse((x-3,y-3,x+3,y+3),fill=0)
im.save('lc.png');print(min(xs),max(xs),min(ys),max(ys))
