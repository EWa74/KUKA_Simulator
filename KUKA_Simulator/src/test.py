# delete this line (commit and push test 2015)
# each item in a matrix is a vector so vector utility functions can be used
file:///F:/EWa_WWW_Tutorials/Scripting/blender_python_reference_2_68_5/mathutils.html#mathutils.Vector
  
import mathutils
from math import radians

vec = mathutils.Vector((1.0, 2.0, 3.0))

mat_rot = mathutils.Matrix.Rotation(radians(90.0), 4, 'X')
mat_trans = mathutils.Matrix.Translation(vec)

mat = mat_trans * mat_rot
mat.invert()

mat3 = mat.to_3x3()
quat1 = mat.to_quaternion()
quat2 = mat3.to_quaternion()

quat_diff = quat1.rotation_difference(quat2)

print(quat_diff.angle)


# Übernehmen der *.src in delta transform loc, rot
'''

Fehlverständnis: mit delta transform kann nicht die tool pos gesetzt werden...
bpy.data.objects[bpy.context.active_object.name].delta_location.x = float(PTPX[0])/1000
bpy.data.objects[bpy.context.active_object.name].delta_location.y = float(PTPY[0])/1000
bpy.data.objects[bpy.context.active_object.name].delta_location.z = float(PTPZ[0])/1000
bpy.data.objects[bpy.context.active_object.name].delta_rotation_euler.x = float(PTPAngleA[0]) * 2*math.pi /360 # in rad angeben
bpy.data.objects[bpy.context.active_object.name].delta_rotation_euler.y = float(PTPAngleB[0]) * 2*math.pi /360
bpy.data.objects[bpy.context.active_object.name].delta_rotation_euler.z = float(PTPAngleC[0]) * 2*math.pi /360
'''


'''
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects['Sphere_ToolPos'].select= True
    original_type = bpy.context.area.type
    bpy.context.area.type = "VIEW_3D"
    bpy.ops.view3d.snap_cursor_to_selected() # setze Cursor-Position auf Origin um die xyz daten schreiben zu können (PTP)
    #bpy.context.area.type = original_type
    bpy.data.objects['Sphere_ToolPos'].select= False
    bpy.ops.object.select_all(action='DESELECT')
    obj.select = True 
    '''
    
    
    
    # Empty_Zentralhand_A6 auf ersten Punkt der Kurve setzen:
    # Achtung: Parenting (Kurve/ Empty) vorher lösen und danach wieder herstellen
    print()
    
    '''
    bpy.ops.object.select_all(action='DESELECT')
    original_type = bpy.context.area.type
    bpy.context.area.type = "VIEW_3D"
    bpy.ops.object.editmode_toggle()
    bpy.context.active_object.data.splines[0].bezier_points[0].select_control_point= True
    bpy.ops.view3d.snap_cursor_to_selected() 
    bpy.context.active_object.data.splines[0].bezier_points[0].select_control_point= False
    bpy.ops.object.editmode_toggle()
    bpy.data.objects['Empty_Zentralhand_A6'].select = True
    bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
    bpy.data.objects['Empty_Zentralhand_A6'].select = False
    
    bpy.context.area.type = original_type
    obj.select = True # Kurve wieder als aktives Objekt setzen
    '''
    
    
    
    
    
    ObjNameEmpty = 'Empty_Zentralhand_A6'
    ObjNameCuve = obj.name
    # - Deselect alle Objekte und in Objekte in richtiger Reihenfolge auswählen
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[ObjNameEmpty].select= True
    obj.select = True
    # - Parenting lösen    
    bpy.ops.object.parent_clear(type='CLEAR') # CLEAR_KEEP_TRANSFORM
    # - deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    # - Kurve selektieren
    obj.select = True
   
    # --> [STRG] + A (Apply Location, Rotation) wird nicht normiert sondern wieder eingelesen! (KUKA ToolPosition)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # -------------------------------------------------------------------------------------------  
    # nach dem Skalieren wird das Parenting wieder hergestellt:
    
    
    # Deselct alle Objekte und in Objekte in richtiger Reihenfolge auswählen
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[ObjNameEmpty].select= True
    obj.select = True
    # Parenting wieder herstellen    
    bpy.ops.object.parent_set(type='FOLLOW', xmirror=False, keep_transform=False)
    #bpy.ops.object.parent_set(type='FOLLOW', xmirror=False, keep_transform=True)
    bpy.ops.object.select_all(action='DESELECT')
    obj.select = True
    
    
    # -------------------------------------------------------------------------------------------  
    # position der Zentralhand A6 auf Kurve ausrichten:
    
    
    # Empty_Zentralhand_A6 auf ersten Punkt der Kurve setzen:
    # Achtung: Parenting (Kurve/ Empty) vorher lösen und danach wieder herstellen
    bpy.ops.object.select_all(action='DESELECT')
    original_type = bpy.context.area.type # wird am Ende der Funktion wieder zurück gesetzt
    bpy.context.area.type = "VIEW_3D"
    bpy.ops.object.editmode_toggle()
    bpy.context.active_object.data.splines[0].bezier_points[0].select_control_point= True
    bpy.ops.view3d.snap_cursor_to_selected() 
    bpy.context.active_object.data.splines[0].bezier_points[0].select_control_point= False
    bpy.ops.object.editmode_toggle()
    bpy.data.objects['Empty_Zentralhand_A6'].select = True
    bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
    bpy.data.objects['Empty_Zentralhand_A6'].select = False
    
    bpy.context.area.type = original_type
    obj.select = True # Kurve wieder als aktives Objekt setzen
    
    
    
    '''
        bpy.context.scene.cursor_location.x = float(PTPX[0])/1000
        bpy.context.scene.cursor_location.y = float(PTPY[0])/1000
        bpy.context.scene.cursor_location.z = float(PTPZ[0])/1000
        ''' 
        
        
  ''' 527 - am Ende der Funktion File2Curve
        # setze Position auf Origin um die xyz daten schreiben zu können (PTP)
        original_type = bpy.context.area.type
        bpy.context.area.type = "VIEW_3D"
        bpy.ops.view3d.snap_cursor_to_selected() 
        bpy.context.area.type = original_type
        
        bpy.ops.object.select_all(action='DESELECT')
        obj.select = True # Kurve wieder als aktives Objekt setzen
        
        
        # - Origin auf Position des 3D-Cursors setzen:

        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
        #bpy.ops.object.select_all(action='DESELECT')
        #obj.select = True # Kurve wieder als aktives Objekt setzen
        '''      
        
        
        
               #bpy.ops.object.editmode_toggle()
        #bpy.context.active_object.data.splines[0].bezier_points[0].select_control_point= True
        # ----
        #bpy.ops.view3d.snap_cursor_to_selected() läuft nicht???
        #alternativ:
        
        #spline[0] - global/ local:
        #x = 2.20/ 1.869 -> rotation: -11.842°
        #y= 0.170/-.679 -> 13.49°
        #z= 0.717/-0.506 -> -2.02°
        #import mathutils
        #from math import radians
         
        
        #bpy.context.scene.cursor_location = bpy.data.objects[obj.name].location
        #eul = mathutils.Euler((bpy.data.objects[obj.name].rotation_euler.x, bpy.data.objects[obj.name].rotation_euler.y, bpy.data.objects[obj.name].rotation_euler.z), 'XYZ')
        #vec = bpy.context.scene.cursor_location
        #vec.rotate(eul)
        #bpy.context.scene.cursor_location = vec


        # ----
        #bpy.context.active_object.data.splines[0].bezier_points[0].select_control_point= False
        #bpy.ops.object.editmode_toggle()
        #bpy.data.objects['Empty_Zentralhand_A6'].select = True
        #bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
        #bpy.data.objects['Empty_Zentralhand_A6'].select = False
        
        
        
        
    
# Origin auf Toolposition setzen
#1. transf. der alten daten der curve auf global
#d.h. bezier_points wird von local auf global transformiert:
point_local = []
point_world_alt = []
object       = bpy.data.objects['BezierCircle']
matrix_world = object.matrix_world
curve_data   = object.data
point_local  = curve_data.splines[0].bezier_points
#2. speicher alte curve data global
point_world_alt = matrix_world * point_local 
#Reihenfolge ist relevant!

#3. verschiebe kurve auf neue Position (inkl. Origin)
# d.h. globale Koordinaten des MESHES ermitteln:
object       = bpy.data.objects['Sphere_ToolPos']
matrix_world = object.matrix_world
meshes_data  = object.data
point_local  = meshes_data.vertices[0].co
point_world  = matrix_world * point_local #Reihenfolge ist relevant!
bpy.data.meshes['Cube'].vertices[0].co
# kruve dort positionieren:
bpy.data.objects[obj.name].location = point_world

#4. transf. der alten daten der curve auf neu local
curve_data.splines[0].bezier_points = point_world_alt



-------------------------------------------------------------
# Origin auf Toolposition setzen
#1. transf. der alten daten der curve auf global
#d.h. bezier_points wird von local auf global transformiert:
point_local = []
point_world_alt = []
object       = bpy.data.objects[obj.name]
matrix_world = object.matrix_world
curve_data   = object.data
point_local  = curve_data.splines[0].bezier_points
#2. speicher alte curve data global
point_world_alt = matrix_world * point_local 
#Reihenfolge ist relevant!

