import numpy as np, json, base64, io, re
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
a=np.array(Image.open('sp.png').convert('L')); H,W=a.shape
line=a<160
closed=ndi.binary_dilation(line,iterations=3)
lab,n=ndi.label(~closed)
border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
P={
 'RA':[(620,340),(745,350),(850,420),(852,600),(620,600)],
 'RT':[(740,300),(905,300),(905,405),(850,420),(745,350)],
 'CT':[(852,382),(1048,382),(1048,597),(852,597)],
 'HD':[(880,250),(1030,250),(1030,330),(1012,382),(895,382),(880,330)],
 'LT':[(1005,300),(1150,300),(1150,335),(1060,410),(1048,410),(1005,382)],
 'LA':[(1060,410),(1150,335),(1310,335),(1310,600),(1048,600),(1048,410)],
 'RL':[(700,600),(852,600),(852,597),(948,597),(948,1060),(700,1060)],
 'LL':[(948,597),(1048,597),(1048,600),(1310,600),(1310,1060),(948,1060)],
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
Image.fromarray(rgb).crop((630,240,1310,1050)).save('preview.png')
np.save('full.npy',full);json.dump(order,open('order.json','w'))
