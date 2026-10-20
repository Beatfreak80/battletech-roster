import numpy as np, json, base64, io, re
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
a=np.array(Image.open('bl.png').convert('L')); H,W=a.shape
line=a<160
closed=ndi.binary_dilation(line,iterations=3)
lab,n=ndi.label(~closed)
border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
for x,y in [(800,400),(820,420),(760,330),(1180,400)]:
    if lab[y,x]:print('bg seed',x,y,lab[y,x],(lab==lab[y,x]).sum());border.add(lab[y,x])
P={
 'RA':[(600,40),(767,40),(767,440),(745,445),(745,725),(600,725)],
 'RT':[(767,40),(905,40),(905,240),(900,355),(870,355),(870,430),(767,430)],
 'HD':[(905,10),(1020,10),(1020,135),(1045,135),(1045,240),(905,240)],
 'CT':[(905,240),(1045,240),(1045,355),(1078,355),(1078,428),(1095,428),(1095,468),(1046,468),(1046,615),(895,615),(895,468),(848,468),(848,428),(870,428),(870,355),(900,355)],
 'LT':[(1020,30),(1190,30),(1190,248),(1166,248),(1166,335),(1160,430),(1078,430),(1078,355),(1045,355),(1045,135),(1020,135)],
 'LA':[(1190,30),(1360,30),(1360,420),(1160,420),(1166,335),(1166,248),(1190,248)],
 'RL':[(745,430),(870,430),(848,428),(848,468),(895,468),(895,1015),(680,1015),(680,725),(745,725)],
 'LL':[(1046,468),(1095,468),(1095,430),(1260,430),(1260,1015),(1046,1015)],
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
Image.fromarray(rgb).crop((600,10,1360,1015)).save('preview.png')
np.save('full.npy',full);json.dump(order,open('order.json','w'))
