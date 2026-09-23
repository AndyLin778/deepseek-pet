"""Two-form Windows desktop pet, rendered from the extracted bead-chart pixels."""
from pathlib import Path
import argparse
import ctypes
import json
import math
import random
import time
import tkinter as tk
from PIL import Image, ImageTk

HERE = Path(__file__).resolve().parent
KEY = '#ff00ff'


def sprite(form, size=3, blink=False):
    im = Image.open(HERE / f'{form}-transparent.png').convert('RGBA')
    # Keep the main connected figure; discard isolated chart/watermark speckles.
    pixels = im.load()
    unseen = {(x,y) for y in range(im.height) for x in range(im.width) if pixels[x,y][3]}
    groups = []
    while unseen:
        seed = unseen.pop()
        group, todo = {seed}, [seed]
        while todo:
            x,y = todo.pop()
            for p in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                if p in unseen:
                    unseen.remove(p)
                    group.add(p)
                    todo.append(p)
        groups.append(group)
    keep = max(groups, key=len)
    for g in groups:
        if g is not keep and len(g) <= 2:
            for p in g:
                pixels[p] = (0,0,0,0)
    # Eyelids reuse the existing dark lash pixels rather than introducing a new palette.
    if blink:
        eyes = [(14,28,19,31),(27,28,32,31)] if form == 'normal' else [(13,21,17,24),(23,21,27,24)]
        for x0,y0,x1,y1 in eyes:
            if x0+2 <= x1-2:
                color=im.getpixel((x0+1,y0))
                for x in range(x0+2,x1-1):
                    im.putpixel((x,y0+1),color)
    factor = size if form == 'normal' else size * 1.24
    return im.resize((round(im.width*factor),round(im.height*factor)),Image.Resampling.NEAREST)


