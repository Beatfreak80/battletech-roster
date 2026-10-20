# build data_cn.json from Centurion.svg and the segmentation (run from the ChaosApp folder after centurion/render.py, render4.py and seg.py)
import json,numpy as np,sys
sys.path.insert(0,'.')
from build_chassis import build
full=np.load('centurion/full.npy');order=json.load(open('centurion/order.json'))
d=build('centurion/Centurion.svg',None,full,order,(680,190,1240,1060),grow=2)
d['sw']=4   # drawn with 4px strokes
json.dump(d,open('data_cn.json','w'));print(d['viewBox'])
