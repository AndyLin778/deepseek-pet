"""Build two Codex v2 atlases directly from the supplied bead-chart pixels.

This intentionally keeps the source palette and nearest-neighbor pixel edges.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import json
import math
import sys

ROOT = Path(__file__).resolve().parent.parent / 'dual-form-pet'
OUT = Path(__file__).resolve().parent
CELL=(192,208)
COUNTS=(6,8,8,4,5,8,6,6,6,8,8)
FORM = {
    'normal': dict(scale=3, foot=57, eyes=[(14,28,19,31),(27,28,32,31)], arm=(35,30,48,51), face=(12,26,34,35), head_end=38),
    'pot': dict(scale=4, foot=46, eyes=[(12,20,18,23),(23,20,29,23)], arm=(29,25,41,40), face=(10,19,30,28), head_end=29),
}


def clean_original(form):
    src=Image.open(ROOT/f'{form}-transparent.png').convert('RGBA')
    # White chart background was removed at extraction. Keep only the main figure.
    pixels=src.load()
    allpx={(x,y) for y in range(src.height) for x in range(src.width) if pixels[x,y][3]}
    groups=[]
    while allpx:
        todo=[allpx.pop()]; group=set(todo)
        while todo:
            x,y=todo.pop()
            for n in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                if n in allpx:
                    allpx.remove(n); group.add(n); todo.append(n)
        groups.append(group)
    main=max(groups,key=len)
    for g in groups:
        if g is not main and len(g)<4:
            for p in g:pixels[p]=(0,0,0,0)
    return src


def blink(src,form):
    src=src.copy()
    d=ImageDraw.Draw(src)
    for x0,y0,x1,y1 in FORM[form]['eyes']:
        # Keep the sclera untouched. Only the narrow iris row closes; filling
        # the whole eye from a nearby sample made the whites turn dark blue.
        sclera=src.getpixel((x0+1,y0))
        left,right=x0+2,x1-2
        if left<=right:
            d.line((left,y0+1,right,y0+1),fill=sclera,width=1)
    return src


def feet(src,form,phase):
    src=src.copy()
    start=FORM[form]['foot']
    mid=src.width//2
    for x0,x1,offset in ((0,mid,phase),(mid,src.width,-phase)):
        clip=src.crop((x0,start,x1,src.height))
        ImageDraw.Draw(src).rectangle((x0,start,x1-1,src.height-1),fill=(0,0,0,0))
        src.alpha_composite(clip,(x0+offset,start))
    return src


def wave(src,form,phase):
    src=src.copy()
    x0,y0,x1,y1=FORM[form]['arm']
    clip=src.crop((x0,y0,x1,y1))
    # Move the sleeve as one pixel-art piece; preserve unchanged body underneath.
    src.alpha_composite(clip,(x0+phase//2,y0-phase))
    return src


def look(src,form,index):
    angle=index*math.pi/8
    sx=math.sin(angle); sy=-math.cos(angle)
    config=FORM[form]
    src=src.copy()
    eye=ImageDraw.Draw(src)
    px=round(2*sx)
    py=round(sy)
    if form=='normal':
        # Shift the two original blue irises inside their existing white apertures.
        for left,center in ((16,17),(27,28)):
            eye.rectangle((left,28,left+2,29),fill=(243,236,239,255))
            position=max(left,min(left+2,center+px))
            eye.point((position,28+py),fill=(31,50,75,255))
            eye.point((position,29+py),fill=(161,208,246,255))
    else:
        for left,center in ((14,15),(24,25)):
            eye.line((left,21,left+2,21),fill=(206,204,212,255))
            eye.point((center+px,21+py),fill=(55,72,138,255))
            if 0<=21+py+1<src.height:
                eye.point((center+px,21+py+1),fill=(156,188,222,255))
    end=config['head_end']
    target=Image.new('RGBA',src.size)
    # The feet stay planted; hair and pot follow the head in a stepped pixel arc.
    for y in range(src.height):
        factor=max(0,1-y/end)
        shift_x=round(6*sx*factor)
        shift_y=round(4*sy*factor)
        line=src.crop((0,y,src.width,y+1))
        target.alpha_composite(line,(shift_x,y+shift_y))
    return target


def frame(src,form,row,col):
    if row>=9:
        raw=look(src,form,(row-9)*8+col)
        dx=dy=0
    else:
        raw=src.copy(); dx=dy=0
        if row==0:
            dy=[0,-1,0,1,0,0][col]
            if col==2:raw=blink(raw,form)
        elif row in (1,2):
            raw=feet(raw,form,[0,1,2,1,0,-1,-2,-1][col]); dx=[0,1,2,1,0,-1,-2,-1][col]
            dy=-(col%2)
            if row==2:raw=raw.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        elif row==3:
            raw=wave(raw,form,[0,2,4,1][col]); dy=[0,-1,-2,0][col]
        elif row==4:
            dy=[0,-2,-8,-4,0][col]
        elif row==5:
            dy=[0,1,2,3,2,1,0,1][col]
            if col in (3,4):raw=blink(raw,form)
        elif row==6:
            dy=[0,-1,-2,-1,0,0][col]
        elif row==7:
            dx=[-1,0,1,0,-1,0][col];dy=[0,-1,-1,0,1,0][col]
            if col==3:raw=blink(raw,form)
        elif row==8:
            dx=[0,0,1,2,1,0][col];dy=[0,1,1,0,-1,0][col]
            if col==2:raw=blink(raw,form)
    scale=FORM[form]['scale']
    raw=raw.resize((raw.width*scale,raw.height*scale),Image.Resampling.NEAREST)
    cell=Image.new('RGBA',CELL)
    x=(CELL[0]-raw.width)//2+dx*scale
    y=CELL[1]-raw.height-2+dy*scale
    cell.alpha_composite(raw,(x,y))
    return cell


def build(form):
    src=clean_original(form)
    atlas=Image.new('RGBA',(1536,2288))
    for row,count in enumerate(COUNTS):
        for col in range(count):
            atlas.alpha_composite(frame(src,form,row,col),(col*192,row*208))
    # V2 slot (row 0, column 6) is the still front-facing pointer neutral.
    atlas.alpha_composite(frame(src,form,0,0),(6*192,0))
    dest=OUT/form
    dest.mkdir(parents=True,exist_ok=True)
    atlas.save(dest/'spritesheet.png')
    atlas.save(dest/'spritesheet.webp',lossless=True,method=6)
    (dest/'pet.json').write_text(json.dumps({
        'id':f'lanlan-{form}',
        'displayName':'deepseek鲸鱼娘 · 普通' if form=='normal' else 'deepseek鲸鱼娘 · 铁锅',
        'description':'拼豆像素画还原的双形态桌宠之一',
        'spriteVersionNumber':2,
        'spritesheetPath':'spritesheet.webp'
    },ensure_ascii=False,indent=2),encoding='utf-8')
    # Compact QA sheet: neutral frame and first/last state examples.
    sample=Image.new('RGBA',(192*8,208*3))
    for c in range(8):
        for r,source_row in enumerate((0,3,9)):
            sample.alpha_composite(atlas.crop((c*192,source_row*208,(c+1)*192,(source_row+1)*208)),(c*192,r*208))
    sample.save(dest/'preview-sheet.png')
    durations=((280,110,110,140,140,320),(120,)*7+(220,),(120,)*7+(220,),
               (140,140,140,280),(140,140,140,140,280),(140,)*7+(240,),
               (150,)*5+(260,),(120,)*5+(220,),(150,)*5+(280,))
    labels=('idle','move-right','move-left','wave','jump','failed','waiting','working','review')
    for row,label in enumerate(labels):
        frames=[atlas.crop((col*192,row*208,(col+1)*192,(row+1)*208)) for col in range(COUNTS[row])]
        frames[0].save(dest/f'{label}.gif',save_all=True,append_images=frames[1:],duration=durations[row],loop=0,disposal=2)


if __name__=='__main__':
    for f in ('normal','pot'):
        build(f)
