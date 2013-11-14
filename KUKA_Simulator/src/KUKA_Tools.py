#git
# 
# Beachte: x=(1,2,3) ist TUPEL, d.h. nicht veraenderbar; x = [1,2,3] ist Listse (veraenderbar)
 
#[point.co for point in bpy.context.active_object.data.splines[0].bezier_points]
# ToDo: handle und tilt zur Ausrichtung jedes PathPoints verwenden (ueber Eingabefeld)
# handling vom POP UP window: alternativ *.src laden ODER default TP auswaehlen --> Panel(bpy_struct)
# Origin verknuepfen mit Tool-Position/ *.src? (rotation???)
# bpy.context.active_object.data.splines[0].bezier_points[1].tilt=3.14  -> Verdrehung um den handle [rad]
# Rotation 
# button um nach editieren der Kurve das Kuka_Empty auf den ersten Kurvenpunkt zu setzen
# todo: rotation des Empty (Zentralhand_A6)  muss extra eingestellte werden! (A, B, C aus .dat -> Kurve)
# bpy.data.objects['OBJ_KUKA_Armature'].pose.bones['Bone_KUKA_Zentralhand_A4'].rotation_euler
# KUKA Modell richtig ausrichten (und spiegeln, da z.Zt. spiegelverkehrt)
# ARMATURE: Position und Winkel auf Plausibilitaet abfragen
# Eigenes Menue erstellen (aus specials Menue entfernen) [done: --> Object Fenster]
# Phyton code aufraeumen
# Doku update
# Info: 
# 0. SAFE POSITION: muss immer von Hand im Menue angegeben werden. auch BASEPosition????
# 1. Kuka startet von HOMEPOSITION und faehrt zur BASEPosition
# 2. Kuka faehrt von der BASEPosition zum ersten Kurvenpunkt
# 3. Die Kurvenpunkte werden abgearbeitet 
# 4. Kuka faehrt zur SAFEPosition 
# 5. Keine Wiederholung: fahre zur HOMEPOSITION
# 6. Wiederholung: Wiederhole Punkte 2, 3, 4
 
# ToDo: ToolPosition auslesen und offset beruecksichtigen MES ={ :  enthalten in *.dat -> OBJ_KUKA_EndEffector zuweisen
# BasePosition: (noch kein korrespondierender KUKA File bekannt !!! -> ALe

'''

${workspace_loc:CurveExport/src/curve_export.py}

Bevel add-on
bpy.data.curves[bpy.context.active_object.data.name].splines[0].bezier_points[0].co=(0,1,1)
'''  
#--- ### Header 
bl_info = { 
    "name": "CurveExport",
    "author": "Eric Wahl",
    "version": (1, 0, 1),
    "blender": (2, 5, 7),
    "api": 36147,
    "location": "View3D >Specials (W-key)",
    "category": "Curve",
    "description": "Import/ Export Kuka Bahnkurve",
    "warning": "",
    "wiki_url": "http://...",
    "tracker_url": "http://..."
    }
#--- ### Imports
import bpy, os
import sys
from bpy.utils import register_module, unregister_module
from bpy.props import FloatProperty, IntProperty
from mathutils import Vector  
from mathutils import *
import mathutils
import math
# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


# todo: globale variablen definieren.....
 

def BasePos2File(BASEPos_Koord, BASEPos_Angle, filepath):
    print('_____________________________________________________________________________')
    print('BasePos2File ')
    print('Remark: this file is not a part of the normal KUKA Ocutbot Software.')
    print('BASEPos_Angle[0]: ' +str(BASEPos_Angle[0]))
    print('BASEPos_Angle[1]: ' +str(BASEPos_Angle[1]))    #
    print('BASEPos_Angle[2]: ' +str(BASEPos_Angle[2])) 
    FilenameSRC = filepath
    FilenameSRC = FilenameSRC.replace(".dat", ".cfg") 
    fout = open(FilenameSRC, 'w')
     
    SkalierungPTP = 1000
    
    fout.write("BASEPos {" + 
                   "X " + "{0:.5f}".format(BASEPos_Koord[0]*SkalierungPTP) + 
                   ", Y " + "{0:.5f}".format(BASEPos_Koord[1]*SkalierungPTP) +
                   ", Z " + "{0:.5f}".format(BASEPos_Koord[2]*SkalierungPTP) + 
                   ", A " + "{0:.5f}".format(BASEPos_Angle[0]) +
                   ", B " + "{0:.5f}".format(BASEPos_Angle[1]) + 
                   ", C " + "{0:.5f}".format(BASEPos_Angle[2]) +
                   "} " + "\n")
    
    fout.close();
    print('BasePos2File geschrieben.')
    print('_____________________________________________________________________________')

def SafePos2File(SAFEPos_Koord, SAFEPos_Angle, filepath):
    print('_____________________________________________________________________________')
    print('SafePos2File ')
    print('Exporting ' + filepath)
    print('SAFEPos_Koord: ' + str(SAFEPos_Koord))
    print('SAFEPos_Angle: ' + str(SAFEPos_Angle)) 
    # -------------------------------------------------------------------------------------------
    # SAFEPosition in *.src schreiben
    '''
    ;FOLD _________ SAFE POSITION _______________
    BAS (#VEL_PTP,20)
    ;ENDFOLD
    PTP {X 82.815240, Y 100.194500, Z -11.291560, A 69.842480, B -2.680786, C -3.097058}
    '''
    
    FilenameSRC = filepath
    FilenameSRC = FilenameSRC.replace(".dat", ".src") 
    fout = open(FilenameSRC, 'w')
    print(FilenameSRC)
     
    SkalierungPTP = 1000
    # Achtung: vertices[0].co ist lokale Angabe (d.h. bzgl. Position seines Origin)!
    
    fout.write("PTP {" + 
                   "X " + "{0:.5f}".format(SAFEPos_Koord[0]*SkalierungPTP) + 
                   ", Y " + "{0:.5f}".format(SAFEPos_Koord[1]*SkalierungPTP) +
                   ", Z " + "{0:.5f}".format(SAFEPos_Koord[2]*SkalierungPTP) + 
                   ", A " + "{0:.5f}".format(SAFEPos_Angle[0]) +
                   ", B " + "{0:.5f}".format(SAFEPos_Angle[1]) + 
                   ", C " + "{0:.5f}".format(SAFEPos_Angle[2]) +
                   "} " + "\n")
    
    fout.close();
    
    print('SAFEPosition geschrieben.')
    print('_____________________________________________________________________________')
    
    # --------------------------------------------------------------------------------------------------------------------------------
    # todo: RfS_LocRot, , WtF_CurveData
    # --------------------------------------------------------------------------------------------------------------------------------
    