class Pet:
    def __init__(self, smoke=False):
        self.root = tk.Tk()
        self.root.title('蓝蓝 · 双形态桌宠')
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-transparentcolor', KEY)
        self.root.configure(bg=KEY)
        self.canvas = tk.Canvas(self.root,width=260,height=300,bg=KEY,highlightthickness=0)
        self.canvas.pack()
        self.item = self.canvas.create_image(130,285,anchor='s')
        self.form, self.size = 'normal',3
        self.paused, self.roam = False,False
        self.state, self.started = 'idle',time.monotonic()
        self.next_blink = self.started + random.uniform(2,4)
        self.blink_until = 0
        self.drag = None
        self.last_double_switch = 0
        self.direction = 1
        self.frames = {}
        self.work = self.work_area()
        l,t,r,b = self.work
        self.x,self.y = r-300,b-320
        self.load_settings()
        self.refresh()
        self.place()
        self.menu = tk.Menu(self.root,tearoff=False)
        self.menu.add_command(label='变身：普通 / 铁锅',command=self.switch)
        self.menu.add_command(label='跳一下',command=lambda:self.act('jump'))
        self.menu.add_command(label='摇摇身体',command=lambda:self.act('wiggle'))
        self.menu.add_command(label='开启 / 关闭散步',command=self.toggle_roam)
        self.menu.add_command(label='暂停 / 继续动画',command=self.toggle_pause)
        self.menu.add_separator()
        for n in (2,3,4):
            self.menu.add_command(label=f'大小：{n}',command=lambda n=n:self.resize(n))
        self.menu.add_separator()
        self.menu.add_command(label='退出',command=self.close)
        self.canvas.bind('<ButtonPress-1>',self.press)
        self.canvas.bind('<B1-Motion>',self.move)
        self.canvas.bind('<ButtonRelease-1>',self.release)
        self.canvas.bind('<Double-Button-1>',lambda e:self.double_switch())
        self.canvas.bind('<Button-3>',self.popup)
        self.root.bind('<Escape>',lambda e:self.close())
        self.root.protocol('WM_DELETE_WINDOW',self.close)
        self.tick()
        if smoke:
            original=self.form
            self.smoke_errors=[]
            for base in (150,950):
                for offset,event in ((0,'<ButtonPress-1>'),(20,'<ButtonRelease-1>'),
                                     (80,'<ButtonPress-1>'),(100,'<ButtonRelease-1>')):
                    self.root.after(base+offset,lambda event=event:self.canvas.event_generate(event,x=130,y=120))
            self.root.after(320,lambda:self.smoke_errors.append('first double-click') if self.form==original else None)
            self.root.after(1120,lambda:self.smoke_errors.append('second double-click') if self.form!=original else None)
            self.root.after(1170,lambda:self.act('jump'))
            self.root.after(1270,lambda:self.resize(4))
            self.root.after(1400,lambda:self.resize(3))
            self.root.after(1600,self.root.destroy)

    def work_area(self):
        from ctypes import wintypes
        rect=wintypes.RECT()
        if ctypes.windll.user32.SystemParametersInfoW(48,0,ctypes.byref(rect),0):
            return rect.left,rect.top,rect.right,rect.bottom
        return 0,0,self.root.winfo_screenwidth(),self.root.winfo_screenheight()

    def load_settings(self):
        try:
            s=json.loads((HERE/'settings.json').read_text(encoding='utf-8'))
            self.form=s.get('form','normal') if s.get('form') in ('normal','pot') else 'normal'
            self.size=s.get('size',3) if s.get('size') in (2,3,4) else 3
            self.x,self.y=int(s.get('x',self.x)),int(s.get('y',self.y))
        except (OSError,ValueError,TypeError):
            pass

    def refresh(self):
        self.frames={}
        self.atlas_frames={}
        for form in ('normal','pot'):
            atlas_path=HERE/f'atlas-{form}.webp'
            if not atlas_path.exists():
                self.frames.update({(form,b):ImageTk.PhotoImage(sprite(form,self.size,b)) for b in (False,True)})
                continue
            atlas=Image.open(atlas_path).convert('RGBA')
            for row,count in enumerate((6,8,8,4,5,8,6,6,6)):
                for col in range(count):
                    cell=atlas.crop((col*192,row*208,(col+1)*192,(row+1)*208))
                    if self.size!=3:
                        cell=cell.resize((round(192*self.size/3),round(208*self.size/3)),Image.Resampling.NEAREST)
                    self.atlas_frames[form,row,col]=ImageTk.PhotoImage(cell)

    def place(self):
        l,t,r,b=self.work
        self.x=max(l,min(r-260,self.x)); self.y=max(t,min(b-300,self.y))
        self.root.geometry(f'260x300{int(self.x):+d}{int(self.y):+d}')

    def act(self,state):
        self.state,self.started=state,time.monotonic()

    def switch(self):
        self.form='pot' if self.form=='normal' else 'normal'
        self.act('transform')

    def double_switch(self):
        now=time.monotonic()
        if now-self.last_double_switch < .4:
            return
        self.last_double_switch=now
        self.switch()

    def resize(self,size):
        self.size=size
        self.refresh()

    def toggle_roam(self):
        self.roam=not self.roam

    def toggle_pause(self):
        self.paused=not self.paused

    def popup(self,e):
        try:
            self.menu.tk_popup(e.x_root,e.y_root)
        finally:
            self.menu.grab_release()

    def press(self,e):
        self.drag=(e.x_root,e.y_root,self.x,self.y)

    def move(self,e):
        if self.drag:
            px,py,x,y=self.drag
            self.x,self.y=x+e.x_root-px,y+e.y_root-py
            self.place()

    def release(self,e):
        self.drag=None

    def tick(self):
        now=time.monotonic()
        elapsed=now-self.started
        dx=dy=0
        blink=False
        if not self.paused:
            if now>=self.next_blink:
                self.blink_until=now+.13
                self.next_blink=now+random.uniform(2.6,5.2)
            blink=now<self.blink_until
            dy=round(2*math.sin(now*2.2))
            if self.state in ('jump','transform'):
                duration=.75 if self.state=='jump' else .42
                if elapsed<duration:
                    dy-=round(38*math.sin(math.pi*elapsed/duration))
                else:
                    self.state='idle'
            elif self.state=='wiggle':
                if elapsed<1.1:
                    dx=round(7*math.sin(elapsed*24))
                else:
                    self.state='idle'
            if self.roam and not self.drag:
                self.x+=self.direction*.65
                if self.x<=self.work[0] or self.x>=self.work[2]-260:
                    self.direction*=-1
                self.place()
                dy+=round(3*abs(math.sin(now*8)))
        if self.atlas_frames:
            if self.roam and not self.drag and self.state=='idle':
                row=1 if self.direction>0 else 2
            else:
                row={'idle':0,'jump':4,'transform':4,'wiggle':3}.get(self.state,0)
            counts=(6,8,8,4,5)
            timing=(.17,.12,.12,.18,.14)
            elapsed_in_row=elapsed if self.state!='idle' else now
            col=min(counts[row]-1,int(elapsed_in_row/timing[row])%counts[row])
            image=self.atlas_frames[self.form,row,col]
        else:
            image=self.frames[self.form,blink]
        self.canvas.itemconfigure(self.item,image=image)
        self.canvas.coords(self.item,130+dx,285+dy)
        self.root.after(33,self.tick)

    def close(self):
        (HERE/'settings.json').write_text(json.dumps(dict(form=self.form,size=self.size,x=self.x,y=self.y)),encoding='utf-8')
        self.root.destroy()


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--smoke-test',action='store_true')
    args=parser.parse_args()
    pet=Pet(args.smoke_test)
    pet.root.mainloop()
    if args.smoke_test and pet.smoke_errors:
        raise SystemExit('Smoke test failed: '+', '.join(pet.smoke_errors))
