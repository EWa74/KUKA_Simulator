#  ***** BEGIN GPL LICENSE BLOCK *****
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  ***** END GPL LICENSE BLOCK *****
# Version: 100R
# Next steps:
# Abgleich mit KUKA und Definition der daraus folgenden GUI Panels
# code optimization: less parenting, more fcurve controlled objekts/bones
# naming convention
# gui panel (add/remove pathpoints, timepts
#
from symbol import except_clause

# todo: geladenes File anzeigen
#git
# V-REP -> Roboter Simulation
# todo: RefreshFunktion (wenn Boje oder Kurve +/- Punkte bekommt. Button Boje +/-; done, aber: inset keyframe fehlt noch
# Listenfeld dazu verwenden um Obj +/-
# TIMEPTS einlesen und I-Keys setzen -> Empty: follow path entfaellt dann: done
# bpy.data.window_managers["WinMan"] ... propvalue
# bpy.app.handlers.frame_change_pre.append(bpy.ops.curve.cureexport('BezierCurve'))
# Window.GetScreenInfo(Window.Types.VIEW3D)
#  
# Beachte: x=(1,2,3) ist TUPEL, d.h. nicht veraenderbar; x = [1,2,3] ist Listse (veraenderbar)
# bpy.data.curves[bpy.context.active_object.data.name].splines[0].bezier_points[0].co.angle(bpy.data.curves[bpy.context.active_object.data.name].splines[0].bezier_points[1].co)
    
# ARMATURE: Position und Winkel auf Plausibilitaet abfragen: bone constraints eingestellt; werden diese ueberschritten "springt" der Arm
# bpy.data.objects['OBJ_KUKA_Armature'].pose.bones['Bone_KUKA_Zentralhand_A4'].rotation_euler 

# handling vom POP UP window: alternativ *.src laden ODER default TP auswaehlen --> Panel(bpy_struct)
# button um nach editieren der Kurve das Kuka_Empty auf den ersten Kurvenpunkt zu setzen

# Phyton code aufraeumen
# Doku update
# Info: 
# 0. SAFE POSITION: muss immer von Hand im Menue angegeben werden. auch BASEPosition!
# 1. Kuka startet von HOMEPOSITION und faehrt zur BASEPosition
# 2. Kuka faehrt von der BASEPosition zum ersten Kurvenpunkt
# 3. Die Kurvenpunkte werden abgearbeitet 
# 4. Kuka faehrt zur SAFEPosition 
# 5. Keine Wiederholung: fahre zur HOMEPOSITION
# 6. Wiederholung: Wiederhole Punkte 2, 3, 4
 
# ToDo: ToolPosition (oder Baseposition) auslesen und offset beruecksichtigen MES ={ :  enthalten in *.dat -> OBJ_KUKA_EndEffector zuweisen
# BasePosition: (noch kein korrespondierender KUKA File bekannt !!! -> ALe
# todo: globale variablen definieren??.....
# todo: Verschiedene Import/ Export Funktionen beruecksichtigen (XYZ/ KUKA YXZ)
# todo: [done] obj. rename um 001.001 etc. zu vermeiden!!!
# Datenmodell und Funktionen beschreiben!!!

# TODO: pruefen ob TIMEPTS = PATHPTS ist und ggf. neue keyframes und TIMEPTS setzen -> Funktion RefreshButton
# TODO: Beschriftung der PATHPTS im 3D view
# TODO: GUI Feld um die Winkel bezogen auf Base oder Tool (bez. sich auf Base) editieren zu koennen
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
import re  # zum sortieren de Objektliste
# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

# Global Variables:
PATHPTSObjName = 'PTPObj_'
Mode = 'XYZ' # YXZ

RotationModeBase = Mode
RotationModePATHPTS = Mode
RotationModeEmpty_Zentralhand_A6 = 'QUATERNION'
RotationModeTransform = Mode # XYZ YXZ

Vorz1 = +1#-1 # +C = X
Vorz2 = +1#-1 # -B = Y
Vorz3 = +1#-1 # -A = Z
        
#objEmpty_A6 = bpy.data.objects['Empty_Zentralhand_A6']
CalledFrom =[] 
filepath=[]

def WtF_KeyPos(Keyword, KeyPos_Koord, KeyPos_Angle, filepath, FileExt, FileMode):
    
    print('_____________________________________________________________________________')
    print('WtF_KeyPos :' + Keyword)  
    # Create a file for output
    # KeyPos_Angle [rad] 
    FilenameSRC = filepath
    FilenameSRC = FilenameSRC.replace(".dat", FileExt) 
    fout = open(FilenameSRC, FileMode) # FileMode: 'a' fuer Append oder 'w' zum ueberschreiben
    print('FileMode :' + FileMode)
    
    # BASEPos, PTP (=SAFEPos), HOMEPos, ADJUSTMENTPos (X, Y, Z, A, B, C) 
    if (Keyword == 'BASEPos' or Keyword =='PTP' or Keyword =='HOMEPos' or Keyword =='ADJUSTMENTPos'):
        print('Keyword :' + Keyword + ' erkannt.')
        Skalierung = 1000
        fout.write( Keyword + " {" + 
                       "X " + "{0:.5f}".format(KeyPos_Koord[0]*Skalierung) + 
                       ", Y " + "{0:.5f}".format(KeyPos_Koord[1]*Skalierung) +
                       ", Z " + "{0:.5f}".format(KeyPos_Koord[2]*Skalierung) + 
                       ", A " + "{0:.5f}".format(KeyPos_Angle[2]*360/(2*math.pi)) +
                       ", B " + "{0:.5f}".format(KeyPos_Angle[1]*360/(2*math.pi)) + 
                       ", C " + "{0:.5f}".format(KeyPos_Angle[0]*360/(2*math.pi)) +
                       "} " + "\n")
    
    # PATHPTS[n]  (X, Y, Z, A, B, C) / LOADPTS[n] (FX, FY, FZ/ TX, TY, TZ)/ 
    if (Keyword == 'PATHPTS' or Keyword == 'LOADPTS'):
        
        # PATHPTS[1]={X 105.1887, Y 125.6457, Z -123.9032, A 68.49588, B -26.74377, C 1.254162 }
        if Keyword == 'PATHPTS': 
            print('Keyword :' + Keyword + ' erkannt.')
            fout.write(";FOLD PATH DATA" + "\n")
            Skalierung = 1000
            ID1X = 'X'; ID1Y = 'Y'
            ID1Z = 'Z'
            ID2X = 'C'
            ID2Y = 'B'
            ID2Z = 'A' 
        
        # LOADPTS[2]={FX NAN, FY NAN, FZ -120, TX NAN, TY NAN, TZ NAN }
        elif Keyword == 'LOADPTS': 
            print('Keyword :' + Keyword + ' erkannt.')
            fout.write(";FOLD LOAD DATA" + "\n")
            Skalierung = 1
            ID1X = 'FX'
            ID1Y = 'FY'
            ID1Z = 'FZ'
            ID2X = 'TZ'
            ID2Y = 'TY'
            ID2Z = 'TX'
            
        count= len(KeyPos_Koord[:][:])    
        for i in range(0,count,1):    
            fout.write(Keyword + "[" + str(i+1) + "]={" + 
                       ID1X + " " + "{0:.5f}".format(KeyPos_Koord[i][0]*Skalierung) + ", " + ID1Y + " " + "{0:.5f}".format(KeyPos_Koord[i][1]*Skalierung) +
                       ", " + ID1Z + " " +"{0:.5f}".format(KeyPos_Koord[i][2]*Skalierung) + ", "+ ID2Z + " " +"{0:.5f}".format(Vorz3 *KeyPos_Angle[i][2]*360/(2*math.pi) ) +
                       ", " + ID2Y + " " +"{0:.5f}".format(Vorz2 *KeyPos_Angle[i][1]*360/(2*math.pi)) + ", "+ ID2X + " " +"{0:.5f}".format(Vorz1 *KeyPos_Angle[i][0]*360/(2*math.pi) ) +
                       "} " + "\n") 
        fout.write(";ENDFOLD" + "\n")
    
    # TIMEPTS / STOPPTS / ACTIONMSK
    if (Keyword == 'TIMEPTS' or Keyword =='STOPPTS' or Keyword =='ACTIONMSK'):
        # TIMEPTS[1]=1.7
        if Keyword == 'TIMEPTS': 
            print('Keyword :' + Keyword + ' erkannt.')
            fout.write(";FOLD TIME DATA" + "\n")
            Count = len(KeyPos_Koord)
    
        for i in range(0,Count,1):    
            fout.write(Keyword +"[" + str(i+1) + "]=" + 
                       "{0:.5f}".format(KeyPos_Koord[i] ) +
                       "\n")
        fout.write(";ENDFOLD" + "\n")
        
    print('close file.')
    fout.close();
        
    print('WtF_KeyPos :' + Keyword + ' geschrieben.')
    print('_____________________________________________________________________________')