def RfS_LocRot(objPATHPTS, dataPATHPTS_Loc, dataPATHPTS_Rot, BASEPos_Koord, BASEPos_Angle):
    # Aufruf von: create_PATHPTSObj
    #todo: under construction/ test ..... Funktionsumkehrung zu SetPATHPTSPosScene
    
    
    # Diese Funktion wird nur bei Export aufgerufen.
    print('_____________________________________________________________________________')
    print('Funktion: RfS_LocRot - lokale Koordinaten bezogen auf Base!')
    
    # todo: auf CurveObj übertragen, Funktion mit RfS_SafePos kombinieren
    
    objBase = bpy.data.objects['Sphere_BASEPos']
    PATHPTS_Angle = []
    # PATHPTS_Angle Angle auch in Abhaengigkeit von BasePos Orientierung exportieren/ speichern!
    PATHPTS_Angle = PATHPTS_Angle +[(dataPATHPTS_Rot[0] -objBase.rotation_euler.x) *360/(2*math.pi)]
    PATHPTS_Angle = PATHPTS_Angle +[(dataPATHPTS_Rot[1] -objBase.rotation_euler.y) *360/(2*math.pi)]
    PATHPTS_Angle = PATHPTS_Angle +[(dataPATHPTS_Rot[2] -objBase.rotation_euler.z) *360/(2*math.pi)]
    print('PATHPTS_Angle - ini: '+'A {0:.3f}'.format(PATHPTS_Angle[0])+' B {0:.3f}'.format(PATHPTS_Angle[1])+' C {0:.3f}'.format(PATHPTS_Angle[2]))
    
    objPATHPTS.rotation_euler = (0,0,0) # um die richtigen Koordinaten zu bekommen
    
    print('PATHPTS: bevor Origin auf BasePos' +str(objPATHPTS.data.vertices[0].co))
    
    # setzen des PATHPTS Origin auf  vertex[0] der BasePosition: 
    SetOrigin(objPATHPTS, objBase)
    
    print('PATHPTS_Angle: '+'A {0:.3f}'.format(PATHPTS_Angle[0])+' B {0:.3f}'.format(PATHPTS_Angle[1])+' C {0:.3f}'.format(PATHPTS_Angle[2]))
    
    print('Umrechnung auf globale Koordinaten....')
    print('Transformation von SafePos auf BasePos...')
    vec = objPATHPTS.data.vertices[0].co # Achtung: Bei Aktuellem Objekt für PATHPTS liegt vertices[0] nicht im Ursprung des Objektes
    print('vec: ' +str(vec))
    eul = mathutils.Euler((objBase.rotation_euler.x, objBase.rotation_euler.y, objBase.rotation_euler.z), 'XYZ')
    print('eul: ' +str(eul))
    vec3d = vec.to_3d()
    mat_rot = eul.to_matrix()
    mat_loc = vec3d
    mat = mat_loc * mat_rot.to_3x3()
    print('mat: ' + str(mat))
    
    #Achtung: lokale Koordinaten (bezogen auf Base) wie in Datei gespeichert
    PATHPTS_Koord = mat
    print('PATHPTS_Koord = point_local: ' + str(PATHPTS_Koord))
    print('PATHPTS_Angle: '+'A {0:.3f}'.format(PATHPTS_Angle[0])+' B {0:.3f}'.format(PATHPTS_Angle[1])+' C {0:.3f}'.format(PATHPTS_Angle[2]))
    
    
    print('PATHPTS-Origin auf PATHPTS setzen ....')
    # setzen des PATHPTS Origin auf  vertex[0] des PATHPTSObj:
    SetOrigin(objPATHPTS, objPATHPTS)
    
    print('PATHPTS_Angle: '+'A {0:.3f}'.format(PATHPTS_Angle[0])+' B {0:.3f}'.format(PATHPTS_Angle[1])+' C {0:.3f}'.format(PATHPTS_Angle[2]))
    
    print('PATHPTS_Angle wieder dem Origin zuweisen')
    objPATHPTS.rotation_euler.x = PATHPTS_Angle[0] *(2*math.pi)/360 +objBase.rotation_euler.x # [rad]
    objPATHPTS.rotation_euler.y = PATHPTS_Angle[1] *(2*math.pi)/360 +objBase.rotation_euler.y# [rad]
    objPATHPTS.rotation_euler.z = PATHPTS_Angle[2] *(2*math.pi)/360 +objBase.rotation_euler.z # [rad]
    
    print('PATHPTS_Koord: ' + str(PATHPTS_Koord))
    print('PATHPTS_Angle: '+'A {0:.3f}'.format(PATHPTS_Angle[0])+' B {0:.3f}'.format(PATHPTS_Angle[1])+' C {0:.3f}'.format(PATHPTS_Angle[2]))
    
    
    print('RfS_LocRot done')
    print('_____________________________________________________________________________')
    return PATHPTS_Koord, PATHPTS_Angle 


   
def WtF_CurveData(obj, PATHPTSObjName, filepath, BASEPos_Koord, BASEPos_Angle):
    # dataPATHPTS_Loc, dataPATHPTS_Rot, 
    print('_____________________________________________________________________________')
    print('WtF_CurveData')  
     
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
    
    #koord = bpy.data.curves[obj.name].splines[0]
    koord = bpy.data.curves[bpy.data.objects[obj.name].data.name].splines[0] # wichtig: name des Datenblocks verwenden
    
    # todo: vector.angle(other vector, fallback) aus import mathutils
    
    
    
    # Achtung: PATHPTS werden noch nicht in Abh. von BASEPos (geschrieben)/ geladen!....
    #n = len(koord.bezier_points.values())
    #for i in range(0,n,1): # Liste erzeugen
    #    PathPointX = PathPointX +[koord.bezier_points[i].co.x]
    #    PathPointY = PathPointY +[koord.bezier_points[i].co.y]
    #    PathPointZ = PathPointZ +[koord.bezier_points[i].co.z]
                
        #
        
    countPATHPTSObj, PATHPTSObjList = count_PATHPTSObj(PATHPTSObjName)
    for i in range(countPATHPTSObj):    
        
        #dataPATHPTS_LocGL, dataPATHPTS_RotGL = RfS_LocRot(bpy.data.objects[PATHPTSObjList[i]], bpy.data.objects[PATHPTSObjList[i]].location, bpy.data.objects[PATHPTSObjList[i]].rotation_euler, BASEPos_Koord, BASEPos_Angle)
        # Achtung: PATHPTSObj für Koordinaten funktioniert nicht da Origins nicht auf Base liegen(.... vgl. Origin)
        
        #dataPATHPTS_LocGL, dataPATHPTS_RotGL = RfS_LocRot(bpy.data.objects[PATHPTSObjList[i]], koord.bezier_points[i].co, bpy.data.objects[PATHPTSObjList[i]].rotation_euler, BASEPos_Koord, BASEPos_Angle)
        dataPATHPTS_LocGL, dataPATHPTS_RotGL = RfS_LocRot(bpy.data.objects[PATHPTSObjList[i]], bpy.data.objects[PATHPTSObjList[i]].location, bpy.data.objects[PATHPTSObjList[i]].rotation_euler, BASEPos_Koord, BASEPos_Angle)
        
        PathPointX = PathPointX +[dataPATHPTS_LocGL[0]]
        PathPointY = PathPointY +[dataPATHPTS_LocGL[1]]
        PathPointZ = PathPointZ +[dataPATHPTS_LocGL[2]]
        
        PathPointA = PathPointA +[dataPATHPTS_RotGL[0]*360/(2* math.pi)] # Grad
        PathPointB = PathPointB +[dataPATHPTS_RotGL[1]*360/(2* math.pi)]
        PathPointC = PathPointC +[dataPATHPTS_RotGL[2]*360/(2* math.pi)]
        
        
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
        
    fout.write(";ENDFOLD" + "\n")
    # Close the file
    fout.close();
    
    print('WtF_CurveData done')
    print('_____________________________________________________________________________')
 
    
class createMatrix(object):
    print('_____________________________________________________________________________')
    print('createMatrix')
    def __init__(self, rows, columns, default=0):
        self.m = []
        for i in range(rows):
            self.m.append([default for j in range(columns)])
    def __getitem__(self, index):
        return self.m[index]
    print('createMatrix done')
    print('_____________________________________________________________________________')
#m = createMatrix(10,5)
#m[3][6] = 7

def ApplyScale(objCurve):
        print('_____________________________________________________________________________')
        print('ApplyScale')
        
        # nur Kurve auswaehlen
        bpy.ops.object.select_all(action='DESELECT')
        objCurve.select = True
        bpy.context.scene.objects.active = objCurve
        # Scaling (nur bei Export noetig)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.select_all(action='DESELECT')
        print('ApplyScale done')
        print('_____________________________________________________________________________')
        
def ClearParenting():
    print('_____________________________________________________________________________')
    print('ClearParenting')
    objSafe = bpy.data.objects['Sphere_SAFEPos']
    objBase = bpy.data.objects['Sphere_BASEPos']
    objCurve = bpy.data.objects['BezierCircle']
    objEmpty_A6 = bpy.data.objects['Empty_Zentralhand_A6']
    
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
    print('SetKukaToCurve done')
    print('_____________________________________________________________________________')


def RfS_BasePos(objCurve, filepath):    
    print('_____________________________________________________________________________')
    print('Read from Scene - RfS_BasePos')
    objBase = bpy.data.objects['Sphere_BASEPos']
    
    print('bringe Base Origin to Center...')
    original_type = bpy.context.area.type
    bpy.context.area.type = "VIEW_3D" 
    bpy.ops.view3d.snap_cursor_to_center()
    objBase.select =True
    bpy.context.scene.objects.active = objBase
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    bpy.context.area.type = original_type
    
    BASEPos_Koord = bpy.data.objects[objBase.name].location
    print('BASEPos_Koord: ' +str(BASEPos_Koord))
    
    #--------------------------
    # origin auf vert[0] setzten um die richtige Rotation zu bekommen
    # Origin der Base auf Vertex[0] setzen   (ohne die Base zu verschieben)
    
    SetOrigin(objBase, objBase)
    
    print('BASEPos_Koord: ' +str(BASEPos_Koord))
    
    # Achtung: Die Winkel BASEPos_Angle werden in Grad benoetigt (wie auch im Import File angegeben):
    BASEPos_Angle = []
    BASEPos_Angle = BASEPos_Angle + [bpy.data.objects[objBase.name].rotation_euler.x * 360 / (2*math.pi)]
    BASEPos_Angle = BASEPos_Angle + [bpy.data.objects[objBase.name].rotation_euler.y * 360 / (2*math.pi)]
    BASEPos_Angle = BASEPos_Angle + [bpy.data.objects[objBase.name].rotation_euler.z * 360 / (2*math.pi)]
    
    print('BASEPos_Koord: ' +str(BASEPos_Koord))
    print('BASEPos_Angle: ' +str(BASEPos_Angle))
    print('Read from Scene - RfS_BasePos done')
    print('_____________________________________________________________________________')
    return BASEPos_Koord, BASEPos_Angle
    
