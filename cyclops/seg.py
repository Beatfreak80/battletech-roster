import numpy as np, json, base64, io, re
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
a=np.array(Image.open('cy.png').convert('L')); H,W=a.shape
line=a<160
closed=ndi.binary_dilation(line,iterations=3)
lab,n=ndi.label(~closed)
border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
# also the open gaps under each arm, between arm and torso
for x,y in [(975,850),(975,760),(970,930),(777,450),(1155,450)]:border.add(lab[y,x])
border.discard(0)
P={
 'RA':[(590,240),(818,240),(818,402),(780,402),(780,520),(770,615),(590,615)],
 'RT':[(818,190),(905,190),(905,575),(870,575),(870,515),(780,515),(780,402),(818,402)],
 'CT':[(905,190),(1007,190),(1007,575),(905,575)],
 'LT':[(1007,190),(1135,190),(1135,402),(1148,402),(1148,515),(1040,515),(1040,575),(1007,575)],
 'LA':[(1135,240),(1345,240),(1345,705),(1162,705),(1158,560),(1148,515),(1148,402),(1135,402)],
 'RL':[(590,615),(770,615),(780,515),(870,515),(870,575),(958,575),(958,720),(995,745),(995,1080),(590,1080)],
 'LL':[(958,720),(958,575),(1040,575),(1040,515),(1148,515),(1158,560),(1162,705),(1345,705),(1345,1080),(995,1080),(995,745)],
 'HD':[(885,0),(1040,0),(1040,298),(885,298)],
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
Image.fromarray(rgb).crop((590,0,1345,1075)).save('preview.png')
np.save('full.npy',full);json.dump(order,open('order.json','w'))
