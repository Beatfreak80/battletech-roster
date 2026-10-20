# build data_lct.json from Locust.svg and the segmentation (run from the ChaosApp folder after locust/seg.py)
import json,numpy as np,sys
sys.path.insert(0,'.')
from build_chassis import build
full=np.load('locust/full.npy');order=json.load(open('locust/order.json'))
d=build('locust/Locust.svg',None,full,order,(900,360,1400,1060),grow=2)
d['sw']=4   # the source art is drawn with 4px strokes, not the usual 6
json.dump(d,open('data_lct.json','w'));print(d['viewBox'])