def RfF_KeyPos(Keyword, filepath, FileExt):
    print('_____________________________________________________________________________')
    print('RfF_KeyPos :' + Keyword)  
    # Create a file for output
    # [Grad] Werte werden eingelesen und in [rad] umgewandelt
    Skalierung  = 1000
    FilenameSRC = filepath
    FilenameSRC = FilenameSRC.replace(".dat", FileExt) 
    fin = open(FilenameSRC)
    gesamtertext = fin.read()
    fin.close
    
    KeyPos_Koord = []
    KeyPos_Angle =[] # rad 
    Merker=[]
    # Umwandeln in eine Liste
    zeilenliste =[]
    zeilenliste = gesamtertext.split(chr(10))

    # BASEPos, PTP (=SAFEPos), HOMEPos, ADJUSTMENTPos (X, Y, Z, A, B, C) 
    if (Keyword == 'BASEPos' or Keyword =='PTP' or Keyword =='HOMEPos' or Keyword =='ADJUSTMENTPos'):
        n=0 # Achtung: hier wird 'ab der' Suchmarken ausgelesen
        suchAnf = Keyword + " {X"
        suchEnd = Keyword + " {X"
        CountI = 0
    
       
    if (Keyword == 'PATHPTS' or Keyword == 'LOADPTS'):
        if Keyword == 'PATHPTS': 
            # PATHPTS[1]={X 105.1887, Y 125.6457, Z -123.9032, A 68.49588, B -26.74377, C 1.254162 }
            print('Keyword :' + Keyword + ' erkannt.')
            n=1 # Achtung: hier wird 'zwischen' den Suchmarken ausgelesen
            suchAnf = "FOLD PATH DATA"
            suchEnd = "ENDFOLD"
            CountI = -2
            
        # LOADPTS[2]={FX NAN, FY NAN, FZ -120, TX NAN, TY NAN, TZ NAN }
        elif Keyword == 'LOADPTS': 
            # LOADPTS[2]={FX NAN, FY NAN, FZ -120, TX NAN, TY NAN, TZ NAN }
            print('Keyword :' + Keyword + ' erkannt.')
            
    if (Keyword == 'TIMEPTS' or Keyword =='STOPPTS' or Keyword =='ACTIONMSK'):
        if Keyword == 'TIMEPTS': 
            # TIMEPTS[1]=1.7
            print('Keyword :' + Keyword + ' erkannt.')
            n=1 # Achtung: hier wird 'zwischen' den Suchmarken ausgelesen
            suchAnf = "FOLD TIME DATA"
            suchEnd = "ENDFOLD"
            CountI = -2
        
    Count = len(zeilenliste)
    PathIndexAnf = 0
    PathIndexEnd = Count
    for i in range(Count):
        if zeilenliste[i].find(suchAnf)!=-1: 
            PathIndexAnf = i
            Merker=1
        if (zeilenliste[i].find(suchEnd)!=-1 and PathIndexAnf!=PathIndexEnd and Merker==1): 
            PathIndexEnd = i
            break
            
    Count = CountI + PathIndexEnd - PathIndexAnf +1 # Achtung: hier wird 'ab der' Suchmarken ausgelesen
    
    if (Keyword == 'BASEPos' or Keyword =='PTP' or Keyword =='HOMEPos' or Keyword =='ADJUSTMENTPos'
        or Keyword == 'PATHPTS' or Keyword == 'LOADPTS'):
    
        # ==========================================
        # Einlesen der PTP Werte (X, Y, Z, A, B C) 
        # ADJUSTMENTPos {X 0.0, Y 0.0, Z 0.0, A -128.2708, B -0.4798438, C -178.1682} 
        # MES = {X -237, Y 0, Z 342, A 0, B 0, C 0 }
        # ==========================================
        PathPointX = []
        PathPointY = []
        PathPointZ = []
        PathAngleA = []
        PathAngleB = []
        PathAngleC = []
        beg=0
        # die Schleife ist eigentlich unnoetig da es nur eine BASEPosition gibt...
        for i in range(0,Count,1):
            IndXA = zeilenliste[PathIndexAnf+n+i].index("X ", beg, len(zeilenliste[PathIndexAnf+n+i])) # Same as find(), but raises an exception if str not found 
            IndXE = zeilenliste[PathIndexAnf+n+i].index(", Y", beg, len(zeilenliste[PathIndexAnf+n+i]))
            PathPointX = PathPointX + [float(zeilenliste[PathIndexAnf+n+i][IndXA+2:IndXE])/Skalierung]
       
            IndYA = zeilenliste[PathIndexAnf+n+i].index("Y ", beg, len(zeilenliste[PathIndexAnf+n+i]))  
            IndYE = zeilenliste[PathIndexAnf+n+i].index(", Z", beg, len(zeilenliste[PathIndexAnf+n+i]))
            PathPointY = PathPointY + [float(zeilenliste[PathIndexAnf+n+i][IndYA+2:IndYE])/Skalierung]
       
            IndZA = zeilenliste[PathIndexAnf+n+i].index("Z ", beg, len(zeilenliste[PathIndexAnf+n+i])) 
            IndZE = zeilenliste[PathIndexAnf+n+i].index(", A", beg, len(zeilenliste[PathIndexAnf+n+i]))
            PathPointZ = PathPointZ + [float(zeilenliste[PathIndexAnf+n+i][IndZA+2:IndZE])/Skalierung]
       
            IndAA = zeilenliste[PathIndexAnf+n+i].index("A ", beg, len(zeilenliste[PathIndexAnf+n+i])) 
            IndAE = zeilenliste[PathIndexAnf+n+i].index(", B", beg, len(zeilenliste[PathIndexAnf+n+i]))
            PathAngleA = PathAngleA + [float(zeilenliste[PathIndexAnf+n+i][IndAA+2:IndAE])*2*math.pi/360]
       
            IndBA = zeilenliste[PathIndexAnf+n+i].index("B ", beg, len(zeilenliste[PathIndexAnf+n+i]))  
            IndBE = zeilenliste[PathIndexAnf+n+i].index(", C", beg, len(zeilenliste[PathIndexAnf+n+i]))
            PathAngleB = PathAngleB + [float(zeilenliste[PathIndexAnf+n+i][IndBA+2:IndBE])*2*math.pi/360]
       
            IndCA = zeilenliste[PathIndexAnf+n+i].index("C ", beg, len(zeilenliste[PathIndexAnf+n+i]))  
            IndCE = len(zeilenliste[PathIndexAnf+n+i])-2 # }   " "+chr(125) funktioniert nicht?!
            PathAngleC = PathAngleC + [float(zeilenliste[PathIndexAnf+n+i][IndCA+2:IndCE])*2*math.pi/360] # [Grad] -> [rad]
            
        # ==========================================    
        # Erstellen der Datenkontainer fuer location und rotation
        # ==========================================    
        
        if Count ==1:
            KeyPos_Koord  = Vector([float(PathPointX[0]), float(PathPointY[0]), float(PathPointZ[0])])
            KeyPos_Angle  = float(str(Vorz1 *PathAngleC[0])), float(str(Vorz1 *PathAngleB[0])), float(str(Vorz1 *PathAngleA[0])) # [rad]
        else:   
            mList= createMatrix(Count,1) # eigene Class "createMatrix" erstellt
            for i in range(0,Count,1):
                mList[i][0:3] = [PathPointX[i], PathPointY[i], PathPointZ[i]]
                KeyPos_Koord = KeyPos_Koord + [mList[i]] 
                
            nList= createMatrix(Count,1)   
            for i in range(0,Count,1):
                nList[i][0:3] = [Vorz1 *PathAngleC[i], Vorz2 *PathAngleB[i], Vorz3 *PathAngleA[i]]      
                KeyPos_Angle = KeyPos_Angle + [nList[i]]
                
    if (Keyword == 'TIMEPTS' or Keyword =='STOPPTS' or Keyword =='ACTIONMSK'):
        if Keyword == 'TIMEPTS': 
            # TIMEPTS[1]=1.7
            print('Keyword :' + Keyword + ' erkannt.')
        beg=0
        i=[]
        for i in range(0,Count,1):
            IndXA = zeilenliste[PathIndexAnf+n+i].index("]=", beg, len(zeilenliste[PathIndexAnf+n+i])) # Same as find(), but raises an exception if str not found 
            IndXE = len(zeilenliste[PathIndexAnf+n+i])
            KeyPos_Koord = KeyPos_Koord + [float(zeilenliste[PathIndexAnf+n+i][IndXA+2:IndXE])]
             
    print('RfF_KeyPos :' + Keyword + ' gelesen.')
    print('_____________________________________________________________________________')
    return KeyPos_Koord, KeyPos_Angle 
    
 
