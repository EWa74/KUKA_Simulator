

def helloworld():
    print('hello world...')

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
    # - Deselct alle Objekte und in Objekte in richtiger Reihenfolge auswählen
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
# todo: testen, Achtung unterscheide zwischen + und - Faellen -> wird nicht benoetigt    
# Teil 2:
    # Mehrheitsentscheid für die Drehrichtung (z.B. +170 oder - 190)
    # wenn y und z negativ, dann x auch negativ
    # wenn x und z negativ, dann y auch negativ
    # wenn x und y negativ, dann z auch negativ
    '''
    for i in range(countObj-1):
        Rot = bpy.data.objects[ObjList[i]].rotation_euler
        if Rot.y >0 and Rot.z >0 and Rot.x<0:
            Rot.x = 2*math.pi + Rot.x
        if Rot.y <0 and Rot.z <0 and Rot.x>0:
            Rot.x = -2*math.pi + Rot.x
        
        if Rot.x >0 and Rot.z >0 and Rot.y<0:
            Rot.y = 2*math.pi + Rot.y
        if Rot.x <0 and Rot.z <0 and Rot.y>0:
            Rot.y = -2*math.pi + Rot.y
        
        if Rot.x >0 and Rot.y >0 and Rot.z<0:
            Rot.z = 2*math.pi + Rot.z
        if Rot.x <0 and Rot.y <0 and Rot.z>0:
            Rot.z = -2*math.pi + Rot.z
    '''
    # Teil 1: Status: wird auch bei quaternion benoetigt!
    # wenn zum erreichen des folgenden Winkels mehr als 180° (PI) zurückzulegen ist, 
    # dann zaehle 360° drauf (wenn er negativ ist) bzw. ziehe 360° (wenn er positiv ist)
    



    bpy.data.objects['Empty_Zentralhand_A6'].animation_data.action.fcurves[4].keyframe_points[1].co
    action_data =action.fcurves
    action.fcurves[rotID[0]].keyframe_points[1].co # Ergebnis: Vector(Frame[1] Wert, quaternion w Wert)
    action.fcurves[rotID[1]].keyframe_points[1].co # Ergebnis: Vector(Frame[1] Wert, quaternion x Wert)
    action.fcurves[rotID[2]].keyframe_points[1].co # Ergebnis: Vector(Frame[1] Wert, quaternion y Wert)
    action.fcurves[rotID[3]].keyframe_points[1].co
    


print(ob.rotation_quaternion)
        print(ob.rotation_euler)
        
        # von Quaternion wieder zurueck nach Euler um Drehungen ueber 360° zu eliminieren:
        ob.rotation_mode = 'XYZ'
        print(ob.rotation_quaternion)
        print(ob.rotation_euler)
        ob.rotation_mode = 'QUATERNION'
        print(ob.rotation_quaternion)
        print(ob.rotation_euler)
        #ob.rotation_euler = bpy.data.objects[TargetObjList[n]].rotation_quaternion.to_euler()
        #ob.rotation_quaternion = bpy.data.objects[TargetObjList[n]].rotation_euler.to_quaternion()
        
def OptimizeRotationQuaternion(ObjList, countObj):
    
    QuaternionList= [bpy.data.objects[ObjList[0]].rotation_euler.to_quaternion()]
    # Teil 1:
    # wenn zum erreichen des folgenden Winkels alle drei Achsen ueber Null gehen müssen, 
    # dann invertiere den folgenden Quaternion
    
    for n in range(countObj-1):
        Rot1 = bpy.data.objects[ObjList[n]].rotation_quaternion.to_euler()
        Rot2 = bpy.data.objects[ObjList[n+1]].rotation_quaternion.to_euler()
        
        DeltaQRota = [(QRot1.w <0 and QRot2.w>0),(QRot1.x <0 and QRot2.x>0),(QRot1.y <0 and QRot2.y>0),(QRot1.z <0 and QRot2.z>0)]
        DeltaQRotb = [(QRot1.w >0 and QRot2.w<0),(QRot1.x >0 and QRot2.x<0),(QRot1.y >0 and QRot2.y<0),(QRot1.z >0 and QRot2.z>0)]
                
        if (DeltaQRota or DeltaQRotb == [1,1,1,1]) == [1,1,1,1]:
            QRot2.w =  - QRot2.w
            QRot2.x =  - QRot2.x
            QRot2.y =  - QRot2.y
            QRot2.z =  - QRot2.z
        
        
        QuaternionList = QuaternionList + [bpy.data.objects[ObjList[n+1]].rotation_euler.to_quaternion()]
        
    return QuaternionList    



        #ob.rotation_euler = bpy.data.objects[TargetObjList[n]].rotation_euler
        
        RotEuler1 = bpy.data.objects[TargetObjList[n]].rotation_euler
        RotQuaternion1 = bpy.data.objects[TargetObjList[n]].rotation_euler.to_quaternion()
        bpy.data.objects[TargetObjList[n]].rotation_mode = 'QUATERNION'
        bpy.data.objects[TargetObjList[n]].rotation_mode = 'XYZ'
        RotEuler2 = bpy.data.objects[TargetObjList[n]].rotation_euler
        RotQuaternion2 = bpy.data.objects[TargetObjList[n]].rotation_euler.to_quaternion()
        ob.rotation_quaternion = bpy.data.objects[TargetObjList[n]].rotation_euler.to_quaternion()
        
        if RotEuler1 != RotEuler2:
            
            ob.rotation_quaternion = - ob.rotation_quaternion
            #ob.rotation_quaternion.w = - ob.rotation_quaternion.w
            #ob.rotation_quaternion.x = - ob.rotation_quaternion.x
            #ob.rotation_quaternion.y = - ob.rotation_quaternion.y
            #ob.rotation_quaternion.z = - ob.rotation_quaternion.z
            
