"""Retain three native chair assemblies while matching the source rounded trapezoid seats."""
import bpy,math

def apply_bar_seats(ROOT):
 changed=[]
 for i in range(1,4):
  for suffix,rx,ry in [('Seat',.26,.232),('BentwoodSeat',.266,.234)]:
   ob=bpy.data.objects[f'BAR-CHAIR-{i:02}-{suffix}']
   for v in ob.data.vertices:
    x,y=v.co.x/rx,v.co.y/ry;r=math.hypot(x,y)
    if r<1e-7:continue
    t=math.atan2(y,x);ex=math.copysign(abs(math.cos(t))**(2/4.5),math.cos(t));ey=math.copysign(abs(math.sin(t))**(2/4.5),math.sin(t))
    # Front edge is broader than the back edge; smooth superellipse corners keep padded shape.
    v.co.x=rx*r*ex*(.94+.08*ey);v.co.y=ry*r*ey
   ob.data.update();ob['evidence_status']='Native padded rounded trapezoid plan silhouette and existing thickness; constrained by source4_d three bentwood chairs';changed.append(ob.name)
 return changed