def RfS_LocRot(objPATHPTS, dataPATHPTS_Loc, dataPATHPTS_Rot, BASEPos_Koord, BASEPos_Angle):
    
    # dataPATHPTS_Rot [rad]
    # BASEPos_Angle [rad]
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
    mat_rotX = mathutils.Matrix.Rotation(BASEPos_Angle[0], 3, 'X') # Global
    mat_rotY = mathutils.Matrix.Rotation(BASEPos_Angle[1], 3, 'Y')
    mat_rotZ = mathutils.Matrix.Rotation(BASEPos_Angle[2], 3, 'Z')
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
        
    PATHPTS_Angle = (Vorz1* newR[0], Vorz2*newR[1], Vorz3*newR[2]) # [rad]
    
    print('PATHPTS_Koord : ' + str(PATHPTS_Koord))
    print('PATHPTS_Angle: '+'C X {0:.3f}'.format(PATHPTS_Angle[0])+' B Y {0:.3f}'.format(PATHPTS_Angle[1])+' A Z {0:.3f}'.format(PATHPTS_Angle[2]))
    
    print('RfS_LocRot done')
    print('_____________________________________________________________________________')
    return PATHPTS_Koord, PATHPTS_Angle 




def RfS_TIMEPTS(objEmpty_A6):
    
    # todo: objSafe -> action_name ...
    
    print('_____________________________________________________________________________')
    print('RfS TIMEPTS')
    
    #objEmpty_A6 = bpy.data.objects['Empty_Zentralhand_A6']
    action_name = bpy.data.objects[objEmpty_A6.name].animation_data.action.name
    print('RfF action_name: ' +str(action_name))
    action=bpy.data.actions[action_name] 
    locID, rotID = FindFCurveID(objEmpty_A6, action)
    
    
    #TIMEPTSCount = len(action.fcurves) # Anzahl der actions (locx, locy, ...)
    TIMEPTSCount = len(action.fcurves[0].keyframe_points) # Anzahl der KeyFrames
    print('RfS TIMEPTSCount: ' +str(TIMEPTSCount))
    # zum schreiben der PATHPTS verwenden:
    action.fcurves[locID[0]].keyframe_points[0].co # Ergebnis: Vector(Frame[0] Wert, x Wert)
    action.fcurves[locID[1]].keyframe_points[0].co # Ergebnis: Vector(Frame[0] Wert, y Wert)
    action.fcurves[locID[2]].keyframe_points[0].co # Ergebnis: Vector(Frame[0] Wert, z Wert)
    action.fcurves[rotID[0]].keyframe_points[1].co # Ergebnis: Vector(Frame[1] Wert, quaternion w Wert)
    action.fcurves[rotID[1]].keyframe_points[1].co # Ergebnis: Vector(Frame[1] Wert, quaternion x Wert)
    action.fcurves[rotID[2]].keyframe_points[1].co # Ergebnis: Vector(Frame[1] Wert, quaternion y Wert)
    action.fcurves[rotID[3]].keyframe_points[1].co # Ergebnis: Vector(Frame[1] Wert, quaternion z Wert)
    
    #action.fcurves[rotID[0]].keyframe_points[1].co # Ergebnis: Vector(Frame[1] Wert, x Wert)
    
    frameNbr=[]
    TIMEPTS=[]
    for n in range(TIMEPTSCount):
        #frameNbr = bpy.context.object.animation_data.action.fcurves[0].keyframe_points[0].co.x
        frameNbr = int(action.fcurves[0].keyframe_points[n].co.x)
        TIMEPTS = TIMEPTS + [frame_to_time(frameNbr)]
        
    # action.fcurves[0].data_path # Wert: location, rotation_euler, scale, delta_location
    
    #bpy.context.object.animation_data.action.fcurves[0].keyframe_points[0].co.x # Wert: Frame[0]
    
    '''
    # clear key frames:
    objEmpty_A6 = bpy.data.objects['Empty_Zentralhand_A6']
    objEmpty_A6.select =True
    bpy.ops.anim.keyframe_clear_v3d()
    '''
    print('TIMEPTS:' + str(TIMEPTS))
    print('TIMEPTSCount:' + str(TIMEPTSCount))
    print('RfS TIMEPTS done')
    print('_____________________________________________________________________________')
    return TIMEPTS, TIMEPTSCount


