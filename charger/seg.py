import numpy as np, json, base64, io, re
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
a=np.array(Image.open('cg.png').convert('L')); H,W=a.shape
line=a<160
closed=ndi.binary_dilation(line,iterations=3)
lab,n=ndi.label(~closed)
border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
for x,y in []:pass
P={
 'RA':[(690,30),(838,30),(838,310),(855,312),(872,372),(850,388),(850,450),(690,450)],
 'RT':[(838,85),(928,85),(928,187),(935,187),(935,445),(850,445),(850,388),(872,372),(855,312),(838,310)],
 'HD':[(895,30),(1080,30),(1080,85),(1060,85),(1060,187),(928,187),(928,85),(895,85)],
 'CT':[(935,187),(1060,187),(1060,445),(935,445)],
 'LT':[(1060,85),(1155,85),(1155,310),(1138,312),(1120,372),(1145,388),(1145,445),(1060,445)],
 'LA':[(1155,30),(1320,30),(1320,515),(1180,515),(1180,390),(1145,388),(1120,372),(1138,312),(1155,310)],
 'RL':[(770,445),(993,445),(993,1060),(770,1060)],
 'LL':[(993,445),(1230,445),(1230,1060),(993,1060)],
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
Image.fromarray(rgb).crop((690,30,1320,1065)).save('preview.png')
np.save('full.npy',full);json.dump(order,open('order.json','w'))