def WtF_KeyPosX(Keyword, KeyPos_Koord, KeyPos_Angle, filepath, FileExt, FileMode):
    # Input: Keyword ( BASEPos, HOMEPos, SAFEPos, ADJUSTMENTPos, ..) Koordinaten und Winkel; Zielverzeichnis
    # Process: 
    # - schreiben der Koordinaten in eine Datei mit Endung *.cfg
    # - Der Dateiname wird von *.dat uebernommen
    # - Die Winkel werden wie folgt zugeordnet: C(X), B(Y), A(Z)
    # Output: BASEPos {X 1023.24963, Y 1794.66641, Z 483.22785, A -35.00001, B -20.00001, C -179.00008} 
        
    print('_____________________________________________________________________________')
    print('WtF_KeyPos :' + Keyword)
    print('Remark: this file is not a part of the normal KUKA Ocutbot Software.')
    print(Keyword + '_Angle A - Z [2]: ' +str(KeyPos_Angle[2]))
    print(Keyword + '_Angle B - Y [1]: ' +str(KeyPos_Angle[1]))    #
    print(Keyword + '_Angle C - X [0]: ' +str(KeyPos_Angle[0])) 
    FilenameSRC = filepath
    FilenameSRC = FilenameSRC.replace(".dat", FileExt) 
    fout = open(FilenameSRC, FileMode) # FileMode: 'a' fuer Append oder 'w' zum ueberschreiben
     
    SkalierungPTP = 1000
    # Winkel von XYZ -> CBA
    fout.write( Keyword + " {" + 
                   "X " + "{0:.5f}".format(KeyPos_Koord[0]*SkalierungPTP) + 
                   ", Y " + "{0:.5f}".format(KeyPos_Koord[1]*SkalierungPTP) +
                   ", Z " + "{0:.5f}".format(KeyPos_Koord[2]*SkalierungPTP) + 
                   ", A " + "{0:.5f}".format(KeyPos_Angle[2]) +
                   ", B " + "{0:.5f}".format(KeyPos_Angle[1]) + 
                   ", C " + "{0:.5f}".format(KeyPos_Angle[0]) +
                   "} " + "\n")
    
    fout.close();
    print('WtF_KeyPos :' + Keyword + ' geschrieben.')
    print('_____________________________________________________________________________')              
            
def WtF_KUKAdat(obj, objEmpty_A6, PATHPTSObjName, filepath, BASEPos_Koord, BASEPos_Angle):
    
    print('_____________________________________________________________________________')
    print('WtF_KUKAdat')  
    # Create a file for output
    print('Exporting ' + filepath)
    fout = open(filepath, 'w')

    # PATHPTS[1]={X 105.1887, Y 125.6457, Z -123.9032, A 68.49588, B -26.74377, C 1.254162 }
    # bpy.data.curves[bpy.context.active_object.data.name].splines[0].bezier_points[0].co.angle(bpy.data.curves[bpy.context.active_object.data.name].splines[0].bezier_points[1].co)
    
    PathPointX = []
    PathPointY = []
    PathPointZ = []
    PathPointA = []
    PathPointB = []
    PathPointC = []
    
    #koord = bpy.data.curves[obj.name].splines[0]
    #koord = bpy.data.curves[bpy.data.objects[obj.name].data.name].splines[0] # wichtig: name des Datenblocks verwenden
    
    PATHPTSObjList, countPATHPTSObj = count_PATHPTSObj(PATHPTSObjName)
    for i in range(countPATHPTSObj):    
        dataPATHPTS_LocGL, dataPATHPTS_RotGL = RfS_LocRot(bpy.data.objects[PATHPTSObjList[i]], bpy.data.objects[PATHPTSObjList[i]].location, bpy.data.objects[PATHPTSObjList[i]].rotation_euler, BASEPos_Koord, BASEPos_Angle)
        
        PathPointX = PathPointX +[dataPATHPTS_LocGL[0]]
        PathPointY = PathPointY +[dataPATHPTS_LocGL[1]]
        PathPointZ = PathPointZ +[dataPATHPTS_LocGL[2]]
        # ABC ->CBA
        PathPointA = PathPointA +[dataPATHPTS_RotGL[2]] # Z - A Grad
        PathPointB = PathPointB +[dataPATHPTS_RotGL[1]] # Y - B
        PathPointC = PathPointC +[dataPATHPTS_RotGL[0]] # X - C 
        
    fout.write(";FOLD PATH DATA" + "\n")
    count= len(PathPointX) 
    # Skalierung: 1:100 (vgl. Import)
    Skalierung = 1000
    
    for i in range(0,count,1):    
        fout.write("PATHPTS[" + str(i+1) + "]={" + 
                   "X " + "{0:.5f}".format(PathPointX[i]*Skalierung) + ", Y " + "{0:.5f}".format(PathPointY[i]*Skalierung) +
                   ", Z " + "{0:.5f}".format(PathPointZ[i]*Skalierung) + ", A " + "{0:.5f}".format(Vorz3 *PathPointA[i] ) +
                   ", B " + "{0:.5f}".format(Vorz2 *PathPointB[i]) + ", C " + "{0:.5f}".format(Vorz1 *PathPointC[i] ) +
                   "} " + "\n")
        
    fout.write(";ENDFOLD" + "\n")
    
    # TIMEPTS[1]=1.7  
    TIMEPTS_PATHPTS, TIMEPTS_PATHPTSCount = RfS_TIMEPTS(objEmpty_A6) # todo: Obj Liste in RfS_TIMEPTS
    
    fout.write(";FOLD TIME DATA" + "\n")
    for i in range(0,TIMEPTS_PATHPTSCount,1):    
        fout.write("TIMEPTS[" + str(i+1) + "]=" + 
                   "{0:.5f}".format(TIMEPTS_PATHPTS[i] ) +
                   "\n")
    fout.write(";ENDFOLD" + "\n")
    
    # Close the file
    fout.close();
    print('WtF_KUKAdat done')
    print('_____________________________________________________________________________')
    
    
