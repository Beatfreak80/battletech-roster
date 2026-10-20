import numpy as np, json, base64, io, re
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
a=np.array(Image.open('lc.png').convert('L')); H,W=a.shape
line=a<160
closed=ndi.binary_dilation(line,iterations=3)
lab,n=ndi.label(~closed)
border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
for x,y in []:border.add(lab[y,x])
border.discard(0)
P={
 'RA':[(900,440),(1040,440),(1040,615),(900,615)],
 'RT':[(1040,440),(1108,440),(1108,645),(1050,645),(1050,615),(1040,615)],
 'LT':[(1205,440),(1290,440),(1290,640),(1205,640)],
 'LA':[(1290,440),(1400,440),(1400,640),(1290,640)],
 'RL':[(900,615),(1040,615),(1050,645),(1085,645),(1085,760),(1150,760),(1150,990),(1115,990),(1115,1060),(900,1060)],
 'LL':[(1215,640),(1400,640),(1400,1060),(1115,1060),(1115,990),(1150,990),(1150,760),(1215,760)],
 # the body pod: its lower 'chin' with the medium laser lens stays centre torso
 'CT':[(1108,440),(1205,440),(1205,640),(1215,640),(1215,715),(1185,760),(1085,760),(1085,645),(1108,645)],
 'HD':[(1125,360),(1195,360),(1195,505),(1125,505)],
}
draw=['RA','RT','LT','LA','RL','LL','CT','HD']   # later shapes overwrite earlier ones
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
line4=np.array(Image.open('lc4.png').convert('L'))<160
ext=np.isin(lab,list(border));ext=ndi.binary_dilation(ext,iterations=4)&~line4
d,(iy,ix)=ndi.distance_transform_edt(assign==0,return_indices=True)
full=assign[iy,ix];full[ext]=0
cols=[(0,0,0),(230,80,80),(240,160,60),(240,220,60),(80,200,120),(60,160,230),(150,90,220),(220,90,180),(40,40,40)]
rgb=np.full(a.shape+(3,),255,np.uint8)
for i in range(1,9):rgb[full==i]=cols[i]
rgb[line]=0
Image.fromarray(rgb).crop((900,360,1400,1060)).save('preview.png')
np.save('full.npy',full);json.dump(order,open('order.json','w'))