#3. verschiebe kurve auf neue Position (inkl. Origin)
# d.h. globale Koordinaten des MESHES ermitteln:
object       = bpy.data.objects['Sphere_ToolPos']
matrix_world = object.matrix_world
meshes_data  = object.data
point_local  = meshes_data.vertices[0].co
point_world  = matrix_world * point_local #Reihenfolge ist relevant!
bpy.data.meshes['Cube'].vertices[0].co
# kruve dort positionieren:
bpy.data.objects[obj.name].location = point_world

#4. transf. der alten daten der curve auf neu local
curve_data.splines[0].bezier_points = point_world_alt
------------------------------------------------------------------
#1. transf. der alten daten der curve auf global
# d.h. bezier_points[0] wird von local auf global transformiert:
# bpy.data.objects['Sphere_ToolPos'].data.vertices[0].co
point_local = []
point_world_alt = []
object       = bpy.data.objects[obj.name]
matrix_world = object.matrix_world
curve_data   = object.data
count= len(bpy.data.objects[obj.name].data.splines[0].bezier_points) 
for n in range(0,count,1):
    point_local_co  = curve_data.splines[0].bezier_points[n].co
    point_local_hl  = curve_data.splines[0].bezier_points[n].handle_left
    point_local_hr  = curve_data.splines[0].bezier_points[n].handle_right
    
    #2. speicher alte curve data global
    point_world_alt_co = point_world_alt + [matrix_world * point_local_co] #Reihenfolge ist relevant!
    point_world_alt_hl = point_world_alt + [matrix_world * point_local_hl] #Reihenfolge ist relevant!
    point_world_alt_hr = point_world_alt + [matrix_world * point_local_hr] #Reihenfolge ist relevant!
#3. verschiebe kurve auf neue Position (inkl. Origin)
# d.h. globale Koordinaten des MESHES ermitteln:
object       = bpy.data.objects['Sphere_ToolPos']
matrix_world = object.matrix_world
meshes_data  = object.data
point_local  = meshes_data.vertices[0].co
point_world  = matrix_world * point_local #Reihenfolge ist relevant!
bpy.data.meshes['Cube'].vertices[0].co
# kruve dort positionieren:
bpy.data.objects[obj.name].location = point_world

#4. transf. der alten daten der curve auf neu local
for n in range(0,count,1):
    curve_data.splines[0].bezier_points[n].co = point_world_alt_co[n]
    curve_data.splines[0].bezier_points[n].handle_left = point_world_alt_hl[n]
    curve_data.splines[0].bezier_points[n].handle_right = point_world_alt_hr[n]
    

# Empty_Zentralhand_A6 auf Startpunkt der Kurve setzen
object_c     = bpy.data.objects[obj.name]
matrix_world = object_c.matrix_world
curve_data   = object_c.data
point_local  = curve_data.splines[0].bezier_points[0].co
point_world  = matrix_world * point_local #Reihenfolge ist relevant!

bpy.data.objects['Empty_Zentralhand_A6'].location = point_world

_________________________________-

Kontext: (ist wohl eher ein neues Thema): Ziel ist es vorhandene Koordinaten (x,y,z, Alpha,Beta, Gamma) in location und rotation auf jeden einzelnen Kurvenpunkt zu übertragen. Das funktioniert für location schon.

2. Frage: Gibt es einen Trick wie man die drei vorgegebenen Winkel am einfachsten auf die Rotation eines Bezierpoints (handle_left, handle_right, tilt) anwendet?
- Problem: 
- Umrechnung auf Vector des handles kann zu DIV0 führen.
- tilt (in Radiant): sollte nicht das Problem sein... 

____________________________________--


- Origin eines Objektes (hier "BezierCircle") auf den Origin eines anderen (hier: "MESHESObject" verlegen.
- Empty auf die erste Koordinate der Curve (local/ global Transformation) setzen. Dazu wird die Curve Koordinate von local -> global transformiert.

Danke an Blendpolis -> tobain :o)

import bpy

obj = bpy.data.objects['BezierCircle']

original_type = bpy.context.area.type
bpy.context.area.type = "VIEW_3D"

# Origin-'BezierCircle' auf Origin-'MESHESObject' verlegen   
bpy.ops.object.select_all(action='DESELECT')
bpy.data.objects['MESHESObject'].select= True
bpy.ops.view3d.snap_cursor_to_selected() 

bpy.ops.object.select_all(action='DESELECT')
obj.select = True 

bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

bpy.context.area.type = original_type
        
# Empty auf Startpunkt des 'BezierCircle' setzen

# Achtung: Delta Location muss auf Nullgesetzt werden:
obj.delta_location = (0,0,0)

objectx       = bpy.data.objects['BezierCircle']
matrix_world = objectx.matrix_world
curve_data   = objectx.data
point_local  = curve_data.splines[0].bezier_points[0].co
point_world  = matrix_world * point_local

bpy.data.objects['Empty'].location = point_world

bpy.ops.object.select_all(action='DESELECT')

________________

def SetUpSceneForFileTransfer(obj, begin, end):
    ObjNameEmpty = 'Empty_Zentralhand_A6'
    ObjNameCuve = obj.name
    
    original_type = bpy.context.area.type
    bpy.context.area.type = "VIEW_3D"
        
    if begin ==1:
        
        # Wichtig: Vor dem Export muss die Lokale-Skalierung erst mit der Global-Skalierung in Übereinstimmung gebracht werden.
        # Entspricht [STRG] + A (Apply Scale)
        # um nicht auch das Tool selber zu beeinflussen muss das parenting dafür gelöst werden.
        # nur für Scaling, da Location, Rotatation (mit Hilfe des Mesh-Objektes 'Sphere_ToolPos') beim Export in *.src file geschrieben wird:
        # --> [STRG] + A (Apply Location, Rotation) wird nicht normiert sondern wieder eingelesen! (KUKA ToolPosition)
        
        # Parenting zwischen Empty und Kurve lösen:
        # - Deselct alle Objekte und in Objekte in richtiger Reihenfolge auswählen
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects[ObjNameEmpty].select= True
        obj.select = True  
        bpy.ops.object.parent_clear(type='CLEAR')
        
        # Parenting zwischen ToolPosition und Kurve lösen:
        bpy.ops.object.select_all(action='DESELECT')
        obj.select = True   
        bpy.data.objects['Sphere_ToolPos'].select= True 
        bpy.ops.object.parent_clear(type='CLEAR')
        
        # nur Kurve auswählen
        bpy.ops.object.select_all(action='DESELECT')
        obj.select = True
        
        # Scaling (nur bei Export nötig, bei Import schadets nichts...)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        
        # Origin auf Toolposition setzen   
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects['Sphere_ToolPos'].select= True
        bpy.ops.view3d.snap_cursor_to_selected() 
        
        bpy.ops.object.select_all(action='DESELECT')
        obj.select = True 
        
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
                
        bpy.ops.object.select_all(action='DESELECT')
        obj.select = True 
        

    elif end ==1:
        # Empty_Zentralhand_A6 auf Startpunkt der Kurve setzen
        # d.h. bezier_points[0] wird von local auf global transformiert:
        
        # Achtung: Delta Location muss auf Nullgesetzt werden:
        obj.delta_location = (0, 0, 0)

        current_obj  = bpy.data.objects[obj.name]
        matrix_world = current_obj.matrix_world
        curve_data   = current_obj.data
        # Wichtig: Beim letzten Punkt in der Kurve [-1] Anfangen, warum auch immer
        # (ansonsten offset zwischen Punkt [0] und [-1]
        point_local  = curve_data.splines[0].bezier_points[-1].co
        point_world  = matrix_world * point_local #Reihenfolge ist relevant!

        bpy.data.objects['Empty_Zentralhand_A6'].location = point_world
        
        # Parenting wieder herstellen:
        # -------------------------------------------------------------------------------------------  
        bpy.data.objects[obj.name].parent = bpy.data.objects['Sphere_ToolPos']
        bpy.data.objects[obj.name].parent_type = 'OBJECT'
        
        bpy.data.objects['Empty_Zentralhand_A6'].parent = bpy.data.objects[obj.name]
        bpy.data.objects['Empty_Zentralhand_A6'].parent_type = 'OBJECT'
        
        # -------------------------------------------------------------------------------------------
        
    bpy.context.area.type = original_type
    
    
_____
Läuft, muss aber 2x aufgerufen werden!!
Scaling nicht berücksichtigt!