def RfS_LocRot(objPATHPTS, dataPATHPTS_Loc, dataPATHPTS_Rot, BASEPos_Koord, BASEPos_Angle):
    # Aufruf von: create_PATHPTSObj, SetSafePos
    # Diese Funktion wird nur bei Export, Refresh (unnoetiger Weise) und Import (ueber replaceCP) aufgerufen.
    # Wiedergabe von LOC/Rot bezogen auf Base
    
    # World2Local - OK
    
    # dataPATHPTS_Loc = Global --> PATHPTS_Koord bezogen auf Base 
    # dataPATHPTS_Rot = Global --> PATHPTS_Angle bezogen auf Base
    print('_____________________________________________________________________________')
    print('Funktion: RfS_LocRotX - lokale Koordinaten bezogen auf Base!')
    
    objBase = bpy.data.objects['Sphere_BASEPos']
    PATHPTS_Angle = []
    
    matrix_world = bpy.data.objects[objBase.name].matrix_world  #global
    point_local  = dataPATHPTS_Loc                              #global 
    
    print('point_local'+ str(point_local))  # neuer Bezugspunkt
    
    #--------------------------------------------------------------------------
    mat_rotX = mathutils.Matrix.Rotation(math.radians(BASEPos_Angle[0]), 3, 'X') # Global
    mat_rotY = mathutils.Matrix.Rotation(math.radians(BASEPos_Angle[1]), 3, 'Y')
    mat_rotZ = mathutils.Matrix.Rotation(math.radians(BASEPos_Angle[2]), 3, 'Z')
    Mrot = mat_rotZ * mat_rotY * mat_rotX
    print('Mrot :'+ str(Mrot))
    mat_rotX2 = mathutils.Matrix.Rotation(dataPATHPTS_Rot[0], 3, 'X') # Global
    mat_rotY2 = mathutils.Matrix.Rotation(dataPATHPTS_Rot[1], 3, 'Y')
    mat_rotZ2 = mathutils.Matrix.Rotation(dataPATHPTS_Rot[2], 3, 'Z')  
    Mrot2 = mat_rotZ2 * mat_rotY2 * mat_rotX2
    print('Mrot2'+ str(Mrot2))
    #--------------------------------------------------------------------------
     
    PATHPTS_Koord = matrix_world.inverted() *point_local    # transpose fuehrt zu einem andren Ergebnis?!
    print('PATHPTS_Koord : '+ str(PATHPTS_Koord))           # neuer Bezugspunkt
    
    matrix_1R0 = Mrot.inverted()  * Mrot2 
    print('matrix_1R0'+ str(matrix_1R0))
    
    newR =matrix_1R0.to_euler('XYZ')
    
    print('newR'+ str(newR))    
    print('newR[0] :'+ str(newR[0]*360/(2*math.pi)))
    print('newR[1] :'+ str(newR[1]*360/(2*math.pi)))
    print('newR[2] :'+ str(newR[2]*360/(2*math.pi)))
        
    PATHPTS_Angle = (Vorz1* newR[0]*360/(2*math.pi), Vorz2*newR[1]*360/(2*math.pi), Vorz3*newR[2]*360/(2*math.pi))
    
    print('PATHPTS_Koord : ' + str(PATHPTS_Koord))
    print('PATHPTS_Angle: '+'C X {0:.3f}'.format(PATHPTS_Angle[0])+' B Y {0:.3f}'.format(PATHPTS_Angle[1])+' A Z {0:.3f}'.format(PATHPTS_Angle[2]))
    
    print('RfS_LocRot done')
    print('_____________________________________________________________________________')
    return PATHPTS_Koord, PATHPTS_Angle 