def FindFCurveID(objEmpty_A6, action):
    print('_____________________________________________________________________________')
    print('FindFCurveID')
   
    #ob_target = objEmpty_A6
    # todo: Unklar: mehrere Actions moeglich?! -> fuehrt ggf. zu einer Liste als Rueckgabewert:
    
    print(action.name)
    
    locID  =[9999, 9999, 9999]
    rotID  =[9999, 9999, 9999, 9999]
    scaleID=[9999, 9999, 9999]
    dlocID =[9999, 9999, 9999]
         
    action_data =action.fcurves
    print(action_data)
    
    for v,action_data in enumerate(action_data):
        if action_data.data_path == "location":
            locID[action_data.array_index] = v
            #ob_target.delta_location[action_data.array_index]=v
            print("location[" + str(action_data.array_index) + "] to (" + str(v) + ").")
        elif action_data.data_path == "rotation_quaternion":
            rotID[action_data.array_index] = v
            #ob_target.delta_rotation_euler[action_data.array_index]=v
            print("rotation_quaternion[" + str(action_data.array_index) + "] to (" + str(v) + ").")
        elif action_data.data_path == "scale":
             scaleID[action_data.array_index] = v
             #ob_target.delta_scale[action_data.array_index]=v
             print("scale[" + str(action_data.array_index) + "] to (" + str(v) + ").")
        elif action_data.data_path == "delta_location":
             dlocID[action_data.array_index] = v
             #ob_target.delta_scale[action_data.array_index]=v
             print("delta_location[" + str(action_data.array_index) + "] to (" + str(v) + ").")
        else:
             print("Unsupported data_path [" + action_data.data_path + "].")
    
    print("fcurves ID from location [" + str(locID) + "].")
    print("fcurves ID from rotation_euler [" + str(rotID) + "].")
    print("fcurves ID from scale [" + str(scaleID) + "].")
    print("fcurves ID from delta_location [" + str(dlocID) + "].")
    print('FindFCurveID done')
    print('_____________________________________________________________________________')
    return locID, rotID
  

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




def SetOrigin(sourceObj, targetObj):
    # todo: Sicherheitsabfrage/bug: 'EDIT' Mode line 919, in SetOrigin
    # TypeError: Converting py args to operator properties:  enum "EDIT" not found in ('OBJECT')
    # -> Verwendung minimieren durch ersetzen der Transformation durch Ueberlagerung der FCurve Werte!
    # Fehler scheint aufzutreten, wenn z.B. Baseobjekt "ge-Hidded" (ausgeblendet) wird....pruefen
    # oder der Layer auf dem BASEPos, SAFEPos liegen ausgeblendet ist
    # Die Funktion hier ist sch...; Achtung: wenn im Editmode nicht Vertex select aktive ist sondern z.B. Faces oder Edges gibt Probleme...
    original_type = bpy.context.area.type
    bpy.context.area.type = "VIEW_3D" 
    
    # Sicherstellen das wir uns im Object Mode befinden:
    original_mode = bpy.context.mode
    if original_mode!= 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
      
    bpy.ops.object.select_all(action='DESELECT')  
    # 2. setzen des sourceObj Origin auf  vertex[0] von targetObj:
    targetObj.select = True 
    
    bpy.context.scene.objects.active = targetObj
    targetObj.data.vertices[0].select= True
    # Achtung: Blender"Bug": Wechsel in Edit mode nachdem Vertex ausgewaehlt wurde!
    bpy.ops.object.mode_set(mode='EDIT', toggle=True)# 
    bpy.ops.view3d.snap_cursor_to_selected() 
    targetObj.data.vertices[0].select= False
    bpy.ops.object.mode_set(mode='EDIT', toggle=True) #
    sourceObj.select = True 
    
    bpy.context.scene.objects.active = sourceObj
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    bpy.ops.object.select_all(action='DESELECT')
    
    bpy.context.area.type = original_type 
    print('Origin von '+ str(sourceObj.name) + ' auf vertex 0 von ' + str(targetObj.name) + ' gesetzt.')
    
    if original_mode!= 'OBJECT':
        bpy.ops.object.mode_set(mode='EDIT', toggle=True)




