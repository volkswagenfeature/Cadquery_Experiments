import cadquery as cq
import math
from collections import namedtuple
from typing import Tuple
# dimensions in mm


######## Packaged Class #############

class v_block:
    #first order aproximation of s/cos(x/2) . 
    #Guarenteed to be larger in range (-179,179) exclusive.
    #Why did I write this instead of just importing a normal cosine?
    #The world may never know. 
    badacos = staticmethod(lambda x: (10200)/(8100-(x/2)**2))
    
    _outline_params_proto = namedtuple('outline','width height groove g_angle',
                                       defaults=[20,20,5,90])
    _stripe_params_proto  = namedtuple('stripe' ,'thickness spacing s_angle',
                                       defaults=[1,2,45])
    _add_params_proto = namedtuple('additional','depth shell_thick ',
                                       defaults=[20,1])
    
    #Initialized in init (later)
    outline_params = None # Of type outline
    stripe_params = None # Of type stripe
    additional_params=None #Of type additional
    max_d = None
    
    # The reference point that is used to spin the infill pattern. 
    # defined in init
    Pivot = None
    
    #Further stuff computationaly assigned
    parent = None # Parent workplane
    p_vector = None # Perpendicular vector
    
    #Temporary placeholder assignments.
    #When class is finalized, will move actual functions into place

    
    def calc_alignment(self) -> Tuple[cq.Vector,cq.Vector]:
        #TODO: Finish this!
        return cq.Vector(0,0,0),cq.Vector(0,0,0)
    def gen_outline(self):
        o = (
                self.parent
                .box(self.outline_params.width, 
                     self.outline_params.height, 
                     self.additional_params.depth)
                .faces(">Y")
                .workplane()
                .moveTo(0,self.outline_params.height/2
                         -self.outline_params.groove)
                .polarLine(self.outline_params.groove*self.badacos(self.outline_params.g_angle),
                           90 - self.outline_params.g_angle/2)
                .hLineTo(0)
                .mirrorY()
                .cutThruAll()
            )
        #o = outline(self.outline_params.width,
        #            self.outline_params.height,
        #            self.additional_params.depth,
        #            self.outline_params.groove,
        #            self.outline_params.g_angle,
        #            self.parent)
        return o
    
    def stripefill(self):#,thickness,spacing,angle,parent,max_d=None,norm=None,offset=cq.Vector(0,0,0)):
        thickness = self.stripe_params.thickness
        spacing = self.stripe_params.spacing
        reps = math.ceil(self.max_d /(thickness + spacing)) + 2
        front_face = self.outline.faces(cq.DirectionMinMaxSelector(self.p_vector)).findFace()
        log(type(front_face))
        
        # TODO: rotation vector has to be changed from (90,0,0) to something which acomidates
        # real pointing of block, rather than just nominal pointing.
        r = cq.Workplane(front_face,front_face.Center()).transformed((90,0,0))
        r = r.center(-self.max_d/2,-self.max_d/2)
        
        
        for _ in range(reps):
            r = r.rect(self.max_d,spacing,False).center(0,thickness+spacing)
        
                
        final = (r.extrude(self.max_d)
                  .rotateAboutCenter(self.p_vector,self.stripe_params.s_angle)
                )
        return final
    
    
    
    def gen_stripes(self):
        s = self.stripefill(self.stripe_params.thickness,
                       self.stripe_params.spacing,
                       self.stripe_params.s_angle,
                       self.parent,
                       self.max_d,
                       cq.Vector(1,1,0),#self.p_vector,
                       self.calc_alignment())
        return s

    
    
    def __init__(self,*args,**kwargs):
        
        o_p = self._outline_params_proto._fields
        s_p = self._stripe_params_proto._fields
        a_p = self._add_params_proto._fields
        
        allargs = o_p + a_p + s_p
        
        # Match each positional argument to its keyword 
        for arg, assigned_val in zip(allargs,args):
            kwargs[arg] = assigned_val
        
        #Gets keys+values in a that are 
        def key_intersect(dict_a,list_b):
            ret = {}
            log(type(dict_a))
            for key in list_b:
                try:
                    ret[key]=dict_a[key]
                except KeyError:
                    continue
            return ret
        self.outline_params = self._outline_params_proto(**key_intersect(kwargs,o_p))
        #print("Outline:",self.outline_params)
        
        self.stripe_params = self._stripe_params_proto(**key_intersect(kwargs,s_p))
        #print("Stripe:",self.stripe_params)
        
        self.additional_params = self._add_params_proto(**key_intersect(kwargs,a_p))
        #print("Additional:",self.additional_params)
        
        self.parent = cq.Workplane("XY") if 'parent' not in kwargs else kwargs['parent']
        
        
        
        # Known problems: If the parent object doesn't have a face to be found this will die.
        # If no parent is specified, it should be fine, because of how parent is assigned above.
        try:
            self.p_vector = self.parent.findFace().normalAt()
        except AttributeError:
            self.p_vector = cq.Vector(0,1,0)


        # Generating outline. Pre-requisite for further generation.
        self.outline = self.gen_outline()
        
        # Generating other vital data
        self.max_d = self.outline.largestDimension()
        
        #Assigning stripes object and shell object
        self.stripes = self.stripefill()
        self.shell = self.outline.faces(">Y or <Y").shell(-self.additional_params.shell_thick,'intersection')
        
        
    def draw(self):
        return self.outline - self.stripes + self.shell

        
    
#o2d=outline_2d(block_width,block_height,block_depth,groove_depth,groove_angle)
#st = stripefill(Rib_thick,Rib_space,groove_angle/2,cq.Workplane("XZ"),35,cq.Vector(0,1,0))

#test = o2d-s + o2d.faces(">Y or <Y").shell(shell_thick,'intersection')
if __name__ == "temp":
    s = v_block(shell_thick=2)
    block = s.draw()
