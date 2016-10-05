# -*- coding: utf-8 -*-    
#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# coding Angabe in Zeilen 1 und 2 fuer Eclipse Luna/ Pydev 3.9 notwendig

#--- ### Header 
bl_info = { 
    "name": "KUKA_OT_Export",
    "author": "Eric Wahl",
    "version": (1, 0, 1),
    "blender": (2, 5, 7),
    "api": 36147,
    "location": "View3D >Objects >KUKA_Tools",
    "category": "Curve",
    "description": "Import/ Editing/ Export Kuka Bahnkurve",
    "warning": "",
    "wiki_url": "http://...",
    "tracker_url": "http://..."
    }

#--- ### Imports
import bpy
# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy_extras.io_utils import ImportHelper
import time # um Zeitstempel im Logfile zu schreiben
import bpy, os
import sys
from bpy.utils import register_module, unregister_module
from bpy.props import FloatProperty, IntProperty
from mathutils import Vector  
from mathutils import *
import mathutils
import math
import re  # zum sortieren de Objektliste
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
from symbol import except_clause
from copy import deepcopy # fuer OptimizeRotation


print('\n\n\n\n\n\n')


global PATHPTSObjName, objBase, objSafe, objCurve, objHome, objEmpty_A6
global Mode, RotationModeBase, RotationModePATHPTS, RotationModeEmpty_Zentralhand_A6, RotationModeTransform
global Vorz1, Vorz2, Vorz3
global CalledFrom, filepath 

'''
def initBlendFile():
    global PATHPTSObjName, objBase, objSafe, objCurve, objHome, objEmpty_A6
    global Mode, RotationModeBase, RotationModePATHPTS, RotationModeEmpty_Zentralhand_A6, RotationModeTransform
    global Vorz1, Vorz2, Vorz3
    global CalledFrom, filepath
    
    if "bpy" in locals():
        #if bpy.data.objects['Sphere_BASEPos'] != None:
        
        
        PATHPTSObjName = 'PTPObj_'
        objBase     = bpy.data.objects['Sphere_BASEPos']
        objSafe     = bpy.data.objects['Sphere_SAFEPos']
        objCurve    = bpy.data.objects['BezierCircle']
        objHome     = bpy.data.objects['Sphere_HOMEPos']
        objEmpty_A6 = bpy.data.objects['Empty_Zentralhand_A6']
        
        Mode = 'XYZ' # YXZ
        
        RotationModeBase = Mode
        RotationModePATHPTS = Mode
        RotationModeEmpty_Zentralhand_A6 = 'QUATERNION' # 'XYZ'
        RotationModeTransform = Mode # XYZ YXZ
        
        Vorz1 = +1#-1 # +C = X
        Vorz2 = +1#-1 # -B = Y
        Vorz3 = +1#-1 # -A = Z
           
        CalledFrom =[] 
        filepath=[]  
        
        print('objBase :' + objBase)
        
    # Global Variables:
    
    
initBlendFile()
'''

def writelog(text=''):
    FilenameLog = bpy.data.filepath
    FilenameLog = FilenameLog.replace(".blend", '.log')
    fout = open(FilenameLog, 'a')
    localtime = time.asctime( time.localtime(time.time()) )
    fout.write(localtime + " : " + str(text) + '\n')
    fout.close();

