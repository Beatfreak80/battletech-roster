import numpy as np, json, base64, io, re
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
a=np.array(Image.open('bj.png').convert('L')); H,W=a.shape
line=a<160
closed=ndi.binary_dilation(line,iterations=3)
lab,n=ndi.label(~closed)
border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
for x,y in []:pass
P={
 'RA':[(690,270),(898,270),(898,470),(860,470),(860,505),(690,505)],
 'RT':[(898,270),(946,270),(946,555),(860,555),(860,470),(898,470)],
 'HD':[(946,225),(1054,225),(1054,300),(1032,300),(1032,338),(968,338),(968,300),(946,300)],
 'CT':[(946,300),(968,300),(968,338),(1032,338),(1032,300),(1054,300),(1054,555),(1045,555),(1045,725),(955,725),(955,555),(946,555)],
 'LT':[(1054,270),(1102,270),(1102,470),(1140,470),(1140,555),(1054,555)],
 'LA':[(1102,270),(1300,270),(1300,505),(1140,505),(1140,470),(1102,470)],
 'RL':[(770,555),(955,555),(955,1015),(770,1015)],
 'LL':[(1045,555),(1230,555),(1230,1015),(1045,1015)],
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
Image.fromarray(rgb).crop((712,231,1281,1007)).save('preview.png')
np.save('full.npy',full);json.dump(order,open('order.json','w'))