def SetObjRelToBase(Obj, Obj_Koord, Obj_Angle, BASEPos_Koord, BASEPos_Angle):
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
        objHome = bpy.data.objects['Sphere_HOMEPos']
        objEmpty_A6 = bpy.data.objects['Empty_Zentralhand_A6']
        
        # Wichtig: Fuer die Interpolation (fcurves) wird Quaternation verwendet um Gimbal Lock zu vermeiden!
        bpy.data.objects[objBase.name].rotation_mode = RotationModeBase
        bpy.data.objects[objSafe.name].rotation_mode = RotationModePATHPTS
        bpy.data.objects[objCurve.name].rotation_mode = RotationModePATHPTS
        bpy.data.objects[objEmpty_A6.name].rotation_mode =RotationModeEmpty_Zentralhand_A6
        
        
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
        #ClearParenting() # hier wird das Parenting geloest!
        
        ApplyScale(objCurve) 
        #--------------------------------------------------------------------------------
        
        #BASEPos_Koord, BASEPos_Angle = objBase.location, [objBase.rotation_euler.x* 360 / (2*math.pi), objBase.rotation_euler.y* 360 / (2*math.pi), objBase.rotation_euler.z* 360 / (2*math.pi)]
        BASEPos_Koord, BASEPos_Angle = objBase.location, objBase.rotation_euler
        
        ADJUSTMENTPos_Koord, ADJUSTMENTPos_Angle = (0,0,0), (0,0,0) #RfS_AdjustmentPos(aus GUI)
        #HOMEPos_Koord, HOMEPos_Angle = objHome.location, [objHome.rotation_euler.x* 360 / (2*math.pi), objHome.rotation_euler.y* 360 / (2*math.pi), objHome.rotation_euler.z* 360 / (2*math.pi)]
        HOMEPos_Koord, HOMEPos_Angle = objHome.location, objHome.rotation_euler
        
        print('_________________CurveExport - BASEPos_Koord' + str(BASEPos_Koord))
        print('_________________CurveExport - BASEPos_Angle' +'X C {0:.3f}'.format(BASEPos_Angle[0])+' Y B {0:.3f}'.format(BASEPos_Angle[1])+' Z A {0:.3f}'.format(BASEPos_Angle[2]))
        
        SAFEPos_Koord, SAFEPos_Angle = RfS_LocRot(objSafe, objSafe.location, objSafe.rotation_euler, BASEPos_Koord, BASEPos_Angle)
        
        print('_________________CurveExport - BASEPos_Koord' + str(BASEPos_Koord))
        print('_________________CurveExport - BASEPos_Angle' +'X C {0:.3f}'.format(BASEPos_Angle[0])+' B Y {0:.3f}'.format(BASEPos_Angle[1])+' Z A {0:.3f}'.format(BASEPos_Angle[2]))
        print('_________________SAFEPos_Koord: ' + str(SAFEPos_Koord))
        print('_________________SAFEPos_Angle' +'A {0:.3f}'.format(SAFEPos_Angle[0])+' B {0:.3f}'.format(SAFEPos_Angle[1])+' C {0:.3f}'.format(SAFEPos_Angle[2]))
        
        
        PathPoint = []
        PathAngle = []  
        PATHPTSObjList, countPATHPTSObj = count_PATHPTSObj(PATHPTSObjName)
        PathPoint = createMatrix(countPATHPTSObj,3)
        PathAngle = createMatrix(countPATHPTSObj,3)
        for i in range(countPATHPTSObj):    
            PathPoint[i][0:2], PathAngle[i][0:2] = RfS_LocRot(bpy.data.objects[PATHPTSObjList[i]], bpy.data.objects[PATHPTSObjList[i]].location, bpy.data.objects[PATHPTSObjList[i]].rotation_euler, BASEPos_Koord, BASEPos_Angle)        
        WtF_KeyPos('PATHPTS',PathPoint, PathAngle, self.filepath, '.dat', 'w')
        
        TIMEPTS_PATHPTS, TIMEPTS_PATHPTSCount = RfS_TIMEPTS(objEmpty_A6)
        WtF_KeyPos('TIMEPTS',TIMEPTS_PATHPTS, '', self.filepath, '.dat', 'a')
            
        print('_________________CurveExport - BASEPos_Koord' + str(BASEPos_Koord))
        print('_________________CurveExport - BASEPos_Angle' +'X C {0:.3f}'.format(BASEPos_Angle[0])+' B Y {0:.3f}'.format(BASEPos_Angle[1])+' Z A {0:.3f}'.format(BASEPos_Angle[2]))
        print('_________________SAFEPos_Koord: ' + str(SAFEPos_Koord))
        print('_________________SAFEPos_Angle' +'A {0:.3f}'.format(SAFEPos_Angle[0])+' B Y {0:.3f}'.format(SAFEPos_Angle[1])+' C {0:.3f}'.format(SAFEPos_Angle[2]))
        
        WtF_KeyPos('BASEPos', BASEPos_Koord, BASEPos_Angle, self.filepath, '.cfg', 'w')
        WtF_KeyPos('ADJUSTMENTPos', ADJUSTMENTPos_Koord, ADJUSTMENTPos_Angle, self.filepath, '.cfg', 'a')
        WtF_KeyPos('HOMEPos', HOMEPos_Koord, HOMEPos_Angle, self.filepath, '.cfg', 'a')
         
        print('_________________CurveExport - BASEPos_Koord' + str(BASEPos_Koord))
        print('_________________CurveExport - BASEPos_Angle' +'X C {0:.3f}'.format(BASEPos_Angle[0])+' X C {0:.3f}'.format(BASEPos_Angle[1])+' Z A {0:.3f}'.format(BASEPos_Angle[2]))
        print('_________________SAFEPos_Koord: ' + str(SAFEPos_Koord))
        print('_________________SAFEPos_Angle' +'A {0:.3f}'.format(SAFEPos_Angle[0])+' B Y {0:.3f}'.format(SAFEPos_Angle[1])+' C {0:.3f}'.format(SAFEPos_Angle[2]))
        WtF_KeyPos('PTP', SAFEPos_Koord, SAFEPos_Angle, self.filepath, '.src', 'w')
        print('_________________CurveExport - BASEPos_Koord' + str(BASEPos_Koord))
        print('_________________CurveExport - BASEPos_Angle' +'X C {0:.3f}'.format(BASEPos_Angle[0])+' X C {0:.3f}'.format(BASEPos_Angle[1])+' Z A {0:.3f}'.format(BASEPos_Angle[2]))
        print('_________________SAFEPos_Koord: ' + str(SAFEPos_Koord))
        print('_________________SAFEPos_Angle' +'X C {0:.3f}'.format(SAFEPos_Angle[0])+' B Y {0:.3f}'.format(SAFEPos_Angle[1])+' Z A {0:.3f}'.format(SAFEPos_Angle[2]))
        #--------------------------------------------------------------------------------
        # Achtung: SetKukaToCurve funktioniert nur richtig, wenn das Parenting vorher geloest wurde!
        SetKukaToCurve(objCurve)
        #SetParenting() # hier wird ein Parenting hergestellt!
        # 2ter Aufruf notwendig, (wegen Kopie der Koordinaten vom parent to child objekt):
        #SetKukaToCurve(context.object) 
        
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
        objHome = bpy.data.objects['Sphere_HOMEPos']
        objCurve = bpy.data.objects['BezierCircle']
        #objCurve = bpy.data.curves[bpy.context.active_object.data.name]
        objEmpty_A6 = bpy.data.objects['Empty_Zentralhand_A6']      
        PATHPTSObjName = 'PTPObj_'
        
        # Wichtig: Verdrehung des Koordinaten Systems (TODO: vgl. Euler Winkel)
        bpy.data.objects[objBase.name].rotation_mode = RotationModeBase
        bpy.data.objects[objSafe.name].rotation_mode = RotationModePATHPTS
        bpy.data.objects[objCurve.name].rotation_mode = RotationModePATHPTS
        bpy.data.objects[objEmpty_A6.name].rotation_mode =RotationModeEmpty_Zentralhand_A6
        
        filename = os.path.basename(self.filepath)
        #realpath = os.path.realpath(os.path.expanduser(self.filepath))
        #fp = open(realpath, 'w')
        ObjName = filename
                
        #ClearParenting()
        ApplyScale(objCurve)
        #--------------------------------------------------------------------------------
        
        print("Erstellen der BezierCurve: done")
        BASEPos_Koord, BASEPos_Angle = RfF_KeyPos('BASEPos', self.filepath, '.cfg')
        try:
            ADJUSTMENTPos_Koord, ADJUSTMENTPos_Angle = RfF_KeyPos('ADJUSTMENTPos', self.filepath, '.cfg')
        except:
            print('failed to load AdjustmentPos')
        try:
            HOMEPos_Koord, HOMEPos_Angle = RfF_KeyPos('HOMEPos', self.filepath, '.cfg')
        except:
            print('failed to load HomePos')
        print('_________________CurveImport - BASEPos_Koord' + str(BASEPos_Koord))
        print('_________________CurveImport - BASEPos_Angle' +'X C {0:.3f}'.format(BASEPos_Angle[0])+' B Y {0:.3f}'.format(BASEPos_Angle[1])+' A Z {0:.3f}'.format(BASEPos_Angle[2]))
        
        # create Container (Location, Rotation) for each path point (PTP): dataPATHPTS_Loc, dataPATHPTS_Rot
        #dataPATHPTS_Loc, dataPATHPTS_Rot, PATHPTSCountFile = RfF_PATHPTS(self.filepath, BASEPos_Koord, BASEPos_Angle) # local, bez. auf Base
        dataPATHPTS_Loc, dataPATHPTS_Rot = RfF_KeyPos('PATHPTS', self.filepath, '.dat')
        PATHPTSCountFile = len(dataPATHPTS_Loc)
        
        SetOrigin(objHome, objHome)
        objHome.location = HOMEPos_Koord
        objHome.rotation_euler = HOMEPos_Angle
        
        SetOrigin(objBase, objBase)
        objBase.location = BASEPos_Koord
        objBase.rotation_euler = BASEPos_Angle
        
        create_PATHPTSObj(dataPATHPTS_Loc, dataPATHPTS_Rot, PATHPTSCountFile, BASEPos_Koord, BASEPos_Angle)
        
        # Kurve: Origin der Kurve auf BASEPosition verschieben
        SetOrigin(objCurve, objBase)
        bpy.data.objects[objCurve.name].rotation_mode =RotationModePATHPTS
        objCurve.location = BASEPos_Koord.x,BASEPos_Koord.y ,BASEPos_Koord.z 
        objCurve.rotation_euler = BASEPos_Angle

        replace_CP(objCurve, PATHPTSObjName, dataPATHPTS_Loc, PATHPTSCountFile, BASEPos_Koord, BASEPos_Angle) 
        
        # Achtung: die Reihenfolge fon SetCurvePos und SetBasePos muss eingehalten werden! 
        # (da sonst die Curve nicht mit der Base mit verschoben wird!
       
        print('_________________CurveImport - BASEPos_Koord' + str(BASEPos_Koord))
        print('_________________CurveImport - BASEPos_Angle' + str(BASEPos_Angle))
        SAFEPos_Koord, SAFEPos_Angle = RfF_KeyPos('PTP', self.filepath, '.src') # PTP = SAFEPos
        print('_________________CurveImport - BASEPos_Koord' + str(BASEPos_Koord))
        print('_________________CurveImport - BASEPos_Angle' +'X C {0:.3f}'.format(BASEPos_Angle[0])+' B Y {0:.3f}'.format(BASEPos_Angle[1])+' A Z {0:.3f}'.format(BASEPos_Angle[2]))
        print('_________________SAFEPos_Koord: ' + str(SAFEPos_Koord))
        print('_________________SAFEPos_Angle' +'X C {0:.3f}'.format(SAFEPos_Angle[0])+' B Y {0:.3f}'.format(SAFEPos_Angle[1])+' A Z {0:.3f}'.format(SAFEPos_Angle[2]))
        # Achtung: Die Reihenfolge der Aufrufe von SetBasePos und SetObjRelToBase darf nicht vertauscht werden!
        SetObjRelToBase(objSafe, SAFEPos_Koord, SAFEPos_Angle, BASEPos_Koord, BASEPos_Angle )        #Transformation Local2World
        print('_________________CurveImport - BASEPos_Koord' + str(BASEPos_Koord))
        print('_________________CurveImport - BASEPos_Angle' +'X C {0:.3f}'.format(BASEPos_Angle[0])+' B Y {0:.3f}'.format(BASEPos_Angle[1])+' A Z {0:.3f}'.format(BASEPos_Angle[2]))
        print('_________________SAFEPos_Koord: ' + str(SAFEPos_Koord))
        print('_________________SAFEPos_Angle' +'A {0:.3f}'.format(SAFEPos_Angle[0])+' B {0:.3f}'.format(SAFEPos_Angle[1])+' C {0:.3f}'.format(SAFEPos_Angle[2]))
        
        # todo: GUI Liste aktualisieren (falls vorhanden), danach Aufruf von GetRoute
        
        #CalledFrom = 'Import'
        PATHPTSObjList, countPATHPTSObj  = count_PATHPTSObj(PATHPTSObjName)
        GetRoute(objEmpty_A6, PATHPTSObjList, countPATHPTSObj, self.filepath)
        
        #--------------------------------------------------------------------------------
        
        # Kuka mit neuer Kurve verknuepfen:
        # der folgende Befehl muss nach dem Parenting nochmal
        # ausgefuehrt werden um die Verschiebung es Empty wieder aufzuheben!
        # Achtung: SetKukaToCurve funktioniert nur richtig, wenn das Parenting vorher geloest wurde!
        
        SetKukaToCurve(objCurve)
        
        # todo: transform func ueberarbeiten:
        #SetObjRelToBase(objEmpty_A6, objEmpty_A6.location, '', objCurve, curve_data.splines[0].bezier_points[-1].co, '')
        
        #SetParenting() # hier wird ein Parenting hergestellt!
        # 2ter Aufruf notwendig, (wegen Kopie der Koordinaten vom parent to child objekt):
        SetKukaToCurve(objCurve) 
        
        return {'FINISHED'} 
    print('CurveImport done')