def SetUpSceneForFileTransfer(obj, begin, end):
    ObjNameEmpty = 'Empty_Zentralhand_A6'
    ObjNameCuve = obj.name
    
    original_type = bpy.context.area.type
    bpy.context.area.type = "VIEW_3D"
        
    if begin ==1:
        
        # Wichtig: Vor dem Export muss die Lokale-Skalierung erst mit der Global-Skalierung in Übereinstimmung gebracht werden.
        # Entspricht [STRG] + A (Apply Scale)
        # um nicht auch das Tool selber zu beeinflussen muss das parenting dafür gelöst werden.
        # nur für Scaling, da Location, Rotatation (mit Hilfe des Mesh-Objektes 'Sphere_ToolPos') beim Export in *.src file geschrieben wird:
        # --> [STRG] + A (Apply Location, Rotation) wird nicht normiert sondern wieder eingelesen! (KUKA ToolPosition)
        
        
        # Origin auf Toolposition setzen   
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects['Sphere_ToolPos'].select= True
        bpy.ops.view3d.snap_cursor_to_selected() 
        
        bpy.ops.object.select_all(action='DESELECT')
        obj.select = True 
        
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
        
        # Empty_Zentralhand_A6 auf Startpunkt der Kurve setzen

        # Achtung: Delta Location muss auf Nullgesetzt werden:
        obj.delta_location = (0,0,0)
        
        object       = bpy.data.objects['BezierCircle']
        matrix_world = object.matrix_world
        curve_data   = object.data
        # Wichtig: Beim letzten Punkt in der Kurve [-1] Anfangen, warum auch immer
        # (ansonsten offset zwischen Punkt [0] und [-1]
        point_local  = curve_data.splines[0].bezier_points[-1].co
        point_world  = matrix_world * point_local
        
        bpy.data.objects['Empty_Zentralhand_A6'].location = point_world
        
        bpy.data.objects['Empty_Zentralhand_A6'].parent = bpy.data.objects[obj.name]
        
    bpy.context.area.type = original_type
    
    
_____
Fehlerhaft:


def SetUpSceneForFileTransfer(obj, begin, end):

    # Achtung: diese Funktion muss 2x hintereinander ausgeführt werden,
    #weil beim parenting die location vom parent auf das child übertragen wird!
        
    # Block 1: Das Empty soll auf den Startpunkt der Kurve gesetzt werden.
    
    original_type = bpy.context.area.type
    bpy.context.area.type = "VIEW_3D"
    
    # Origin auf Toolposition setzen   
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects['Sphere_ToolPos'].select= True
    bpy.ops.view3d.snap_cursor_to_selected() 
    
    bpy.ops.object.select_all(action='DESELECT')
    obj.select = True 
    
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    
    # Block 2: Das Empty soll auf den Startpunkt der Kurve gesetzt werden.       
    
    # Achtung: Delta Location muss auf Nullgesetzt werden:
    obj.delta_location = (0,0,0)
    
    object       = bpy.data.objects['BezierCircle']
    matrix_world = object.matrix_world
    curve_data   = object.data
    point_local  = curve_data.splines[0].bezier_points[0].co
    point_world  = matrix_world * point_local
    
    bpy.data.objects['Empty_Zentralhand_A6'].location = point_world
    
    # Parenting wieder herstellen:
    # -------------------------------------------------------------------------------------------  
    bpy.data.objects['Empty_Zentralhand_A6'].parent = bpy.data.objects[obj.name]
    #bpy.data.objects['Empty_Zentralhand_A6'].parent_type = 'OBJECT'
    # -------------------------------------------------------------------------------------------
    
    '''
    # Block 3: Die Curve soll der ToolPos folgen.       
    
    # Achtung: Delta Location muss auf Nullgesetzt werden:
    obj.delta_location = (0,0,0)
    
    object       = bpy.data.objects['Sphere_ToolPos']
    matrix_world = object.matrix_world
    meshes_data  = object.data
    point_local  = meshes_data.vertices[0].co
    point_world  = matrix_world * point_local
    
    bpy.data.objects['BezierCircle'].location = point_world
    
    # Parenting wieder herstellen:
    # -------------------------------------------------------------------------------------------  
    bpy.data.objects[obj.name].parent = bpy.data.objects['Sphere_ToolPos']
    bpy.data.objects[obj.name].parent_type = 'OBJECT'
    # -------------------------------------------------------------------------------------------
    '''
    
    
    
    bpy.context.area.type = original_type
    _____________________________________________________-
    
    
        # Problem: vertex[0] hat als global setting die xyz werte. Soll: als local (mit origin auf Base)
        
        # Lsg.:
        # 1. transformation der local settings (aus *.src) auf global
        # 2. setzen des SafePos Origin auf vertex[0]
        # 3. übertragen mit .location
        # 4. origin auf base setzen (wir von der Funktion 'SetUpSceneForFileTransfer' übernommen.
        
        # 1. transformation der local settings (aus *.src) auf global:
        
        
        
        object       = bpy.data.objects[objSafe.name]
        matrix_world = object.matrix_world
        meshes_data  = object.data
        # Vector (PTPX + PTPY + PTPZ)
        point_local  = meshes_data.vertices[0].co
        point_world  = matrix_world * point_local
        
        # 2. setzen des SafePos Origin auf vertex[0]:
        original_type = bpy.context.area.type # wird am Ende der Funktion wieder zurück gesetzt
        bpy.context.area.type = "VIEW_3D"
        bpy.ops.object.editmode_toggle()
        # bpy.data.objects['Sphere_SAFEPos'].data.vertices[0].select
        meshes_data.vertices[0].select= True
        bpy.ops.view3d.snap_cursor_to_selected() 
        meshes_data.vertices[0].select= False
        bpy.ops.object.editmode_toggle()
        bpy.data.objects[objSafe.name].select = True
        bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
        bpy.data.objects[objSafe.name].select = False
        bpy.context.area.type = original_type
        
        # 3. übertragen mit .location:
        # SAFEPosition initialisieren:
        bpy.data.objects[objSafe.name].location.x = point_world.x/SkalierungPTP
        bpy.data.objects[objSafe.name].location.y = point_world.y/SkalierungPTP
        bpy.data.objects[objSafe.name].location.z = point_world.z/SkalierungPTP
        bpy.data.objects[objSafe.name].rotation_euler.x = float(PTPAngleA[0]) * 2*math.pi /360 # in rad angeben
        bpy.data.objects[objSafe.name].rotation_euler.y = float(PTPAngleB[0]) * 2*math.pi /360
        bpy.data.objects[objSafe.name].rotation_euler.z = float(PTPAngleC[0]) * 2*math.pi /360   
        
        
 # Object SafePosition auf lokale Base-Koordinaten umrechnen/ setzen

        # Achtung: Delta Location muss auf Nullgesetzt werden:
        #obj.delta_location = (0,0,0)
        
        #object       = bpy.data.objects[objBase.name]
        #matrix_world = object.matrix_world
        #meshes_data  = object.data
        #point_local  = meshes_data.vertices[0].co
        #point_world  = matrix_world * point_local
         
        

if KUKAObj=="SAFE-Pos":
        
        # Origin der SafePosition auf den Origin von BasePosition setzen:
        
        
        objBase = bpy.data.objects['Sphere_BASEPos']
        objSafe = bpy.data.objects['Sphere_SAFEPos']
        # Origin auf BASEPosition setzen   
        bpy.data.objects[objSafe.name].location = bpy.data.objects[objBase.name].location
        #bpy.ops.object.select_all(action='DESELECT')
        #bpy.data.objects[objBase.name].select= True
        #bpy.ops.view3d.snap_cursor_to_selected() 
        #bpy.ops.object.select_all(action='DESELECT')
        #objSafe.select = True 
        #bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
        #-----------------------------------
        bpy.ops.object.select_all(action='DESELECT')    
        
        #bpy.data.scenes['Scene'].frame_current = original_scene
        print('SAFE-Pos done')
    
          
    bpy.context.area.type = original_type    
    print('SetUpSceneForFileTransfer done')
    
#--------------------------------------------------------------------------------------------------------
    def SetUpSceneForFileTransfer(objCurve, KUKAObj):
    print('SetUpSceneForFileTransfer')
    ObjNameEmpty = 'Empty_Zentralhand_A6'
    ObjNameCuve = objCurve.name
    
    # Empty offset wenn nicht bei frame 1 importiert wird. Scene wechsel hilft nicht....
    #original_scene = bpy.data.scenes['Scene'].frame_current
    #bpy.data.scenes['Scene'].frame_current = 1
    
    
    original_type = bpy.context.area.type
    bpy.context.area.type = "VIEW_3D"
    
    if KUKAObj=="BASE-Pos":
        #-----------------------------------
        # Origin der Curve auf BASEPosition setzen   (ohne die Base zu verschieben)
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects['Sphere_BASEPos'].select= True
        bpy.ops.view3d.snap_cursor_to_selected() 
        bpy.ops.object.select_all(action='DESELECT')
        objCurve.select = True 
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
        #-----------------------------------
        bpy.ops.object.select_all(action='DESELECT')
        #-----------------------------------
        print('BASE-Pos done')
      
    if KUKAObj=="EMPTY-ZH-A6":
        # Empty_Zentralhand_A6 auf Startpunkt der Kurve setzen
        # Achtung: Delta Location muss auf Nullgesetzt werden:
        objCurve.delta_location = (0,0,0)
        
        object       = bpy.data.objects['BezierCircle']
        matrix_world = object.matrix_world
        curve_data   = object.data
        # Wichtig: Beim letzten Punkt in der Kurve [-1] Anfangen, warum auch immer
        # (ansonsten offset zwischen Punkt [0] und [-1]
        point_local  = curve_data.splines[0].bezier_points[-1].co
        point_world  = matrix_world * point_local
        
        bpy.data.objects['Empty_Zentralhand_A6'].location = point_world
        
        
        #-----------------------------------
        bpy.ops.object.select_all(action='DESELECT')
        #-----------------------------------
        print('EMPTY-ZH-A6 done')
        
    '''    
    if KUKAObj=="SAFE-Pos":
        bpy.ops.object.select_all(action='DESELECT') 
        #-----------------------------------  
        # Origin der SafePosition auf den Origin von BasePosition setzen (ohne die SafePos zu verschieben):
        objBase = bpy.data.objects['Sphere_BASEPos']
        objSafe = bpy.data.objects['Sphere_SAFEPos']
        
            
        # 1. World Koordinaten der SafePos ermitteln: 
        # 2. Origin auf BASEPosition setzen        --> vgl. SetSafePos (685++)
        
        
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects['Sphere_SAFEPos'].select= True
        bpy.ops.view3d.snap_cursor_to_selected() 
        bpy.ops.object.select_all(action='DESELECT')
        objBase.select = True 
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
        #-----------------------------------
        bpy.ops.object.select_all(action='DESELECT')
        #-----------------------------------
        
               
        #bpy.data.objects[objSafe.name].location = bpy.data.objects[objBase.name].location
        #-----------------------------------
        bpy.ops.object.select_all(action='DESELECT')    
        #bpy.data.scenes['Scene'].frame_current = original_scene
        print('SAFE-Pos done')
    '''
          
    bpy.context.area.type = original_type    
    print('SetUpSceneForFileTransfer done')
