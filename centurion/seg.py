import numpy as np, json, base64, io, re
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
a=np.array(Image.open('cn.png').convert('L')); H,W=a.shape
line=a<160
closed=ndi.binary_dilation(line,iterations=3)
lab,n=ndi.label(~closed)
border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
for x,y in [(825,545),(1090,545)]:border.add(lab[y,x])
P={
 'RA':[(680,330),(812,330),(812,512),(826,512),(826,596),(806,650),(680,662)],
 'RT':[(812,378),(910,378),(910,582),(826,582),(826,512),(812,512)],
 'CT':[(910,378),(1007,378),(1007,582),(910,582)],
 'LT':[(1007,378),(1104,378),(1104,582),(1007,582)],
 'LA':[(1104,330),(1240,330),(1240,830),(1104,830)],
 'RL':[(680,662),(806,650),(826,596),(826,582),(958,582),(958,1060),(680,1060)],
 'LL':[(958,582),(1104,582),(1104,830),(1240,830),(1240,1060),(958,1060)],
 'HD':[(880,190),(1035,190),(1035,378),(880,378)],
}
order=['RA','RT','CT','LT','LA','RL','LL','HD']
locmap=np.zeros((H,W),np.uint8)
for i,k in enumerate(order,1):
    im=Image.new('L',(W,H),0);ImageDraw.Draw(im).polygon(P[k],fill=1);locmap[np.array(im)==1]=i
assign=np.zeros((H,W),np.uint8)
for c in range(1,n+1):
    if c in border:continue
    m=lab==c;vals=locmap[m];vals=vals[vals>0]
    if len(vals)==0:continue
    cnt=np.bincount(vals,minlength=len(order)+1)
    assign[m]=cnt.argmax() if cnt.max()>=0.85*len(vals) else locmap[m]
# the outline is drawn 4px wide: regions come from the 6px render (keeps small gaps closed),
# but the outside is trimmed right up to the 4px line so no fill shows beyond it
line4=np.array(Image.open('cn4.png').convert('L'))<160
ext=np.isin(lab,list(border));ext=ndi.binary_dilation(ext,iterations=4)&~line4
d,(iy,ix)=ndi.distance_transform_edt(assign==0,return_indices=True)
full=assign[iy,ix];full[ext]=0
cols=[(0,0,0),(230,80,80),(240,160,60),(240,220,60),(80,200,120),(60,160,230),(150,90,220),(220,90,180),(40,40,40)]
rgb=np.full(a.shape+(3,),255,np.uint8)
for i in range(1,9):rgb[full==i]=cols[i]
rgb[line]=0
Image.fromarray(rgb).crop((680,190,1240,1060)).save('preview.png')
np.save('full.npy',full);json.dump(order,open('order.json','w'))
