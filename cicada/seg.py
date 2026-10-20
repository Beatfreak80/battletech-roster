import numpy as np, json, base64, io, re
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
a=np.array(Image.open('cd.png').convert('L')); H,W=a.shape
line=a<160
closed=ndi.binary_dilation(line,iterations=3)
lab,n=ndi.label(~closed)
border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
for x,y in []:pass
P={
 'RA':[(760,460),(833,460),(833,672),(760,672)],
 'RT':[(833,450),(894,450),(894,677),(833,677)],
 'CT':[(894,492),(1067,492),(1067,705),(894,705)],
 'LT':[(1067,450),(1128,450),(1128,677),(1067,677)],
 'LA':[(1128,460),(1200,460),(1200,672),(1128,672)],
 'RL':[(760,672),(833,672),(833,677),(894,677),(894,705),(980,705),(980,1060),(760,1060)],
 'LL':[(980,705),(1067,705),(1067,677),(1128,677),(1128,672),(1200,672),(1200,1060),(980,1060)],
 'HD':[(895,330),(1066,330),(1066,492),(895,492)],
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
Image.fromarray(rgb).crop((760,320,1200,1060)).save('preview.png')
np.save('full.npy',full);json.dump(order,open('order.json','w'))