#--------------------------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------
    # snipset - SetSafePos [01] -> Test.py
    # -------------------------------------------------------------------------------
    bpy.ops.object.select_all(action='DESELECT')      
    # 2. setzen des SafePos Origin auf  vertex[0] der safe:
    objSafe.select = True 
    bpy.context.scene.objects.active = objSafe
    bpy.data.objects[objSafe.name].data.vertices[0].select= True
    # Achtung: Blender"Bug": Wechsel in Edit mode nachdem Vertex ausgewählt wurde!
    bpy.ops.object.mode_set(mode='EDIT', toggle=True)
    bpy.ops.view3d.snap_cursor_to_selected() 
    bpy.data.objects[objSafe.name].data.vertices[0].select= False
    bpy.ops.object.mode_set(mode='EDIT', toggle=True)
    objSafe.select = True 
    bpy.context.scene.objects.active = objSafe
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    bpy.ops.object.select_all(action='DESELECT')
    
    
    # -------------------------------------------------------------------------------
    # snipset - SetSafePos [02] -> Test.py
    # -------------------------------------------------------------------------------
    # 4. origin wieder auf base setzen (ohne die SafePos zu verschieben)
    bpy.ops.object.select_all(action='DESELECT')      
    # 2. setzen des SafePos Origin auf  vertex[0] der base:
    objBase.select = True 
    bpy.context.scene.objects.active = objBase
    bpy.data.objects[objBase.name].data.vertices[0].select= True
    # Achtung: Blender"Bug": Wechsel in Edit mode nachdem Vertex ausgewählt wurde!
    bpy.ops.object.mode_set(mode='EDIT', toggle=True)
    bpy.ops.view3d.snap_cursor_to_selected() 
    bpy.data.objects[objBase.name].data.vertices[0].select= False
    bpy.ops.object.mode_set(mode='EDIT', toggle=True)
    objSafe.select = True 
    bpy.context.scene.objects.active = objSafe
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    bpy.ops.object.select_all(action='DESELECT')


    #-----------------------------------  
    # Origin der SafePosition auf den Origin von BasePosition setzen (ohne die SafePos zu verschieben):
    # 1. Origin auf BASEPosition setzen 
    #-----------------------------------
    
    bpy.ops.object.select_all(action='DESELECT')      
    # 2. setzen des SafePos Origin auf  vertex[0] der base:
    objBase.select = True 
    bpy.context.scene.objects.active = objBase
    bpy.data.objects[objBase.name].data.vertices[0].select= True
    # Achtung: Blender"Bug": Wechsel in Edit mode nachdem Vertex ausgewählt wurde!
    bpy.ops.object.mode_set(mode='EDIT', toggle=True)
    bpy.ops.view3d.snap_cursor_to_selected() 
    bpy.data.objects[objBase.name].data.vertices[0].select= False
    bpy.ops.object.mode_set(mode='EDIT', toggle=True)
    objSafe.select = True 
    bpy.context.scene.objects.active = objSafe
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    bpy.ops.object.select_all(action='DESELECT')


---------------------------

    
    
    print('Transformation loc + rot von SafePos auf GlobalKoordinaten...')
    #eul = mathutils.Euler((objBase.rotation_euler.x, objBase.rotation_euler.y, objBase.rotation_euler.z), 'XYZ')
    eul = mathutils.Euler((math.radians(BASEPos_Angle[0]), math.radians(BASEPos_Angle[1]), math.radians(BASEPos_Angle[2])), 'XYZ')
    print('eul: ' +str(eul))
    mat_rot = eul.to_matrix()
    mat_loc = objSafe.matrix_world
    mat = mat_loc.to_3x3() * mat_rot.to_3x3()
    
    

---------------------------