class KUKA_OT_Import (bpy.types.Operator, ImportHelper): # OT fuer Operator Type
    '''
    writelog('KUKA_OT_Import- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ') 
    writelog('- - - - - - - - - - - - -  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')
    '''
    
    # bpy.ops.object.kuka_import(
    
    
    ''' Import selected curve '''
    bl_idname = "object.kuka_import"
    bl_label = "KUKA_OT_Import (TB)" #Toolbar - Label
    bl_description = "Import selected Curve2" # Kommentar im Specials Kontextmenue
    bl_options = {'REGISTER', 'UNDO'} #Set this options, if you want to update  
    #                                  parameters of this operator interactively 
    #                                  (in the Tools pane)
    
    # check poll() to avoid exception.
    '''
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='EDIT')
    '''  
    @classmethod
    def poll(cls, context):
        return (bpy.context.active_object.type == 'CURVE') # Test, ob auch wirklich ein 'CURVE' Objekt aktiv ist.
    # wenn kein CURVE Objekt aktiv ist, ist der Button inaktiv
    
    # ImportHelper mixin class uses this
    filename_ext = ".dat"

    filter_glob = StringProperty(
            default="*.dat",
            options={'HIDDEN'},
            )
 
    def execute(self, context):  
        '''
        writelog('- - - - - - - - - - - - -  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')
        writelog(' FUNKTIONSAUFRUF KUKA_OT_Import')
        writelog('- - - - - - - - - - - - -  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')
        '''
        
        # Wichtig: Verdrehung des Koordinaten Systems (TODO: vgl. Euler Winkel)
        objBase.rotation_mode     = RotationModeBase
        objSafe.rotation_mode     = RotationModePATHPTS
        objCurve.rotation_mode    = RotationModePATHPTS
        objEmpty_A6.rotation_mode = RotationModeEmpty_Zentralhand_A6
        
        filename = os.path.basename(self.filepath)
        #realpath = os.path.realpath(os.path.expanduser(self.filepath))
        #fp = open(realpath, 'w')
        ObjName = filename
                
        ApplyScale(objCurve)
        #--------------------------------------------------------------------------------
        
        '''
        writelog("Erstellen der BezierCurve: done")
        '''
        
        BASEPos_Koord, BASEPos_Angle = RfF_KeyPos('BASEPos', self.filepath, '.cfg')
        try:
            ADJUSTMENTPos_Koord, ADJUSTMENTPos_Angle = RfF_KeyPos('ADJUSTMENTPos', self.filepath, '.cfg')
        except:
            writelog('failed to load AdjustmentPos')
        try:
            HOMEPos_Koord, HOMEPos_Angle = RfF_KeyPos('HOMEPos', self.filepath, '.cfg')
        except:
            writelog('failed to load HomePos')
        '''
        
        writelog('_________________KUKA_OT_Import - BASEPos_Koord' + str(BASEPos_Koord))
        writelog('_________________KUKA_OT_Import - BASEPos_Angle' +'X C {0:.3f}'.format(BASEPos_Angle[0])+' B Y {0:.3f}'.format(BASEPos_Angle[1])+' A Z {0:.3f}'.format(BASEPos_Angle[2]))
        '''
            
        # create Container (Location, Rotation) for each path point (PTP): dataPATHPTS_Loc, dataPATHPTS_Rot
        #dataPATHPTS_Loc, dataPATHPTS_Rot, PATHPTSCountFile = RfF_PATHPTS(self.filepath, BASEPos_Koord, BASEPos_Angle) # local, bez. auf Base
        dataPATHPTS_Loc, dataPATHPTS_Rot = RfF_KeyPos('PATHPTS', self.filepath, '.dat') # relativ (bez. auf Base)
        PATHPTSCountFile       = len(dataPATHPTS_Loc)
        
        #PATHPTSObjList, countPATHPTSObj  = count_PATHPTSObj(PATHPTSObjName)
        
        SetOrigin(objHome, objHome)
        objHome.location       = HOMEPos_Koord
        objHome.rotation_euler = HOMEPos_Angle
        
        SetOrigin(objBase, objBase)
        objBase.location       = BASEPos_Koord
        objBase.rotation_euler = BASEPos_Angle
        
        # todo: update_ObjList
        # PATHPTSObjList an create_PATHPTSObj uebergeben
                
        create_PATHPTSObj(dataPATHPTS_Loc, dataPATHPTS_Rot, PATHPTSCountFile, BASEPos_Koord, BASEPos_Angle) # relative Koordinaten
        
        # Achtung: die Reihenfolge fon SetCurvePos und SetBasePos muss eingehalten werden! 
        # (da sonst die Curve nicht mit der Base mit verschoben wird!
        
        '''
        
       
        writelog('_________________KUKA_OT_Import - BASEPos_Koord' + str(BASEPos_Koord))
        writelog('_________________KUKA_OT_Import - BASEPos_Angle' + str(BASEPos_Angle))
        '''
        
        SAFEPos_Koord, SAFEPos_Angle = RfF_KeyPos('PTP', self.filepath, '.src') # PTP = SAFEPos
        '''
        writelog('_________________KUKA_OT_Import - BASEPos_Koord' + str(BASEPos_Koord))
        writelog('_________________KUKA_OT_Import - BASEPos_Angle' +'X C {0:.3f}'.format(BASEPos_Angle[0])+' B Y {0:.3f}'.format(BASEPos_Angle[1])+' A Z {0:.3f}'.format(BASEPos_Angle[2]))
        writelog('_________________SAFEPos_Koord: ' + str(SAFEPos_Koord))
        writelog('_________________SAFEPos_Angle' +'X C {0:.3f}'.format(SAFEPos_Angle[0])+' B Y {0:.3f}'.format(SAFEPos_Angle[1])+' A Z {0:.3f}'.format(SAFEPos_Angle[2]))
        '''
        
        # Achtung: Die Reihenfolge der Aufrufe von SetBasePos und get_absolute darf nicht vertauscht werden!
        
        objSafe.location, objSafe.rotation_euler = get_absolute(SAFEPos_Koord, SAFEPos_Angle, BASEPos_Koord, BASEPos_Angle )        #Transformation Local2World
        '''
        writelog('_________________KUKA_OT_Import - BASEPos_Koord' + str(BASEPos_Koord))
        writelog('_________________KUKA_OT_Import - BASEPos_Angle' +'X C {0:.3f}'.format(BASEPos_Angle[0])+' B Y {0:.3f}'.format(BASEPos_Angle[1])+' A Z {0:.3f}'.format(BASEPos_Angle[2]))
        writelog('_________________SAFEPos_Koord: ' + str(SAFEPos_Koord))
        writelog('_________________SAFEPos_Angle' +'A {0:.3f}'.format(SAFEPos_Angle[0])+' B {0:.3f}'.format(SAFEPos_Angle[1])+' C {0:.3f}'.format(SAFEPos_Angle[2]))
        '''
        # todo: GUI Liste aktualisieren (falls vorhanden), danach Aufruf von DefRoute
        
        # Kurve: Origin der Kurve auf BASEPosition verschieben
        SetOrigin(objCurve, objBase)
        bpy.data.objects[objCurve.name].rotation_mode = RotationModePATHPTS
        objCurve.location       = BASEPos_Koord.x,BASEPos_Koord.y ,BASEPos_Koord.z 
        objCurve.rotation_euler = BASEPos_Angle

        Route_ObjList = DefRoute(objEmpty_A6, self.filepath)
        countRoute_ObjList = len(Route_ObjList)
        PathPoint = createMatrix(countRoute_ObjList,3)
        PathAngle = createMatrix(countRoute_ObjList,3)
        for i in range(countRoute_ObjList):    
            PathPoint[i][0:3], PathAngle[i][0:3] = get_relative(bpy.data.objects[Route_ObjList[i]].location, bpy.data.objects[Route_ObjList[i]].rotation_euler, BASEPos_Koord, BASEPos_Angle)        
        
        replace_CP(objCurve, PathPoint)  #relativ, weil Origin der Kurve auf BasePos liegt!
          
        bpy.ops.object.select_all(action='DESELECT')
        objEmpty_A6.select=True
        bpy.context.scene.objects.active = objEmpty_A6
        #--------------------------------------------------------------------------------
        return {'FINISHED'} 
    
    
    '''
    writelog('KUKA_OT_Import done')
    '''
    
    
    