def RfF_BasePos(filepath):
    print('_____________________________________________________________________________')
    print('Read from File - RfF_BasePos')
    
    # ==========================================    
    # Import der BasePosition = KUKA (*.cfg) Kreation von mir!
    # ==========================================    
    try:
        FilenameSRC = filepath
        FilenameSRC = FilenameSRC.replace(".dat", ".cfg") 
        d = open(FilenameSRC)
        gesamtertext = d.read()
        d.close
        # Umwandeln in eine Liste
        zeilenliste =[]
        zeilenliste = gesamtertext.split(chr(10))
    
        # ==========================================
        # Suche nach "PTP"
        # ==========================================
        suchAnf = "BASEPos {X"
        suchEnd = "BASEPos {X"
        PATHPTSCountPTP = len(zeilenliste)
        PathIndexAnf = 0
        PathIndexEnd = PATHPTSCountPTP
        for i in range(PATHPTSCountPTP):
            if zeilenliste[i].find(suchAnf)!=-1: 
                PathIndexAnf = i
            if (zeilenliste[i].find(suchEnd)!=-1 and PathIndexAnf!=PathIndexEnd): 
                PathIndexEnd = i
                break
        PATHPTSCountPTP = PathIndexEnd - PathIndexAnf +1 # Achtung: hier wird 'ab der' Suchmarken ausgelesen
        
        # ==========================================
        # Einlesen der PTP Werte (X, Y, Z, A, B C) 
        # BASEPos {X 82.815240, Y 100.194500, Z -11.291560, A 69.842480, B -2.680786, C -3.097058}
        # ==========================================
        PTPX = []
        PTPY = []
        PTPZ = []
        PTPAngleA = []
        PTPAngleB = []
        PTPAngleC = []
        beg=0
        # die Schleife ist eigentlich unnoetig da es nur eine BASEPosition gibt...
        for i in range(0,PATHPTSCountPTP,1):
            IndXA = zeilenliste[PathIndexAnf+i].index("X ", beg, len(zeilenliste[PathIndexAnf])) # Same as find(), but raises an exception if str not found 
            IndXE = zeilenliste[PathIndexAnf+i].index(", Y", beg, len(zeilenliste[PathIndexAnf]))
            PTPX = PTPX + [float(zeilenliste[PathIndexAnf+i][IndXA+2:IndXE])]
       
            IndYA = zeilenliste[PathIndexAnf+i].index("Y ", beg, len(zeilenliste[PathIndexAnf]))  
            IndYE = zeilenliste[PathIndexAnf+i].index(", Z", beg, len(zeilenliste[PathIndexAnf]))
            PTPY = PTPY + [float(zeilenliste[PathIndexAnf+i][IndYA+2:IndYE])]
       
            IndZA = zeilenliste[PathIndexAnf+i].index("Z ", beg, len(zeilenliste[PathIndexAnf])) 
            IndZE = zeilenliste[PathIndexAnf+i].index(", A", beg, len(zeilenliste[PathIndexAnf]))
            PTPZ = PTPZ + [float(zeilenliste[PathIndexAnf+i][IndZA+2:IndZE])]
       
            IndAA = zeilenliste[PathIndexAnf+i].index("A ", beg, len(zeilenliste[PathIndexAnf])) 
            IndAE = zeilenliste[PathIndexAnf+i].index(", B", beg, len(zeilenliste[PathIndexAnf]))
            PTPAngleA = PTPAngleA + [float(zeilenliste[PathIndexAnf+i][IndAA+2:IndAE])] # * (2*math.pi)/360 als rad einlesen!
            print('PTPAngleA' +str(PTPAngleA))
            IndBA = zeilenliste[PathIndexAnf+i].index("B ", beg, len(zeilenliste[PathIndexAnf]))  
            IndBE = zeilenliste[PathIndexAnf+i].index(", C", beg, len(zeilenliste[PathIndexAnf]))
            PTPAngleB = PTPAngleB + [float(zeilenliste[PathIndexAnf+i][IndBA+2:IndBE])]
            print('PTPAngleB' +str(PTPAngleB))
            IndCA = zeilenliste[PathIndexAnf+i].index("C ", beg, len(zeilenliste[PathIndexAnf]))  
            IndCE = len(zeilenliste[PathIndexAnf+i])-2 # }   " "+chr(125) funktioniert nicht?!
            PTPAngleC = PTPAngleC + [float(zeilenliste[PathIndexAnf+i][IndCA+2:IndCE])]
            print('PTPAngleC' +str(PTPAngleC))
        SkalierungPTP = 1000
        BASEPos_Koord  = Vector([float(PTPX[0])/SkalierungPTP, float(PTPY[0])/SkalierungPTP, float(PTPZ[0])/SkalierungPTP])
        BASEPos_Angle  = float(str(PTPAngleA[0])), float(str(PTPAngleB[0])), float(str(PTPAngleC[0])) # in Grad
    except: 
        print('RfF_BasePos exception')
    print('RfF_BasePos done')
    print('_____________________________________________________________________________')
    return BASEPos_Koord, BASEPos_Angle    

def SetBasePos(objCurve, objBase, BASEPos_Koord, BASEPos_Angle):
    print('_____________________________________________________________________________')
    print('SetBasePos: Globale Koordinaten!')
    print('BASEPos_Koord' + str(BASEPos_Koord)) 
    print('BASEPos_Angle' + str(BASEPos_Angle))
    
    #-----------------------------------
    # Origin der Base auf Vertex[0] setzen   (ohne die Base zu verschieben)
    SetOrigin(objBase, objBase)
      
    try:  
        # BasePosition initialisieren:
        objBase.location = BASEPos_Koord.x, BASEPos_Koord.y, BASEPos_Koord.z
        print('BASEPos_Koord' + str(BASEPos_Koord)) 
        print('BASEPos_Angle' + str(BASEPos_Angle))
        
    except: 
        print('SetBasePos exception')
        #  IOError, wenn file not found (laeuft (im debug mode?) nicht....
        # falls kein *.src vorhanden, setze die delta transform/ BASEPosition auf Null:
        
        # POP UP Window:
        # todo: POP UP window ....
        #bpy.ops.object.dialog_operator('INVOKE_DEFAULT')
        objBase.location = 0,0,0
        objBase.rotation_euler = 0,0,0
    
    objBase.rotation_euler.x = (BASEPos_Angle[0] * (2*math.pi) /360) 
    objBase.rotation_euler.y = (BASEPos_Angle[1] * (2*math.pi) /360)
    objBase.rotation_euler.z = (BASEPos_Angle[2] * (2*math.pi) /360)
    print('nach rotation_euler')
    print('BASEPos_Angle' + str(BASEPos_Angle))
    print('SetBasePos done')
    print('_____________________________________________________________________________')


def SetCurvePos(objCurve, objBase, BASEPos_Koord, BASEPos_Angle):
    print('_____________________________________________________________________________')
    print('SetCurvePos: in Abhaengigkeit von Base Position')
    print('BASEPos_Koord' + str(BASEPos_Koord)) 
    print('BASEPos_Angle' + str(BASEPos_Angle))
    #-----------------------------------
    # Origin der Curve auf BASEPosition setzen   (ohne die Curve zu verschieben)
    SetOrigin(objCurve, objBase)
    # Kurve: Origin der Kurve auf BASEPosition verschieben
    objCurve.location = BASEPos_Koord.x,BASEPos_Koord.y ,BASEPos_Koord.z 
    
    print('SetCurvePos done')
    print('_____________________________________________________________________________')

