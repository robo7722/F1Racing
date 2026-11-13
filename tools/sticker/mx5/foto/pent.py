from cut import *
import numpy as np
P=np.array([(1150,2100),(1215,2300),(1310,2500),(1440,2640),(1600,2690),(1720,2630),(1790,2400),(1745,2200),(1590,2000),(1450,1930),(1300,1920),(1200,1955)],float)
def fit(p):
    x,y=p[:,0],p[:,1]; D=np.stack([x*x,x*y,y*y,x,y,np.ones_like(x)],1); V=np.linalg.svd(D-0*D.mean(0),full_matrices=False)[2]; A,B,C,Dd,E,F=V[-1]
    M=np.array([[A,B/2],[B/2,C]]); cen=np.linalg.solve(2*M,-np.array([Dd,E])); k=cen@M@cen-F; return cen,M/k
sc=np.array([1500,2300.]); 
im=src(7); a=np.asarray(im.crop((900,1700,2100,3000))).astype(float)/255; m=(a.min(2)>0.5); ys,xs=np.nonzero(m); pts=np.stack([xs+900,ys+1700],1).astype(float)
cen,M=fit((P-sc)/500); 
for it in range(4):
    q=(pts-sc)/500-cen; r=np.sqrt(np.einsum('ij,jk,ik->i',q,M,q)); sel=np.abs(r-1)<0.07-0.01*it; cen,M=fit((pts[sel]-sc)/500); print(sel.sum(),cen*500+sc)
w,v=np.linalg.eigh(M); S=v@np.diag(1/np.sqrt(w))@v.T*500; C=cen*500+sc; print('axes',500/np.sqrt(w))
# Aussenring = 1.19 x Innenring (geschaetzt), Ausschnitt 1.3
R=1.5; N=900
def warp(rot):
    c,s=np.cos(rot),np.sin(rot); Rm=np.array([[c,-s],[s,c]]); T=S@Rm*R
    # Ausgabe (u,v) in [-1,1] -> Foto
    co=[]
    for (u,vv) in [(-1,-1),(-1,1),(1,1),(1,-1)]: co+=list(C+T@np.array([u,vv]))
    return src(7).transform((N,N),Image.QUAD,co,Image.BICUBIC)
import sys
rot=float(sys.argv[1]) if len(sys.argv)>1 else 0
im=warp(rot); im.save('pent_raw.png')
a=np.asarray(im).astype(float)/255; al=sm(a[:,:,1],0.33,0.5)
yy,xx=np.mgrid[0:N,0:N]; rr=np.hypot(xx-N/2,yy-N/2)/(N/2); al*= (rr<0.97)
out=Image.new('RGBA',(N,N),(255,255,255,0)); out.putalpha(Image.fromarray((al*255).astype('uint8'))); out.save('out/pent.png')
