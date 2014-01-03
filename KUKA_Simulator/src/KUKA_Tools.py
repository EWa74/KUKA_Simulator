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

${workspace_loc:KUKA_OT_Export/src/curve_export.py}

Bevel add-on
bpy.data.curves[bpy.context.active_object.data.name].splines[0].bezier_points[0].co=(0,1,1)
'''  
#--- ### Header 
bl_info = { 
    "name": "KUKA_OT_Export",
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

# Global Variables:
PATHPTSObjName = 'PTPObj_'
objBase     = bpy.data.objects['Sphere_BASEPos']
objSafe     = bpy.data.objects['Sphere_SAFEPos']
objCurve    = bpy.data.objects['BezierCircle']
#objCurve = bpy.data.curves[bpy.context.active_object.data.name]
objHome     = bpy.data.objects['Sphere_HOMEPos']
objEmpty_A6 = bpy.data.objects['Empty_Zentralhand_A6']

Mode = 'XYZ' # YXZ

RotationModeBase = Mode
RotationModePATHPTS = Mode
RotationModeEmpty_Zentralhand_A6 = 'QUATERNION'
RotationModeTransform = Mode # XYZ YXZ

Vorz1 = +1#-1 # +C = X
Vorz2 = +1#-1 # -B = Y
Vorz3 = +1#-1 # -A = Z
   
CalledFrom =[] 
filepath=[]

#import kuka_dat -> bug?: wird beim debuggen nicht aktualisiert....
#from kuka_dat import *
#import kuka_dat
# http://wiki.blender.org/index.php/Doc:2.6/Manual/Extensions/Python/Properties
# http://www.blender.org/documentation/blender_python_api_2_57_1/bpy.props.html


def writelog(text=''):
    FilenameLog = bpy.data.filepath
    FilenameLog = FilenameLog.replace(".blend", '.log')
    fout = open(FilenameLog, 'a')
    localtime = time.asctime( time.localtime(time.time()) )
    fout.write(localtime + " : " + str(text) + '\n')
    fout.close();

class ObjectSettings(bpy.types.PropertyGroup):
    ID = bpy.props.IntProperty()
    # type: BASEPos, PTP, HOMEPos, ADJUSTMENTPos
    type = bpy.props.StringProperty()
    
    PATHPTS = bpy.props.FloatVectorProperty(size=6)
    
    # LOADPTS[1]={FX NAN, FY NAN, FZ NAN, TX NAN, TY NAN, TZ NAN }
    # bpy.data.objects['PTPObj_001'].PATHPTS.LOADPTS[:] 
    LOADPTS = bpy.props.IntVectorProperty(size=6)
    LOADPTSmsk = bpy.props.BoolVectorProperty(size=6) # fuer NAN Eintrag
    LOADPTSmsk = (False, False, False, False, False, False)
    
    # TTIMEPTS[1]=0.2
    TIMEPTS = bpy.props.FloatProperty()
    
    # STOPPTS[1]=1
    STOPPTS = bpy.props.BoolProperty()
    STOPPTS = 'False'
    
    # ACTIONMSK[1]=0
    ACTIONMSK = bpy.props.BoolProperty()
    ACTIONMSK = 'False'
    
    # RouteName
    RouteName = bpy.props.StringProperty()
    
    # RouteNbr
    RouteNbr = bpy.props.IntProperty()  
    
bpy.utils.register_class(ObjectSettings)

bpy.types.Object.kuka = \
    bpy.props.PointerProperty(type=ObjectSettings)

class createMatrix(object):
    writelog('_____________________________________________________________________________')
    writelog('createMatrix')
    def __init__(self, rows, columns, default=0):
        self.m = []
        for i in range(rows):
            self.m.append([default for j in range(columns)])
    def __getitem__(self, index):
        return self.m[index]
    writelog('createMatrix done')
    writelog('_____________________________________________________________________________')  


   
def WtF_KeyPos(Keyword, KeyPos_Koord, KeyPos_Angle, filepath, FileExt, FileMode):
    
    writelog('_____________________________________________________________________________')
    writelog('WtF_KeyPos :' + Keyword)  
    # Create a file for output
    # KeyPos_Angle [rad] 
    FilenameSRC = filepath
    FilenameSRC = FilenameSRC.replace(".dat", FileExt) 
    fout = open(FilenameSRC, FileMode) # FileMode: 'a' fuer Append oder 'w' zum ueberschreiben
    writelog('FileMode :' + FileMode)
    
    # BASEPos, PTP (=SAFEPos), HOMEPos, ADJUSTMENTPos (X, Y, Z, A, B, C) 
    if (Keyword == 'BASEPos' or Keyword =='PTP' or Keyword =='HOMEPos' or Keyword =='ADJUSTMENTPos'):
        writelog('Keyword :' + Keyword + ' erkannt.')
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
            writelog('Keyword :' + Keyword + ' erkannt.')
            fout.write(";FOLD PATH DATA" + "\n")
            Skalierung = 1000
            ID1X = 'X'; ID1Y = 'Y'
            ID1Z = 'Z'
            ID2X = 'C'
            ID2Y = 'B'
            ID2Z = 'A' 
        
        # LOADPTS[2]={FX NAN, FY NAN, FZ -120, TX NAN, TY NAN, TZ NAN }
        elif Keyword == 'LOADPTS': 
            writelog('Keyword :' + Keyword + ' erkannt.')
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
            writelog('Keyword :' + Keyword + ' erkannt.')
            fout.write(";FOLD TIME DATA" + "\n")
            Count = len(KeyPos_Koord)
    
        for i in range(0,Count,1):    
            fout.write(Keyword +"[" + str(i+1) + "]=" + 
                       "{0:.5f}".format(KeyPos_Koord[i] ) +
                       "\n")
        fout.write(";ENDFOLD" + "\n")
        
    writelog('close file.')
    fout.close();
        
    writelog('WtF_KeyPos :' + Keyword + ' geschrieben.')
    writelog('_____________________________________________________________________________')

def RfF_KeyPos(Keyword, filepath, FileExt):
    writelog('_____________________________________________________________________________')
    writelog('RfF_KeyPos :' + Keyword)  
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
            writelog('Keyword :' + Keyword + ' erkannt.')
            n=1 # Achtung: hier wird 'zwischen' den Suchmarken ausgelesen
            suchAnf = "FOLD PATH DATA"
            suchEnd = "ENDFOLD"
            CountI = -2
            
        # LOADPTS[2]={FX NAN, FY NAN, FZ -120, TX NAN, TY NAN, TZ NAN }
        elif Keyword == 'LOADPTS': 
            # LOADPTS[2]={FX NAN, FY NAN, FZ -120, TX NAN, TY NAN, TZ NAN }
            writelog('Keyword :' + Keyword + ' erkannt.')
            
    if (Keyword == 'TIMEPTS' or Keyword =='STOPPTS' or Keyword =='ACTIONMSK'):
        if Keyword == 'TIMEPTS': 
            # TIMEPTS[1]=1.7
            writelog('Keyword :' + Keyword + ' erkannt.')
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
            writelog('Keyword :' + Keyword + ' erkannt.')
        beg=0
        i=[]
        for i in range(0,Count,1):
            IndXA = zeilenliste[PathIndexAnf+n+i].index("]=", beg, len(zeilenliste[PathIndexAnf+n+i])) # Same as find(), but raises an exception if str not found 
            IndXE = len(zeilenliste[PathIndexAnf+n+i])
            KeyPos_Koord = KeyPos_Koord + [float(zeilenliste[PathIndexAnf+n+i][IndXA+2:IndXE])]
             
    writelog('RfF_KeyPos :' + Keyword + ' gelesen.')
    writelog('_____________________________________________________________________________')
    return KeyPos_Koord, KeyPos_Angle 
    
 
def RfS_TIMEPTS(objEmpty_A6):
    
    # todo: objSafe -> action_name ...
    
    writelog('_____________________________________________________________________________')
    writelog('RfS TIMEPTS')
    
    #objEmpty_A6 = bpy.data.objects['Empty_Zentralhand_A6']
    action_name = bpy.data.objects[objEmpty_A6.name].animation_data.action.name
    writelog('RfF action_name: ' +str(action_name))
    action=bpy.data.actions[action_name] 
    locID, rotID = FindFCurveID(objEmpty_A6, action)
    
    
    #TIMEPTSCount = len(action.fcurves) # Anzahl der actions (locx, locy, ...)
    TIMEPTSCount = len(action.fcurves[0].keyframe_points) # Anzahl der KeyFrames
    writelog('RfS TIMEPTSCount: ' +str(TIMEPTSCount))
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
    writelog('TIMEPTS:' + str(TIMEPTS))
    writelog('TIMEPTSCount:' + str(TIMEPTSCount))
    writelog('RfS TIMEPTS done')
    writelog('_____________________________________________________________________________')
    return TIMEPTS, TIMEPTSCount


def FindFCurveID(objEmpty_A6, action):
    writelog('_____________________________________________________________________________')
    writelog('FindFCurveID')
   
    #ob_target = objEmpty_A6
    # todo: Unklar: mehrere Actions moeglich?! -> fuehrt ggf. zu einer Liste als Rueckgabewert:
    
    writelog(action.name)
    
    locID  =[9999, 9999, 9999]
    rotID  =[9999, 9999, 9999, 9999]
    scaleID=[9999, 9999, 9999]
    dlocID =[9999, 9999, 9999]
         
    action_data =action.fcurves
    writelog(action_data)
    
    for v,action_data in enumerate(action_data):
        if action_data.data_path == "location":
            locID[action_data.array_index] = v
            #ob_target.delta_location[action_data.array_index]=v
            writelog("location[" + str(action_data.array_index) + "] to (" + str(v) + ").")
        elif action_data.data_path == "rotation_quaternion":
            rotID[action_data.array_index] = v
            #ob_target.delta_rotation_euler[action_data.array_index]=v
            writelog("rotation_quaternion[" + str(action_data.array_index) + "] to (" + str(v) + ").")
        elif action_data.data_path == "scale":
             scaleID[action_data.array_index] = v
             #ob_target.delta_scale[action_data.array_index]=v
             writelog("scale[" + str(action_data.array_index) + "] to (" + str(v) + ").")
        elif action_data.data_path == "delta_location":
             dlocID[action_data.array_index] = v
             #ob_target.delta_scale[action_data.array_index]=v
             writelog("delta_location[" + str(action_data.array_index) + "] to (" + str(v) + ").")
        else:
             writelog("Unsupported data_path [" + action_data.data_path + "].")
    
    writelog("fcurves ID from location [" + str(locID) + "].")
    writelog("fcurves ID from rotation_euler [" + str(rotID) + "].")
    writelog("fcurves ID from scale [" + str(scaleID) + "].")
    writelog("fcurves ID from delta_location [" + str(dlocID) + "].")
    writelog('FindFCurveID done')
    writelog('_____________________________________________________________________________')
    return locID, rotID
  

def ApplyScale(objCurve):
        writelog('_____________________________________________________________________________')
        writelog('ApplyScale')
        
        # nur Kurve auswaehlen
        bpy.ops.object.select_all(action='DESELECT')
        objCurve.select = True
        bpy.context.scene.objects.active = objCurve
        # Scaling (nur bei Export noetig)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.select_all(action='DESELECT')
        writelog('ApplyScale done')
        writelog('_____________________________________________________________________________')

    
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
    writelog('Origin von '+ str(sourceObj.name) + ' auf vertex 0 von ' + str(targetObj.name) + ' gesetzt.')
    
    if original_mode!= 'OBJECT':
        bpy.ops.object.mode_set(mode='EDIT', toggle=True)

def get_relative(dataPATHPTS_Loc, dataPATHPTS_Rot, BASEPos_Koord, BASEPos_Angle):
    
    # dataPATHPTS_Loc/Rot [rad]: absolute
    # BASEPos_Koord/Angle [rad]: absolute
    # Aufruf von: Diese Funktion wird nur bei Refresh und Import aufgerufen.
    # Wiedergabe von LOC/Rot bezogen auf Base
    
    # World2Local - OK (absolute -> relative)
    
    # Gegeben: Mtrans, Mrot = Base / Vtrans_abs, Mrot_abs
    # Ges:  Mrot_rel, Vtrans_rel
    #
    # Mworld  / Mworld_rel / Mworld_abs mit world = trans * rot
    # Mtrans  / Mtrans_rel / Mtrans_abs
    # Mrot    / Mrot_rel   / Mrot_abs
    #
    # dataPATHPTS_Loc = Global --> PATHPTS_Koord bezogen auf Base 
    # dataPATHPTS_Rot = Global --> PATHPTS_Angle bezogen auf Base
    writelog('_____________________________________________________________________________')
    writelog('Funktion: get_relativeX - lokale Koordinaten bezogen auf Base!')
            
    Mtrans    = mathutils.Matrix.Translation(Vector(BASEPos_Koord))
    Vtrans_abs = dataPATHPTS_Loc                              #global 
    writelog('Vtrans_abs'+ str(Vtrans_abs))  # neuer Bezugspunkt
    
    #--------------------------------------------------------------------------
    MrotX = mathutils.Matrix.Rotation(BASEPos_Angle[0], 3, 'X') # Global
    MrotY = mathutils.Matrix.Rotation(BASEPos_Angle[1], 3, 'Y')
    MrotZ = mathutils.Matrix.Rotation(BASEPos_Angle[2], 3, 'Z')
    Mrot = MrotZ * MrotY * MrotX
    writelog('Mrot :'+ str(Mrot))
    
    Mworld_rel = Mtrans * Mrot.to_4x4()
    
    Mrot_absX = mathutils.Matrix.Rotation(dataPATHPTS_Rot[0], 3, 'X') # Global
    Mrot_absY = mathutils.Matrix.Rotation(dataPATHPTS_Rot[1], 3, 'Y')
    Mrot_absZ = mathutils.Matrix.Rotation(dataPATHPTS_Rot[2], 3, 'Z')  
    Mrot_abs = Mrot_absZ * Mrot_absY * Mrot_absX
    writelog('Mrot_abs :'+ str(Mrot_abs))
    #--------------------------------------------------------------------------
     
    #PATHPTS_Koord = matrix_world.inverted() *point_local    # transpose fuehrt zu einem andren Ergebnis?!
    Vtrans_rel   = Mworld_rel.inverted() *Vtrans_abs  
    PATHPTS_Koord = Vtrans_rel
    
    writelog('PATHPTS_Koord : '+ str(PATHPTS_Koord))           # neuer Bezugspunkt
    
    Mrot_rel = Mrot.inverted()  * Mrot_abs 
    writelog('Mrot_rel'+ str(Mrot_rel))
    
    newR = Mrot_rel.to_euler('XYZ')
    
    writelog('newR'+ str(newR))    
    writelog('newR[0] :'+ str(newR[0]*360/(2*math.pi)))
    writelog('newR[1] :'+ str(newR[1]*360/(2*math.pi)))
    writelog('newR[2] :'+ str(newR[2]*360/(2*math.pi)))
        
    PATHPTS_Angle = (Vorz1* newR[0], Vorz2*newR[1], Vorz3*newR[2]) # [rad]     
    
    writelog('PATHPTS_Koord : ' + str(PATHPTS_Koord))
    writelog('PATHPTS_Angle: '+'C X {0:.3f}'.format(PATHPTS_Angle[0])+' B Y {0:.3f}'.format(PATHPTS_Angle[1])+' A Z {0:.3f}'.format(PATHPTS_Angle[2]))
    
    writelog('get_relative done')
    writelog('_____________________________________________________________________________')
    return PATHPTS_Koord, PATHPTS_Angle 

def get_absolute(Obj_Koord, Obj_Angle, BASEPos_Koord, BASEPos_Angle):
    # Obj_Koord und Obj_Angle sind lokale Angaben bezogen auf Base
    # Aufruf bei Import
    # Obj_Koord, Obj_Angle [rad]: relativ
    # BASEPos_Koord, BASEPos_Angle [rad]: absolut 
    
    # Transformation Local2World
    
    # Gegeben: Mtrans, Mrot = Base --> Mworld/ Mrot_rel, Vtrans_rel --> Mworld_rel
    # Ges:  Vtrans_abs, Mrot_abs
    #
    # Mworld  / Mworld_rel / Mworld_abs mit world = trans * rot
    # Mtrans  / Mtrans_rel / Mtrans_abs
    # Mrot    / Mrot_rel   / Mrot_abs
    
    # 01012014 objBase = bpy.data.objects['Sphere_BASEPos']
    #bpy.data.objects[Obj.name].rotation_mode =RotationModeTransform
    
    matrix_world =bpy.data.objects[objBase.name].matrix_world
    #point_local  = Obj_Koord 
    
    Mtrans     = mathutils.Matrix.Translation(Vector(BASEPos_Koord))
    Vtrans_rel = Obj_Koord                              #lokal 
    writelog('Vtrans_rel'+ str(Vtrans_rel))  # neuer Bezugspunkt
      
    MrotX = mathutils.Matrix.Rotation(BASEPos_Angle[0], 3, 'X') # C = -179 Global
    MrotY = mathutils.Matrix.Rotation(BASEPos_Angle[1], 3, 'Y') # B = -20
    MrotZ = mathutils.Matrix.Rotation(BASEPos_Angle[2], 3, 'Z') # A = -35
    Mrot = MrotZ * MrotY * MrotX
    writelog('Mrot'+ str(Mrot))
    
    Mworld = Mtrans * Mrot.to_4x4()
    
    Mrot_relX = mathutils.Matrix.Rotation(Obj_Angle[0], 3, 'X') # Local (bez. auf Base)
    Mrot_relY = mathutils.Matrix.Rotation(Obj_Angle[1], 3, 'Y') # 0,20,35 = X = -C, Y = -B, Z = -A
    Mrot_relZ = mathutils.Matrix.Rotation(Obj_Angle[2], 3, 'Z')
    Mrot_rel = Mrot_relZ * Mrot_relY * Mrot_relX # KUKA Erg.
    writelog('Mrot_rel'+ str(Mrot_rel))

    Mrot_abs = Mrot_rel.transposed() * Mrot.transposed()       
    Mrot_abs = Mrot_abs.transposed()
    rotEuler =Mrot_abs.to_euler('XYZ')
    
    writelog('rotEuler'+ str(rotEuler))
    writelog('rotEuler[0] :'+ str(rotEuler[0]*360/(2*math.pi)))
    writelog('rotEuler[1] :'+ str(rotEuler[1]*360/(2*math.pi)))
    writelog('rotEuler[2] :'+ str(rotEuler[2]*360/(2*math.pi)))
        
    Vtrans_abs = Mworld *Vtrans_rel
    writelog('Vtrans_abs :'+ str(Vtrans_abs))
       
    return Vtrans_abs, rotEuler
 
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
    
    # Teil 1:
    # wenn zum erreichen des folgenden Winkels mehr als 180° (PI) zurueckzulegen ist, 
    # dann zaehle 360Grad drauf (wenn er negativ ist) bzw. ziehe 360Grad (wenn er positiv ist)
    
    
    for i in range(countObj-1):
        Rot1 = bpy.data.objects[ObjList[i]].rotation_euler
        Rot2 = bpy.data.objects[ObjList[i+1]].rotation_euler
        Rot2old = deepcopy(Rot2)

        Rot2Q = bpy.data.objects[ObjList[i+1]].rotation_euler.to_quaternion()

        
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
        
        ''' 
        # Quaternation-Flip disabled
        new = [round(Rot2.to_quaternion()[0],6), round(Rot2.to_quaternion()[1],6),round(Rot2.to_quaternion()[2],6), round(Rot2.to_quaternion()[3],6)]
        old = [-round(Rot2old.to_quaternion()[0],6), -round(Rot2old.to_quaternion()[1],6),-round(Rot2old.to_quaternion()[2],6), -round(Rot2old.to_quaternion()[3],6)]
        
        if new[:] == old[:]: # notwendig um Quaternion flip zu vermeiden
            Rot2.x = Rot2old.x
            Rot2.y = Rot2old.y
            Rot2.z = Rot2old.z
        '''
        print('')
                               
def OptimizeRotationQuaternion(ObjList, countObj):
    # Status: on hold...
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


# ________________________________________________________________________________________________________________________

def count_PATHPTSObj(PATHPTSObjName):
    writelog('_____________________________________________________________________________')
    writelog('count_PATHPTSObj')
    countPATHPTSObj = 0
    countObj = 0
    PATHPTSObjList=[]
    
    for item in bpy.data.objects:
        if item.type == "MESH":
            countObj = countObj +1
            writelog(item.name)  
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
    writelog('PATHPTSObjList sorted: ' + str(PATHPTSObjList))
    
      
    
    writelog('Anzahl an Objekten in der Szene - countObj: ' +str(countObj))
    writelog('Anzahl an PathPoint Objekten in der Szene - countPATHPTSObj: ' +str(countPATHPTSObj))
    writelog('count_PATHPTSObj')
    writelog('_____________________________________________________________________________')
    return PATHPTSObjList, countPATHPTSObj

def renamePATHObj(PATHPTSObjList):
    writelog('_____________________________________________________________________________')
    writelog('renamePATHObj')
         
    for n in range(len(PATHPTSObjList)-1,0, -1): 
        bpy.data.objects[PATHPTSObjList[n]].name = PATHPTSObjName + str("%03d" %(n+1)) # "%03d" % 2
        PATHPTSObjList[n] = PATHPTSObjName + str("%03d" %(n+1)) # "%03d" % 2  
    writelog('renamePATHObj done')
    writelog('_____________________________________________________________________________')
    return PATHPTSObjList

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
             
    # Korrektur der TIMEPTS Werte, wenn groesser der Anzahl an PATHPTS    
    # Achtung: wird noch nicht benoetigt, da in der Funktion erst alle KeyFrames geloescht werden. D.h. TIMEPTS Werte 
    # bleiben ggf. ungenutzt, ohne Fehler zu erzeugen.
    # Achtung: wuerde Sinn machen eine Klasse PATHPTS erstellen um die Zuordnung von Zeit, Kraft, etc. zu bekommen.
        
    writelog('ValidateTIMEPTS done')    
    writelog('_____________________________________________________________________________')
    return TIMEPTS
    
    # Korrektur der TIMEPTS Werte, wenn groesser der Anzahl an PATHPTS 
    

def frame_to_time(frame_number):
        fps = bpy.context.scene.render.fps
        raw_time = (frame_number - 1) / fps
        return round(raw_time, 3)
    
def time_to_frame(time_value):
    fps = bpy.context.scene.render.fps
    frame_number = (time_value * fps) +1
    return int(round(frame_number, 0))    
    



#### Curve creation functions
# ________________________________________________________________________________________________________________________
# Bezier
# ________________________________________________________________________________________________________________________

def replace_CP(objCurve, dataPATHPTS_Loc):
    
    # dataPATHPTS_Loc: relativ, weil Origin der Kurve auf BasePos liegt!
    writelog('_____________________________________________________________________________')
    writelog('replace_CP')
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
    
    bpy.ops.object.mode_set(mode='EDIT', toggle=False) # switch to edit mode
    
    bezierCurve.dimensions = '3D'
    #bzs = bpy.data.curves[bpy.context.active_object.data.name].splines[0].bezier_points
    bzs = bezierCurve.splines[0].bezier_points
    PATHPTSCount = len(bzs)
    
    # sicherstellen das kein ControlPoint selektiert ist:
    for n in range(PATHPTSCount):
        bzs[n].select_control_point= False
        bzs[n].select_right_handle = False
        bzs[n].select_left_handle = False             
    CountCP = 0
    PATHPTSCountFile = len(dataPATHPTS_Loc[:])
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
            bzs[delList[n]].select_control_point=True
            bzs[delList[n]].select_right_handle = True
            bzs[delList[n]].select_left_handle = True
            #bpy.ops.curve.delete(type='SELECTED') # erzeugte Fehler bei Wechsel von Version 2.68-2 auf 2.69
            bpy.ops.curve.delete()
        CountCP = len(bzs)
    
    for n in range(CountCP):
        if (PATHPTSCount-1) >= n: # Wenn ein Datenpunkt auf der vorhandenen Kurve da ist,
            # Waehle einen Punkt auf der vorhandenen Kurve aus:
            bzs[n].select_control_point = True
            writelog(bzs[n])
            writelog('Select control point:' + str(bzs[n].select_control_point))
            
            bzs[n].handle_left_type='VECTOR'
            writelog(bzs[n].handle_left_type)
            
            bzs[n].handle_right_type='VECTOR'
            writelog(bzs[n].handle_right_type)
            
            if (PATHPTSCountFile-1) >= n: # Wenn ein Datenpunkt im File da ist, nehm ihn und ersetzte damit den aktellen Punkt
                writelog()
                bzs[n].handle_left  =  dataPATHPTS_Loc[n-1]
                bzs[n].co           = dataPATHPTS_Loc[n] 
                bzs[n].handle_right = dataPATHPTS_Loc[n-PATHPTSCountFile+1] 
                
                bzs[n].select_control_point = False  
                
        else: # wenn kein Kurvenpunkt zum ueberschreiben da ist, generiere einen neuen und schreibe den File-Datenpunkt
            bzs.add(1) 
        
            bzs[n].handle_left = dataPATHPTS_Loc[n-1] 
            bzs[n].co =  dataPATHPTS_Loc[n] 
            bzs[n].handle_right = dataPATHPTS_Loc[n-PATHPTSCountFile+1] 
            
            bzs[n].handle_right_type='VECTOR'
            bzs[n].handle_left_type='VECTOR'
    
    if original_mode!= 'OBJECT':
        bpy.ops.object.mode_set(mode='EDIT', toggle=True)
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False) # switch back to object mode
    
    bpy.context.area.type = original_type 
        
    writelog('replace_CP done')
    writelog('_____________________________________________________________________________')
    



  
class KUKA_OT_Export (bpy.types.Operator, ExportHelper):
    writelog('KUKA_OT_Export - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ') 
    writelog('- - - - - - - - - - - - -  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')
    #bpy.ops.curve.KUKA_OT_Export(
                              
    # Export selected curve of the mesh
    bl_idname = "object.kuka_export"
    bl_label = "KUKA_OT_Export (TB)" #Toolbar - Label
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
        
        writelog('FUNKTIONSAUFRUF - KUKA_OT_Export')
        
        # Wichtig: Fuer die Interpolation (fcurves) wird Quaternation verwendet um Gimbal Lock zu vermeiden!
        objBase.rotation_mode     = RotationModeBase
        objSafe.rotation_mode     = RotationModePATHPTS
        objCurve.rotation_mode    = RotationModePATHPTS
        objEmpty_A6.rotation_mode = RotationModeEmpty_Zentralhand_A6
        
        
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
        writelog('- - - - - - - - - - - - -  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')
        writelog(' FUNKTIONSAUFRUF KUKA_OT_Export KUKA_Tools')
        writelog('- - - - - - - - - - - - -  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')
        
        ApplyScale(objCurve) 
        #--------------------------------------------------------------------------------
        
        #BASEPos_Koord, BASEPos_Angle = objBase.location, [objBase.rotation_euler.x* 360 / (2*math.pi), objBase.rotation_euler.y* 360 / (2*math.pi), objBase.rotation_euler.z* 360 / (2*math.pi)]
        BASEPos_Koord, BASEPos_Angle = objBase.location, objBase.rotation_euler
        
        ADJUSTMENTPos_Koord, ADJUSTMENTPos_Angle = (0,0,0), (0,0,0) #RfS_AdjustmentPos(aus GUI)
        #HOMEPos_Koord, HOMEPos_Angle = objHome.location, [objHome.rotation_euler.x* 360 / (2*math.pi), objHome.rotation_euler.y* 360 / (2*math.pi), objHome.rotation_euler.z* 360 / (2*math.pi)]
        HOMEPos_Koord, HOMEPos_Angle = objHome.location, objHome.rotation_euler
        
        writelog('_________________KUKA_OT_Export - BASEPos_Koord' + str(BASEPos_Koord))
        writelog('_________________KUKA_OT_Export - BASEPos_Angle' +'X C {0:.3f}'.format(BASEPos_Angle[0])+' Y B {0:.3f}'.format(BASEPos_Angle[1])+' Z A {0:.3f}'.format(BASEPos_Angle[2]))
        
        SAFEPos_Koord, SAFEPos_Angle = get_relative(objSafe.location, objSafe.rotation_euler, BASEPos_Koord, BASEPos_Angle)
        
        writelog('_________________KUKA_OT_Export - BASEPos_Koord' + str(BASEPos_Koord))
        writelog('_________________KUKA_OT_Export - BASEPos_Angle' +'X C {0:.3f}'.format(BASEPos_Angle[0])+' B Y {0:.3f}'.format(BASEPos_Angle[1])+' Z A {0:.3f}'.format(BASEPos_Angle[2]))
        writelog('_________________SAFEPos_Koord: ' + str(SAFEPos_Koord))
        writelog('_________________SAFEPos_Angle' +'A {0:.3f}'.format(SAFEPos_Angle[0])+' B {0:.3f}'.format(SAFEPos_Angle[1])+' C {0:.3f}'.format(SAFEPos_Angle[2]))
        
        
        PathPoint = []
        PathAngle = []  
        PATHPTSObjList, countPATHPTSObj = count_PATHPTSObj(PATHPTSObjName)
        PathPoint = createMatrix(countPATHPTSObj,3)
        PathAngle = createMatrix(countPATHPTSObj,3)
        for i in range(countPATHPTSObj):    
            PathPoint[i][0:3], PathAngle[i][0:3] = get_relative(bpy.data.objects[PATHPTSObjList[i]].location, bpy.data.objects[PATHPTSObjList[i]].rotation_euler, BASEPos_Koord, BASEPos_Angle)        
        WtF_KeyPos('PATHPTS',PathPoint, PathAngle, self.filepath, '.dat', 'w')
        
        TIMEPTS_PATHPTS, TIMEPTS_PATHPTSCount = RfS_TIMEPTS(objEmpty_A6)
        WtF_KeyPos('TIMEPTS',TIMEPTS_PATHPTS, '', self.filepath, '.dat', 'a')
            
        writelog('_________________KUKA_OT_Export - BASEPos_Koord' + str(BASEPos_Koord))
        writelog('_________________KUKA_OT_Export - BASEPos_Angle' +'X C {0:.3f}'.format(BASEPos_Angle[0])+' B Y {0:.3f}'.format(BASEPos_Angle[1])+' Z A {0:.3f}'.format(BASEPos_Angle[2]))
        writelog('_________________SAFEPos_Koord: ' + str(SAFEPos_Koord))
        writelog('_________________SAFEPos_Angle' +'A {0:.3f}'.format(SAFEPos_Angle[0])+' B Y {0:.3f}'.format(SAFEPos_Angle[1])+' C {0:.3f}'.format(SAFEPos_Angle[2]))
        
        WtF_KeyPos('BASEPos', BASEPos_Koord, BASEPos_Angle, self.filepath, '.cfg', 'w')
        WtF_KeyPos('ADJUSTMENTPos', ADJUSTMENTPos_Koord, ADJUSTMENTPos_Angle, self.filepath, '.cfg', 'a')
        WtF_KeyPos('HOMEPos', HOMEPos_Koord, HOMEPos_Angle, self.filepath, '.cfg', 'a')
         
        writelog('_________________KUKA_OT_Export - BASEPos_Koord' + str(BASEPos_Koord))
        writelog('_________________KUKA_OT_Export - BASEPos_Angle' +'X C {0:.3f}'.format(BASEPos_Angle[0])+' X C {0:.3f}'.format(BASEPos_Angle[1])+' Z A {0:.3f}'.format(BASEPos_Angle[2]))
        writelog('_________________SAFEPos_Koord: ' + str(SAFEPos_Koord))
        writelog('_________________SAFEPos_Angle' +'A {0:.3f}'.format(SAFEPos_Angle[0])+' B Y {0:.3f}'.format(SAFEPos_Angle[1])+' C {0:.3f}'.format(SAFEPos_Angle[2]))
        WtF_KeyPos('PTP', SAFEPos_Koord, SAFEPos_Angle, self.filepath, '.src', 'w')
        writelog('_________________KUKA_OT_Export - BASEPos_Koord' + str(BASEPos_Koord))
        writelog('_________________KUKA_OT_Export - BASEPos_Angle' +'X C {0:.3f}'.format(BASEPos_Angle[0])+' X C {0:.3f}'.format(BASEPos_Angle[1])+' Z A {0:.3f}'.format(BASEPos_Angle[2]))
        writelog('_________________SAFEPos_Koord: ' + str(SAFEPos_Koord))
        writelog('_________________SAFEPos_Angle' +'X C {0:.3f}'.format(SAFEPos_Angle[0])+' B Y {0:.3f}'.format(SAFEPos_Angle[1])+' Z A {0:.3f}'.format(SAFEPos_Angle[2]))
        #--------------------------------------------------------------------------------
        
        bpy.ops.object.select_all(action='DESELECT')
        objEmpty_A6.select=True
        bpy.context.scene.objects.active = objEmpty_A6
        
        return {'FINISHED'}
    writelog('KUKA_OT_Export done')  

class KUKA_OT_Import (bpy.types.Operator, ImportHelper): # OT fuer Operator Type
    writelog('KUKA_OT_Import- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ') 
    writelog('- - - - - - - - - - - - -  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')
    ''' Import selected curve '''
    bl_idname = "object.kuka_import"
    bl_label = "KUKA_OT_Import (TB)" #Toolbar - Label
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
        writelog('- - - - - - - - - - - - -  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')
        writelog(' FUNKTIONSAUFRUF KUKA_OT_Import')
        writelog('- - - - - - - - - - - - -  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')
        
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
        
        writelog("Erstellen der BezierCurve: done")
        BASEPos_Koord, BASEPos_Angle = RfF_KeyPos('BASEPos', self.filepath, '.cfg')
        try:
            ADJUSTMENTPos_Koord, ADJUSTMENTPos_Angle = RfF_KeyPos('ADJUSTMENTPos', self.filepath, '.cfg')
        except:
            writelog('failed to load AdjustmentPos')
        try:
            HOMEPos_Koord, HOMEPos_Angle = RfF_KeyPos('HOMEPos', self.filepath, '.cfg')
        except:
            writelog('failed to load HomePos')
        writelog('_________________KUKA_OT_Import - BASEPos_Koord' + str(BASEPos_Koord))
        writelog('_________________KUKA_OT_Import - BASEPos_Angle' +'X C {0:.3f}'.format(BASEPos_Angle[0])+' B Y {0:.3f}'.format(BASEPos_Angle[1])+' A Z {0:.3f}'.format(BASEPos_Angle[2]))
        
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
       
        writelog('_________________KUKA_OT_Import - BASEPos_Koord' + str(BASEPos_Koord))
        writelog('_________________KUKA_OT_Import - BASEPos_Angle' + str(BASEPos_Angle))
        SAFEPos_Koord, SAFEPos_Angle = RfF_KeyPos('PTP', self.filepath, '.src') # PTP = SAFEPos
        writelog('_________________KUKA_OT_Import - BASEPos_Koord' + str(BASEPos_Koord))
        writelog('_________________KUKA_OT_Import - BASEPos_Angle' +'X C {0:.3f}'.format(BASEPos_Angle[0])+' B Y {0:.3f}'.format(BASEPos_Angle[1])+' A Z {0:.3f}'.format(BASEPos_Angle[2]))
        writelog('_________________SAFEPos_Koord: ' + str(SAFEPos_Koord))
        writelog('_________________SAFEPos_Angle' +'X C {0:.3f}'.format(SAFEPos_Angle[0])+' B Y {0:.3f}'.format(SAFEPos_Angle[1])+' A Z {0:.3f}'.format(SAFEPos_Angle[2]))
        # Achtung: Die Reihenfolge der Aufrufe von SetBasePos und get_absolute darf nicht vertauscht werden!
        
        objSafe.location, objSafe.rotation_euler = get_absolute(SAFEPos_Koord, SAFEPos_Angle, BASEPos_Koord, BASEPos_Angle )        #Transformation Local2World
        writelog('_________________KUKA_OT_Import - BASEPos_Koord' + str(BASEPos_Koord))
        writelog('_________________KUKA_OT_Import - BASEPos_Angle' +'X C {0:.3f}'.format(BASEPos_Angle[0])+' B Y {0:.3f}'.format(BASEPos_Angle[1])+' A Z {0:.3f}'.format(BASEPos_Angle[2]))
        writelog('_________________SAFEPos_Koord: ' + str(SAFEPos_Koord))
        writelog('_________________SAFEPos_Angle' +'A {0:.3f}'.format(SAFEPos_Angle[0])+' B {0:.3f}'.format(SAFEPos_Angle[1])+' C {0:.3f}'.format(SAFEPos_Angle[2]))
        
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
    writelog('KUKA_OT_Import done')

class KUKA_OT_RefreshButton (bpy.types.Operator):
    writelog('KUKA_OT_RefreshButton- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ') 
    writelog('- - - - - - - - - - - - -  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')
    
    
    ''' Import selected curve '''
    bl_idname = "object.refreshbutton"
    bl_label = "Refresh (TB)" #Toolbar - Label
    bl_description = "Set Animation Data" # Kommentar im Specials Kontextmenue
    bl_options = {'REGISTER', 'UNDO'} #Set this options, if you want to update  
    #                                  parameters of this operator interactively 
    #                                  (in the Tools pane) 
 
    def execute(self, context):  
        writelog('- - -refreshbutton - - - - - - -')
        writelog('Testlog von KUKA_OT_RefreshButton')
        
        objBase.rotation_mode     = RotationModeBase
        objSafe.rotation_mode     = RotationModePATHPTS
        objCurve.rotation_mode    = RotationModePATHPTS
        objEmpty_A6.rotation_mode = RotationModeEmpty_Zentralhand_A6
        
        
        ApplyScale(objCurve) 
        #--------------------------------------------------------------------------------
        
        BASEPos_Koord, BASEPos_Angle = objBase.location, objBase.rotation_euler
        HOMEPos_Koord, HOMEPos_Angle = objHome.location, objHome.rotation_euler
        
        SAFEPos_Koord, SAFEPos_Angle = get_relative(objSafe.location, objSafe.rotation_euler, BASEPos_Koord, BASEPos_Angle)
        PATHPTSObjList, countPATHPTSObj  = count_PATHPTSObj(PATHPTSObjName)
        
        
        #dataPATHPTS_Loc, dataPATHPTS_Rot, PATHPTSCountFile = get_relative(objSafe, objSafe.location, objSafe.rotation_euler, BASEPos_Koord, BASEPos_Angle)
        
        SetOrigin(objCurve, objBase)
        bpy.data.objects[objCurve.name].rotation_mode =RotationModePATHPTS
        objCurve.location       = BASEPos_Koord.x,BASEPos_Koord.y ,BASEPos_Koord.z 
        objCurve.rotation_euler = BASEPos_Angle
        
        
        filepath ='none'
        Route_ObjList = DefRoute(objEmpty_A6, filepath)
        countRoute_ObjList = len(Route_ObjList)
        PathPoint = createMatrix(countRoute_ObjList,3)
        PathAngle = createMatrix(countRoute_ObjList,3)
        for i in range(countRoute_ObjList):    
            PathPoint[i][0:3], PathAngle[i][0:3] = get_relative(bpy.data.objects[Route_ObjList[i]].location, bpy.data.objects[Route_ObjList[i]].rotation_euler, BASEPos_Koord, BASEPos_Angle)        
        
        replace_CP(objCurve, PathPoint)  #relativ, weil Origin der Kurve auf BasePos liegt!
        
        bpy.ops.object.select_all(action='DESELECT')
        objEmpty_A6.select=True
        bpy.context.scene.objects.active = objEmpty_A6
        
        return {'FINISHED'} 
    writelog('- - -KUKA_OT_RefreshButton done- - - - - - -')     



def DefRoute(objEmpty_A6, filepath):
    # Diese Funktion wird erst interessant, wenn Routen ueber mehrere Objektgruppen erzeugt werden sollen.
    # in RefreshButton den Ablauf: [HomePos, n x (Safepos, PATHPTS, Safepos), HomePos] festlegen        
    
    # 1. Schritt: Umsetzung nur fuer einfache Reihenfolge
    
    # todo: GUI Liste abfragen (falls vorhanden) Reihenfolge der Objektgruppen/-Objekte zum erstellen der Route
    # n x [....] beruecksichtigen...???
    
    # todo: Bei Bearbeitung und Konkatonierung per GUI Ablauf (Object.RouteNbr)
    
    # Festlegen der TIMEPTS fuer jedes beteiligte Objekt:
    PATHPTSObjList, countPATHPTSObj  = count_PATHPTSObj(PATHPTSObjName)
    PATHPTSObjList =  renamePATHObj(PATHPTSObjList)
        
    if filepath != 'none': # Aufruf von Button Import
        TIMEPTS_PATHPTS, NAN = RfF_KeyPos('TIMEPTS', filepath, '.dat')
        TIMEPTS_PATHPTSCount = len (TIMEPTS_PATHPTS)
        
        # Korrektur der TIMEPTS Werte, wenn kleiner der Anzahl an PATHPTS:
        TIMEPTS_PATHPTS = ValidateTIMEPTS(PATHPTSObjList, TIMEPTS_PATHPTS)
        
        for i in range(TIMEPTS_PATHPTSCount):    
            bpy.data.objects[PATHPTSObjList[i]].kuka.TIMEPTS = TIMEPTS_PATHPTS[i]
        
    elif filepath == 'none': # Aufruf von Button RefreshButton
        #TIMEPTS_PATHPTS, TIMEPTS_PATHPTSCount = RfS_TIMEPTS(objEmpty_A6)
        TIMEPTS_PATHPTS = []
        for i in range(countPATHPTSObj):
            TIMEPTS_PATHPTS = TIMEPTS_PATHPTS + [bpy.data.objects[PATHPTSObjList[i]].kuka.TIMEPTS]
            if TIMEPTS_PATHPTS[i] == 0:
                TIMEPTS_PATHPTS[i] = TIMEPTS_PATHPTS[i-1]+1
                bpy.data.objects[PATHPTSObjList[i]].kuka.TIMEPTS = TIMEPTS_PATHPTS[i]
            
    # Korrektur der TIMEPTS Werte, wenn kleiner der Anzahl an PATHPTS:  
    TIMEPTS_PATHPTS = ValidateTIMEPTS(PATHPTSObjList, TIMEPTS_PATHPTS)
    TIMEPTS_PATHPTSCount = len (TIMEPTS_PATHPTS)   # Achtung: Aufruf dieser Zeile vor ValidateTIMEPTS hat die uebergabe von TIMEPTS_PATHPTS in INTEGER gewandelt!
    
    TIMEPTS_Safe = TIMEPTS_PATHPTS[TIMEPTS_PATHPTSCount-1] + 2 # Sekunden
    objSafe.kuka.TIMEPTS = TIMEPTS_Safe
    TIMEPTS_Home = 0 # Sekunden
    objHome.kuka.TIMEPTS = TIMEPTS_Home
    
    # todo: Aufrufen der HomePos am Anfang und am Ende... (RouteNbr)
    
    # Festlegen der Reihenfolge der Objekte:
    Route_ObjList = [objHome.name] + PATHPTSObjList + [objSafe.name]
    Route_TIMEPTS = [TIMEPTS_Home] + TIMEPTS_PATHPTS + [TIMEPTS_Safe]          

    #Route_ObjList = PATHPTSObjList + [objSafe.name]
    #Route_TIMEPTS = TIMEPTS_PATHPTS + [TIMEPTS_Safe]      
    
    #Route_ObjList = PATHPTSObjList
    #Route_TIMEPTS = TIMEPTS_PATHPTS
    
    OptimizeRotation(Route_ObjList) 
     
    # todo: Validierung der Objekte.TIMEPTS (ob jedes Objekt einen plausiblen Wert hat)
    
    SetKeyFrames(objEmpty_A6, Route_ObjList, Route_TIMEPTS)
    return Route_ObjList
    
         
def SetKeyFrames(objEmpty_A6, TargetObjList, TIMEPTS):
    # Diese Funktion soll spaeter anhand einer chronologisch geordneten Objektgruppen 
    # und Objekt/PATHPTS - Liste die KeyFrames eintragen
    
    original_type         = bpy.context.area.type
    bpy.context.area.type = "VIEW_3D"
    bpy.ops.object.select_all(action='DESELECT')
          
    #scene = bpy.context.scene
    #fps = scene.render.fps
    #fps_base = scene.render.fps_base
     
    raw_time=[]
    frame_number=[]
    
    bpy.context.scene.objects.active = objEmpty_A6
    
    objEmpty_A6.select = True
    bpy.ops.anim.keyframe_clear_v3d() #Remove all keyframe animation for selected objects

    ob = bpy.context.active_object
    ob.rotation_mode = 'QUATERNION'
    
    #QuaternionList = OptimizeRotationQuaternion(TargetObjList, TIMEPTSCount)
    
    for n in range(len(TargetObjList)):
        writelog(n)
        #bpy.context.scene.frame_set(time_to_frame(TIMEPTS[n])) 
        bpy.context.scene.frame_set(time_to_frame(bpy.data.objects[TargetObjList[n]].kuka.TIMEPTS))
        ob.location = bpy.data.objects[TargetObjList[n]].location
        # todo - done: keyframes auf quaternion um gimbal lock zu vermeiden
                
        ob.rotation_quaternion = bpy.data.objects[TargetObjList[n]].rotation_euler.to_quaternion()
           
        ob.keyframe_insert(data_path="location", index=-1)
        # file:///F:/EWa_WWW_Tutorials/Scripting/blender_python_reference_2_68_5/bpy.types.bpy_struct.html#bpy.types.bpy_struct.keyframe_insert
        
        ob.keyframe_insert(data_path="rotation_quaternion", index=-1)
        #ob.keyframe_insert(data_path="rotation_euler", index=-1)
            
    if len(TIMEPTS)> len(TargetObjList):
        writelog('Achtung: mehr TIMEPTS als PATHPTS-Objekte vorhanden')
    # todo: end frame not correct if PATHPTS added....
    bpy.context.scene.frame_end = time_to_frame(TIMEPTS[len(TIMEPTS)-1])
    
    bpy.data.scenes['Scene'].frame_current=1
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.area.type = original_type 
                 


def create_PATHPTSObj(dataPATHPTS_Loc, dataPATHPTS_Rot, PATHPTSCountFile, BASEPos_Koord, BASEPos_Angle ):
    # Aufruf von: KUKA_OT_Import
    original_type = bpy.context.area.type
    bpy.context.area.type = "VIEW_3D" 
    bpy.ops.object.select_all(action='DESELECT')
    writelog('_____________________________________________________________________________')
    writelog('create_PATHPTSObj')
    # erstellen von 'PATHPTSCountFile' Mesh Objekten an den Positionen 'dataPATHPTS_Loc' mit der Ausrichtung 'dataPATHPTS_Rot'
    PATHPTSObjName = 'PTPObj_'
    # 1. Wieviele PTPObj Objekte sind in der Scene vorhanden? (Beachte: Viele Objekte koennen den selben Datencontainer verwenden)
    PATHPTSObjList, countPATHPTSObj  = count_PATHPTSObj(PATHPTSObjName)
    writelog('Es sind ' + str(countPATHPTSObj) + 'PATHPTSObj in der Szene vorhanden.' )
    writelog('Folgende PATHPTSObj wurden in der Szene gefunden: ' + str(PATHPTSObjList))
    # Datencontainer:  
    for mesh in bpy.data.meshes:
        writelog(mesh.name)  
    # 2. Anpassen der Anzahl der Objekte auf 'PATHPTSCountFile'
    # sicherstellen das kein ControlPoint selektiert ist:
    bpy.ops.object.select_all(action='DESELECT')
    
    if PATHPTSCountFile <= countPATHPTSObj:
        CountCP = countPATHPTSObj
        writelog('Der Import hat weniger oder gleich viele PATHPTS als in der Szene bereits vorhanden.')
    if PATHPTSCountFile > countPATHPTSObj:
        CountCP = PATHPTSCountFile
        writelog('Der Import hat mehr PATHPTS als in der Szene bereits vorhanden.')
    # 3. Zuweisen von dataPATHPTS_Loc
    # 4. Zuweisen von dataPATHPTS_Rot
    # kuerze die Laenge der aktuellen Kurve auf die File-Kurve, wenn noetig
    if PATHPTSCountFile < countPATHPTSObj:
        writelog('Loeschen der ueberfluessigen PATHPTS Objekte aus der Szene...')
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
            writelog('Waehle Objekt aus: ' + str(PATHPTSObjList[n]))
            
            if (PATHPTSCountFile-1) >= n: # Wenn ein Datenpunkt (PATHPTS) im File da ist, uebertrage loc und rot auf PATHPTSObj
                writelog('PATHPTS Objekt ' + str(n) + ' vorhanen:' + str(bpy.data.objects[PATHPTSObjList[n]].name))
                writelog('IF - uebertrage loc: ' + str(dataPATHPTS_Loc[n]) 
                      + ' und rot Daten:' + str(dataPATHPTS_Rot[n]) 
                      + ' vom File auf Objekt:' + str(PATHPTSObjList[n]))
                
                bpy.data.objects[PATHPTSObjList[n]].rotation_mode =RotationModePATHPTS
                
                #get_absolute(bpy.data.objects[PATHPTSObjList[n]], Vector(dataPATHPTS_Loc[n]), dataPATHPTS_Rot[n], BASEPos_Koord, BASEPos_Angle) #Transformation Local2World
                bpy.data.objects[PATHPTSObjList[n]].location, bpy.data.objects[PATHPTSObjList[n]].rotation_euler = get_absolute(Vector(dataPATHPTS_Loc[n]), dataPATHPTS_Rot[n], BASEPos_Koord, BASEPos_Angle) #Transformation Local2World
                
                      
        else: # wenn kein Kurvenpunkt zum ueberschreiben da ist, generiere einen neuen und schreibe den File-Datenpunkt
            writelog('Kein weiteres PATHPTS Objekt mehr in der Szene vorhanden.')
            writelog('Erstelle neues PATHPTS Objekt.')
            
            # add an new MESH object
            writelog('bpy.context.area.type: ' + bpy.context.area.type)
            bpy.ops.object.add(type='MESH')  
            #bpy.context.object.name = PATHPTSObjName + str(n+1) # "%03d" % 2
            bpy.context.object.name = PATHPTSObjName + str("%03d" %(n+1)) # "%03d" % 2
            PATHPTSObjList, countPATHPTSObj  = count_PATHPTSObj(PATHPTSObjName)
            bpy.data.objects[PATHPTSObjList[n]].data = bpy.data.objects[PATHPTSObjList[1]].data
            
            # todo - test: .TIMEPTS einfuegen - eigene Class fuer PATHPTS erstellen!!!
            
            
            writelog('IF - uebertrage loc: ' + str(dataPATHPTS_Loc[n]) 
                      + ' und rot Daten:' + str(dataPATHPTS_Rot[n]) 
                      + ' vom File auf Objekt:' + str(PATHPTSObjList[n]))
            bpy.data.objects[PATHPTSObjList[n]].rotation_mode =RotationModePATHPTS
            
            #get_absolute(bpy.data.objects[PATHPTSObjList[n]], Vector(dataPATHPTS_Loc[n]), dataPATHPTS_Rot[n], BASEPos_Koord, BASEPos_Angle) #Transformation Local2World
            bpy.data.objects[PATHPTSObjList[n]].location, bpy.data.objects[PATHPTSObjList[n]].rotation_euler = get_absolute(Vector(dataPATHPTS_Loc[n]), dataPATHPTS_Rot[n], BASEPos_Koord, BASEPos_Angle) #Transformation Local2World
               
    bpy.context.area.type = original_type 
    writelog('create_PATHPTSObj done')
    writelog('_____________________________________________________________________________')
    
    

       
class KUKA_PT_Panel(bpy.types.Panel):
    writelog('_____________________________________________________________________________')
    writelog()
    writelog('KUKA_PT_Panel....')
    writelog()
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
        sub.operator("object.kuka_import")  
        row.operator("object.kuka_export") 
        
        # Set KeyFrames Button:
        layout.label(text="Refresh Button:")
        row = layout.row(align=True)
        
        row.operator("object.refreshbutton")  
           
    writelog('KUKA_PT_Panel done')
    writelog('_____________________________________________________________________________')


#class CURVE_OT_RefreshButtonButton(bpy.types.Operator):
 



    



# ________________________________________________________________________________________________________________________


#--- ### Register
#ToDo: KUKA Operator nicht regestriert....
def register():
    bpy.utils.register_class(KUKA_PT_Panel)  
    register_module(__name__)
    
def unregister():
    bpy.utils.unregister_class(KUKA_PT_Panel) 
    unregister_module(__name__)

#--- ### Main code    
if __name__ == '__main__':
    register()