def SetCurvePos(objCurve, objBase, BASEPos_Koord, BASEPos_Angle):
    print('_____________________________________________________________________________')
    print('SetCurvePos: in Abhaengigkeit von Base Position')
    print('BASEPos_Koord' + str(BASEPos_Koord)) 
    print('BASEPos_Angle' + str(BASEPos_Angle))
    #-----------------------------------
    # Origin der Curve auf BASEPosition setzen   (ohne die Curve zu verschieben)
    SetOrigin(objCurve, objBase)
    # Kurve: Origin der Kurve auf BASEPosition verschieben
    bpy.data.objects[objCurve.name].rotation_mode =RotationModePATHPTS #n YXZ, XYZ
    objCurve.location = BASEPos_Koord.x,BASEPos_Koord.y ,BASEPos_Koord.z 
    objCurve.rotation_euler = BASEPos_Angle[0] *(2*math.pi)/360,  BASEPos_Angle[1] *(2*math.pi)/360,BASEPos_Angle[2] *(2*math.pi)/360
    print('SetCurvePos done')
    print('_____________________________________________________________________________') 
    
def SetObjRelToBaseX(Obj, Obj_Koord, Obj_Angle, BASEPos_Koord, BASEPos_Angle):
    # Obj_Koord und Obj_Angle sind lokale Angaben bezogen auf Base
    # Aufruf bei Import
    # Obj_Angle [rad]
    # BASEPos_Angle [rad]
    # Transformation Local2World
    
    objBase = bpy.data.objects['Sphere_BASEPos']
    bpy.data.objects[Obj.name].rotation_mode =RotationModeTransform
    
    matrix_world =bpy.data.objects[objBase.name].matrix_world
    point_local  = Obj_Koord    
    if (Obj_Angle !='' and BASEPos_Angle !=''):
        print('point_local'+ str(point_local))  # neuer Bezugspunkt
        mat_rotX = mathutils.Matrix.Rotation(BASEPos_Angle[0], 3, 'X') # C = -179 Global
        mat_rotY = mathutils.Matrix.Rotation(BASEPos_Angle[1], 3, 'Y') # B = -20
        mat_rotZ = mathutils.Matrix.Rotation(BASEPos_Angle[2], 3, 'Z') # A = -35
        Mrot = mat_rotZ * mat_rotY * mat_rotX
        print('Mrot'+ str(Mrot))
        mat_rotX2 = mathutils.Matrix.Rotation(Obj_Angle[0], 3, 'X') # Local (bez. auf Base)
        mat_rotY2 = mathutils.Matrix.Rotation(Obj_Angle[1], 3, 'Y') # 0,20,35 = X = -C, Y = -B, Z = -A
        mat_rotZ2 = mathutils.Matrix.Rotation(Obj_Angle[2], 3, 'Z')
        Mrot2 = mat_rotZ2 * mat_rotY2 * mat_rotX2 # KUKA Erg.
        print('Mrot2'+ str(Mrot2))
    
        rot_matrix_world = Mrot2.transposed() * Mrot.transposed()       
        rot_matrix_world = rot_matrix_world.transposed()
        rotEuler =rot_matrix_world.to_euler('XYZ')
        Obj.rotation_euler = rotEuler
    
    print('rotEuler'+ str(rotEuler))
    print('rotEuler[0] :'+ str(rotEuler[0]*360/(2*math.pi)))
    print('rotEuler[1] :'+ str(rotEuler[1]*360/(2*math.pi)))
    print('rotEuler[2] :'+ str(rotEuler[2]*360/(2*math.pi)))
    
    point_world = matrix_world *point_local
    Obj.location = point_world #Vector_World
    print('point_world :'+ str(point_world))
       
    return



