# build per-chassis drawing data: compact line art, location masks, hit map and label anchors
import re, json, base64, io, sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi
def build(svg_path, png_path, full, order, box, dx=0.0, dy=0.0):
    src=open(svg_path).read()
    lines=[]
    for p in re.findall(r'points="([^"]+)"',src):
        nums=[float(v) for v in p.replace(',',' ').split()]
        lines.append(' '.join(f"{nums[i]+dx:.1f},{nums[i+1]+dy:.1f}" for i in range(0,len(nums),2)))
    art=''.join(f'<polyline points="{l}"/>' for l in lines)
    X0,Y0,X1,Y1=box
    masks={};idx=np.zeros((Y1-Y0,X1-X0),np.uint8);anchors={}
    for i,k in enumerate(order,1):
        m=full==i;ys,xs=np.where(m);x0,x1,y0,y1=xs.min(),xs.max()+1,ys.min(),ys.max()+1
        im=Image.fromarray((m[y0:y1,x0:x1]*255).astype(np.uint8)).convert('1');b=io.BytesIO();im.save(b,'PNG',optimize=True)
        masks[k]=dict(x=int(x0),y=int(y0),w=int(x1-x0),h=int(y1-y0),png=base64.b64encode(b.getvalue()).decode())
        idx[m[Y0:Y1,X0:X1]]=i*20
        d=ndi.distance_transform_edt(m);y,x=np.unravel_index(d.argmax(),d.shape);anchors[k]=[int(x),int(y)]
    b=io.BytesIO();Image.fromarray(idx).save(b,'PNG',optimize=True)
    return dict(art=art,masks=masks,order=order,index=dict(x=X0,y=Y0,w=X1-X0,h=Y1-Y0,png=base64.b64encode(b.getvalue()).decode()),
                anchors=anchors,viewBox=f"{X0} {Y0} {X1-X0} {Y1-Y0}")
if __name__=='__main__':
    full=np.load('spider/full.npy');order=json.load(open('spider/order.json'))
    d=build('spider/Spider.svg','spider/sp.png',full,order,(630,240,1310,1050))
    json.dump(d,open('data_sdr.json','w'))
    print(len(d['art']),{k:len(v['png']) for k,v in d['masks'].items()})
