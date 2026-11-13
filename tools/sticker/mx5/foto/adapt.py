from cut import *
from scipy import ndimage
import numpy as np
def adapt(im,name,win=160,lo=0.38,hi=0.62,minarea=150):
    a=np.asarray(im.convert('RGB')).astype(float)/255; g=ndimage.gaussian_filter(a[...,1],1.0)
    hiL=ndimage.gaussian_filter(ndimage.maximum_filter(g,win),win/3); loL=ndimage.gaussian_filter(ndimage.minimum_filter(g,win),win/3)
    al=sm((g-loL)/np.maximum(hiL-loL,0.08),lo,hi); lab,n=ndimage.label(al>0.5)
    ar=ndimage.sum(np.ones_like(al),lab,range(1,n+1)); keep=np.isin(lab,[k+1 for k,v in enumerate(ar) if v>=minarea]); al*=ndimage.binary_dilation(keep,iterations=3)
    out=Image.new('RGBA',im.size,(255,255,255,0)); out.putalpha(Image.fromarray((al*255).astype('uint8'))); out.save(f'out/{name}.png'); return out
adapt(Image.open('src/p11.png').crop((1000,300,2560,2370)).resize((720,1095),Image.LANCZOS),'oni')
adapt(Image.open('src/p11.png').crop((1120,4365,2610,4520)).resize((745,78),Image.LANCZOS),'insta',win=60,minarea=15)
sheet(['oni','insta'],'s6.png')