'''    
def RfS_SafePos():
    print('_____________________________________________________________________________')
    print('Read from Scene - RfS_SafePos')
    objSafe = bpy.data.objects['Sphere_SAFEPos']
    objBase = bpy.data.objects['Sphere_BASEPos']
    SAFEPos_Angle = []
    # SafePos Angle auch in Abhaengigkeit von BasePos Orientierung exportieren/ speichern!
    SAFEPos_Angle = SAFEPos_Angle +[(objSafe.rotation_euler.x -objBase.rotation_euler.x) *360/(2*math.pi)]
    SAFEPos_Angle = SAFEPos_Angle +[(objSafe.rotation_euler.y -objBase.rotation_euler.y) *360/(2*math.pi)]
    SAFEPos_Angle = SAFEPos_Angle +[(objSafe.rotation_euler.z -objBase.rotation_euler.z) *360/(2*math.pi)]
    print('SAFEPos_Angle - ini: '+'A {0:.3f}'.format(SAFEPos_Angle[0])+' B {0:.3f}'.format(SAFEPos_Angle[1])+' C {0:.3f}'.format(SAFEPos_Angle[2]))
    
    objSafe.rotation_euler = (0,0,0) # um die richtigen Koordinaten zu bekommen
    
    print('SAFEPos_Koord: bevor Origin auf BasePos' +str(objSafe.data.vertices[0].co))
    
    # setzen des SafePos Origin auf  vertex[0] der BasePosition: 
    SetOrigin(objSafe, objBase)
    
    print('SAFEPos_Angle: '+'A {0:.3f}'.format(SAFEPos_Angle[0])+' B {0:.3f}'.format(SAFEPos_Angle[1])+' C {0:.3f}'.format(SAFEPos_Angle[2]))
    
    print('Umrechnung auf globale Koordinaten....')
    print('Transformation von SafePos auf BasePos...')
    vec = objSafe.data.vertices[0].co
    print('vec: ' +str(vec))
    eul = mathutils.Euler((objBase.rotation_euler.x, objBase.rotation_euler.y, objBase.rotation_euler.z), 'XYZ')
    print('eul: ' +str(eul))
    vec3d = vec.to_3d()
    mat_rot = eul.to_matrix()
    mat_loc = vec3d
    mat = mat_loc * mat_rot.to_3x3()
    print('mat: ' + str(mat))
    
    #Achtung: lokale Koordinaten (bezogen auf Base) wie in Datei gespeichert
    SAFEPos_Koord = mat
    print('SAFEPos_Koord = point_local: ' + str(SAFEPos_Koord))
    print('SAFEPos_Angle: '+'A {0:.3f}'.format(SAFEPos_Angle[0])+' B {0:.3f}'.format(SAFEPos_Angle[1])+' C {0:.3f}'.format(SAFEPos_Angle[2]))
    
    
    print('Safe-Origin auf Safe setzen ....')
    # setzen des SafePos Origin auf  vertex[0] der SafePosition:
    SetOrigin(objSafe, objSafe)
    
    print('SAFEPos_Angle: '+'A {0:.3f}'.format(SAFEPos_Angle[0])+' B {0:.3f}'.format(SAFEPos_Angle[1])+' C {0:.3f}'.format(SAFEPos_Angle[2]))
    
    print('SAFEPos_Angle wieder dem Origin zuweisen')
    objSafe.rotation_euler.x = SAFEPos_Angle[0] *(2*math.pi)/360 +objBase.rotation_euler.x # [rad]
    objSafe.rotation_euler.y = SAFEPos_Angle[1] *(2*math.pi)/360 +objBase.rotation_euler.y# [rad]
    objSafe.rotation_euler.z = SAFEPos_Angle[2] *(2*math.pi)/360 +objBase.rotation_euler.z # [rad]
    
    print('SAFEPos_Koord: ' + str(SAFEPos_Koord))
    print('SAFEPos_Angle: '+'A {0:.3f}'.format(SAFEPos_Angle[0])+' B {0:.3f}'.format(SAFEPos_Angle[1])+' C {0:.3f}'.format(SAFEPos_Angle[2]))
    
    print('Read from Scene - RfS_SafePos DONE')
    print('_____________________________________________________________________________')
    return SAFEPos_Koord, SAFEPos_Angle
'''    
    
def RfF_SafePos(filepath):
    print('_____________________________________________________________________________')
    print('Read from File - RfF_SafePos')
    # Achtung: Curve Object wird uebergeben aber nicht genutzt!
    # -> feste Zuweisung von Objekt 'Sphere_SAFEPos'
    
    #objSafe = bpy.data.objects['Sphere_SAFEPos']
    #bpy.ops.object.select_all(action='DESELECT')
    #bpy.data.objects[objSafe.name].select= True
    
    # ==========================================    
    # Import der SAFEPosition = KUKA (*.src)
    # ==========================================    
    try:
        
        FilenameSRC = filepath
        FilenameSRC = FilenameSRC.replace(".dat", ".src") 
        d = open(FilenameSRC)
        gesamtertext = d.read()
        d.close
        # Umwandeln in eine Liste
        zeilenliste =[]
        zeilenliste = gesamtertext.split(chr(10))
    
        # ==========================================
        # Suche nach "PTP"
        # ==========================================
        suchAnf = "PTP {X"
        suchEnd = "PTP {X"
        PATHPTSCountPTP = len(zeilenliste)
        PathIndexAnf = 0
        PathIndexEnd = PATHPTSCountPTP
        for i in range(PATHPTSCountPTP):
            if zeilenliste[i].find(suchAnf)!=-1: 
                PathIndexAnf = i
            if (zeilenliste[i].find(suchEnd)!=-1 and PathIndexAnf!=PathIndexEnd): 
                PathIndexEnd = i
                break
        PATHPTSCountPTP = PathIndexEnd - PathIndexAnf +1 # Achtung: hier wird 'ab der' Suchmarken ausgelesen
        
        # ==========================================
        # Einlesen der PTP Werte (X, Y, Z, A, B C) 
        # PTP {X 82.815240, Y 100.194500, Z -11.291560, A 69.842480, B -2.680786, C -3.097058}
        # ==========================================
        PTPX = []
        PTPY = []
        PTPZ = []
        PTPAngleA = []
        PTPAngleB = []
        PTPAngleC = []
        beg=0
        # die Schleife ist eigentlich unnoetig da es nur eine SAFEPosition gibt...
        for i in range(0,PATHPTSCountPTP,1):
            IndXA = zeilenliste[PathIndexAnf+i].index("X ", beg, len(zeilenliste[PathIndexAnf])) # Same as find(), but raises an exception if str not found 
            IndXE = zeilenliste[PathIndexAnf+i].index(", Y", beg, len(zeilenliste[PathIndexAnf]))
            PTPX = PTPX + [float(zeilenliste[PathIndexAnf+i][IndXA+2:IndXE])]
       
            IndYA = zeilenliste[PathIndexAnf+i].index("Y ", beg, len(zeilenliste[PathIndexAnf]))  
            IndYE = zeilenliste[PathIndexAnf+i].index(", Z", beg, len(zeilenliste[PathIndexAnf]))
            PTPY = PTPY + [float(zeilenliste[PathIndexAnf+i][IndYA+2:IndYE])]
       
            IndZA = zeilenliste[PathIndexAnf+i].index("Z ", beg, len(zeilenliste[PathIndexAnf])) 
            IndZE = zeilenliste[PathIndexAnf+i].index(", A", beg, len(zeilenliste[PathIndexAnf]))
            PTPZ = PTPZ + [float(zeilenliste[PathIndexAnf+i][IndZA+2:IndZE])]
       
            IndAA = zeilenliste[PathIndexAnf+i].index("A ", beg, len(zeilenliste[PathIndexAnf])) 
            IndAE = zeilenliste[PathIndexAnf+i].index(", B", beg, len(zeilenliste[PathIndexAnf]))
            PTPAngleA = PTPAngleA + [float(zeilenliste[PathIndexAnf+i][IndAA+2:IndAE])]
       
            IndBA = zeilenliste[PathIndexAnf+i].index("B ", beg, len(zeilenliste[PathIndexAnf]))  
            IndBE = zeilenliste[PathIndexAnf+i].index(", C", beg, len(zeilenliste[PathIndexAnf]))
            PTPAngleB = PTPAngleB + [float(zeilenliste[PathIndexAnf+i][IndBA+2:IndBE])]
       
            IndCA = zeilenliste[PathIndexAnf+i].index("C ", beg, len(zeilenliste[PathIndexAnf]))  
            IndCE = len(zeilenliste[PathIndexAnf+i])-2 # }   " "+chr(125) funktioniert nicht?!
            PTPAngleC = PTPAngleC + [float(zeilenliste[PathIndexAnf+i][IndCA+2:IndCE])]
        
        SkalierungPTP  = 1000
        SAFEPos_Koord  = Vector([float(PTPX[0])/SkalierungPTP, float(PTPY[0])/SkalierungPTP, float(PTPZ[0])/SkalierungPTP])
        print('SAFEPos_Koord' + str(SAFEPos_Koord))
        SAFEPos_Angle  = float(str(PTPAngleA[0])), float(str(PTPAngleB[0])), float(str(PTPAngleC[0])) # in Grad
        print('SAFEPos_Angle' + str(SAFEPos_Angle))
        print('RfF_SafePos - passed')
        return SAFEPos_Koord, SAFEPos_Angle
        
    except: 
        #  IOError, wenn file not found (laeuft (im debug mode?) nicht....
        # falls kein *.src vorhanden, setze die delta transform/ SAFEPosition auf Null:
        
        # POP UP Window:
        # todo: POP UP window ....
        #bpy.ops.object.dialog_operator('INVOKE_DEFAULT')
        print('RfF_SafePos - exeption - INVOKE_DEFAULT')
    print('Read from File - RfF_SafePos done')
    print('_____________________________________________________________________________')
    
def SetOrigin(sourceObj, targetObj):
    
    original_type = bpy.context.area.type
    bpy.context.area.type = "VIEW_3D" 
    
    # Sicherstellen das wir uns im Object Mode befinden:
    
    original_mode = bpy.context.mode
    if original_mode!= 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        
    
    # tdo: deselect läuft mit curve nicht... prüfen ob notwendig...
    # 
    
    
    bpy.ops.object.select_all(action='DESELECT')  
    # 2. setzen des sourceObj Origin auf  vertex[0] von targetObj:
    targetObj.select = True 
    bpy.context.scene.objects.active = targetObj
    targetObj.data.vertices[0].select= True
    # Achtung: Blender"Bug": Wechsel in Edit mode nachdem Vertex ausgewaehlt wurde!
    bpy.ops.object.mode_set(mode='EDIT', toggle=True)
    bpy.ops.view3d.snap_cursor_to_selected() 
    targetObj.data.vertices[0].select= False
    bpy.ops.object.mode_set(mode='EDIT', toggle=True)
    sourceObj.select = True 
    bpy.context.scene.objects.active = sourceObj
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    bpy.ops.object.select_all(action='DESELECT')
    
    bpy.context.area.type = original_type 
    print('Origin von '+ str(sourceObj.name) + ' auf vertex 0 von ' + str(targetObj.name) + ' gesetzt.')
    
    if original_mode!= 'OBJECT':
        bpy.ops.object.mode_set(mode='EDIT', toggle=True)
     
        