def SetSafePos(filepath, objCurve, SAFEPos_Koord, SAFEPos_Angle, BASEPos_Koord, BASEPos_Angle):
    print('_____________________________________________________________________________')
    print('Funktion: SetSafePos - lokale Koordinaten bezogen auf Base!')
    objBase = bpy.data.objects['Sphere_BASEPos']
    objSafe = bpy.data.objects['Sphere_SAFEPos']
    print('BASEPos_Koord: ' +str(BASEPos_Koord))
    print('BASEPos_Angle: ' +str(BASEPos_Angle))
    print('SAFEPos_Koord: ' +str(SAFEPos_Koord))    # OK
    print('SAFEPos_Angle: ' +str(SAFEPos_Angle))  
    print('')
    backup_SAFEPos_Koord = [] # erzeugen einer realen Kopie - keine Referenz!
    for i in SAFEPos_Koord:
        backup_SAFEPos_Koord.append(i)
    print('backup_SAFEPos_Koord' + str(backup_SAFEPos_Koord))
    point_world = objSafe.location
    bpy.data.objects[objSafe.name].rotation_euler = (0,0,0)
    
    print('point_world der SafePos vor der Transformation: ' + str(point_world))
    original_type = bpy.context.area.type
    bpy.context.area.type = "VIEW_3D" 
   
    
    # ----------------------------------------------------------------------
    # transformation der local settings (aus *.src/ scene, beziehen sich auf Origin Safe =Origin Base) auf global
    # Achtung: Origin muss für die Transformation schon auf der Base-Position sein!
    # 1. setzen des SafePos Origin auf vertex[0] der BasePos
    # 2.1 vgl. local Koordinaten. Wenn gleich zu SAFEPos_Koord, dann kommen sie aus Scene -> keine weitere Aktion
    # 2.2 wenn ungleich SAFEPos_Koord, dann 
    # 2.2.1 SafePos Origin auf Vertex[0] von sich selber
    # 2.2.2 neue Position setzen (transform loc/global)
    # 3. SafePos Origin wieder auf BasePos setzen
    
    
    #print('bpy.context.mode' + str(bpy.context.mode))
    #-----------------------------------  
    # Origin der SafePosition auf den Origin von BasePosition setzen (ohne die SafePos zu verschieben):
    # 1. Safe-Origin auf BasePosition setzen 
    #-----------------------------------
    bpy.ops.object.select_all(action='DESELECT')      
    # 2. setzen des SafePos Origin auf  vertex[0] der BasePosition:
    objBase.select = True 
    bpy.context.scene.objects.active = objBase
    bpy.data.objects[objBase.name].data.vertices[0].select= True
    # Achtung: Blender"Bug": Wechsel in Edit mode nachdem Vertex ausgewählt wurde!
    bpy.ops.object.mode_set(mode='EDIT', toggle=True)
    bpy.ops.view3d.snap_cursor_to_selected() 
    bpy.data.objects[objBase.name].data.vertices[0].select= False
    bpy.ops.object.mode_set(mode='EDIT', toggle=True)
    objSafe.select = True 
    bpy.context.scene.objects.active = objSafe
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    bpy.ops.object.select_all(action='DESELECT')
    #-----------------------------------
    print('Safe-Origin auf BasePosition gesetzt.')
    
        
    
    
    # .location ist global -> locale Vorgabe auf global umrechnen:
    # Achtung: da SAFEPos aus File muss auch die BasePos aus File verwendet werden! (d.h.SetBasePos ist zuerst auszufürhen!)
    # 1. World Koordinaten der SafePos ermitteln:  
    # 1. transformation der local settings (aus *.src) auf global:
    matrix_world = mathutils.Matrix.Translation(BASEPos_Koord)
    point_local  = bpy.data.objects[objSafe.name].data.vertices[0].co #SAFEPos_Koord
    #Vector(SAFEPos_Koord, float(PTPY[0])/SkalierungPTP, float(PTPZ[0])/SkalierungPTP]) #meshes_data.vertices[0].co
    point_world  = matrix_world * point_local
    
    print('')
    print('point_local der SafePos : ' + str(point_local))
    print('point_world der SafePos (nach der Transformation) : ' + str(point_world))
    
    
    print('BASEPos_Koord: ' +str(BASEPos_Koord))
    print('BASEPos_Angle: ' +str(BASEPos_Angle))
    print('SAFEPos_Koord: ' +str(SAFEPos_Koord))
    print('backup_SAFEPos_Koord' + str(backup_SAFEPos_Koord))
    print('SAFEPos_Angle: ' +str(SAFEPos_Angle)) 

    # 3. übertragen mit .location:
    # SAFEPosition initialisieren:
    # Achtung: verschoben auferhalb von IF, weil Origin jetzt nicht auf SafePos sitzt
    #bpy.data.objects[objSafe.name].location = point_world 
    # todo: bei Rotation von SafePos wird nicht richtig rotiert...
    # Annahme: Origin von SafePos darf nicht auf BasePos bleiben (nur während der Verarbeitung um die lokale Position zu bestimmen)
    # - > prüfen....
     
    # ----------------------------------------------------------------------
        
    # todo: wenn basepos/safepos zueinander verschoben werden, funktioniert der import nicht richtig
    
    #----------------------------------------------------------------------
    # übertragen der rotation:
    # todo testen
    #-----------------------------------  
    # Origin der SafePosition auf den Origin von SafePosition setzen (ohne die SafePos zu verschieben):
    # 1. Origin auf SafePosition setzen 
    #-----------------------------------
    # 1. Safe-Origin auf SafePos setzen 
    #-----------------------------------
    bpy.ops.object.select_all(action='DESELECT')      
    # 2. setzen des SafePos Origin auf  vertex[0] der safe:
    objSafe.select = True 
    bpy.context.scene.objects.active = objSafe
    bpy.data.objects[objSafe.name].data.vertices[0].select= True
    # Achtung: Blender"Bug": Wechsel in Edit mode nachdem Vertex ausgewählt wurde!
    bpy.ops.object.mode_set(mode='EDIT', toggle=True)
    bpy.ops.view3d.snap_cursor_to_selected() 
    bpy.data.objects[objSafe.name].data.vertices[0].select= False
    bpy.ops.object.mode_set(mode='EDIT', toggle=True)
    objSafe.select = True 
    bpy.context.scene.objects.active = objSafe
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    bpy.ops.object.select_all(action='DESELECT')
    
    print('Safe-Origin auf SafePosition gesetzt.')
    #-----------------------------------
    # -------------------------------------------------------------------------------
    # snipset - SetSafePos [01] -> Test.py
    # -------------------------------------------------------------------------------
    bpy.data.objects[objSafe.name].location = point_world
    print('Safe-Origin  = SafePos auf point_world  gesetzt.')
    #-----------------------------------
    
    print('SAFEPos_Angle wieder dem Origin zuweisen')
    bpy.data.objects[objSafe.name].rotation_euler.x = SAFEPos_Angle[0] *(2*math.pi)/360 # [rad]
    bpy.data.objects[objSafe.name].rotation_euler.y = SAFEPos_Angle[1] *(2*math.pi)/360 # [rad]
    bpy.data.objects[objSafe.name].rotation_euler.z = SAFEPos_Angle[2] *(2*math.pi)/360 # [rad]
    
    print('BASEPos_Koord: ' +str(BASEPos_Koord))
    print('BASEPos_Angle: ' +str(BASEPos_Angle))
    print('SAFEPos_Koord: ' +str(SAFEPos_Koord))    
    print('backup_SAFEPos_Koord' + str(backup_SAFEPos_Koord))
    print('SAFEPos_Angle: ' +str(SAFEPos_Angle)) 
    
    SAFEPos_Koord = [] # erzeugen einer realen Kopie keine Referenz!
    for i in backup_SAFEPos_Koord:
        SAFEPos_Koord.append(i)
    SAFEPos_Koord = Vector(SAFEPos_Koord)    
    #print('SAFEPos_Koord zurückgeschrieben von backup_SAFEPos_Koord:')    
    print('SAFEPos_Koord: ' +str(SAFEPos_Koord)) 
    bpy.context.area.type = original_type     
    
    print('SAFEPos_local done')
    print('_____________________________________________________________________________')
    return SAFEPos_Koord
    
# ----------------------------------------------------------------------------------------------------------------------

vertArray
#splineType = 'BEZIER'
    #vertArray = vertsToPoints(dataPTP_Loc, splineType) # wofür????
    
    '''
    createCurve(vertArray, self, align_matrix)
    '''
# get array of vertcoordinates acording to splinetype
def vertsToPoints(Verts, splineType):
    print('_____________________________________________________________________________')
    print('vertsToPoints')
    # main vars
    vertArray = []

    # array for BEZIER spline output (V3)
    if splineType == 'BEZIER':
        for v in Verts:
            vertArray += v

    # array for nonBEZIER output (V4)
    else:
        for v in Verts:
            vertArray += v
            if splineType == 'NURBS':
                vertArray.append(1) #for nurbs w=1
            else: #for poly w=0
                vertArray.append(0)
    return vertArray
    print('vertsToPoints done')
    print('_____________________________________________________________________________')


def createCurve(objCurve, dataPTP_Loc, PathCount):
    print('_____________________________________________________________________________')
    print('createCurve')
    #origin = (0,0,0)
    #bezierCurve = bpy.data.curves[bpy.context.active_object.data.name] #bpy.context.active_object #.data.name
    bezierCurve = bpy.data.curves[objCurve.name] #bpy.context.active_object #.data.name
    replace_CP(bezierCurve, dataPTP_Loc, PathCount) 
    #replace_CP(bezierCurve, dataPTP_Loc, PathCount) 
    print('createCurve done')
    print('_____________________________________________________________________________')
'''  
    #scene.objects.link(new_obj) # place in active scene
    #new_obj.select = True # set as selected
    #scene.objects.active = new_obj  # set as active
    
    #new_obj.matrix_world = align_matrix # apply matrix
'''

def replace_CP(cu, dataPTP_Loc, PathCountFile):
    print('_____________________________________________________________________________')
    print('replace_CP')
    #bpy.data.curves[bpy.context.active_object.data.name].user_clear()
    #bpy.data.curves.remove(bpy.data.curves[bpy.context.active_object.data.name])
    
    bpy.ops.object.mode_set(mode='EDIT', toggle=False) # switch to edit mode
    
    cu.dimensions = '3D'
    
    bzs = bpy.data.curves[bpy.context.active_object.data.name].splines[0].bezier_points
    PathCount = len(bzs)
    
    # sicherstellen das kein ControlPoint selektiert ist:
    for n in range(PathCount):
        bpy.data.curves[bpy.context.active_object.data.name].splines[0].bezier_points[n].select_control_point= False
        bpy.data.curves[bpy.context.active_object.data.name].splines[0].bezier_points[n].select_right_handle = False
        bpy.data.curves[bpy.context.active_object.data.name].splines[0].bezier_points[n].select_left_handle = False             
    CountCP = 0
    
    if PathCountFile <= PathCount:
        CountCP = PathCount
    if PathCountFile >= PathCount:
        CountCP = PathCountFile
    
    # kuerze die Laenge der aktuellen Kurve auf die File-Kurve, wenn noetig
    if PathCountFile < PathCount:
        delList =[]
        zuViel = PathCount - PathCountFile
        delList = [PathCountFile]*(PathCountFile+zuViel)
        
        for n in range(PathCountFile, PathCountFile+zuViel, 1):      
            bpy.data.curves[bpy.context.active_object.data.name].splines[0].bezier_points[delList[n]].select_control_point=True
            bpy.data.curves[bpy.context.active_object.data.name].splines[0].bezier_points[delList[n]].select_right_handle = True
            bpy.data.curves[bpy.context.active_object.data.name].splines[0].bezier_points[delList[n]].select_left_handle = True
            bpy.ops.curve.delete(type='SELECTED')
        CountCP = len(bzs)
    
    for n in range(CountCP):
        if (PathCount-1) >= n: # Wenn ein Datenpunkt auf der vorhandenen Kurve da ist,
            # Waehle einen Punkt auf der vorhandenen Kurve aus:
            bpy.data.curves[bpy.context.active_object.data.name].splines[0].bezier_points[n].select_control_point = True
            print(bpy.data.curves[bpy.context.active_object.data.name].splines[0].bezier_points[n])
            print('Select control point:' + str(bpy.data.curves[bpy.context.active_object.data.name].splines[0].bezier_points[n].select_control_point))
            
            bpy.data.curves[bpy.context.active_object.data.name].splines[0].bezier_points[n].handle_left_type='VECTOR'
            print(bpy.data.curves[bpy.context.active_object.data.name].splines[0].bezier_points[n].handle_left_type)
            
            bpy.data.curves[bpy.context.active_object.data.name].splines[0].bezier_points[n].handle_right_type='VECTOR'
            print(bpy.data.curves[bpy.context.active_object.data.name].splines[0].bezier_points[n].handle_right_type)
            
            
            if (PathCountFile-1) >= n: # Wenn ein Datenpunkt im File da ist, nehm ihn und ersetzte damit den aktellen Punkt
                bzs[n].co = Vector(dataPTP_Loc[n])/1000
                bzs[n].handle_left = Vector(dataPTP_Loc[n-1])/1000
                bzs[n].handle_right = Vector(dataPTP_Loc[n-PathCountFile+1])/1000 # n-PathCount+1 weil er nur vom ersten Element auf das letzte springt
                bpy.data.curves[bpy.context.active_object.data.name].splines[0].bezier_points[n].select_control_point = False      
        else: # wenn kein Kurvenpunkt zum ueberschreiben da ist, generiere einen neuen und schreibe den File-Datenpunkt
            bzs.add(1) #spline.bezier_points.add(1)
            
            bzs[n].co = Vector(dataPTP_Loc[n])/1000
            bzs[n].handle_left = Vector(dataPTP_Loc[n-1])/1000 #bzs[n-1].co
            bzs[n].handle_right = Vector(dataPTP_Loc[n-PathCountFile+1])/1000 #bzs[n+1].co
            bzs[n].handle_right_type='VECTOR'
            bzs[n].handle_left_type='VECTOR'
            print(bzs[n])
            print(bzs[n].select_control_point)
            print(bzs[n].handle_left_type)
            print('handle_right' + str(bzs[n].handle_right_type))
            print(bzs[n])
            
    
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False) # switch back to object mode
    print('replace_CP done')
    print('_____________________________________________________________________________')
    
    