class KUKA_PT_Panel(bpy.types.Panel):
    '''
    writelog('_____________________________________________________________________________')
    writelog()
    writelog('KUKA_PT_Panel....')
    writelog()
    '''
    
    
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "KUKA Panel" # heading of panel
    #bl_idname = "SCENE_PT_layout"
    bl_idname = "OBJECT_PT_layout"
    
    # bpy.ops.OBJECT_PT_layout.module.... 
    
    bl_space_type = 'PROPERTIES' # window type panel is displayed in
    bl_region_type = 'WINDOW' # region of window panel is displayed in
    bl_context = "object"
    #bl_context = "scene"
    
    
    def draw(self, context):
        
        
        ob = context.object
        
        layout = self.layout

        scene = context.scene
        #scene = context.object
        # Create a simple row.
        layout.label(text=" EWa: Simple Row:")

        row = layout.row()
        row.prop(scene, "frame_start")
        row.prop(scene, "frame_end")

        # Create an row where the buttons are aligned to each other.
        layout.label(text=" Aligned Row:")

        row = layout.row(align=True)
        row.prop(scene, "frame_start")
        row.prop(scene, "frame_end")

        # Create two columns, by using a split layout.
        layout.label(text="Tool location / orientation:")
        row = layout.row()

        row.column().prop(ob, "delta_location")
        if ob.rotation_mode == 'QUATERNION':
            row.column().prop(ob, "delta_rotation_quaternion", text="Rotation")
        elif ob.rotation_mode == 'AXIS_ANGLE':
            #row.column().label(text="Tool_Rotation")
            #row.column().prop(pchan, "delta_rotation_angle", text="Angle")
            #row.column().prop(pchan, "delta_rotation_axis", text="Axis")
            #row.column().prop(ob, "delta_rotation_axis_angle", text="Rotation")
            row.column().label(text="Not for Axis-Angle")
        else:
            row.column().prop(ob, "delta_rotation_euler", text="Delta Rotation")
        
        
        layout.label(text="Base location / orientation:")
        row = layout.row()

        row.column().prop(ob, "delta_location")
        if ob.rotation_mode == 'QUATERNION':
            row.column().prop(ob, "delta_rotation_quaternion", text="Rotation")
        elif ob.rotation_mode == 'AXIS_ANGLE':
            #row.column().label(text="Tool_Rotation")
            #row.column().prop(pchan, "delta_rotation_angle", text="Angle")
            #row.column().prop(pchan, "delta_rotation_axis", text="Axis")
            #row.column().prop(ob, "delta_rotation_axis_angle", text="Rotation")
            row.column().label(text="Not for Axis-Angle")
        else:
            row.column().prop(ob, "delta_rotation_euler", text="Delta Rotation")
            
        #row.column().prop(ob, "delta_scale")
         
        
        # Init variable from blendFile:
        layout.label(text="Init variable from blendFile:")
        row = layout.row(align=True)
        sub = row.row()
        sub.scale_x = 1.0
        sub.operator("object.kuka_init_blendfile")  
        #row.operator("object.object_settings")  
        
        # Import/ Export Button:
        layout.label(text="Curvepath Import/ Export:")
        row = layout.row(align=True)        
        sub = row.row()
        sub.scale_x = 1.0
        sub.operator("object.kuka_import")  
        
        '''
        row.operator("object.kuka_export") 
        
        # Set KeyFrames Button:
        layout.label(text="Refresh Button:")
        row = layout.row(align=True)
        
        row.operator("object.refreshbutton")  
        
        # Animate PTPs Button:
        layout.label(text="Animate PTPs:")
        row = layout.row(align=True)
        
        row.operator("object.animateptps")  
        
        # Set BGE Action Button:
        layout.label(text="create BGE (Euler) Action:")
        row = layout.row(align=True)
        
        row.operator("object.bge_actionbutton") 
        
        # Set Initialize blend-File Button:
        layout.label(text="Initialize blend-File:")
        row = layout.row(align=True)
        
        row.operator("object.init_blend_file")  
        '''
        
        #pass 
    '''       
    writelog('KUKA_PT_Panel done')
    writelog('_____________________________________________________________________________')
    '''    
    
