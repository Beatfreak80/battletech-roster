import numpy as np, json, base64, io, re
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
a=np.array(Image.open('cp.png').convert('L')); H,W=a.shape
line=a<160
closed=ndi.binary_dilation(line,iterations=3)
lab,n=ndi.label(~closed)
border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
for x,y in []:pass
P={
 'RA':[(640,150),(838,150),(838,490),(640,490)],
 'RT':[(838,300),(925,300),(925,578),(838,578)],
 'CT':[(925,300),(1022,300),(1022,578),(925,578)],
 'LT':[(1022,300),(1108,300),(1108,578),(1022,578)],
 'LA':[(1108,150),(1300,150),(1300,490),(1108,490)],
 'RL':[(640,578),(974,578),(974,1010),(640,1010)],
 'LL':[(974,578),(1300,578),(1300,1010),(974,1010)],
 'HD':[(922,150),(1033,150),(1033,350),(1016,350),(1016,505),(932,505),(932,350),(922,350)],
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
Image.fromarray(rgb).crop((640,150,1300,1005)).save('preview.png')
np.save('full.npy',full);json.dump(order,open('order.json','w'))