class ClassRefreshButton (bpy.types.Operator):
    print('ClassRefreshButton- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ') 
    print('- - - - - - - - - - - - -  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')
    ''' Import selected curve '''
    bl_idname = "curve.refreshbutton"
    bl_label = "Refresh (TB)" #Toolbar - Label
    bl_description = "Set Animation Data" # Kommentar im Specials Kontextmenue
    bl_options = {'REGISTER', 'UNDO'} #Set this options, if you want to update  
    #                                  parameters of this operator interactively 
    #                                  (in the Tools pane) 
 
    def execute(self, context):  
        print('- - -refreshbutton - - - - - - -')
        #testen-...
        objBase = bpy.data.objects['Sphere_BASEPos']
        objSafe = bpy.data.objects['Sphere_SAFEPos']
        objCurve = bpy.data.objects['BezierCircle']
        objEmpty_A6 = bpy.data.objects['Empty_Zentralhand_A6']
        PATHPTSObjName = 'PTPObj_'
        
        ApplyScale(objCurve) 
        #--------------------------------------------------------------------------------
        
        BASEPos_Koord, BASEPos_Angle = objBase.location, objBase.rotation_euler
        SAFEPos_Koord, SAFEPos_Angle = RfS_LocRot(objSafe, objSafe.location, objSafe.rotation_euler, BASEPos_Koord, BASEPos_Angle)
        PATHPTSObjList, countPATHPTSObj  = count_PATHPTSObj(PATHPTSObjName)
        
        OptimizeRotation(PATHPTSObjList, countPATHPTSObj) # todo: testen und auch bei export einfuehren
        #dataPATHPTS_Loc, dataPATHPTS_Rot, PATHPTSCountFile = RfS_LocRot(objSafe, objSafe.location, objSafe.rotation_euler, BASEPos_Koord, BASEPos_Angle)
        
        SetOrigin(objCurve, objBase)
        bpy.data.objects[objCurve.name].rotation_mode =RotationModePATHPTS
        objCurve.location = BASEPos_Koord.x,BASEPos_Koord.y ,BASEPos_Koord.z 
        objCurve.rotation_euler = BASEPos_Angle
        replace_CP(objCurve, PATHPTSObjName, '', countPATHPTSObj, BASEPos_Koord, BASEPos_Angle) 
        
        SetKukaToCurve(objCurve)
        
        filepath ='none'
        GetRoute(objEmpty_A6, PATHPTSObjList, countPATHPTSObj, filepath)
        
                
        return {'FINISHED'} 
    print('- - -ClassRefreshButton done- - - - - - -')     

def OptimizeRotation(ObjList, countObj):
    
    # Begrenze Rotation auf 360°
    for i in range(countObj-1):
        Rot = bpy.data.objects[ObjList[i]].rotation_euler
        modRot= math.modf(Rot.x/ (2*math.pi)) # Ergebnis: (Rest, n)
        Rot.x = modRot[0] * (2*math.pi) 
        modRot= math.modf(Rot.y/ (2*math.pi)) # Ergebnis: (Rest, n)
        Rot.y = modRot[0] * (2*math.pi) 
        modRot= math.modf(Rot.z/ (2*math.pi)) # Ergebnis: (Rest, n)
        Rot.z = modRot[0] * (2*math.pi) 
    
    # Teil 1:
    # wenn zum erreichen des folgenden Winkels mehr als 180° (PI) zurueckzulegen ist, 
    # dann zaehle 360° drauf (wenn er negativ ist) bzw. ziehe 360° (wenn er positiv ist)
    
    
    for i in range(countObj-1):
        Rot1 = bpy.data.objects[ObjList[i]].rotation_euler
        Rot2 = bpy.data.objects[ObjList[i+1]].rotation_euler
        
        DeltaRot = [math.fabs(Rot2.x - Rot1.x),math.fabs(Rot2.y - Rot1.y),math.fabs(Rot2.z - Rot1.z)]
                
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
       
                    
def OptimizeRotationQuaternion(ObjList, countObj):
    
    QuaternionList= [bpy.data.objects[ObjList[0]].rotation_euler.to_quaternion()]
    # Teil 1:
    # wenn zum erreichen des folgenden Winkels alle drei Achsen ueber Null gehen muessen, 
    # dann invertiere den folgenden Quaternion
    # besser: wenn die Eulerwinkel vorher ungleich nachher sind, dann Quaternation*-1
    
    ob.rotation_mode = 'QUATERNION'
    for n in range(countObj-1):
        RotEuler = bpy.data.objects[ObjList[n]].rotation_euler
        RotQuaternion = bpy.data.objects[ObjList[n]].rotation_quaternion
        
        QuaternionList = QuaternionList + [bpy.data.objects[ObjList[n+1]].rotation_euler.to_quaternion()]
        
    return QuaternionList    
        