class KUKA_OT_InitBlendFile(bpy.types.Operator):
    bl_idname = "object.kuka_init_blendfile"
    bl_label = "initialize blend File" #Toolbar - Label
    bl_description = "set object releated variables" # Kommentar im Specials Kontextmenue
    bl_options = {'REGISTER', 'UNDO'} #Set this options, if you want to update  
    #                                  parameters of this operator interactively 
    #                                  (in the Tools pane)
    
    # bpy.ops.object.kuka_init_blendfile(

    '''
    @classmethod
    def poll(cls, context):
        return ("bpy" in locals()) # Test, ob bpy geladen ist
    '''
    
    
    def execute(self, context):  
        global PATHPTSObjName, objBase, objSafe, objCurve, objHome, objEmpty_A6
        global Mode, RotationModeBase, RotationModePATHPTS, RotationModeEmpty_Zentralhand_A6, RotationModeTransform
        global Vorz1, Vorz2, Vorz3
        global CalledFrom, filepath 
        # Global Variables:
        PATHPTSObjName = 'PTPObj_'
        objBase     = bpy.data.objects['Sphere_BASEPos']
        objSafe     = bpy.data.objects['Sphere_SAFEPos']
        objCurve    = bpy.data.objects['BezierCircle']
        objHome     = bpy.data.objects['Sphere_HOMEPos']
        objEmpty_A6 = bpy.data.objects['Empty_Zentralhand_A6']
        
        Mode = 'XYZ' # YXZ
        
        RotationModeBase = Mode
        RotationModePATHPTS = Mode
        RotationModeEmpty_Zentralhand_A6 = 'QUATERNION' # 'XYZ'
        RotationModeTransform = Mode # XYZ YXZ
        
        Vorz1 = +1#-1 # +C = X
        Vorz2 = +1#-1 # -B = Y
        Vorz3 = +1#-1 # -A = Z
           
        CalledFrom =[] 
        filepath=[]  
        print('\n KUKA_OT_initBlendFile')
        return {'FINISHED'} 

# store keymaps here to access after registration
addon_keymaps = []

def register():
    bpy.utils.register_module(__name__)
    
        
    '''
    # handle the keymap
    wm = bpy.context.window_manager
    # Note that in background mode (no GUI available), keyconfigs are not available either, so we have to check this
    # to avoid nasty errors in background case.
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new(ObjectCursorArray.bl_idname, 'SPACE', 'PRESS', ctrl=True, shift=True)
        kmi.properties.total = 4
        addon_keymaps.append((km, kmi))
    '''    
        
def unregister():
    bpy.utils.unregister_module(__name__)
    '''
    # Note: when unregistering, it's usually good practice to do it in reverse order you registered.
    # Can avoid strange issues like keymap still referring to operators already unregistered...
    # handle the keymap
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    '''
    
    
if __name__ == "__main__":
    register()

