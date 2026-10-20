# build data_wth.json from Whitworth.svg and the segmentation (run from the ChaosApp folder after whitworth/seg.py)
import json,numpy as np,sys
sys.path.insert(0,'.')
from build_chassis import build
full=np.load('whitworth/full.npy');order=json.load(open('whitworth/order.json'))
d=build('whitworth/Whitworth.svg',None,full,order,(700,120,1240,1000),grow=2)
d['sw']=4   # the source art is drawn with 4px strokes, not the usual 6
json.dump(d,open('data_wth.json','w'));print(d['viewBox'],d['anchors'])
