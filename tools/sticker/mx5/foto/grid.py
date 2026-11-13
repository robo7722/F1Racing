import sys
from PIL import Image,ImageDraw
def grid(i,box,name,step=50,sc=None):
    im=Image.open(f'src/p{i}.png').crop(box)
    sc=sc or min(3,1500/max(im.size)); im=im.resize((int(im.width*sc),int(im.height*sc)),Image.LANCZOS); d=ImageDraw.Draw(im)
    x=(box[0]//step+1)*step
    while x<box[2]:
        X=(x-box[0])*sc; d.line([X,0,X,im.height],fill=(0,255,255),width=1); d.text((X+2,2),str(x),fill=(255,255,0)); x+=step
    y=(box[1]//step+1)*step
    while y<box[3]:
        Y=(y-box[1])*sc; d.line([0,Y,im.width,Y],fill=(0,255,255),width=1); d.text((2,Y+2),str(y),fill=(255,255,0)); y+=step
    im.save(name)
if __name__=='__main__':
    a=sys.argv; grid(int(a[1]),tuple(map(int,a[2:6])),a[6],int(a[7]) if len(a)>7 else 50)
