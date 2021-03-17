import cadquery as cq
from typing import Generator

#Barbed fitting
class BarbFitting:
    #the basic cone/cylinder that serves as the body of the fitting
    body = None
    
    def __init__ (self, maj_dia: float,length: float, barb: Generator, 
                  tip: [None, float]= None, taper: float=0, parent=None  ):
        if taper == 0:
            body = cq.Solid.makeCylinder(maj_dia,length)
        else:
            body = cq.Solid.makeCone(maj_dia,maj_dia*(1-taper),length)
        
        self.parent = cq.Workplane() if parent is None else parent
        self.parent = self.parent.add(body)
b = BarbFitting(2,10,range(0),taper = .25)
SHOW = b.parent