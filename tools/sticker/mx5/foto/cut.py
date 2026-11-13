import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
_c={}
def src(i):
    if i not in _c: _c[i]=Image.open(f'src/p{i}.png')
    return _c[i]
def sm(x,a,b): return np.clip((x-a)/(b-a),0,1)
def cut(name,i,quad,w,h,lo=0.55,hi=0.75,ks=1.6,minarea=30,sym=False,ss=2,mode='white',pad=0):
    """quad: TL,TR,BR,BL im Foto. Ergebnis: weisser Aufkleber auf transparent, w x h."""
    TL,TR,BR,BL=quad
    im=src(i).transform((w*ss,h*ss),Image.QUAD,(*TL,*BL,*BR,*TR),Image.BICUBIC)
    a=np.asarray(im).astype(float)/255; mx=a.max(2); mn=a.min(2); s=(mx-mn)/np.maximum(mx,1e-3)
    if mode=='white': sc=mx-ks*s
    else: sc=1-mx-ks*s     # schwarze Aufkleber
    al=sm(sc,lo,hi)
    lab,n=ndimage.label(al>0.5)
    if n:
        ar=ndimage.sum(np.ones_like(al),lab,range(1,n+1)); keep=np.isin(lab,[k+1 for k,v in enumerate(ar) if v>=minarea*ss*ss])
        al*=ndimage.binary_dilation(keep,iterations=2*ss)
    if sym: al=np.maximum(al,al[:,::-1])*0.5+0.5*np.minimum(al,al[:,::-1]) if sym=='avg' else np.maximum(al,al[:,::-1])
    A=Image.fromarray((al*255).astype('uint8')).resize((w,h),Image.LANCZOS)
    out=Image.new('RGBA',(w,h),(255,255,255,0)); out.putalpha(A); out.save(f'out/{name}.png'); return out
def door(name,i,x0,x1,y0,y1,f=2.2,H=None,s0=0.1,yr=1800,k=0.00055,**kw):
    sl=lambda y:s0+(y-yr)*k; dx=x1-x0
    ln=min(0,-0.18*(2150-(y0+y1)/2)/200)*(y1-y0)
    q=[(x0-ln/2,y0),(x1-ln/2,y0+dx*sl(y0)),(x1+ln/2,y1+dx*sl(y1)),(x0+ln/2,y1)]
    H=H or int((y1-y0)*3); W=int(H*dx*f/(y1-y0)); return cut(name,i,q,W,H,**kw)
def sheet(names,fn,bg=(110,10,20)):
    ims=[Image.open(f'out/{n}.png') for n in names]; W=max(i.width for i in ims)+20; H=sum(i.height+14 for i in ims)+10
    s=Image.new('RGB',(W,H),bg); y=10
    for im in ims: s.paste(im,(10,y),im); y+=im.height+14
    s.save(fn)