def RefreshButton_todo(objEmpty_A6, TIMEPTS, TIMEPTSCount):
    
    # todo: under construction.....
    # KeyFrames (in der Scene) setzen, unabhaengig ob TIMPTS from Scene/ from File
    # Aufruf von: CurveImport
    original_type = bpy.context.area.type
    bpy.context.area.type = "VIEW_3D" 
    bpy.ops.object.select_all(action='DESELECT')
    print('_____________________________________________________________________________')
    print('RefreshButton_todo_PATHPTS')
    # erstellen von 'TIMEPTSCount' KeyFrames an den Positionen 'dataPATHPTS_Loc' mit der Ausrichtung 'dataPATHPTS_Rot'
    # fuer das Objekt objEmpty_A6
    PATHPTSObjName = 'PTPObj_'
    # 1. Wieviele PTPObj Objekte sind in der Scene vorhanden? (Beachte: Viele Objekte koennen den selben Datencontainer verwenden)
    PATHPTSObjList, countPATHPTSObj  = count_PATHPTSObj(PATHPTSObjName)
    print('Es sind ' + str(countPATHPTSObj) + 'PATHPTSObj in der Szene vorhanden.' )
    # todo
    TIMEPTS, TIMEPTSCount = RfS_TIMEPTS(objEmpty_A6)
    print('Es sind ' + str(TIMEPTSCount) + 'TIMEPTS in der Szene vorhanden.' )
    print('Folgende PATHPTSObj wurden in der Szene gefunden: ' + str(PATHPTSObjList))
    
    
    # Datencontainer:  
    for mesh in bpy.data.meshes:
        print(mesh.name)  
    # 2. Anpassen der Anzahl der Objekte auf 'PATHPTSCountFile'
    # sicherstellen das kein ControlPoint selektiert ist:
    bpy.ops.object.select_all(action='DESELECT')
    
    if PATHPTSCountFile <= countPATHPTSObj:
        CountCP = countPATHPTSObj
        print('Der Import hat weniger oder gleich viele PATHPTS als in der Szene bereits vorhanden.')
    if PATHPTSCountFile > countPATHPTSObj:
        CountCP = PATHPTSCountFile
        print('Der Import hat mehr PATHPTS als in der Szene bereits vorhanden.')
    # 3. Zuweisen von dataPATHPTS_Loc
    # 4. Zuweisen von dataPATHPTS_Rot
    # kuerze die Laenge der aktuellen Kurve auf die File-Kurve, wenn noetig
    if PATHPTSCountFile < countPATHPTSObj:
        print('Loeschen der ueberfluessigen PATHPTS Objekte aus der Szene...')
        delList =[]
        zuViel = countPATHPTSObj - PATHPTSCountFile
        delList = [PATHPTSCountFile]*(PATHPTSCountFile+zuViel)
        
        for n in range(PATHPTSCountFile, PATHPTSCountFile+zuViel, 1):      
            bpy.data.objects[PATHPTSObjList[n]].select = True
            bpy.ops.object.delete()
            bpy.ops.object.select_all(action='DESELECT')
        PATHPTSObjList, countPATHPTSObj  = count_PATHPTSObj(PATHPTSObjName)
        CountCP = countPATHPTSObj
        
    for n in range(CountCP):
        if (countPATHPTSObj-1) >= n: # Wenn ein PATHPTS Objekt vorhandenen ist,
            # Waehle eine PATHPTS Objekt aus:
            bpy.data.objects[PATHPTSObjList[n]].select
            print('Waehle Objekt aus: ' + str(PATHPTSObjList[n]))
            
            if (PATHPTSCountFile-1) >= n: # Wenn ein Datenpunkt (PATHPTS) im File da ist, uebertrage loc und rot auf PATHPTSObj
                print('PATHPTS Objekt ' + str(n) + ' vorhanen:' + str(bpy.data.objects[PATHPTSObjList[n]].name))
                print('IF - uebertrage loc: ' + str(dataPATHPTS_Loc[n]) 
                      + ' und rot Daten:' + str(dataPATHPTS_Rot[n]) 
                      + ' vom File auf Objekt:' + str(PATHPTSObjList[n]))
                
                SetObjRelToBase(bpy.data.objects[PATHPTSObjList[n]], Vector(dataPATHPTS_Loc[n]), dataPATHPTS_Rot[n], BASEPos_Koord, BASEPos_Angle) #Transformation Local2World
                      
        else: # wenn kein Kurvenpunkt zum ueberschreiben da ist, generiere einen neuen und schreibe den File-Datenpunkt
            print('Kein weiteres PATHPTS Objekt mehr in der Szene vorhanden.')
            print('Erstelle neues PATHPTS Objekt.')
            
            # add an new MESH object
            print('bpy.context.area.type: ' + bpy.context.area.type)
            bpy.ops.object.add(type='MESH')  
            #bpy.context.object.name = PATHPTSObjName + str(n+1) # "%03d" % 2
            bpy.context.object.name = PATHPTSObjName + str("%03d" %(n+1)) # "%03d" % 2
            PATHPTSObjList, countPATHPTSObj  = count_PATHPTSObj(PATHPTSObjName)
            bpy.data.objects[PATHPTSObjList[n]].data = bpy.data.objects[PATHPTSObjList[1]].data
            print('IF - uebertrage loc: ' + str(dataPATHPTS_Loc[n]) 
                      + ' und rot Daten:' + str(dataPATHPTS_Rot[n]) 
                      + ' vom File auf Objekt:' + str(PATHPTSObjList[n]))
            
            SetObjRelToBase(bpy.data.objects[PATHPTSObjList[n]], Vector(dataPATHPTS_Loc[n]), dataPATHPTS_Rot[n], BASEPos_Koord, BASEPos_Angle) #Transformation Local2World
                
    bpy.context.area.type = original_type 
    print('RefreshButton_todo_PATHPTS done')
    print('_____________________________________________________________________________')  
    
    
def SetKukaToCurve(objCurve):
    print('_____________________________________________________________________________')
    print('SetKukaToCurve')
    # Achtung: SetKukaToCurve funktioniert nur richtig, wenn das Parenting vorher geloest wurde!
    
    '''
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects['Empty_Zentralhand_A6'].select
    bpy.data.objects['BezierCircle'].select
    bpy.ops.object.parent_clear(type='CLEAR')
    '''
    
    # Empty_Zentralhand_A6 auf Startpunkt der Kurve setzen
    # Achtung: Delta Location muss auf Nullgesetzt werden:
    bpy.data.objects[objCurve.name].rotation_mode = RotationModeTransform #RotationModePATHPTS
    objCurve.delta_location = (0,0,0)
    
    matrix_world = objCurve.matrix_world
    # Wichtig: Beim letzten Punkt in der Kurve [-1] Anfangen, warum auch immer
    # (ansonsten offset zwischen Punkt [0] und [-1]
    point_local  = objCurve.data.splines[0].bezier_points[-1].co
    
    point_world  = matrix_world * point_local
    
    bpy.data.objects['Empty_Zentralhand_A6'].location = point_world
    
    #-----------------------------------
    bpy.ops.object.select_all(action='DESELECT')
    #-----------------------------------
    print('SetKukaToCurve done')
    print('_____________________________________________________________________________')
    
