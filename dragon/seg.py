import numpy as np, json, base64, io, re
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
a=np.array(Image.open('dr.png').convert('L')); H,W=a.shape
line=a<160
closed=ndi.binary_dilation(line,iterations=3)
lab,n=ndi.label(~closed)
border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
for x,y in [(780,540),(1110,550)]:border.add(lab[y,x])  # enclosed gaps between arms and torso
P={
 'RA':[(600,195),(760,195),(760,700),(600,700)],
 'RT':[(760,195),(870,195),(870,358),(862,358),(862,602),(760,602)],
 'HD':[(870,195),(1015,195),(1015,358),(870,358)],
 'CT':[(862,358),(1023,358),(1023,602),(862,602)],
 'LT':[(1015,195),(1145,195),(1145,550),(1124,550),(1124,602),(1023,602),(1023,358),(1015,358)],
 'LA':[(1145,195),(1310,195),(1310,700),(1124,700),(1124,550),(1145,550)],
 'RL':[(745,602),(945,602),(945,1060),(700,1060),(700,700),(745,700)],
 'LL':[(945,602),(1145,602),(1145,672),(1175,672),(1175,1060),(945,1060)],
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
ext=np.isin(lab,list(border));ext=ndi.binary_dilation(ext,iterations=3)&~line
d,(iy,ix)=ndi.distance_transform_edt(assign==0,return_indices=True)
full=assign[iy,ix];full[ext]=0
cols=[(0,0,0),(230,80,80),(240,160,60),(240,220,60),(80,200,120),(60,160,230),(150,90,220),(220,90,180),(40,40,40)]
rgb=np.full(a.shape+(3,),255,np.uint8)
for i in range(1,9):rgb[full==i]=cols[i]
rgb[line]=0
Image.fromarray(rgb).crop((600,190,1310,1065)).save('preview.png')
np.save('full.npy',full);json.dump(order,open('order.json','w'))
