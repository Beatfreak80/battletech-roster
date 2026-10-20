# build data_enf.json from Enforcer.svg and the segmentation (run from the ChaosApp folder after enforcer/seg.py)
import json,numpy as np,sys
sys.path.insert(0,'.')
from build_chassis import build
full=np.load('enforcer/full.npy');order=json.load(open('enforcer/order.json'))
d=build('enforcer/Enforcer.svg',None,full,order,(650,200,1230,1060),grow=2)
d['sw']=4   # the source art is drawn with 4px strokes, not the usual 6
json.dump(d,open('data_enf.json','w'));print(d['viewBox'],d['anchors'])