# set Kuka to HOMEPos
        #objEmpty_A6.location, objEmpty_A6.rotation_euler = SetObjRelToBase(bpy.data.objects[PATHPTSObjName + str('001')].location, bpy.data.objects[PATHPTSObjName+ str('001')].rotation_euler, BASEPos_Koord, BASEPos_Angle)
        #objEmpty_A6.location, objEmpty_A6.rotation_euler = HOMEPos_Koord, HOMEPos_Angle
        

def ClearParenting():
    print('_____________________________________________________________________________')
    print('ClearParenting')
    objSafe = bpy.data.objects['Sphere_SAFEPos']
    objBase = bpy.data.objects['Sphere_BASEPos']
    objCurve = bpy.data.objects['BezierCircle']
    objEmpty_A6 = bpy.data.objects['Empty_Zentralhand_A6']
    # testen: objEmpty_A6 = bpy.context.scene.objects.get('Empty_Zentralhand_A6')
    # 1. Parenting zwischen BASEPosition und Kurve loesen:
    bpy.ops.object.select_all(action='DESELECT')
    objCurve.select = True   
    objBase.select= True
    bpy.context.scene.objects.active = objBase 
    bpy.ops.object.parent_clear(type='CLEAR')
    
    # 2. Parenting zwischen Zentralhand_A6 (Empty) und Kurve loesen:
    bpy.ops.object.select_all(action='DESELECT')
    objEmpty_A6.select=True
    objCurve.select=True
    bpy.context.scene.objects.active = objCurve
    bpy.ops.object.parent_clear(type='CLEAR')
    
    # 3. Parenting zwischen SAFEPosition und Kurve loesen:
    bpy.ops.object.select_all(action='DESELECT')
    objCurve.select = True   
    objSafe.select= True 
    bpy.context.scene.objects.active = objSafe
    bpy.ops.object.parent_clear(type='CLEAR')
    print('ClearParenting done')
    print('_____________________________________________________________________________')
    
def SetParenting():
    print('_____________________________________________________________________________')
    print('SetParenting')
    objCurve = bpy.data.objects['BezierCircle']
    objEmpty_A6 = bpy.data.objects['Empty_Zentralhand_A6']
    # Parenting zwischen Zentralhand_A6 (Emppty) und Kurve:
    bpy.ops.object.select_all(action='DESELECT')
    objEmpty_A6.select=True
    objCurve.select=True
    bpy.context.scene.objects.active = objCurve
    objEmpty_A6.parent=objCurve
    bpy.ops.object.parent_set(type='FOLLOW', xmirror=False, keep_transform=True)
        
    # Parenting zwischen BASEPosition und Kurve:
    #bpy.data.objects['Sphere_BASEPos'].parent=bpy.data.objects['BezierCircle']  
        
    print('SetParenting done')
    print('_____________________________________________________________________________')

def writelog(text):
    FilenameLog = bpy.data.filepath
    FilenameLog = FilenameLog.replace(".blend", '.log')
    fout = open(FilenameLog, 'a')
    localtime = time.asctime( time.localtime(time.time()) )
    fout.write(localtime + " : " + text)
    fout.close();