def SetObjRelToBase(Obj, Obj_Koord, Obj_Angle, BASEPos_Koord, BASEPos_Angle):
    # Diese Funktion wird nur bei Import aufgerufen.
    print('_____________________________________________________________________________')
    print('Funktion: SetObjRelToBase - lokale Koordinaten bezogen auf Base!')
    objBase = bpy.data.objects['Sphere_BASEPos']
    #Obj = bpy.data.objects['Sphere_SAFEPos']
    print('BASEPos_Koord: ' +str(BASEPos_Koord))
    print('BASEPos_Angle: ' +str(BASEPos_Angle))
    print('Obj_Koord: ' +str(Obj_Koord))
    print('Obj_Angle: ' +str(Obj_Angle))  
    print('')
    matrix_world = mathutils.Matrix.Translation(BASEPos_Koord)
    point_local  = Obj_Koord
    point_world  = matrix_world * point_local
    print(' Obj local bezogen auf Base: point_local ' +str(point_local))
    print(' Obj local bezogen auf World: point_world ' +str(point_world))
    print('')
    print('Transformation von Obj auf GlobalKoordinaten...')
    eul = mathutils.Euler((math.radians(BASEPos_Angle[0]), math.radians(BASEPos_Angle[1]), math.radians(BASEPos_Angle[2])), 'XYZ')
    print('eul: ' +str(eul))
    mat_rot = eul.to_matrix()
    mat_loc = point_local 
    mat = mat_rot * mat_loc 
    print('mat: ' +str(mat))
    
    print('Rotation von SafeKood bezogen auf BaseKoordinaten...')
    matrix_world = mathutils.Matrix.Translation(BASEPos_Koord)
    print('matrix_world: ' +str(matrix_world))
    point_local  = mat
    point_world  = matrix_world * point_local
    print('point_world2: ' +str(point_world))
    
    print('BASEPos_Koord: ' +str(BASEPos_Koord))
    print('BASEPos_Angle: ' +str(BASEPos_Angle))
    print('Obj_Koord: ' +str(Obj_Koord))
    print('Obj_Angle: ' +str(Obj_Angle)) 
    
    SetOrigin(Obj, Obj)
    
    Obj.location = point_world
    print('Safe-Origin  = Obj auf point_world  gesetzt.')
    #-----------------------------------
    # todo: Info - aktuell treten im Debug Mode Fehler auf falsche/ ueberfluessige Funktionsaufrufe....
    
    print('Obj_Angle wieder dem Origin zuweisen unter Beruecksichtigung der BaseOrientierung:')
    
    Obj.rotation_euler.x = (BASEPos_Angle[0] +Obj_Angle[0]) *(2*math.pi)/360 # [rad]
    Obj.rotation_euler.y = (BASEPos_Angle[1] +Obj_Angle[1]) *(2*math.pi)/360 # [rad]
    Obj.rotation_euler.z = (BASEPos_Angle[2] +Obj_Angle[2]) *(2*math.pi)/360 # [rad]
        
    print('BASEPos_Koord: ' +str(BASEPos_Koord))
    print('BASEPos_Angle: ' +str(BASEPos_Angle))
    print('Obj_Koord: ' +str(Obj_Koord))    
    print('Obj_Angle: ' +str(Obj_Angle)) 
    
    print('SetObjRelToBase done')
    print('_____________________________________________________________________________')
    return 
    
def RfF_PATHPTS_LocRot(objCurve, filepath):     
    print('_____________________________________________________________________________')
    print('RfF_PATHPTS_LocRot')
    #todo: Abfragen ob selektiertes Obj. auch wirklich curve ist (und nur ein Obj. selectiert ist)
    #bpy.data.curves[DataName].splines[0].bezier_points[0].co=(0,1,1)
    SkalierungPTP  = 1000
    # Zugriffsversuch
    #try:
    d = open(filepath)
    #d = open("E84_BFS_Sport_Sitz_1032_10_08_BT.dat")  
        #d = open("KUKA-TEST.dat")  
    #except:
    #    print("Dateizugriff nicht erfolgreich")
    #    sys.exit(0) # Achtung: wenn de Datei nicht gefunden wurde fuehrt dies zum Blender Absturz mit Fehler "blender not freed memory blocks"
    
    # lesen der gesamten Textdatei (*.dat)
    gesamtertext = d.read()
    # schliessen der Datei
    d.close
    # Umwandeln in eine Liste
    zeilenliste = gesamtertext.split(chr(10))

    # ==========================================
    # Suche nach "FOLD PATH DATA" und "ENDFOLD"
    # ==========================================
    suchAnf = "FOLD PATH DATA"
    suchEnd = "ENDFOLD"
    PATHPTSCount = len(zeilenliste)
    PathIndexAnf = 0
    PathIndexEnd = PATHPTSCount
    for i in range(PATHPTSCount):
        if zeilenliste[i].find(suchAnf)!=-1: 
            PathIndexAnf = i
        if (zeilenliste[i].find(suchEnd)!=-1 and PathIndexAnf!=PATHPTSCount): 
            PathIndexEnd = i
            break
    print("...")
    PATHPTSCount = PathIndexEnd - (PathIndexAnf+1) # Achtung: hier wird 'zwischen' den Suchmarken ausgelesen
    
    # ==========================================
    # Einlesen der PATHPTS Werte (X, Y, Z, A, B C) 
    # PATHPTS[1]={X 105.1887, Y 125.6457, Z -123.9032, A 68.49588, B -26.74377, C 1.254162 }
    # ==========================================
    PathPointX = []
    PathPointY = []
    PathPointZ = []
    PathAngleA = []
    PathAngleB = []
    PathAngleC = []
    beg=0
   
    for i in range(0,PATHPTSCount,1):
        IndXA = zeilenliste[PathIndexAnf+1+i].index("X ", beg, len(zeilenliste[PathIndexAnf+1])) # Same as find(), but raises an exception if str not found 
        IndXE = zeilenliste[PathIndexAnf+1+i].index(", Y", beg, len(zeilenliste[PathIndexAnf+1]))
        PathPointX = PathPointX + [float(zeilenliste[PathIndexAnf+1+i][IndXA+2:IndXE])/SkalierungPTP]
   
        IndYA = zeilenliste[PathIndexAnf+1+i].index("Y ", beg, len(zeilenliste[PathIndexAnf+1]))  
        IndYE = zeilenliste[PathIndexAnf+1+i].index(", Z", beg, len(zeilenliste[PathIndexAnf+1]))
        PathPointY = PathPointY + [float(zeilenliste[PathIndexAnf+1+i][IndYA+2:IndYE])/SkalierungPTP]
   
        IndZA = zeilenliste[PathIndexAnf+1+i].index("Z ", beg, len(zeilenliste[PathIndexAnf+1])) 
        IndZE = zeilenliste[PathIndexAnf+1+i].index(", A", beg, len(zeilenliste[PathIndexAnf+1]))
        PathPointZ = PathPointZ + [float(zeilenliste[PathIndexAnf+1+i][IndZA+2:IndZE])/SkalierungPTP]
   
        IndAA = zeilenliste[PathIndexAnf+1+i].index("A ", beg, len(zeilenliste[PathIndexAnf+1])) 
        IndAE = zeilenliste[PathIndexAnf+1+i].index(", B", beg, len(zeilenliste[PathIndexAnf+1]))
        PathAngleA = PathAngleA + [float(zeilenliste[PathIndexAnf+1+i][IndAA+2:IndAE])]
   
        IndBA = zeilenliste[PathIndexAnf+1+i].index("B ", beg, len(zeilenliste[PathIndexAnf+1]))  
        IndBE = zeilenliste[PathIndexAnf+1+i].index(", C", beg, len(zeilenliste[PathIndexAnf+1]))
        PathAngleB = PathAngleB + [float(zeilenliste[PathIndexAnf+1+i][IndBA+2:IndBE])]
   
        IndCA = zeilenliste[PathIndexAnf+1+i].index("C ", beg, len(zeilenliste[PathIndexAnf+1]))  
        IndCE = len(zeilenliste[PathIndexAnf+1+i])-2 # }   " "+chr(125) funktioniert nicht?!
        PathAngleC = PathAngleC + [float(zeilenliste[PathIndexAnf+1+i][IndCA+2:IndCE]) ] # in Grad

    print('RfF_PATHPTS_LocRot - Pathpositions und Angles initialisiert')
    # ==========================================    
    # Erstellen der Datenkontainer fuer location und rotation
    # ==========================================    
    
    mList= createMatrix(PATHPTSCount,1) # eigene Class "createMatrix" erstellt
    dataPATHPTS_Loc = []
    for i in range(0,PATHPTSCount,1):
        mList[i][0:3] = [PathPointX[i], PathPointY[i], PathPointZ[i]]
        dataPATHPTS_Loc = dataPATHPTS_Loc + [mList[i]] 
     
    mList= createMatrix(PATHPTSCount,1)  
    dataPATHPTS_Rot =[]
    for i in range(0,PATHPTSCount,1):
        mList[i][0:3] = [PathAngleA[i], PathAngleB[i], PathAngleC[i]]
        dataPATHPTS_Rot = dataPATHPTS_Rot + [mList[i]]

    # ToDo: !!!!
    # Curve Type auf Bezier umstellen und A, B, C Winkel einlesen, 
    
    print('RfF_PATHPTS_LocRot - Curve data - splines ersetzt')
    print('_____________________________________________________________________________')
    return dataPATHPTS_Loc, dataPATHPTS_Rot, PATHPTSCount


   
    # ==========================================    
    # Suche nach "FOLD LOAD DATA" und "ENDFOLD"
    # Einlesen der LOADPTS Werte ()
    # LOADPTS[1]={FX NAN, FY NAN, FZ NAN, TX NAN, TY NAN, TZ NAN }
    # ==========================================
    
    # ==========================================
    # Suche nach "FOLD TIME DATA" und "ENDFOLD"
    # Einlesen der TIMEPTS Werte ()
    # TIMEPTS[1]=0.2
    # ==========================================
    
    # ==========================================
    # Suche nach "FOLD STOP DATA" und "ENDFOLD"
    # Einlesen der STOPPTS Werte ()
    # STOPPTS[1]=1
    # ==========================================
    
    # ==========================================    
    # Suche nach "FOLD ACTION DATA" und "ENDFOLD"
    # Einlesen der ACTIONMSK Werte )
    # ACTIONMSK[1]=0
    # ==========================================

    
