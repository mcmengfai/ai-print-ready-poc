from pathlib import Path
from PIL import Image, ImageDraw
out=Path(__file__).with_name('demo-poster.png')
w,h=1800,2550
img=Image.new('RGB',(w,h),(20,20,30))
d=ImageDraw.Draw(img)
for y in range(h):
    r=int(30+180*y/h); g=int(40+80*(1-y/h)); b=int(120+100*(1-y/h))
    d.line([(0,y),(w,y)], fill=(r,g,b))
for i in range(18):
    x=(i*137)%w; y=(i*211)%h; rad=120+(i%5)*35
    color=[(255,0,180),(0,255,180),(80,120,255),(255,220,0)][i%4]
    d.ellipse((x-rad,y-rad,x+rad,y+rad), fill=color)
d.rectangle((120,160,w-120,520), fill=(255,255,255))
d.text((170,230),'AI PRINT READY DEMO', fill=(15,15,15))
d.rectangle((140,h-420,w-140,h-150), outline=(255,255,255), width=8)
d.text((180,h-340),'A1 poster / bleed / DPI / color risk test', fill=(255,255,255))
img.save(out, dpi=(72,72))
print(out)
