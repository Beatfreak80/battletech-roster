import numpy as np, json, base64, io, re
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
a=np.array(Image.open('at.png').convert('L')); H,W=a.shape
line=a<160
closed=ndi.binary_dilation(line,iterations=3)
lab,n=ndi.label(~closed)
border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
for x,y in []:pass
P={
 'RA':[(560,0),(740,0),(740,245),(795,255),(795,425),(560,440)],
 'RT':[(740,0),(936,0),(936,425),(795,425),(795,255),(740,245)],
 'CT':[(936,0),(1071,0),(1071,425),(1126,425),(1126,460),(927,460),(927,425),(936,425)],
 'LT':[(1071,0),(1268,0),(1268,245),(1214,255),(1214,425),(1071,425)],
 'LA':[(1268,0),(1450,0),(1450,620),(1300,620),(1250,505),(1214,495),(1214,255),(1268,245)],
 'RL':[(560,440),(795,425),(927,425),(927,460),(1030,460),(1030,620),(1004,620),(1004,1080),(560,1080)],
 'LL':[(1030,460),(1126,460),(1126,425),(1214,425),(1214,495),(1250,505),(1300,620),(1300,1080),(1004,1080),(1004,620),(1030,620)],
 'HD':[(874,0),(1133,0),(1133,165),(1072,216),(936,216),(874,165)],
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
Image.fromarray(rgb).crop((560,0,1450,1070)).save('preview.png')
np.save('full.npy',full);json.dump(order,open('order.json','w'))