class CurveExport (bpy.types.Operator, ExportHelper):
    print('CurveExport - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ') 
    print('- - - - - - - - - - - - -  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')
    #bpy.ops.curve.curveexport(
                              
    # Export selected curve of the mesh
    bl_idname = "curve.curveexport"
    bl_label = "CurveExport (TB)" #Toolbar - Label
    bl_description = "Export selected Curve1" # Kommentar im Specials Kontextmenue
    bl_options = {'REGISTER', 'UNDO'} #Set this options, if you want to update  
    #                                  parameters of this operator interactively 
    #                                  (in the Tools pane) 
    
    # ExportHelper mixin class uses this
    filename_ext = ".dat"

    filter_glob = StringProperty(
            default="*.dat",
            options={'HIDDEN'},
            )

    def execute(self, context):
        
        print('FUNKTIONSAUFRUF - CurveExport')
        objBase = bpy.data.objects['Sphere_BASEPos']
        objSafe = bpy.data.objects['Sphere_SAFEPos']
        objCurve = bpy.data.objects['BezierCircle']
        objEmpty_A6 = bpy.data.objects['Empty_Zentralhand_A6']
        PATHPTSObjName = 'PTPObj_'
        filename = os.path.basename(self.filepath)
        #realpath = os.path.realpath(os.path.expanduser(self.filepath))
        #fp = open(realpath, 'w')
        ObjName = filename
            
        # Wichtig: Vor dem Export muss die Lokale-Skalierung erst mit der Global-Skalierung in uebereinstimmung gebracht werden.
        # Entspricht [STRG] + A (Apply Scale)
        # um nicht auch das Tool selber zu beeinflussen muss das parenting dafuer geloest werden. (--> def ApplyScale)
        
        # nur fuer Scaling, da Location, Rotatation (mit Hilfe des Mesh-Objektes 'Sphere_BASEPos') beim Export in *.src file geschrieben wird:
        # --> [STRG] + A (Apply Location, Rotation) wird nicht normiert sondern wieder eingelesen! (KUKA BASEPosition)
        print('- - - - - - - - - - - - -  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')
        print(' FUNKTIONSAUFRUF CurveExport KUKA_Tools')
        print('- - - - - - - - - - - - -  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')
        ClearParenting() # hier wird das Parenting geloest!
        
        ApplyScale(context.object) 
        #--------------------------------------------------------------------------------
        
        BASEPos_Koord, BASEPos_Angle = RfS_BasePos(context.object, self.filepath)
        print('_________________CurveExport - BASEPos_Koord' + str(BASEPos_Koord))
        print('_________________CurveExport - BASEPos_Angle' +'A {0:.3f}'.format(BASEPos_Angle[0])+' B {0:.3f}'.format(BASEPos_Angle[1])+' C {0:.3f}'.format(BASEPos_Angle[2]))
        
        #SAFEPos_Koord, SAFEPos_Angle = RfS_SafePos()
        SAFEPos_Koord, SAFEPos_Angle = RfS_LocRot(objSafe, objSafe.location, objSafe.rotation_euler, BASEPos_Koord, BASEPos_Angle)
        
        print('_________________CurveExport - BASEPos_Koord' + str(BASEPos_Koord))
        print('_________________CurveExport - BASEPos_Angle' +'A {0:.3f}'.format(BASEPos_Angle[0])+' B {0:.3f}'.format(BASEPos_Angle[1])+' C {0:.3f}'.format(BASEPos_Angle[2]))
        print('_________________SAFEPos_Koord: ' + str(SAFEPos_Koord))
        print('_________________SAFEPos_Angle' +'A {0:.3f}'.format(SAFEPos_Angle[0])+' B {0:.3f}'.format(SAFEPos_Angle[1])+' C {0:.3f}'.format(SAFEPos_Angle[2]))
        
    
        #todo: RfS_CurveData.....
        #dataPATHPTS_Loc, dataPATHPTS_Rot, PATHPTSCountFile = RfS_LocRot()
        #WtF_CurveData(context.object, self.filepath, dataPATHPTS_Loc, dataPATHPTS_Rot, BASEPos_Koord, BASEPos_Angle)
        WtF_CurveData(context.object, PATHPTSObjName, self.filepath, BASEPos_Koord, BASEPos_Angle)
        
        
        print('_________________CurveExport - BASEPos_Koord' + str(BASEPos_Koord))
        print('_________________CurveExport - BASEPos_Angle' +'A {0:.3f}'.format(BASEPos_Angle[0])+' B {0:.3f}'.format(BASEPos_Angle[1])+' C {0:.3f}'.format(BASEPos_Angle[2]))
        print('_________________SAFEPos_Koord: ' + str(SAFEPos_Koord))
        print('_________________SAFEPos_Angle' +'A {0:.3f}'.format(SAFEPos_Angle[0])+' B {0:.3f}'.format(SAFEPos_Angle[1])+' C {0:.3f}'.format(SAFEPos_Angle[2]))
        BasePos2File(BASEPos_Koord, BASEPos_Angle, self.filepath)
        print('_________________CurveExport - BASEPos_Koord' + str(BASEPos_Koord))
        print('_________________CurveExport - BASEPos_Angle' +'A {0:.3f}'.format(BASEPos_Angle[0])+' B {0:.3f}'.format(BASEPos_Angle[1])+' C {0:.3f}'.format(BASEPos_Angle[2]))
        print('_________________SAFEPos_Koord: ' + str(SAFEPos_Koord))
        print('_________________SAFEPos_Angle' +'A {0:.3f}'.format(SAFEPos_Angle[0])+' B {0:.3f}'.format(SAFEPos_Angle[1])+' C {0:.3f}'.format(SAFEPos_Angle[2]))
        SafePos2File(SAFEPos_Koord, SAFEPos_Angle, self.filepath)
        print('_________________CurveExport - BASEPos_Koord' + str(BASEPos_Koord))
        print('_________________CurveExport - BASEPos_Angle' +'A {0:.3f}'.format(BASEPos_Angle[0])+' B {0:.3f}'.format(BASEPos_Angle[1])+' C {0:.3f}'.format(BASEPos_Angle[2]))
        print('_________________SAFEPos_Koord: ' + str(SAFEPos_Koord))
        print('_________________SAFEPos_Angle' +'A {0:.3f}'.format(SAFEPos_Angle[0])+' B {0:.3f}'.format(SAFEPos_Angle[1])+' C {0:.3f}'.format(SAFEPos_Angle[2]))
        #--------------------------------------------------------------------------------
        # Achtung: SetKukaToCurve funktioniert nur richtig, wenn das Parenting vorher geloest wurde!
        SetKukaToCurve(context.object)
        SetParenting() # hier wird ein Parenting hergestellt!
        # 2ter Aufruf notwendig, (wegen Kopie der Koordinaten vom parent to child objekt):
        SetKukaToCurve(context.object) 
        
        return {'FINISHED'}
    print('CurveExport done')  

