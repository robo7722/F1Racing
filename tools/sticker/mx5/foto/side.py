import numpy as np, json
from PIL import Image, ImageDraw
R=0.344; zf=1.396; zr=-1.277
M=[(zf,R),(zf,2*R),(zf,0),(zf+R,R),(zf-R,R),(zr,R),(zr,2*R),(zr,0),(zr+R,R),(zr-R,R)]
P=[(885,1560),(885,1217),(885,1900),(545,1560),(1240,1560),(3065,1395),(3065,1125),(3065,1655),(2870,1395),(3255,1395)]
A=[]
for (z,y),(u,v) in zip(M,P):
    A.append([z,y,1,0,0,0,-u*z,-u*y,-u]); A.append([0,0,0,z,y,1,-v*z,-v*y,-v])
H=np.linalg.svd(np.array(A))[2][-1].reshape(3,3); H/=H[2,2]
def m2p(z,y):
    q=H@np.array([z,y,1.0]); return q[:2]/q[2]
for m,p in zip(M,P): print(m,p,np.round(m2p(*m)))
np.save('H.npy',H)
S=500; Z0,Z1,Y1=2.35,-2.35,1.35; W=int((Z0-Z1)*S); Hh=int(Y1*S)
def rect(z0,y0,z1,y1,w,h,src='src/p10.png'):   # z0 = linker Rand (vorn), y0 = oben; projektiv
    T=np.array([[(z1-z0)/w,0,z0],[0,(y1-y0)/h,y0],[0,0,1]]); G=H@T; G=G/G[2,2]
    return Image.open(src).transform((w,h),Image.PERSPECTIVE,G.flatten()[:8],Image.BICUBIC)
if __name__=='__main__':
    im=rect(Z0,Y1,Z1,0,W,Hh); im.save('side_rect.png'); d=ImageDraw.Draw(im)
    for k in range(-23,24):
        z=k/10; x=(Z0-z)*S; d.line([x,0,x,Hh],fill=(0,255,255) if k%5 else (255,255,0)); 
        if k%5==0: d.text((x+2,2),str(z),fill=(255,255,0))
    for k in range(0,14):
        y=k/10; Y=(Y1-y)*S; d.line([0,Y,W,Y],fill=(0,255,255) if k%5 else (255,255,0)); d.text((2,Y+2),str(y),fill=(255,255,0))
    im.save('side_grid.png'); im.crop((300,150,1500,650)).save('sg1.png'); im.crop((1100,100,2350,600)).save('sg2.png'); im.crop((0,250,700,650)).resize((1400,800)).save('sg0.png')
