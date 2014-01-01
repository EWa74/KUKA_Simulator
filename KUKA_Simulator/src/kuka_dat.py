#import kuka_dat_test
import bpy

class ObjectSettings(bpy.types.PropertyGroup):
    ID = bpy.props.IntProperty()
    # type: BASEPos, PTP, HOMEPos, ADJUSTMENTPos
    type = bpy.props.StringProperty()
    
    # LOADPTS[1]={FX NAN, FY NAN, FZ NAN, TX NAN, TY NAN, TZ NAN }
    # bpy.data.objects['PTPObj_001'].PATHPTS.LOADPTS[:] 
    LOADPTS = bpy.props.IntVectorProperty(size=6)
    LOADPTSmsk = bpy.props.BoolVectorProperty(size=6) # fuer NAN Eintrag
    
    # TTIMEPTS[1]=0.2
    TTIMEPTS = bpy.props.FloatProperty()
    
    # STOPPTS[1]=1
    STOPPTS = bpy.props.BoolProperty()
    
    # ACTIONMSK[1]=0
    ACTIONMSK = bpy.props.BoolProperty()
    

bpy.utils.register_class(ObjectSettings)

bpy.types.Object.PATHPTS = \
    bpy.props.PointerProperty(type=ObjectSettings)
    
    
print('Hallo kuka_dat')
#kuka_dat_test.Eric()
print('Hallo kuka_dat ...')