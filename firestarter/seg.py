import numpy as np, json, base64, io, re
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
a=np.array(Image.open('fs.png').convert('L')); H,W=a.shape
line=a<160
closed=ndi.binary_dilation(line,iterations=3)
lab,n=ndi.label(~closed)
border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
for x,y in [(980,900),(980,820),(980,1000)]:border.add(lab[y,x])
border.discard(0)
P={
 'HD':[(900,395),(1070,395),(1070,512),(900,512)],
 'RA':[(770,480),(882,480),(882,690),(865,690),(865,745),(770,745)],
 'RT':[(882,512),(950,512),(950,690),(882,690)],
 'CT':[(950,512),(1012,512),(1012,690),(950,690)],
 'LT':[(1012,512),(1078,512),(1078,690),(1012,690)],
 'LA':[(1078,480),(1195,480),(1195,745),(1095,745),(1095,690),(1078,690)],
 'RL':[(865,690),(982,690),(982,1080),(830,1080),(830,745),(865,745)],
 'LL':[(982,690),(1095,690),(1095,745),(1140,745),(1140,1080),(982,1080)],
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
Image.fromarray(rgb).crop((760,390,1200,1080)).save('preview.png')
np.save('full.npy',full);json.dump(order,open('order.json','w'))