class CurveImport (bpy.types.Operator, ImportHelper):
    print('CurveImport- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ') 
    print('- - - - - - - - - - - - -  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')
    ''' Import selected curve '''
    bl_idname = "curve.curveimport"
    bl_label = "CurveImport (TB)" #Toolbar - Label
    bl_description = "Import selected Curve2" # Kommentar im Specials Kontextmenue
    bl_options = {'REGISTER', 'UNDO'} #Set this options, if you want to update  
    #                                  parameters of this operator interactively 
    #                                  (in the Tools pane) 

    # ImportHelper mixin class uses this
    filename_ext = ".dat"

    filter_glob = StringProperty(
            default="*.dat",
            options={'HIDDEN'},
            )
 
    def execute(self, context):  
        print('- - - - - - - - - - - - -  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')
        print(' FUNKTIONSAUFRUF CurveImport')
        print('- - - - - - - - - - - - -  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')
        objBase = bpy.data.objects['Sphere_BASEPos']
        objSafe = bpy.data.objects['Sphere_SAFEPos']
        objCurve = bpy.data.objects['BezierCircle']
        #objCurve = bpy.data.curves[bpy.context.active_object.data.name]
        objEmpty_A6 = bpy.data.objects['Empty_Zentralhand_A6']      
        PATHPTSObjName = 'PTPObj_'
    
        filename = os.path.basename(self.filepath)
        #realpath = os.path.realpath(os.path.expanduser(self.filepath))
        #fp = open(realpath, 'w')
        ObjName = filename
        
        ClearParenting()
        ApplyScale(context.object)
        #--------------------------------------------------------------------------------
        
        
              
        print("Erstellen der BezierCurve: done")
        BASEPos_Koord, BASEPos_Angle = RfF_BasePos(self.filepath)
        print('_________________CurveImport - BASEPos_Koord' + str(BASEPos_Koord))
        print('_________________CurveImport - BASEPos_Angle' +'A {0:.3f}'.format(BASEPos_Angle[0])+' B {0:.3f}'.format(BASEPos_Angle[1])+' C {0:.3f}'.format(BASEPos_Angle[2]))
        
        # create Container (Location, Rotation) for each path point (PTP): dataPATHPTS_Loc, dataPATHPTS_Rot
        dataPATHPTS_Loc, dataPATHPTS_Rot, PATHPTSCountFile = RfF_PATHPTS_LocRot(context.object, self.filepath) 
        
        
        SetBasePos(context.object, objBase, BASEPos_Koord, BASEPos_Angle)
        # todo: testen!!!!
        create_PATHPTSObj(dataPATHPTS_Loc, dataPATHPTS_Rot, PATHPTSCountFile, BASEPos_Koord, BASEPos_Angle)
        
        bezierCurve = bpy.data.curves[objCurve.name] #bpy.context.active_object #.data.name
        #replace_CP(bezierCurve, PATHPTSObjName, dataPATHPTS_Loc, PATHPTSCountFile, BASEPos_Koord, BASEPos_Angle) 
        
        # todo:
        #- Winkel der PATHPTS werden falsch exportiert
        #- Ungenaugkeiten/ rundungsfehler beim Import der Splinepoints NICHT ABER bei der PATHPTS Objekten???
        
        # Achtung: die Reihenfolge fon SetCurvePos und SetBasePos muss eingehalten werden! 
        # (da sonst die Curve nicht mit der Base mit verschoben wird!
        #SetCurvePos(context.object, objBase, BASEPos_Koord, BASEPos_Angle)
        
        
        print('_________________CurveImport - BASEPos_Koord' + str(BASEPos_Koord))
        print('_________________CurveImport - BASEPos_Angle' + str(BASEPos_Angle))
        SAFEPos_Koord, SAFEPos_Angle = RfF_SafePos(self.filepath)
        print('_________________CurveImport - BASEPos_Koord' + str(BASEPos_Koord))
        print('_________________CurveImport - BASEPos_Angle' +'A {0:.3f}'.format(BASEPos_Angle[0])+' B {0:.3f}'.format(BASEPos_Angle[1])+' C {0:.3f}'.format(BASEPos_Angle[2]))
        print('_________________SAFEPos_Koord: ' + str(SAFEPos_Koord))
        print('_________________SAFEPos_Angle' +'A {0:.3f}'.format(SAFEPos_Angle[0])+' B {0:.3f}'.format(SAFEPos_Angle[1])+' C {0:.3f}'.format(SAFEPos_Angle[2]))
        # Achtung: Die Reihenfolge der Aufrufe von SetBasePos und SetObjRelToBase darf nicht vertauscht werden!
        SetObjRelToBase(objSafe, SAFEPos_Koord, SAFEPos_Angle, BASEPos_Koord, BASEPos_Angle )        
        print('_________________CurveImport - BASEPos_Koord' + str(BASEPos_Koord))
        print('_________________CurveImport - BASEPos_Angle' +'A {0:.3f}'.format(BASEPos_Angle[0])+' B {0:.3f}'.format(BASEPos_Angle[1])+' C {0:.3f}'.format(BASEPos_Angle[2]))
        print('_________________SAFEPos_Koord: ' + str(SAFEPos_Koord))
        print('_________________SAFEPos_Angle' +'A {0:.3f}'.format(SAFEPos_Angle[0])+' B {0:.3f}'.format(SAFEPos_Angle[1])+' C {0:.3f}'.format(SAFEPos_Angle[2]))
        
        #--------------------------------------------------------------------------------
        
        # Kuka mit neuer Kurve verknuepfen:
        # der folgende Befehl muss nach dem Parenting nochmal
        # ausgefuehrt werden um die Verschiebung es Empty wieder aufzuheben!
        # Achtung: SetKukaToCurve funktioniert nur richtig, wenn das Parenting vorher geloest wurde!
        SetKukaToCurve(context.object)
        SetParenting() # hier wird ein Parenting hergestellt!
        # 2ter Aufruf notwendig, (wegen Kopie der Koordinaten vom parent to child objekt):
        SetKukaToCurve(context.object) 
        
        return {'FINISHED'} 
    print('CurveImport done')

'''   
class kuka(bpy.types.Operator):
    bl_idname = "curve.kuka_pathpts"
    bl_label = "lalala-label" #Toolbar - Label
    #bl_description = "Import selected Curve2"
    bl_options = {'REGISTER', 'UNDO'}
    
    
    bpy.ops.curve.kuka_pathpts.x = bpy.props.FloatProperty(name="Test Prob")
                                                 
                               
    def beschleunigen(self, wert):
        self.geschwindigkeit += wert
        
'''
               
class KUKAPanel(bpy.types.Panel):
    print('_____________________________________________________________________________')
    print()
    print('KUKAPanel....')
    print()
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "KUKA Panel" # heading of panel
    #bl_idname = "SCENE_PT_layout"
    bl_idname = "OBJECT_PT_layout"
    
    # bpy.ops.OBJECT_PT_layout.module....
    
    bl_space_type = 'PROPERTIES' # window type panel is displayed in
    bl_region_type = 'WINDOW' # region of window panel is displayed in
    bl_context = "object"
    #bl_context = "scene"
    
    # check poll() to avoid exception.
    '''
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='EDIT')
    '''
    
    @classmethod
    def poll(cls, context):
        return (bpy.context.active_object.type == 'CURVE') # Test, ob auch wirklich ein 'CURVE' Objekt aktiv ist.

    
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
        
        # Import/ Export Button:
        layout.label(text="Curvepath Import/ Export:")
        row = layout.row(align=True)        
        sub = row.row()
        sub.scale_x = 1.0
        sub.operator("curve.curveimport")
        row.operator("curve.curveexport")      
    print('KUKAPanel done')
    print('_____________________________________________________________________________')

#### Curve creation functions
# ________________________________________________________________________________________________________________________
# Bezier
# ________________________________________________________________________________________________________________________

