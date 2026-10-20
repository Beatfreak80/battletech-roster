# build data_crb.json from Crab.svg and the segmentation (run from the ChaosApp folder after crab/seg.py)
import json,numpy as np,sys
sys.path.insert(0,'.')
from build_chassis import build
full=np.load('crab/full.npy');order=json.load(open('crab/order.json'))
d=build('crab/Crab.svg',None,full,order,(605,410,1405,1060),grow=2)
d['sw']=4   # the source art is drawn with 4px strokes, not the usual 6
json.dump(d,open('data_crb.json','w'));print(d['viewBox'],d['anchors'])