______________________________

     bpy.ops.curve.spin(center=(0.0, 0.0, 0.0), axis=(0.0, 0.0, 0.0))

    Undocumented (contribute)
    Parameters:    

        center (float array of 3 items in [-inf, inf], (optional)) – Center, Center in global view space
        axis (float array of 3 items in [-1, 1], (optional)) – Axis, Axis in global view space


bpy.ops.curve.tilt_clear()

    Undocumented (contribute)

 bpy.ops.curve.vertex_add(location=(0.0, 0.0, 0.0))

    Undocumented (contribute)
    Parameters:    location (float array of 3 items in [-inf, inf], (optional)) – Location, Location to add new vertex at.
______________________________
#----------------------------------------------------------
# File popup.py
# from API documentation
#----------------------------------------------------------
 
#import bpy
from bpy.props import *
 
theFloat = 9.8765
theBool = False
theString = "Lorem ..."
theEnum = 'one'
 
class DialogOperator(bpy.types.Operator):
    print('DialogOperator')
    bl_idname = "object.dialog_operator"
    bl_label = "Simple Dialog Operator"
 
    my_float = FloatProperty(name="Some Floating Point", 
        min=0.0, max=100.0)
    my_bool = BoolProperty(name="Toggle Option")
    my_string = StringProperty(name="String Value")
    my_enum = EnumProperty(name="Enum value",
        items = [('one', 'eins', 'un'), 
                 ('two', 'zwei', 'deux'),
                 ('three', 'drei', 'trois')])
 
    def execute(self, context):
        message = "%.3f, %d, '%s' %s" % (self.my_float, 
            self.my_bool, self.my_string, self.my_enum)
        self.report({'INFO'}, message)
        print(message)
        return {'FINISHED'}
 
    def invoke(self, context, event):
        global theFloat, theBool, theString, theEnum
        self.my_float = theFloat
        self.my_bool = theBool
        self.my_string = theString
        self.my_enum = theEnum
        return context.window_manager.invoke_props_dialog(self)
 
    print('DialogOperator done')
     
bpy.utils.register_class(DialogOperator)
 
# Invoke the dialog when loading
bpy.ops.object.dialog_operator('INVOKE_DEFAULT')
 
#
#    Panel in tools region
#
class DialogPanel(bpy.types.Panel):
    print('DialogPanel')
    bl_label = "Dialog"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
 
    def draw(self, context):
        global theFloat, theBool, theString, theEnum
        theFloat = 12.345
        theBool = True
        theString = "Code snippets"
        theEnum = 'two'
        self.layout.operator("object.dialog_operator")
    print('DialogPanel done')
 
# Axis: ( used in 3DCurve Turbulence )
def AxisFlip(x,y,z, x_axis=1, y_axis=1, z_axis=1, flip=0 ):
    print('_____________________________________________________________________________')
    print('AxisFlip')
    if flip != 0:
        flip *= -1
    else: flip = 1
    x *= x_axis*flip
    y *= y_axis*flip
    z *= z_axis*flip
    return x,y,z
    print('AxisFlip done')
    print('_____________________________________________________________________________')

# calculates the matrix for the new object
# depending on user pref
def align_matrix(context):
    print('_____________________________________________________________________________')
    print('align_matrix')
    loc = Matrix.Translation(context.scene.cursor_location)
    obj_align = context.user_preferences.edit.object_align
    if (context.space_data.type == 'VIEW_3D'
        and obj_align == 'VIEW'):
        rot = context.space_data.region_3d.view_matrix.to_3x3().inverted().to_4x4()
    else:
        rot = Matrix()
    align_matrix = loc * rot
    return align_matrix
    print('align_matrix done')
    print('_____________________________________________________________________________')
    
    # sets bezierhandles to auto
def setBezierHandles(obj, mode = 'AUTOMATIC'):
    print('_____________________________________________________________________________')
    print('setBezierHandles')
    scene = bpy.context.scene
    if obj.type != 'CURVE':
        return
    scene.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT', toggle=True)
    bpy.ops.curve.select_all(action='SELECT')
    bpy.ops.curve.handle_type_set(type=mode)
    bpy.ops.object.mode_set(mode='OBJECT', toggle=True)
    print('setBezierHandles done')
    print('_____________________________________________________________________________')
    