def replace_CP(bezierCurve, PATHPTSObjName, dataPATHPTS_Loc, PATHPTSCountFile, BASEPos_Koord, BASEPos_Angle):
    print('_____________________________________________________________________________')
    print('replace_CP')
    #bpy.data.curves[bpy.context.active_object.data.name].user_clear()
    #bpy.data.curves.remove(bpy.data.curves[bpy.context.active_object.data.name])
    
    countPATHPTSObj, PATHPTSObjList = count_PATHPTSObj(PATHPTSObjName)
    
    bpy.ops.object.mode_set(mode='EDIT', toggle=False) # switch to edit mode
    
    bezierCurve.dimensions = '3D'
    #bzs = bpy.data.curves[bpy.context.active_object.data.name].splines[0].bezier_points
    bzs = bezierCurve.splines[0].bezier_points
    PATHPTSCount = len(bzs)
    
    # sicherstellen das kein ControlPoint selektiert ist:
    for n in range(PATHPTSCount):
        bezierCurve.splines[0].bezier_points[n].select_control_point= False
        bezierCurve.splines[0].bezier_points[n].select_right_handle = False
        bezierCurve.splines[0].bezier_points[n].select_left_handle = False             
    CountCP = 0
    
    if PATHPTSCountFile <= PATHPTSCount:
        CountCP = PATHPTSCount
    if PATHPTSCountFile > PATHPTSCount:
        CountCP = PATHPTSCountFile
    
    # kuerze die Laenge der aktuellen Kurve auf die File-Kurve, wenn noetig
    if PATHPTSCountFile < PATHPTSCount:
        delList =[]
        zuViel = PATHPTSCount - PATHPTSCountFile
        delList = [PATHPTSCountFile]*(PATHPTSCountFile+zuViel)
        
        for n in range(PATHPTSCountFile, PATHPTSCountFile+zuViel, 1):      
            bezierCurve.splines[0].bezier_points[delList[n]].select_control_point=True
            bezierCurve.splines[0].bezier_points[delList[n]].select_right_handle = True
            bezierCurve.splines[0].bezier_points[delList[n]].select_left_handle = True
            #bpy.ops.curve.delete(type='SELECTED') # erzeugte Fehler bei Wechsel von Version 2.68-2 auf 2.69
            bpy.ops.curve.delete()
        CountCP = len(bzs)
    
    for n in range(CountCP):
        if (PATHPTSCount-1) >= n: # Wenn ein Datenpunkt auf der vorhandenen Kurve da ist,
            # Waehle einen Punkt auf der vorhandenen Kurve aus:
            bezierCurve.splines[0].bezier_points[n].select_control_point = True
            print(bezierCurve.splines[0].bezier_points[n])
            print('Select control point:' + str(bezierCurve.splines[0].bezier_points[n].select_control_point))
            
            bezierCurve.splines[0].bezier_points[n].handle_left_type='VECTOR'
            print(bezierCurve.splines[0].bezier_points[n].handle_left_type)
            
            bezierCurve.splines[0].bezier_points[n].handle_right_type='VECTOR'
            print(bezierCurve.splines[0].bezier_points[n].handle_right_type)
            
            NewLocRot =[]
            
            
            if (PATHPTSCountFile-1) >= n: # Wenn ein Datenpunkt im File da ist, nehm ihn und ersetzte damit den aktellen Punkt
                print()
                
                NewLocRot = NewLocRot + [RfS_LocRot(bpy.data.objects[PATHPTSObjList[n-1]], bpy.data.objects[PATHPTSObjList[n-1]].location, bpy.data.objects[PATHPTSObjList[n-1]].rotation_euler, BASEPos_Koord, BASEPos_Angle)]
                NewLocRot = NewLocRot + [RfS_LocRot(bpy.data.objects[PATHPTSObjList[n]], bpy.data.objects[PATHPTSObjList[n]].location, bpy.data.objects[PATHPTSObjList[n]].rotation_euler, BASEPos_Koord, BASEPos_Angle)]
                NewLocRot = NewLocRot + [RfS_LocRot(bpy.data.objects[PATHPTSObjList[n-PATHPTSCountFile+1]], bpy.data.objects[PATHPTSObjList[n-PATHPTSCountFile+1]].location, bpy.data.objects[PATHPTSObjList[n-PATHPTSCountFile+1]].rotation_euler, BASEPos_Koord, BASEPos_Angle)]
                #bzs[n] führte zu Fehlermeldung ???:
                bezierCurve.splines[0].bezier_points[n].handle_left = NewLocRot[0][0]
                bezierCurve.splines[0].bezier_points[n].co = NewLocRot[1][0]
                bezierCurve.splines[0].bezier_points[n].handle_right = NewLocRot[2][0]
                
                bezierCurve.splines[0].bezier_points[n].select_control_point = False  
                
        else: # wenn kein Kurvenpunkt zum ueberschreiben da ist, generiere einen neuen und schreibe den File-Datenpunkt
            bzs.add(1) #spline.bezier_points.add(1)
            
            #todo: Daten sollten eigentlich von dataPATHPTS_Loc verwendet werden:
            NewLocRot = NewLocRot + [RfS_LocRot(bpy.data.objects[PATHPTSObjList[n-1]], bpy.data.objects[PATHPTSObjList[n-1]].location, bpy.data.objects[PATHPTSObjList[n-1]].rotation_euler, BASEPos_Koord, BASEPos_Angle)]
            NewLocRot = NewLocRot + [RfS_LocRot(bpy.data.objects[PATHPTSObjList[n]], bpy.data.objects[PATHPTSObjList[n]].location, bpy.data.objects[PATHPTSObjList[n]].rotation_euler, BASEPos_Koord, BASEPos_Angle)]
            NewLocRot = NewLocRot + [RfS_LocRot(bpy.data.objects[PATHPTSObjList[n-PATHPTSCountFile+1]], bpy.data.objects[PATHPTSObjList[n-PATHPTSCountFile+1]].location, bpy.data.objects[PATHPTSObjList[n-PATHPTSCountFile+1]].rotation_euler, BASEPos_Koord, BASEPos_Angle)]
            
            bezierCurve.splines[0].bezier_points[n].handle_left = NewLocRot[0][0]
            bezierCurve.splines[0].bezier_points[n].co = NewLocRot[1][0]
            bezierCurve.splines[0].bezier_points[n].handle_right = NewLocRot[2][0]
            
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
    

def count_PATHPTSObj(PATHPTSObjName):
    print('_____________________________________________________________________________')
    print('count_PATHPTSObj')
    countPATHPTSObj = 0
    countObj = 0
    PATHPTSObjList=[]
    #PATHPTSObjName = 'PTPObj_'
    for item in bpy.data.objects:
        if item.type == "MESH":
            countObj = countObj +1
            print(item.name)  
            if PATHPTSObjName in item.name:
                countPATHPTSObj = countPATHPTSObj +1
                PATHPTSObjList = PATHPTSObjList + [item.name]
    print('Anzahl an Objekten in der Szene - countObj: ' +str(countObj))
    print('Anzahl an PathPoint Objekten in der Szene - countPATHPTSObj: ' +str(countPATHPTSObj))
    print('count_PATHPTSObj')
    print('_____________________________________________________________________________')
    return countPATHPTSObj, PATHPTSObjList,
    
    
def create_PATHPTSObj(dataPATHPTS_Loc, dataPATHPTS_Rot, PATHPTSCountFile, BASEPos_Koord, BASEPos_Angle ):
    # Aufruf von: CurveImport
    # TESTEN !!!!!!!!!!!!!!!!!! -> OK,...
    original_type = bpy.context.area.type
    bpy.context.area.type = "VIEW_3D" 
    bpy.ops.object.select_all(action='DESELECT')
    print('_____________________________________________________________________________')
    print('create_PATHPTSObj')
    # erstellen von 'PATHPTSCountFile' Mesh Objekten an den Positionen 'dataPATHPTS_Loc' mit der Ausrichtung 'dataPATHPTS_Rot'
    PATHPTSObjName = 'PTPObj_'
    # 1. Wieviele PTPObj Objekte sind in der Scene vorhanden? (Beachte: Viele Objekte koennen den selben Datencontainer verwenden)
    countPATHPTSObj, PATHPTSObjList = count_PATHPTSObj(PATHPTSObjName)
    print('Es sind ' + str(countPATHPTSObj) + 'PATHPTSObj in der Szene vorhanden.' )
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
        countPATHPTSObj, PATHPTSObjList = count_PATHPTSObj(PATHPTSObjName)
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
                
                SetObjRelToBase(bpy.data.objects[PATHPTSObjList[n]], Vector(dataPATHPTS_Loc[n]), dataPATHPTS_Rot[n], BASEPos_Koord, BASEPos_Angle)
                      
        else: # wenn kein Kurvenpunkt zum ueberschreiben da ist, generiere einen neuen und schreibe den File-Datenpunkt
            print('Kein weiteres PATHPTS Objekt mehr in der Szene vorhanden.')
            print('Erstelle neues PATHPTS Objekt.')
            
            # add an new MESH object
            print('bpy.context.area.type: ' + bpy.context.area.type)
            bpy.ops.object.add(type='MESH')  
            bpy.context.object.name = PATHPTSObjName + str(n+1) 
            countPATHPTSObj, PATHPTSObjList = count_PATHPTSObj(PATHPTSObjName)
            bpy.data.objects[PATHPTSObjList[n]].data = bpy.data.objects[PATHPTSObjList[1]].data
            print('IF - uebertrage loc: ' + str(dataPATHPTS_Loc[n]) 
                      + ' und rot Daten:' + str(dataPATHPTS_Rot[n]) 
                      + ' vom File auf Objekt:' + str(PATHPTSObjList[n]))
            
            SetObjRelToBase(bpy.data.objects[PATHPTSObjList[n]], Vector(dataPATHPTS_Loc[n]), dataPATHPTS_Rot[n], BASEPos_Koord, BASEPos_Angle)
                
    bpy.context.area.type = original_type 
    print('create_PATHPTSObj done')
    print('_____________________________________________________________________________')


# ________________________________________________________________________________________________________________________


#--- ### Register
#ToDo: KUKA Operator nicht regestriert....
def register():
    bpy.utils.register_class(KUKAPanel)  
    register_module(__name__)
    
def unregister():
    bpy.utils.unregister_class(KUKAPanel)
    unregister_module(__name__)

#--- ### Main code    
if __name__ == '__main__':
    register()
