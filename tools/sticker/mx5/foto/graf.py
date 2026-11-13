from side import *
from scipy import ndimage
z0,z1,y0,y1=0.40,-2.0,0.95,0.42; S2=700; w=int((z0-z1)*S2); h=int((y0-y1)*S2)
im=rect(z0,y0,z1,y1,w,h); im.save('graf_raw.png'); a=np.asarray(im).astype(float)/255
r,g,b=a[...,0],a[...,1],a[...,2]; red=r-np.maximum(g,b); mx=a.max(2)
m=(red<0.10)&(mx<0.62)
m=ndimage.binary_opening(m,iterations=2); m=ndimage.binary_closing(m,iterations=3)
Image.fromarray((m*255).astype('uint8')).save('graf_mask.png')
d=ImageDraw.Draw(im)
for k in range(-20,5):
    x=(z0-k/10)*S2; d.line([x,0,x,h],fill=(0,255,255)); d.text((x+2,2),str(k/10),fill=(255,255,0))
for k in range(4,10):
    Y=(y0-k/10)*S2; d.line([0,Y,w,Y],fill=(0,255,255)); d.text((2,Y+2),str(k/10),fill=(255,255,0))
im.save('graf_grid.png')