def Curve2File(obj, filepath):
    print('_____________________________________________________________________________')
    print('Curve2File')  
     
    # Create a file for output
    
    print('Exporting ' + filepath)
    fout = open(filepath, 'w')

    # PATHPTS[1]={X 105.1887, Y 125.6457, Z -123.9032, A 68.49588, B -26.74377, C 1.254162 }
    # TRANSFORM_OT_translate
    # bpy.ops.transform.translate(value=(1,1,1))
    # Transform Modal Map:  Property Value  Translate:  KeyMapItem.propvalue 
    #  bpy.data.window_managers["WinMan"] ... propvalue
    # space_userpref_keymap.py
    # bpy.app.handlers.frame_change_pre.append(bpy.ops.curve.cureexport('BezierCurve'))
    # Window.GetScreenInfo(Window.Types.VIEW3D)
    # Die Info der Handles in PathPointA, B, C schreiben
    # Jedesmal wenn handle_left geaendert wird soll ein skript aufgerufen werden das die 
    # Roboterhand entsprechend mit dreht -> angel ????
    # bpy.data.curves[bpy.context.active_object.data.name].splines[0].bezier_points[0].co.angle(bpy.data.curves[bpy.context.active_object.data.name].splines[0].bezier_points[1].co)
    
    PathPointX = []
    PathPointY = []
    PathPointZ = []
    PathPointA = []
    PathPointB = []
    PathPointC = []
    PathAngleA = []
    PathAngleB = []
    PathAngleC = []
    PathAngleAx = []
    PathAngleBy = []
    PathAngleCz = []
    PathPointABC = []
    PathPointAB = []
    PathPointAC = []
    PathPointBC = []
    PathAngleABC=[]
    PathAngleAxByCz = []
    ValRot = []
    ValOrth = []
    #koord = bpy.data.curves[obj.name].splines[0]
    koord = bpy.data.curves[bpy.data.objects[obj.name].data.name].splines[0] # wichtig: name des Datenblocks verwenden
    
    # todo: vector.angle(other vector, fallback) aus import mathutils

    n = len(koord.bezier_points.values())
    for i in range(0,n,1): # Liste erzeugen
        PathPointX = PathPointX +[koord.bezier_points[i].co.x]
        PathPointY = PathPointY +[koord.bezier_points[i].co.y]
        PathPointZ = PathPointZ +[koord.bezier_points[i].co.z]
        # handle left fuer 2tes Koordinatensystem?!
        # was ist, wenn spline[1, 2, ...]?
        # BUG: wenn Hadle.left Wert = 0 -> DIV 0 -> error
        koord.bezier_points[i].handle_left_type='FREE'
        
        
        # todo in Grad speichern!!! testen...
        
        
        PathPointA = PathPointA +[koord.bezier_points[i].handle_left.x*360/(2* math.pi)] # Grad
        PathPointB = PathPointB +[koord.bezier_points[i].handle_left.y*360/(2* math.pi)]
        PathPointC = PathPointC +[koord.bezier_points[i].handle_left.z*360/(2* math.pi)]
        PathPointABC = PathPointABC + [math.sqrt(math.pow(PathPointA[i], 2) 
                            + math.pow(PathPointB[i], 2) 
                            + math.pow(PathPointC[i], 2))]
        PathPointAB = PathPointAB + [math.sqrt(math.pow(PathPointA[i], 2) 
                            + math.pow(PathPointB[i], 2))]
        PathPointAC = PathPointAC + [math.sqrt(math.pow(PathPointA[i], 2) 
                            + math.pow(PathPointC[i], 2))]
        PathPointBC = PathPointBC + [math.sqrt(math.pow(PathPointB[i], 2) 
                            + math.pow(PathPointC[i], 2))]
       
        # Achtung: Bei der folgenden Berechnung wird der "Fehler" gemacht das der Betrag des Vektors
        # aus allen drei Achsen berechnet wird. Das hat zur folge das der berechnete Winkel auf kuerzestem
        # Weg zwischen der Koordinatenachse und dem Vektor aufgespannt wird.
        
        '''
        PathAngleA = PathAngleA + [math.degrees(math.acos(PathPointA[i]/PathPointABC[i]))]
        PathAngleB = PathAngleB + [math.degrees(math.acos(PathPointB[i]/PathPointABC[i]))]
        PathAngleC = PathAngleC + [math.degrees(math.acos(PathPointC[i]/PathPointABC[i]))]
        PathAngleABC = PathAngleABC + [PathAngleA[i] + PathAngleB[i] + PathAngleC[i]]
        '''
        
        
        # Um den Winkel zu berechnen der ORTHOGONAL zur Koordinatenachse aufgespannt wird 
        # ist der Betrag des auf den Koordinatenursprungs projezierten Vektors zu berechnen.
        
        
        '''
        PathAngleAx = PathAngleAx + [math.degrees(math.acos(PathPointA[i]/PathPointAB[i]))]
        PathAngleBy = PathAngleBy + [math.degrees(math.acos(PathPointB[i]/PathPointBC[i]))]
        PathAngleCz = PathAngleCz + [math.degrees(math.acos(PathPointC[i]/PathPointAC[i]))]       
        PathAngleAxByCz = PathAngleAxByCz + [PathAngleAx[i] + PathAngleBy[i] + PathAngleCz[i]]         
       '''
   
        # Validation: cos²PathAngleAx + cos²PathAngleBy + cos²PathAngleCz = 1
        # Cos/Sin are expecting radians not degrees
       
        '''
        ValRot = ValRot + [(math.pow(math.cos(PathAngleA[i] *math.pi/180.0),2) + math.pow(math.cos(PathAngleB[i]*math.pi/180.0),2) + math.pow(math.cos(PathAngleC[i]*math.pi/180.0),2))]
        ValOrth = ValOrth + [(math.pow(math.cos(PathAngleAx[i]*math.pi/180.0),2) + math.pow(math.cos(PathAngleBy[i]*math.pi/180.0),2) + math.pow(math.cos(PathAngleCz[i]*math.pi/180.0),2))]
        '''
        
    # Die Angaben die im Kuka Programm angegebenen Winkel sind keine der beiden oben berechneten. 
    # --> Quaternion, Gimbal lock,wrist flip, spatial rotations (ToDo....)
    # siehe Kuka: MES = {X -237, Y 0, Z 342, A 0, B 0, C 0 }
    # siehe Kuka: OFFSET_FILE[] = "offset0022.dat"  
    
    
    # bpy.ops.transform.translate(value=(X2,Y2,Z2),const raint_orientation='GLOBAL') 
    fout.write(";FOLD PATH DATA" + "\n")
    count= len(PathPointX) 
    # Skalierung: 1:100 (vgl. Import)
    Skalierung = 1000
    
    for i in range(0,count,1): # String erzeugen/ schreiben
        '''        
        StrPathPoint = ("PATHPTS[" + str(i) + "]={" +
                        "X " + str(PathPointX[i]) + ", Y " + str(PathPointY[i]) +  
                        ", Z " +str(PathPointZ[i]) +", A " + str(PathPointA[i]) + 
                        ", B " + str(PathPointB[i]) +", C " + str(PathPointC[i]) +
                        "} ")
        fout.write(StrPathPoint + "\n")
        '''        
        fout.write("PATHPTS[" + str(i+1) + "]={" + 
                   "X " + "{0:.5f}".format(PathPointX[i]*Skalierung) + ", Y " + "{0:.5f}".format(PathPointY[i]*Skalierung) +
                   ", Z " + "{0:.5f}".format(PathPointZ[i]*Skalierung) + ", A " + "{0:.5f}".format(PathPointA[i] ) +
                   ", B " + "{0:.5f}".format(PathPointB[i]) + ", C " + "{0:.5f}".format(PathPointC[i] ) +
                   "} " + "\n")
        '''
        fout.write("PATHPAngles[" + str(i) + "]={" + 
                   "Angle(A) " + "{0:.5f}".format(PathAngleA[i]) + ", Angle(B) " + "{0:.5f}".format(PathAngleB[i]) +
                   ", Angle(C) " + "{0:.5f}".format(PathAngleC[i]) + ", PathAngleABC " + "{0:.3f}".format(PathAngleABC[i]) + 
                   "PathPointABC " + "{0:.3f}".format(PathPointABC[i]) + "\n" +
                   "ValRot: " + "{0:.3f}".format(ValRot[i]) + "\n")        
        fout.write("PATHPAngles[" + str(i) + "]={" + 
                   "Angle(Ax) " + "{0:.5f}".format(PathAngleAx[i]) + ", Angle(By) " + "{0:.5f}".format(PathAngleBy[i]) +
                   ", Angle(Cz) " + "{0:.5f}".format(PathAngleCz[i]) +  
                   "ValOrth: " + "{0:.3f}".format(ValOrth[i]) + "\n")        
'''
        # Write out the data
        #dump(fout, ob.data)
    fout.write(";ENDFOLD" + "\n")
    # Close the file
    fout.close();
    
    print('Curve2File done')
    print('_____________________________________________________________________________')


PATHPTS_Koord = point_world
    print('PATHPTS-Origin  = PATHPTS auf point_world  gesetzt.')

    print('PATHPTS_Angle wieder dem Origin zuweisen unter Beruecksichtigung der BaseOrientierung:')
    PATHPTS_Angle=[]
    for i in range(0,3):
        PATHPTS_Angle = PATHPTS_Angle + [-(BASEPos_Angle[i] +dataPATHPTS_Rot[i])*(2*math.pi)/360 ] # [rad]
        
def SetAnimation():
    positions = (0,0,2),(0,1,2),(3,2,1),(3,4,1),(1,2,1)
    start_pos = (0,0,0)
     
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, size=0.3, location=start_pos)
    bpy.ops.object.shade_smooth()
    ob = bpy.context.active_object
     
    frame_num = 0
     
    for position in positions:
        bpy.context.scene.frame_set(frame_num)
        ob.location = position
        ob.keyframe_insert(data_path="location", index=-1)
        frame_num += 10

    # snipset
     
    scene = bpy.context.scene
     
    fps = scene.render.fps
    fps_base = scene.render.fps_base
     
    def frame_to_time(frame_number):
        raw_time = (frame_number - 1) / fps
        return round(raw_time, 3)
     
    # key frames, try this with location
    # keyframes on a cube
    print('---')
    for key in bpy.data.actions[0].fcurves:
        for marker in key.keyframe_points:
            frame = marker.co.x
            frame_time = frame_to_time(frame)
            print(frame, frame_time)
        break
     
    # time line markers
    for k, v in scene.timeline_markers.items():
        frame = v.frame
        frame_time = frame_to_time(frame)
        print(frame, frame_time) 
        
import bpy


TIMEPTS=[]
raw_time=[]

objEmpty_A6 = bpy.data.objects['Empty_Zentralhand_A6'] 
scene = bpy.context.scene
fps = scene.render.fps
fps_base = scene.render.fps_base

#countPATHPTSObj, PATHPTSObjList = count_PATHPTSObj(PATHPTSObjName)
countPATHPTSObj = 4
PATHPTSObjList =('PTPObj_001','PTPObj_002','PTPObj_003','PTPObj_004')


n=1 # Schleife fehlt noch....

bpy.context.scene.objects.active = objEmpty_A6

#bpy.data.objects[PATHPTSObjList[n]]

ob = bpy.context.active_object

def frame_to_time(frame_number):
    raw_time = (frame_number - 1) / fps
    return round(raw_time, 3)

TIMEPTS=TIMEPTS + [24]

def time_to_frame(time_value):
    frame_number = (raw_time * fps) +1
    return round(frame_number, 3)

for position in PATHPTSObjList:
    
    bpy.context.scene.frame_set(time_to_frame(TIMEPTS[n-1]))
    ob.location = bpy.data.objects[PATHPTSObjList[n-1]].location
    ob.keyframe_insert(data_path="location", index=-1)
    
    
    
