import numpy as np, json, base64, io, re
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
a=np.array(Image.open('ef.png').convert('L')); H,W=a.shape
line=a<160
closed=ndi.binary_dilation(line,iterations=3)
lab,n=ndi.label(~closed)
border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
for x,y in [(935,700),(935,850),(940,1000)]:border.add(lab[y,x])
border.discard(0)
P={
 'RL':[(650,505),(945,505),(945,1060),(650,1060)],
 'LL':[(945,505),(1225,505),(1225,1060),(945,1060)],
 'RT':[(850,300),(880,300),(880,505),(805,505),(805,350),(850,350)],
 'CT':[(880,300),(1020,300),(1020,505),(880,505)],
 'LT':[(1020,300),(1050,300),(1050,350),(1080,350),(1080,505),(1020,505)],
 'RA':[(650,255),(850,255),(850,350),(805,350),(805,597),(650,597)],
 'LA':[(1050,255),(1225,255),(1225,597),(1080,597),(1080,350),(1050,350)],
 'HD':[(855,200),(1045,200),(1045,300),(855,300)],
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
line4=np.array(Image.open('ef4.png').convert('L'))<160
ext=np.isin(lab,list(border));ext=ndi.binary_dilation(ext,iterations=4)&~line4
d,(iy,ix)=ndi.distance_transform_edt(assign==0,return_indices=True)
full=assign[iy,ix];full[ext]=0
cols=[(0,0,0),(230,80,80),(240,160,60),(240,220,60),(80,200,120),(60,160,230),(150,90,220),(220,90,180),(40,40,40)]
rgb=np.full(a.shape+(3,),255,np.uint8)
for i in range(1,9):rgb[full==i]=cols[i]
rgb[line]=0
Image.fromarray(rgb).crop((650,200,1230,1060)).save('preview.png')
np.save('full.npy',full);json.dump(order,open('order.json','w'))
