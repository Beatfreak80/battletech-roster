import numpy as np, json, base64, io, re
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
a=np.array(Image.open('cb.png').convert('L')); H,W=a.shape
line=a<160
closed=ndi.binary_dilation(line,iterations=3)
lab,n=ndi.label(~closed)
border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
for x,y in []:border.add(lab[y,x])
border.discard(0)
P={
 'RL':[(690,640),(1000,640),(1000,1060),(690,1060)],
 'LL':[(1000,640),(1310,640),(1310,1060),(1000,1060)],
 'RT':[(845,415),(970,415),(970,560),(905,560),(905,650),(845,650)],
 # the dome is centre torso; the head is the top pod plus the neck block above the dome
 'CT':[(960,548),(1047,548),(1080,558),(1105,590),(1115,640),(1110,688),(1000,712),(890,688),(885,640),(895,590),(920,558)],
 'LT':[(1035,415),(1162,415),(1162,650),(1100,650),(1100,560),(1035,560)],
 'RA':[(605,500),(845,500),(845,640),(800,640),(800,760),(605,760)],
 'LA':[(1162,500),(1405,500),(1405,770),(1210,770),(1210,640),(1162,640)],
 'HD':[(970,405),(1037,405),(1037,482),(1047,482),(1047,548),(960,548),(960,482),(970,482)],
}
# legs split the pelvis down the centre line; later shapes overwrite earlier ones
draw=['RL','LL','RT','CT','LT','RA','LA','HD']
order=['RA','RT','CT','LT','LA','RL','LL','HD']
locmap=np.zeros((H,W),np.uint8)
for k in draw:
    im=Image.new('L',(W,H),0);ImageDraw.Draw(im).polygon(P[k],fill=1);locmap[np.array(im)==1]=order.index(k)+1
assign=np.zeros((H,W),np.uint8)
for c in range(1,n+1):
    if c in border:continue
    m=lab==c;vals=locmap[m];vals=vals[vals>0]
    if len(vals)==0:continue
    cnt=np.bincount(vals,minlength=len(order)+1)
    assign[m]=cnt.argmax() if cnt.max()>=0.85*len(vals) else locmap[m]
# the outline is drawn 4px wide: regions come from the 6px render (keeps small gaps closed),
# but the outside is trimmed right up to the 4px line so no fill shows beyond it
line4=np.array(Image.open('cb4.png').convert('L'))<160
ext=np.isin(lab,list(border));ext=ndi.binary_dilation(ext,iterations=4)&~line4
d,(iy,ix)=ndi.distance_transform_edt(assign==0,return_indices=True)
full=assign[iy,ix];full[ext]=0
cols=[(0,0,0),(230,80,80),(240,160,60),(240,220,60),(80,200,120),(60,160,230),(150,90,220),(220,90,180),(40,40,40)]
rgb=np.full(a.shape+(3,),255,np.uint8)
for i in range(1,9):rgb[full==i]=cols[i]
rgb[line]=0
Image.fromarray(rgb).crop((605,410,1405,1060)).save('preview.png')
np.save('full.npy',full);json.dump(order,open('order.json','w'))