class kuka_data (bpy.types.Operator):
#class kuka_data (bpy.types.BlendData):    
    print('kuka_data- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ') 
    print('- - - - - - - - - - - - -  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')
    ''' Import selected curve '''
    # dir(bpy.ops.scene.kuka_data)
    
    bl_idname = "scene.kuka_data"
    bl_label = "kuka_data (TB)" #Toolbar - Label
    bl_description = "contains all required info for animation" # Kommentar im Specials Kontextmenue
    bl_options = {'REGISTER', 'UNDO'} #Set this options, if you want to update  
    #                                  parameters of this operator interactively 
    #                                  (in the Tools pane) 
    
    'Optional class documentation string'
    # todo: Klasse definieren: PATHPTS.loc/rot/TIMEPTS/LOADPTS/STOPPTS/ACTIONMSK
    
    PATHPTSCount = 0 
    TIMEPTSCount = 1
    LOADPTSCount = 2
    STOPPTSCount = 3
    ACTIONMSKCount = 4
    '''
    def __init__(self, name, salary): 
      self.name = name
      self.salary = salary
    '''  
    # todo: Objektstruktur überdenken...... (Objekt/ Klasse: an Empty aufhängen?!  Methoden: RfF_LocRot, .... Eigenschaften: PATHPTS,...
    
    def SetAnimationNew(self, context, TIMEPTS, TIMEPTSCount): 
        self.AnimationSetup = SetAnimation(TIMEPTS, TIMEPTSCount)
        print ("Total setAnimation %d" % kuka_data.setAnimation) 
 
    
    def PATHPTS(self, wert): 
        PATHPTSCount += wert
        print ("Total PATHPTS %d" % kuka_data.PATHPTSCount) 
 
    def TIMEPTS(self): 
        print ("Total TIMEPTS %d" % kuka_data.TIMEPTSCount)  
        
    def LOADPTS(self): 
        print ("Total LOADPTS %d" % kuka_data.LOADPTSCount)  
        
    def STOPPTS(self): 
        print ("Total STOPPTS %d" % kuka_data.STOPPTSCount)  
    
    def ACTIONMSK(self): 
        print ("Total ACTIONMSK %d" % kuka_data.ACTIONMSKCount)  
        
    print('kuka_data- done - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ') 
    print('- - - - - - - - - - - - -  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')    



import bpy


class MyProperties(bpy.types.PropertyGroup):
    selected_object_index = bpy.props.IntProperty(
            default=-1,
            min=-1,
            options={'HIDDEN', 'SKIP_SAVE', },
            )


class MYSCENE_UL_objects(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, translate=False, icon_value=icon)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


class UIListPanelExample(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "UIList Panel"
    bl_idname = "OBJECT_PT_ui_list_example"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout

        myScene = context.scene
        myProps = context.scene.myProps

        layout.template_list(
                listtype_name="MYSCENE_UL_objects",
                dataptr=myScene,
                propname="objects",
                active_dataptr=myProps,
                active_propname="selected_object_index",
                rows=2,
                type='DEFAULT',
                )


def register():
    bpy.utils.register_class(MYSCENE_UL_objects)
    bpy.utils.register_class(UIListPanelExample)
    bpy.utils.register_class(MyProperties)
    bpy.types.Scene.myProps = bpy.props.PointerProperty(type=MyProperties)


def unregister():
    bpy.utils.unregister_class(MYSCENE_UL_objects)
    bpy.utils.unregister_class(UIListPanelExample)
    bpy.utils.unregister_class(MyProperties)
    del bpy.types.Scene.myProps


if __name__ == "__main__":
    register()
    
def RfS_LocRotX(objPATHPTS, dataPATHPTS_Loc, dataPATHPTS_Rot, BASEPos_Koord, BASEPos_Angle):
    # Aufruf von: create_PATHPTSObj, SetSafePos
    # Diese Funktion wird nur bei Export aufgerufen.
    # Wiedergabe von LOC/Rot bezogen auf Base
    print('_____________________________________________________________________________')
    print('Funktion: RfS_LocRot - lokale Koordinaten bezogen auf Base!')
    
    objBase = bpy.data.objects['Sphere_BASEPos']
    PATHPTS_Angle = []
    # PATHPTS_Angle Angle auch in Abhaengigkeit von BasePos Orientierung exportieren/ speichern!
    # TODO: FALSCHE Zerlegung der Winkel in Abh. von Base!!!!!
    PATHPTS_Angle = PATHPTS_Angle +[(dataPATHPTS_Rot[0] -objBase.rotation_euler.x) *360/(2*math.pi)]# C(X)
    PATHPTS_Angle = PATHPTS_Angle +[(dataPATHPTS_Rot[1] -objBase.rotation_euler.y) *360/(2*math.pi)]# B(Y)
    PATHPTS_Angle = PATHPTS_Angle +[(dataPATHPTS_Rot[2] -objBase.rotation_euler.z) *360/(2*math.pi)]# A(Z)
    print('PATHPTS_Angle - ini: '+'C X {0:.3f}'.format(PATHPTS_Angle[0])+' B Y {0:.3f}'.format(PATHPTS_Angle[1])+' A Z {0:.3f}'.format(PATHPTS_Angle[2]))
    
    objPATHPTS.rotation_euler = (0,0,0) # um die richtigen Koordinaten zu bekommen 
    print('PATHPTS: bevor Origin auf BasePos' +str(objPATHPTS.data.vertices[0].co))
    
    # setzen des PATHPTS Origin auf  vertex[0] der BasePosition: 
    SetOrigin(objPATHPTS, objBase)
    
    print('PATHPTS_Angle: '+'C X {0:.3f}'.format(PATHPTS_Angle[0])+' B Y {0:.3f}'.format(PATHPTS_Angle[1])+' A Z {0:.3f}'.format(PATHPTS_Angle[2]))
    
    print('Umrechnung auf globale Koordinaten....')
    print('Transformation von SafePos auf BasePos...')
    vec = objPATHPTS.data.vertices[0].co # Achtung: Bei Aktuellem Objekt fuer PATHPTS liegt vertices[0] nicht im Ursprung des Objektes
    print('vec: ' +str(vec))
    eul = mathutils.Euler((objBase.rotation_euler.x, objBase.rotation_euler.y, objBase.rotation_euler.z), RotationModeTransform) # XYZ
    print('eul: ' +str(eul))
    vec3d = vec.to_3d()
    mat_rot = eul.to_matrix()
    mat_loc = vec3d
    mat = mat_loc * mat_rot.to_3x3()
    print('mat: ' + str(mat))
    
    #Achtung: lokale Koordinaten (bezogen auf Base) wie in Datei gespeichert
    PATHPTS_Koord = mat
    print('PATHPTS_Koord = point_local: ' + str(PATHPTS_Koord))
    print('PATHPTS_Angle: '+'C X {0:.3f}'.format(PATHPTS_Angle[0])+' B Y {0:.3f}'.format(PATHPTS_Angle[1])+' A Z {0:.3f}'.format(PATHPTS_Angle[2]))
    
    print('PATHPTS-Origin auf PATHPTS setzen ....')
    # setzen des PATHPTS Origin auf  vertex[0] des PATHPTSObj:
    SetOrigin(objPATHPTS, objPATHPTS)
    
    print('PATHPTS_Angle: '+'C X {0:.3f}'.format(PATHPTS_Angle[0])+' B Y {0:.3f}'.format(PATHPTS_Angle[1])+' A Z {0:.3f}'.format(PATHPTS_Angle[2]))
    
    print('PATHPTS_Angle wieder dem Origin zuweisen')
    objPATHPTS.rotation_euler.x = PATHPTS_Angle[0] *(2*math.pi)/360 +objBase.rotation_euler.x # C(X)[rad]
    objPATHPTS.rotation_euler.y = PATHPTS_Angle[1] *(2*math.pi)/360 +objBase.rotation_euler.y # B(Y)[rad]
    objPATHPTS.rotation_euler.z = PATHPTS_Angle[2] *(2*math.pi)/360 +objBase.rotation_euler.z # A(Z)[rad]
    
    print('PATHPTS_Koord: ' + str(PATHPTS_Koord))
    print('PATHPTS_Angle: '+'A {0:.3f}'.format(PATHPTS_Angle[0])+' B {0:.3f}'.format(PATHPTS_Angle[1])+' C {0:.3f}'.format(PATHPTS_Angle[2]))
    
    
    # todo: hier muss dann adjustment wieder abgezogen werden....
    
    print('RfS_LocRot done')
    print('_____________________________________________________________________________')
    return PATHPTS_Koord, PATHPTS_Angle 
    
    
MatrixDef= createMatrix(3,3)
MatrixDef = [(0.8192, -0.5736, 0.0),(0.5735, -0.8190, -0.0),(0,0,-1)]
a= Matrix(MatrixDef) * Mrot # 
b = Mrot * Matrix(MatrixDef)    


 0.8192 -0.5736  0.0
-0.5735 -0.8190  0.0
  0.0000  0.0000 -1.00

    



def createMatrix(rows, columns, default = 0):
    m = []
    for i in range(rows):
        m.append([default for j in range(columns)])
    return m


MDef= createMatrix(3,3)
MDef = [(0.8192, -0.5736, 0.0),(0.5735, -0.8190, -0.0),(0,0,-1)]
MatrixDef = Matrix(MDef) 

rotEulerMDef =MatrixDef.to_euler('XYZ')
print('rotEulerMDef :'+ repr(rotEulerMDef))
print()
print('rotEulerMDef[0] :'+ repr(rotEulerMDef[0]*360/(2*3.14)))
print('rotEulerMDef] :'+ repr(rotEulerMDef[1]*360/(2*3.14)))
print('rotEulerMDef[2] :'+ repr(rotEulerMDef[2]*360/(2*3.14)))

    
    
    
    
    
    
    
    
    
    
    