def SetKeyFrames(objEmpty_A6, TargetObjList, TIMEPTS):
    # Diese Funktion soll spaeter anhand einer chronologisch geordneten Objektgruppen 
    # und Objekt/PATHPTS - Liste die KeyFrames eintragen
    
    
    # TODO: pruefen ob TIMEPTS = PATHPTS ist und ggf. neue keyframes und TIMEPTS setzen
    
    original_type         = bpy.context.area.type
    bpy.context.area.type = "VIEW_3D"
    bpy.ops.object.select_all(action='DESELECT')
     
    #TargetObjList = bpy.data.objects[PATHPTSObjList[n]] 
         
    #scene = bpy.context.scene
    #fps = scene.render.fps
    #fps_base = scene.render.fps_base
    
    PATHPTSObjList, countPATHPTSObj = count_PATHPTSObj(PATHPTSObjName)
    
    TIMEPTS = ValidateTIMEPTS(countPATHPTSObj, PATHPTSObjList, TIMEPTS)
    PATHPTSObjList =  renamePATHObj(PATHPTSObjList)
    
    
    TargetObjList = PATHPTSObjList # todo: Bei Bearbeitung und Konkatonierung per GUI Ablauf 
    # von GetRout u. SetKeyFrames ueberdenken
    
    raw_time=[]
    frame_number=[]
    
    bpy.context.scene.objects.active = objEmpty_A6
    
    # todo: Achtung, bei Konkatonation von KeyFrames muss der folgende Aufruf entfallen:
    objEmpty_A6.select = True
    bpy.ops.anim.keyframe_clear_v3d() #Remove all keyframe animation for selected objects
    # --- Alternativ kann die TIMEPTS Reihe gemerged werden (Safepos + PathPTS); Vorteil: 
    
    ob = bpy.context.active_object
    #bpy.data.objects[objCurve.name].rotation_mode = 'QUATERNION'
    ob.rotation_mode = 'QUATERNION'
    
    #QuaternionList = OptimizeRotationQuaternion(TargetObjList, TIMEPTSCount)
    
    for n in range(countPATHPTSObj):
        writelog(n)
        bpy.context.scene.frame_set(time_to_frame(TIMEPTS[n])) 
        ob.location = bpy.data.objects[TargetObjList[n]].location
        # todo - done: keyframes auf quaternion um gimbal lock zu vermeiden
                
        ob.rotation_quaternion = bpy.data.objects[TargetObjList[n]].rotation_euler.to_quaternion()
           
        ob.keyframe_insert(data_path="location", index=-1)
        # file:///F:/EWa_WWW_Tutorials/Scripting/blender_python_reference_2_68_5/bpy.types.bpy_struct.html#bpy.types.bpy_struct.keyframe_insert
        
        ob.keyframe_insert(data_path="rotation_quaternion", index=-1)
        #ob.keyframe_insert(data_path="rotation_euler", index=-1)
            
    if len(TIMEPTS)> countPATHPTSObj:
        writelog('Achtung: mehr TIMEPTS als PATHPTS-Objekte vorhanden')
    # todo: end frame not correct if PATHPTS added....
    bpy.context.scene.frame_end = time_to_frame(TIMEPTS[TIMEPTSCount-1])
    
    bpy.data.scenes['Scene'].frame_current=1
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.area.type = original_type 


        MRot2old = Rot2old.to_quaternion().to_matrix()
        MRot2 = Rot2.to_quaternion().to_matrix()
        DRot2old = MRot2old.determinant()
        DRot2 = MRot2.determinant()
        
def ValidateTIMEPTS(PATHPTSObjList, TIMEPTS):
    writelog('_____________________________________________________________________________')
    writelog('ValidateTIMEPTS')
    countPATHPTSObj = len(PATHPTSObjList)
        
    # Korrektur der TIMEPTS Werte, wenn kleiner der Anzahl an PATHPTS
    while len(TIMEPTS)<countPATHPTSObj:
        for i in range(countPATHPTSObj):
            if PATHPTSObjList[i].find('.')!=-1: # wenn Objektname = "PTPObj_017.001", wichtig, um festzustellen wo das PTPObj eingefuegt wurde
                # Geschw. des letzten Positionswechsels ermitteln:
                if (i+1) < countPATHPTSObj:
                    s = bpy.data.objects[PATHPTSObjList[i+1]].location - bpy.data.objects[PATHPTSObjList[i-1]].location
                    v = s.length/(TIMEPTS[i]-TIMEPTS[i-1]) # [i] weil i der alte i+1 Eintrag ist
                    # Zeit fuer eingefuegten PATHPTS mit dieser Geschw. ermitteln und einfuegen:
                    s = bpy.data.objects[PATHPTSObjList[i+1]].location - bpy.data.objects[PATHPTSObjList[i]].location
                elif (i+1) >= countPATHPTSObj:
                    s = bpy.data.objects[PATHPTSObjList[i-1]].location - bpy.data.objects[PATHPTSObjList[i-2]].location
                    v = s.length/(TIMEPTS[i-1]-TIMEPTS[i-2])
                    # Zeit fuer eingefuegten PATHPTS mit dieser Geschw. ermitteln und einfuegen:
                    s = bpy.data.objects[PATHPTSObjList[i-1]].location - bpy.data.objects[PATHPTSObjList[i-2]].location
                
                deltaT = abs(s.length /v)
                NewTIMEPTS = deltaT + TIMEPTS[i-1] # v=s/t -> t = s/v
                TIMEPTS.insert( i, NewTIMEPTS)
                # alle anderen TIMEPTS zeitlich um NewTIMEPTS verschieben:
                for n in range(i+1, len(TIMEPTS)):
                    TIMEPTS[n] = TIMEPTS[n] +  deltaT