def GetRoute(objEmpty_A6, ObjList, countObj, filepath):
    # Diese Funktion wird erst interessant, wenn Routen ueber mehrere Objektgruppen erzeugt werden sollen.
    # in RefreshButton den Ablauf: [Ruhepos, n x (Safepos, PATHPTS, Safepos), Ruhepos] festlegen        
    
    # 1. Schritt: Umsetzung nur fuer einfache Reihenfolge
    
    # todo: GUI Liste abfragen (falls vorhanden) Reihenfolge der Objektgruppen/-Objekte zum erstellen der Route
    # n x [....] beruecksichtigen...???
        
    if filepath != 'none': # Aufruf von Button Import
        TIMEPTS_PATHPTS, NAN = RfF_KeyPos('TIMEPTS', filepath, '.dat')
        TIMEPTS_PATHPTSCount = len (TIMEPTS_PATHPTS)
        # todo
        #TIMEPTS_Safe = 0
        #TIMEPTS_SafeCount = 1
    elif ObjList != '': # Aufruf von Button RefreshButton
        TIMEPTS_PATHPTS, TIMEPTS_PATHPTSCount = RfS_TIMEPTS(objEmpty_A6)
        #todo:
        #TIMEPTS_Safe, TIMEPTS_SafeCount  = RfS_TIMEPTS(objEmpty_A6, objSafe.name)
        
    #TIMEPTS_Safe, TIMEPTS_SafeCount = RfS_TIMEPTS(objEmpty_A6, objSafe.name) 
    # todo: Klasse definieren: PATHPTS.loc/rot/TIMEPTS/LOADPTS/STOPPTS/ACTIONMSK
         
    Route_ObjList = ObjList                    # spaeter: [objSafe.name, PATHPTSObjList] .... syntax pruefen...
    Route_TIMEPTS = TIMEPTS_PATHPTS            # spaeter: [TIMEPTS_Safe, TIMEPTS_PATHPTS]
    Route_TIMEPTSCount = TIMEPTS_PATHPTSCount  # spaeter: [TIMEPTS_SafeCount, TIMEPTS_PATHPTSCount]
    
    RefreshButton(objEmpty_A6, Route_ObjList, Route_TIMEPTS, Route_TIMEPTSCount)
         
                    
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
    
    #@classmethod
    #def poll(cls, context):
    #    return (bpy.context.active_object.type == 'CURVE') # Test, ob auch wirklich ein 'CURVE' Objekt aktiv ist.

    
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
        
        # Set KeyFrames Button:
        layout.label(text="Refresh Button:")
        row = layout.row(align=True)
        
        row.operator("curve.refreshbutton")  
           
    print('KUKAPanel done')
    print('_____________________________________________________________________________')


#class CURVE_OT_RefreshButtonButton(bpy.types.Operator):
 


#### Curve creation functions
# ________________________________________________________________________________________________________________________
# Bezier
# ________________________________________________________________________________________________________________________

def replace_CP(objCurve, PATHPTSObjName, dataPATHPTS_Loc, PATHPTSCountFile, BASEPos_Koord, BASEPos_Angle):
    
    # todo: replace durch create Fkt ersetzten/ ergaenzen und die alte Kurve loeschen
    
    print('_____________________________________________________________________________')
    print('replace_CP')
    #bpy.data.curves[bpy.context.active_object.data.name].user_clear()
    #bpy.data.curves.remove(bpy.data.curves[bpy.context.active_object.data.name])
    bezierCurve = bpy.data.curves[objCurve.name] #bpy.context.active_object #.data.name
    bpy.data.objects[objCurve.name].rotation_mode =RotationModePATHPTS
    
    original_type = bpy.context.area.type
    bpy.context.area.type = "VIEW_3D" 
    
    # Sicherstellen das wir uns im Object Mode befinden:
    original_mode = bpy.context.mode
    if original_mode!= 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
      
    bpy.ops.object.select_all(action='DESELECT')  
    objCurve.select = True 
    bpy.context.scene.objects.active = objCurve
    
    #bpy.data.objects['BezierCircle'].select=True
    
    PATHPTSObjList, countPATHPTSObj = count_PATHPTSObj(PATHPTSObjName)
    
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
                #bzs[n] fuehrte zu Fehlermeldung ???:
                bezierCurve.splines[0].bezier_points[n].handle_left = NewLocRot[0][0]
                bezierCurve.splines[0].bezier_points[n].co = NewLocRot[1][0]
                bezierCurve.splines[0].bezier_points[n].handle_right = NewLocRot[2][0]
                
                bezierCurve.splines[0].bezier_points[n].select_control_point = False  
                
        else: # wenn kein Kurvenpunkt zum ueberschreiben da ist, generiere einen neuen und schreibe den File-Datenpunkt
            #bzs.add(1) #spline.bezier_points.add(1)
            #bpy.data.curves['BezierCircle'].splines[0].bezier_points.add(1)
            bezierCurve.splines[0].bezier_points.add(1) #spline.bezier_points.add(1)
            #todo: Daten sollten eigentlich von dataPATHPTS_Loc verwendet werden:
            NewLocRot = NewLocRot + [RfS_LocRot(bpy.data.objects[PATHPTSObjList[n-1]], bpy.data.objects[PATHPTSObjList[n-1]].location, bpy.data.objects[PATHPTSObjList[n-1]].rotation_euler, BASEPos_Koord, BASEPos_Angle)]
            NewLocRot = NewLocRot + [RfS_LocRot(bpy.data.objects[PATHPTSObjList[n]], bpy.data.objects[PATHPTSObjList[n]].location, bpy.data.objects[PATHPTSObjList[n]].rotation_euler, BASEPos_Koord, BASEPos_Angle)]
            NewLocRot = NewLocRot + [RfS_LocRot(bpy.data.objects[PATHPTSObjList[n-PATHPTSCountFile+1]], bpy.data.objects[PATHPTSObjList[n-PATHPTSCountFile+1]].location, bpy.data.objects[PATHPTSObjList[n-PATHPTSCountFile+1]].rotation_euler, BASEPos_Koord, BASEPos_Angle)]
            
            bezierCurve.splines[0].bezier_points[n].handle_left = NewLocRot[0][0]
            bezierCurve.splines[0].bezier_points[n].co = NewLocRot[1][0]
            bezierCurve.splines[0].bezier_points[n].handle_right = NewLocRot[2][0]
            
            bezierCurve.splines[0].bezier_points[n].handle_right_type='VECTOR'
            bezierCurve.splines[0].bezier_points[n].handle_left_type='VECTOR'
            print(bezierCurve.splines[0].bezier_points[n])
            print(bezierCurve.splines[0].bezier_points[n].select_control_point)
            print(bezierCurve.splines[0].bezier_points[n].handle_left_type)
            print('handle_right' + str(bezierCurve.splines[0].bezier_points[n].handle_right_type))
            print(bezierCurve.splines[0].bezier_points[n])
            
    
    if original_mode!= 'OBJECT':
        bpy.ops.object.mode_set(mode='EDIT', toggle=True)
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False) # switch back to object mode
    
    bpy.context.area.type = original_type 
        
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
          
    # Nullen voranstellen: http://blenderscripting.blogspot.de/2011/05/padding-number-with-zeroes.html
    # oder neu sortieren:       http://blenderscripting.blogspot.de/2011/05/python-32-semi-natural-sorting.html    
    pattern = '\d+'  # one or more numerical characters  
    def SortObjList(pose):  
        match = re.search(pattern, pose)  
        return int(match.group())  
    PATHPTSObjList = sorted(PATHPTSObjList, key=SortObjList)
    print('PATHPTSObjList sorted: ' + str(PATHPTSObjList))
    
      
    
    print('Anzahl an Objekten in der Szene - countObj: ' +str(countObj))
    print('Anzahl an PathPoint Objekten in der Szene - countPATHPTSObj: ' +str(countPATHPTSObj))
    print('count_PATHPTSObj')
    print('_____________________________________________________________________________')
    return PATHPTSObjList, countPATHPTSObj

