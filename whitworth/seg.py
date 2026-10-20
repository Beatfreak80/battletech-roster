import numpy as np, json, base64, io, re
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
a=np.array(Image.open('wh.png').convert('L')); H,W=a.shape
line=a<160
closed=ndi.binary_dilation(line,iterations=3)
lab,n=ndi.label(~closed)
border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
for x,y in []:border.add(lab[y,x])
border.discard(0)
P={
 'RL':[(700,512),(960,512),(960,880),(945,880),(945,1000),(700,1000)],
 'LL':[(960,512),(1240,512),(1240,1000),(945,1000),(945,880),(960,880)],
 'RT':[(803,268),(876,268),(876,512),(803,512)],
 'CT':[(876,268),(1048,268),(1048,512),(876,512)],
 'LT':[(1048,268),(1116,268),(1116,512),(1048,512)],
 'RA':[(700,268),(803,268),(803,516),(700,516)],
 'LA':[(1116,268),(1240,268),(1240,516),(1116,516)],
 'HD':[(840,110),(1080,110),(1080,268),(840,268)],
}
# legs split the pelvis down the centre line; later shapes overwrite earlier ones
draw=['RL','LL','RT','CT','LT','RA','LA','HD']
order=['RA','RT','CT','LT','LA','RL','LL','HD']
locmap=np.zeros((H,W),np.uint8)
for k in draw:
    im=Image.new('L',(W,H),0);ImageDraw.Draw(im).polygon(P[k],fill=1);locmap[np.array(im)==1]=order.index(k)+1
assign=np.zeros((H,W),np.uint8)
for c in range(1,n+1):
    if c in border:continue
    m=lab==c;vals=locmap[m];vals=vals[vals>0]
    if len(vals)==0:continue
    cnt=np.bincount(vals,minlength=len(order)+1)
    assign[m]=cnt.argmax() if cnt.max()>=0.85*len(vals) else locmap[m]
# the outline is drawn 4px wide: regions come from the 6px render (keeps small gaps closed),
# but the outside is trimmed right up to the 4px line so no fill shows beyond it
line4=np.array(Image.open('wh4.png').convert('L'))<160
ext=np.isin(lab,list(border));ext=ndi.binary_dilation(ext,iterations=4)&~line4
d,(iy,ix)=ndi.distance_transform_edt(assign==0,return_indices=True)
full=assign[iy,ix];full[ext]=0
cols=[(0,0,0),(230,80,80),(240,160,60),(240,220,60),(80,200,120),(60,160,230),(150,90,220),(220,90,180),(40,40,40)]
rgb=np.full(a.shape+(3,),255,np.uint8)
for i in range(1,9):rgb[full==i]=cols[i]
rgb[line]=0
Image.fromarray(rgb).crop((700,120,1240,1000)).save('preview.png')
np.save('full.npy',full);json.dump(order,open('order.json','w'))