def OptimizeRotation(ObjList):
    countObj = len(ObjList)
    # Begrenze Rotation auf 360 Grad
    for i in range(countObj-1):
        
        Rot   = bpy.data.objects[ObjList[i]].rotation_euler
        modRot= math.modf(Rot.x/ (2*math.pi)) # Ergebnis: (Rest, n)
        Rot.x = modRot[0] * (2*math.pi) 
        modRot= math.modf(Rot.y/ (2*math.pi)) # Ergebnis: (Rest, n)
        Rot.y = modRot[0] * (2*math.pi) 
        modRot= math.modf(Rot.z/ (2*math.pi)) # Ergebnis: (Rest, n)
        Rot.z = modRot[0] * (2*math.pi) 
        
        
        '''
        if Rot.x <0:
            Rot.x = Rot.x + (2*math.pi)
        if Rot.y <0:
            Rot.y = Rot.y + (2*math.pi) 
        if Rot.z <0:
            Rot.z = Rot.z + (2*math.pi)
        '''
    
    # Teil 1:
    # wenn zum erreichen des folgenden Winkels mehr als 180Grad (PI) zurueckzulegen ist, 
    # dann zaehle 360Grad drauf (wenn er negativ ist) bzw. ziehe 360Grad ab (wenn er positiv ist)
    

    for i in range(countObj-1):
        Rot1 = bpy.data.objects[ObjList[i]].rotation_euler
        Rot2 = bpy.data.objects[ObjList[i+1]].rotation_euler
        Rot2old = deepcopy(Rot2)

        #Rot2Q = bpy.data.objects[ObjList[i+1]].rotation_euler.to_quaternion()

        
        #DeltaRot = [Rot2.x - Rot1.x,Rot2.y - Rot1.y,Rot2.z - Rot1.z]
        '''
        # wenn eine Drehung von - auf + oder + auf - erfolgt, korregiere das DeltaRot:
        if Rot1.x <  0 and Rot2.x >=0:
            DeltaRot[0] = Rot2.x - (2*math.pi + Rot1.x)
        if Rot1.x >= 0 and Rot2.x <0:
            DeltaRot[0] = (Rot2.x + 2*math.pi) - Rot1.x
        
        if Rot1.y <  0 and Rot2.y >=0:
            DeltaRot[1] = Rot2.y - (2*math.pi + Rot1.y)
        if Rot1.y >= 0 and Rot2.y <0:
            DeltaRot[1] = (Rot2.y + 2*math.pi) - Rot1.y
        
        if Rot1.z <  0 and Rot2.z >=0:
            DeltaRot[2] = Rot2.z - (2*math.pi + Rot1.z)
        if Rot1.z >= 0 and Rot2.z <0:
            DeltaRot[2] = (Rot2.z + 2*math.pi) - Rot1.z
        '''
        
        
        '''        
        if  DeltaRot[0] > math.pi and Rot2.x < 0: # Achtung nur immer den folgenden aendern, da sonst nicht rueckwaertskompatibel
            Rot2.x =  2*math.pi + Rot2.x
        elif DeltaRot[0] > math.pi and Rot2.x >=0:
            Rot2.x = -2*math.pi + Rot2.x #-
            
        if  DeltaRot[1] > math.pi and Rot2.y < 0: # Achtung nur immer den folgenden aendern, da sonst nicht rueckwaertskompatibel
            Rot2.y =  2*math.pi + Rot2.y
        elif DeltaRot[1] > math.pi and Rot2.y >=0:
            Rot2.y = -2*math.pi + Rot2.y #-
        
        if  DeltaRot[2] > math.pi and Rot2.z < 0: # Achtung nur immer den folgenden aendern, da sonst nicht rueckwaertskompatibel
            Rot2.z =  2*math.pi + Rot2.z
        elif DeltaRot[2] > math.pi and Rot2.z >=0:
            Rot2.z = -2*math.pi + Rot2.z #-
        '''
        
        # Quaternation-Flip disabled
        # ohne OptimRotation: Quaternion(( 0.1570675 9691238403, -0.639445 6028938293,  0.7424664497375488,  -0.1232177 3916482925))
        # ohne flip:          Quaternion(( 0.1570675 3730773926, -0.639445 7221031189,  0.742466 390132904,  -0.1232177 9131889343))
        # nach 1. flip (OK) : Quaternion((-0.1570675 0750541687,  0.639445 6624984741, -0.742466 4497375488,  0.1232177 7641773224)) auch ohne flip
        # nach 2. flip (NOK): Quaternion(( 0.1570675 9691238403, -0.639445 6028938293,  0.742466 4497375488, -0.1232177 3916482925))
        
        
        rF = 12
        new = [round(Rot2.to_quaternion()[0],rF), round(Rot2.to_quaternion()[1],rF),round(Rot2.to_quaternion()[2],rF), round(Rot2.to_quaternion()[3],rF)]
        old = [-round(Rot2old.to_quaternion()[0],rF), -round(Rot2old.to_quaternion()[1],rF),-round(Rot2old.to_quaternion()[2],rF), -round(Rot2old.to_quaternion()[3],rF)]
        
        if new[:] == old[:]: # notwendig um Quaternion flip zu vermeiden
            Rot2.x = Rot2old.x
            Rot2.y = Rot2old.y
            Rot2.z = Rot2old.z
        
        print('')
        
    # Korrektur der TIMEPTS Werte, wenn groesser der Anzahl an PATHPTS    
    # Achtung: wird noch nicht benoetigt, da in der Funktion erst alle KeyFrames geloescht werden. D.h. TIMEPTS Werte 
    # bleiben ggf. ungenutzt, ohne Fehler zu erzeugen.
    # Achtung: wuerde Sinn machen eine Klasse PATHPTS erstellen um die Zuordnung von Zeit, Kraft, etc. zu bekommen.
        
    writelog('ValidateTIMEPTS done')    
    writelog('_____________________________________________________________________________')
    return TIMEPTS
    
    # Korrektur der TIMEPTS Werte, wenn groesser der Anzahl an PATHPTS         