def renamePATHObj(PATHPTSObjList):
    print('_____________________________________________________________________________')
    print('renamePATHObj')
    #count =len(PATHPTSObjList)
    #PATHPTSObjList = []
     
    for n in range(len(PATHPTSObjList)-1,0, -1): 
        bpy.data.objects[PATHPTSObjList[n]].name = PATHPTSObjName + str("%03d" %(n+1)) # "%03d" % 2
        PATHPTSObjList[n] = PATHPTSObjName + str("%03d" %(n+1)) # "%03d" % 2  
    print('renamePATHObj done')
    print('_____________________________________________________________________________')
    return PATHPTSObjList

def ValidateTIMEPTS(countPATHPTSObj, PATHPTSObjList, TIMEPTS):
    print('_____________________________________________________________________________')
    print('ValidateTIMEPTS')
    
    
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
             
    # Korrektur der TIMEPTS Werte, wenn groesser der Anzahl an PATHPTS    
    # Achtung: wird noch nicht benoetigt, da in der Funktion erst alle KeyFrames geloescht werden. D.h. TIMEPTS Werte 
    # bleiben ggf. ungenutzt, ohne Fehler zu erzeugen.
    # Achtung: wuerde Sinn machen eine Klasse PATHPTS erstellen um die Zuordnung von Zeit, Kraft, etc. zu bekommen.
        
    print('ValidateTIMEPTS done')    
    print('_____________________________________________________________________________')
    return TIMEPTS
    
    # Korrektur der TIMEPTS Werte, wenn groesser der Anzahl an PATHPTS 
    
def create_PATHPTSObj(dataPATHPTS_Loc, dataPATHPTS_Rot, PATHPTSCountFile, BASEPos_Koord, BASEPos_Angle ):
    # Aufruf von: CurveImport
    original_type = bpy.context.area.type
    bpy.context.area.type = "VIEW_3D" 
    bpy.ops.object.select_all(action='DESELECT')
    print('_____________________________________________________________________________')
    print('create_PATHPTSObj')
    # erstellen von 'PATHPTSCountFile' Mesh Objekten an den Positionen 'dataPATHPTS_Loc' mit der Ausrichtung 'dataPATHPTS_Rot'
    PATHPTSObjName = 'PTPObj_'
    # 1. Wieviele PTPObj Objekte sind in der Scene vorhanden? (Beachte: Viele Objekte koennen den selben Datencontainer verwenden)
    PATHPTSObjList, countPATHPTSObj  = count_PATHPTSObj(PATHPTSObjName)
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
        PATHPTSObjList, countPATHPTSObj  = count_PATHPTSObj(PATHPTSObjName)
        CountCP = countPATHPTSObj
        
    for n in range(CountCP):
        if (countPATHPTSObj-1) >= n: # Wenn ein PATHPTS Objekt vorhandenen ist,
            # Waehle eine PATHPTS Objekt aus:
            bpy.data.objects[PATHPTSObjList[n]].rotation_mode =RotationModePATHPTS
            bpy.data.objects[PATHPTSObjList[n]].select
            print('Waehle Objekt aus: ' + str(PATHPTSObjList[n]))
            
            if (PATHPTSCountFile-1) >= n: # Wenn ein Datenpunkt (PATHPTS) im File da ist, uebertrage loc und rot auf PATHPTSObj
                print('PATHPTS Objekt ' + str(n) + ' vorhanen:' + str(bpy.data.objects[PATHPTSObjList[n]].name))
                print('IF - uebertrage loc: ' + str(dataPATHPTS_Loc[n]) 
                      + ' und rot Daten:' + str(dataPATHPTS_Rot[n]) 
                      + ' vom File auf Objekt:' + str(PATHPTSObjList[n]))
                
                bpy.data.objects[PATHPTSObjList[n]].rotation_mode =RotationModePATHPTS
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
            
            # todo - test: .TIMEPTS einfuegen - eigene Class fuer PATHPTS erstellen!!!
            
            
            print('IF - uebertrage loc: ' + str(dataPATHPTS_Loc[n]) 
                      + ' und rot Daten:' + str(dataPATHPTS_Rot[n]) 
                      + ' vom File auf Objekt:' + str(PATHPTSObjList[n]))
            bpy.data.objects[PATHPTSObjList[n]].rotation_mode =RotationModePATHPTS
            SetObjRelToBase(bpy.data.objects[PATHPTSObjList[n]], Vector(dataPATHPTS_Loc[n]), dataPATHPTS_Rot[n], BASEPos_Koord, BASEPos_Angle) #Transformation Local2World
                
    bpy.context.area.type = original_type 
    print('create_PATHPTSObj done')
    print('_____________________________________________________________________________')
    
    
    
    
    
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
    
def frame_to_time(frame_number):
        fps = bpy.context.scene.render.fps
        raw_time = (frame_number - 1) / fps
        return round(raw_time, 3)
    
def time_to_frame(time_value):
    fps = bpy.context.scene.render.fps
    frame_number = (time_value * fps) +1
    return int(round(frame_number, 0))    
    
def RefreshButton(objEmpty_A6, TargetObjList, TIMEPTS, TIMEPTSCount):
    # Diese Funktion soll spaeter anhand einer chronologisch geordneten Objektgruppen 
    # und Objekt/PATHPTS - Liste die KeyFrames eintragen
    
    
    # TODO: pruefen ob TIMEPTS = PATHPTS ist und ggf. neue keyframes und TIMEPTS setzen
    
    original_type = bpy.context.area.type
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
    # von GetRout u. RefreshButton ueberdenken
    
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
        print(n)
        bpy.context.scene.frame_set(time_to_frame(TIMEPTS[n])) 
        ob.location = bpy.data.objects[TargetObjList[n]].location
        # todo - done: keyframes auf quaternion um gimbal lock zu vermeiden
                
        ob.rotation_quaternion = bpy.data.objects[TargetObjList[n]].rotation_euler.to_quaternion()
           
        ob.keyframe_insert(data_path="location", index=-1)
        # file:///F:/EWa_WWW_Tutorials/Scripting/blender_python_reference_2_68_5/bpy.types.bpy_struct.html#bpy.types.bpy_struct.keyframe_insert
        
        ob.keyframe_insert(data_path="rotation_quaternion", index=-1)
        #ob.keyframe_insert(data_path="rotation_euler", index=-1)
            
    if len(TIMEPTS)> countPATHPTSObj:
        print('Achtung: mehr TIMEPTS als PATHPTS-Objekte vorhanden')
    # todo: end frame not correct if PATHPTS added....
    bpy.context.scene.frame_end = time_to_frame(TIMEPTS[TIMEPTSCount-1])
    
    bpy.data.scenes['Scene'].frame_current=1
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.area.type = original_type 
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
