from cut import *
from side import rect
from scipy import ndimage
import numpy as np
from PIL import ImageDraw, ImageFont
def white(im,lo,hi,ks=1.5,minarea=30,name=None,chan=None):
    a=np.asarray(im.convert('RGB')).astype(float)/255; mx=a.max(2); mn=a.min(2); s=(mx-mn)/np.maximum(mx,1e-3)
    sc=a[...,chan] if chan is not None else mx-ks*s
    al=sm(sc,lo,hi); lab,n=ndimage.label(al>0.5)
    if n:
        ar=ndimage.sum(np.ones_like(al),lab,range(1,n+1)); keep=np.isin(lab,[k+1 for k,v in enumerate(ar) if v>=minarea]); al*=ndimage.binary_dilation(keep,iterations=3)
    out=Image.new('RGBA',im.size,(255,255,255,0)); out.putalpha(Image.fromarray((al*255).astype('uint8')))
    if name: out.save(f'out/{name}.png')
    return out
# Seite (Foto 10, auf das Modell entzerrt)
white(rect(0.57,0.86,0.29,0.35,420*2,765*2).resize((420,765),Image.LANCZOS) if 0 else rect(0.57,0.86,0.29,0.35,420,765),0.42,0.6,ks=1.4,minarea=12,name='stack')
white(rect(0.875,0.855,0.60,0.76,412,142),0.42,0.6,ks=1.4,minarea=40,name='pirelli')
# Haube (Foto 11, frontal), senkrecht um 1.146 gestreckt (Haube liegt schraeg zur Kamera)
im=Image.open('src/p11.png').crop((1000,300,2560,2370)).resize((720,1095),Image.LANCZOS)
white(im,0.33,0.45,chan=1,minarea=200,name='oni')
im=Image.open('src/p11.png').crop((1120,4365),) if 0 else Image.open('src/p11.png').crop((1120,4365,2610,4520)).resize((745,78),Image.LANCZOS)
white(im,0.36,0.5,chan=1,minarea=20,name='insta')
im=Image.open('src/p12.png').transform((1000,105),Image.QUAD,(1370,2790,1370,3020,3920,3272,3920,2962),Image.BICUBIC)
white(im,0.5,0.75,chan=1,minarea=50,name='mazdaspeed')
# Grafik (schwarz) aus der Maske
m=np.asarray(Image.open('graf_mask.png')).astype(float)/255; h,w=m.shape
yy,xx=np.mgrid[0:h,0:w]
top=150-(xx-75)*0.0835-7
m=m*(xx>60)*(xx<885)*(yy>top)*(yy<303)
t=Image.new('L',(w,h),0); d=ImageDraw.Draw(t); d.polygon([(880,77),(1200,57),(1510,50),(1200,78),(1010,104),(880,126)],fill=255)
m=np.maximum(m,np.asarray(t)/255.)
m=ndimage.gaussian_filter(m,2.0); al=sm(m,0.4,0.6)
g=Image.new('RGBA',(w,h),(11,11,13,0)); g.putalpha(Image.fromarray((al*255).astype('uint8'))); g=g.crop((56,36,1520,308)); g.save('out/grafik.png'); print('grafik',g.size)
# Pentagramm: schwarze Scheibe + weisse Zeichnung
p=Image.open('out/pent.png').resize((360,360),Image.LANCZOS); a=np.asarray(p)[...,3]/255.
yy,xx=np.mgrid[0:360,0:360]; rr=np.hypot(xx-179.5,yy-179.5); disc=sm(178-rr,0,2); a=a*(rr<172)
rgb=(a[...,None]*242+(1-a[...,None])*np.array([10,10,12])).astype('uint8')
Image.fromarray(np.dstack([rgb,(disc*255).astype('uint8')]),'RGBA').save('out/pent2.png')
# R.Nemec mit Flagge (Seitenscheibe)
F=ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Bold.otf',64); im=Image.new('RGBA',(520,96),(255,255,255,0)); d=ImageDraw.Draw(im)
for k,c in enumerate([(255,255,255),(11,78,162),(238,28,37)]): d.rectangle([4,12+k*24,112,12+(k+1)*24],fill=c+(255,))
d.polygon([(26,26),(58,26),(58,58),(42,74),(26,58)],fill=(238,28,37,255),outline=(255,255,255,255)); d.line([(42,34),(42,62)],fill=(255,255,255,255),width=4); d.line([(33,42),(51,42)],fill=(255,255,255,255),width=3); d.line([(35,50),(49,50)],fill=(255,255,255,255),width=3)
d.text((126,48),'R.Nemec',font=F,fill=(255,255,255,255),anchor='lm'); im=im.crop(im.getbbox()); im.save('out/nemec.png'); print(im.size)
# Reste
for n,sz in [('n666',(350,200)),('limitless',(590,128)),('fish',(512,214)),('banner',(1100,128))]:
    Image.open(f'out/{n}.png').resize(sz,Image.LANCZOS).save(f'out/{n}_s.png')
im=Image.open('out/oni.png')
sheet(['stack','pirelli','insta','mazdaspeed','nemec'],'s4.png'); 
s=Image.new('RGB',(1500,1100),(110,10,20)); 
for n,(x,y) in {'oni':(0,0),'grafik':(0,0),'pent2':(760,300),'stack':(1000,300)}.items():
    i=Image.open(f'out/{n}.png'); 
    if n=='grafik': s.paste(i,(20,820),i)
    else: s.paste(i,(x,y),i)
s.save('s5.png')
