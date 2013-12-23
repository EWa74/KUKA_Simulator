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
# bpy.data.objects['OBJ_KUKA_Armature'].pose.bones['Bone_KUKA_Zentralhand_A4'].rotation_euler 
# handling vom POP UP window: alternativ *.src laden ODER default TP auswaehlen --> Panel(bpy_struct)
# button um nach editieren der Kurve das Kuka_Empty auf den ersten Kurvenpunkt zu setzen

# KUKA Modell richtig ausrichten (und spiegeln, da z.Zt. spiegelverkehrt)
# ARMATURE: Position und Winkel auf Plausibilitaet abfragen: bone constraints eingestellt; werden diese ueberschritten "springt" der Arm
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
 
# ToDo: ToolPosition (oder Baseposition) auslesen und offset beruecksichtigen MES ={ :  enthalten in *.dat -> OBJ_KUKA_EndEffector zuweisen
# BasePosition: (noch kein korrespondierender KUKA File bekannt !!! -> ALe
# todo: globale variablen definieren??.....
# todo: Verschiedene Import/ Export Funktionen beruecksichtigen (XYZ/ KUKA YXZ)
# todo: obj. rename um 001.001 etc. zu vermeiden!!!
# Datenmodell und Funktionen beschreiben!!!

# TODO: pruefen ob TIMEPTS = PATHPTS ist und ggf. neue keyframes und TIMEPTS setzen -> Funktion RefreshButton
# TODO: Beschriftung der PATHPTS im 3D view
# TODO: GUI Feld um die Winkel bezogen auf Base oder Tool (bez. sich auf Base) editieren zu k�nnen
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
RotationModeEmpty_Zentralhand_A6 = Mode

RotationModeTransform = Mode # XYZ YXZ

Vorz1 = +1#-1 # +C = X
Vorz2 = +1#-1 # -B = Y
Vorz3 = +1#-1 # -A = Z

# Erg.: Einstellung noch nicht verstanden....
# + + + : Y nach rechts verdr. Z Tool = -X PATHPTS / 
# + + - : +x-y-z, Bahn dreht rechts 
# + - + : +x-y-z, Bahn dreht rechts 
# + - - : +x-y-z, Bahn dreht rechts, OK, nur Schale m�sste umgedreht werden 
# - + + : +x-y-z, Bahn dreht rechts
# - + - : +x-y-z, Bahn dreht links
# - - + : +x-y-z, Bahn dreht links
# - - - : +x-y-z, Bahn dreht links
        
#objEmpty_A6 = bpy.data.objects['Empty_Zentralhand_A6']
CalledFrom =[] 
filepath=[]
   
def WtF_BasePos(BASEPos_Koord, BASEPos_Angle, filepath):
    print('_____________________________________________________________________________')
    print('WtF_BasePos ')
    print('Remark: this file is not a part of the normal KUKA Ocutbot Software.')
    print('BASEPos_Angle A - Z [2]: ' +str(BASEPos_Angle[2]))
    print('BASEPos_Angle B - Y [1]: ' +str(BASEPos_Angle[1]))    #
    print('BASEPos_Angle C - X [0]: ' +str(BASEPos_Angle[0])) 
    FilenameSRC = filepath
    FilenameSRC = FilenameSRC.replace(".dat", ".cfg") 
    fout = open(FilenameSRC, 'w')
     
    SkalierungPTP = 1000
    # ABC ->CBA
    fout.write("BASEPos {" + 
                   "X " + "{0:.5f}".format(BASEPos_Koord[0]*SkalierungPTP) + 
                   ", Y " + "{0:.5f}".format(BASEPos_Koord[1]*SkalierungPTP) +
                   ", Z " + "{0:.5f}".format(BASEPos_Koord[2]*SkalierungPTP) + 
                   ", A " + "{0:.5f}".format(BASEPos_Angle[2]) +
                   ", B " + "{0:.5f}".format(BASEPos_Angle[1]) + 
                   ", C " + "{0:.5f}".format(BASEPos_Angle[0]) +
                   "} " + "\n")
    
    fout.close();
    print('WtF_BasePos geschrieben.')
    print('_____________________________________________________________________________')

# TODO: Funktionen verallgemeinern: WtF HOMEPos, BasePos, SafePos, AdjPos arbeiten gleich... 

def WtF_HomePos(HOMEPos_Koord, HOMEPos_Angle, filepath):
    print('_____________________________________________________________________________')
    print('WtF_BasePos ')
    print('Remark: this file is not a part of the normal KUKA Ocutbot Software.')
    print('HOMEPos_Angle A - Z [2]: ' +str(HOMEPos_Angle[2]))
    print('HOMEPos_Angle B - Y [1]: ' +str(HOMEPos_Angle[1]))    #
    print('HOMEPos_Angle C - X [0]: ' +str(HOMEPos_Angle[0])) 
    FilenameSRC = filepath
    FilenameSRC = FilenameSRC.replace(".dat", ".cfg") 
    fout = open(FilenameSRC, 'a')
     
    SkalierungPTP = 1000
    # ABC ->CBA
    
    #HOMEPos {X 418.8189, Y 644.8495, Z 1223.978, A -178.2708, B -0.4798438, C -128.1682} 
    fout.write("HOMEPos {" + 
                   "X " + "{0:.5f}".format(HOMEPos_Koord[0]*SkalierungPTP) + 
                   ", Y " + "{0:.5f}".format(HOMEPos_Koord[1]*SkalierungPTP) +
                   ", Z " + "{0:.5f}".format(HOMEPos_Koord[2]*SkalierungPTP) + 
                   ", A " + "{0:.5f}".format(Vorz3 *HOMEPos_Angle[2]) +
                   ", B " + "{0:.5f}".format(Vorz2 *HOMEPos_Angle[1]) + 
                   ", C " + "{0:.5f}".format(Vorz1 *HOMEPos_Angle[0]) +
                   "} " + "\n")
    
    fout.close();
    print('WtF_HomePos geschrieben.')
    print('_____________________________________________________________________________')
    
def WtF_AdjustmentPos(ADJUSTMENTPos_Koord, ADJUSTMENTPos_Angle, filepath):
    print('_____________________________________________________________________________')
    print('WtF_AdjustmentPos ')
    print('Remark: this file is not a part of the normal KUKA Ocutbot Software.')
    print('ADJUSTMENTPos_Angle A - Z [2]: ' +str(ADJUSTMENTPos_Angle[2]))
    print('ADJUSTMENTPos_Angle B - Y [1]: ' +str(ADJUSTMENTPos_Angle[1]))    #
    print('ADJUSTMENTPos_Angle C - X [0]: ' +str(ADJUSTMENTPos_Angle[0])) 
    FilenameSRC = filepath
    FilenameSRC = FilenameSRC.replace(".dat", ".cfg") 
    fout = open(FilenameSRC, 'a')
     
    SkalierungPTP = 1000
    # ABC ->CBA
    
    #ADJUSTMENTPos {X 0.0, Y 0.0, Z 0.0, A 0.0, B 0.0, C 0.0}
    fout.write("ADJUSTMENTPos {" + 
                   "X " + "{0:.5f}".format(ADJUSTMENTPos_Koord[0]*SkalierungPTP) + 
                   ", Y " + "{0:.5f}".format(ADJUSTMENTPos_Koord[1]*SkalierungPTP) +
                   ", Z " + "{0:.5f}".format(ADJUSTMENTPos_Koord[2]*SkalierungPTP) + 
                   ", A " + "{0:.5f}".format(Vorz3 *ADJUSTMENTPos_Angle[2]) +
                   ", B " + "{0:.5f}".format(Vorz2 *ADJUSTMENTPos_Angle[1]) + 
                   ", C " + "{0:.5f}".format(Vorz1 *ADJUSTMENTPos_Angle[0]) +
                   "} " + "\n")
     
    fout.close();
    print('WtF_AdjustmentPos geschrieben.')
    print('_____________________________________________________________________________')
    
def WtF_SafePos(SAFEPos_Koord, SAFEPos_Angle, filepath):
    print('_____________________________________________________________________________')
    print('WtF_SafePos ')
    print('Exporting ' + filepath)
    print('SAFEPos_Koord: ' + str(SAFEPos_Koord))
    print('SAFEPos_Angle C - X [0],B - Y [1], A - Z [2]: ' + str(SAFEPos_Angle)) 
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
    # ABC ->CBA
    fout.write("PTP {" + 
                   "X " + "{0:.5f}".format(SAFEPos_Koord[0]*SkalierungPTP) + 
                   ", Y " + "{0:.5f}".format(SAFEPos_Koord[1]*SkalierungPTP) +
                   ", Z " + "{0:.5f}".format(SAFEPos_Koord[2]*SkalierungPTP) + 
                   ", A " + "{0:.5f}".format(Vorz3 *SAFEPos_Angle[2]) +
                   ", B " + "{0:.5f}".format(Vorz2 *SAFEPos_Angle[1]) + 
                   ", C " + "{0:.5f}".format(Vorz1 *SAFEPos_Angle[0]) +
                   "} " + "\n")
    
    fout.close();
    
    print('SAFEPosition geschrieben.')
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

def RfF_AdjustmentPos(filepath):
    print('_____________________________________________________________________________')
    print('Read from File - RfF_AdjustmentPos')
    
    # ==========================================    
    # Import der RfF_AdjustmentPos = KUKA (*.cfg) Kreation von mir!
    # Die Adjustmentposition soll die Verschiebung des realen Roboters zur virtuellen CAD-Welt ber�cksichtigen [TEST]
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
        suchAnf = "ADJUSTMENTPos {X"
        suchEnd = "ADJUSTMENTPos {X"
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
        # ADJUSTMENTPos {X 0.0, Y 0.0, Z 0.0, A -128.2708, B -0.4798438, C -178.1682} 
        # MES = {X -237, Y 0, Z 342, A 0, B 0, C 0 }
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
            IndXA = zeilenliste[PathIndexAnf+i].index("X ", beg, len(zeilenliste[PathIndexAnf+i])) # Same as find(), but raises an exception if str not found 
            IndXE = zeilenliste[PathIndexAnf+i].index(", Y", beg, len(zeilenliste[PathIndexAnf+i]))
            PTPX = PTPX + [float(zeilenliste[PathIndexAnf+i][IndXA+2:IndXE])]
       
            IndYA = zeilenliste[PathIndexAnf+i].index("Y ", beg, len(zeilenliste[PathIndexAnf+i]))  
            IndYE = zeilenliste[PathIndexAnf+i].index(", Z", beg, len(zeilenliste[PathIndexAnf+i]))
            PTPY = PTPY + [float(zeilenliste[PathIndexAnf+i][IndYA+2:IndYE])]
       
            IndZA = zeilenliste[PathIndexAnf+i].index("Z ", beg, len(zeilenliste[PathIndexAnf+i])) 
            IndZE = zeilenliste[PathIndexAnf+i].index(", A", beg, len(zeilenliste[PathIndexAnf+i]))
            PTPZ = PTPZ + [float(zeilenliste[PathIndexAnf+i][IndZA+2:IndZE])]
       
            IndAA = zeilenliste[PathIndexAnf+i].index("A ", beg, len(zeilenliste[PathIndexAnf+i])) 
            IndAE = zeilenliste[PathIndexAnf+i].index(", B", beg, len(zeilenliste[PathIndexAnf+i]))
            PTPAngleA = PTPAngleA + [float(zeilenliste[PathIndexAnf+i][IndAA+2:IndAE])] # * (2*math.pi)/360 als rad einlesen!
            print('PTPAngleA' +str(PTPAngleA))
            IndBA = zeilenliste[PathIndexAnf+i].index("B ", beg, len(zeilenliste[PathIndexAnf+i]))  
            IndBE = zeilenliste[PathIndexAnf+i].index(", C", beg, len(zeilenliste[PathIndexAnf+i]))
            PTPAngleB = PTPAngleB + [float(zeilenliste[PathIndexAnf+i][IndBA+2:IndBE])]
            print('PTPAngleB' +str(PTPAngleB))
            IndCA = zeilenliste[PathIndexAnf+i].index("C ", beg, len(zeilenliste[PathIndexAnf+i]))  
            IndCE = len(zeilenliste[PathIndexAnf+i])-2 # }   " "+chr(125) funktioniert nicht?!
            PTPAngleC = PTPAngleC + [float(zeilenliste[PathIndexAnf+i][IndCA+2:IndCE])]
            print('PTPAngleC' +str(PTPAngleC))
        SkalierungPTP = 1000
        
        ADJUSTMENTPos_Koord  = Vector([float(PTPX[0])/SkalierungPTP, float(PTPY[0])/SkalierungPTP, float(PTPZ[0])/SkalierungPTP])
        # XYZ = CBA
        # A = -Z
        # TESTEN!!!!
        ADJUSTMENTPos_Angle  = float(str(Vorz1 *PTPAngleC[0])), float(str(Vorz1 *PTPAngleB[0])), float(str(Vorz1 *PTPAngleA[0])) # in Grad
    except: 
        print('RfF_AdjustmentPos exception')
    print('RfF_AdjustmentPos done')
    print('_____________________________________________________________________________')
    return ADJUSTMENTPos_Koord, ADJUSTMENTPos_Angle    

def RfF_HomePos(filepath):
    print('_____________________________________________________________________________')
    print('Read from File - RfF_HomePos')
    
    # ==========================================    
    # Import der RfF_HomePos = KUKA (*.cfg) Kreation von mir!
    # Die RfF_HomePosition sol ...
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
        suchAnf = "HOMEPos {X"
        suchEnd = "HOMEPos {X"
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
        # HOMEPos {X 653.4455, Y 922.3803, Z 842.2034, A -128.2708, B -0.4798438, C -178.1682} 
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
            IndXA = zeilenliste[PathIndexAnf+i].index("X ", beg, len(zeilenliste[PathIndexAnf+i])) # Same as find(), but raises an exception if str not found 
            IndXE = zeilenliste[PathIndexAnf+i].index(", Y", beg, len(zeilenliste[PathIndexAnf+i]))
            PTPX = PTPX + [float(zeilenliste[PathIndexAnf+i][IndXA+2:IndXE])]
       
            IndYA = zeilenliste[PathIndexAnf+i].index("Y ", beg, len(zeilenliste[PathIndexAnf+i]))  
            IndYE = zeilenliste[PathIndexAnf+i].index(", Z", beg, len(zeilenliste[PathIndexAnf+i]))
            PTPY = PTPY + [float(zeilenliste[PathIndexAnf+i][IndYA+2:IndYE])]
       
            IndZA = zeilenliste[PathIndexAnf+i].index("Z ", beg, len(zeilenliste[PathIndexAnf+i])) 
            IndZE = zeilenliste[PathIndexAnf+i].index(", A", beg, len(zeilenliste[PathIndexAnf+i]))
            PTPZ = PTPZ + [float(zeilenliste[PathIndexAnf+i][IndZA+2:IndZE])]
       
            IndAA = zeilenliste[PathIndexAnf+i].index("A ", beg, len(zeilenliste[PathIndexAnf+i])) 
            IndAE = zeilenliste[PathIndexAnf+i].index(", B", beg, len(zeilenliste[PathIndexAnf+i]))
            PTPAngleA = PTPAngleA + [float(zeilenliste[PathIndexAnf+i][IndAA+2:IndAE])] # * (2*math.pi)/360 als rad einlesen!
            print('PTPAngleA' +str(PTPAngleA))
            IndBA = zeilenliste[PathIndexAnf+i].index("B ", beg, len(zeilenliste[PathIndexAnf+i]))  
            IndBE = zeilenliste[PathIndexAnf+i].index(", C", beg, len(zeilenliste[PathIndexAnf+i]))
            PTPAngleB = PTPAngleB + [float(zeilenliste[PathIndexAnf+i][IndBA+2:IndBE])]
            print('PTPAngleB' +str(PTPAngleB))
            IndCA = zeilenliste[PathIndexAnf+i].index("C ", beg, len(zeilenliste[PathIndexAnf+i]))  
            IndCE = len(zeilenliste[PathIndexAnf+i])-2 # }   " "+chr(125) funktioniert nicht?!
            PTPAngleC = PTPAngleC + [float(zeilenliste[PathIndexAnf+i][IndCA+2:IndCE])]
            print('PTPAngleC' +str(PTPAngleC))
        SkalierungPTP = 1000
        
        HOMEPos_Koord  = Vector([float(PTPX[0])/SkalierungPTP, float(PTPY[0])/SkalierungPTP, float(PTPZ[0])/SkalierungPTP])
        # XYZ = CBA
        # A = -Z
        # TESTEN!!!!
        HOMEPos_Angle  = float(str(Vorz1 *PTPAngleC[0])), float(str(Vorz2 *PTPAngleB[0])), float(str(Vorz3 *PTPAngleA[0])) # in Grad
    except: 
        print('RfF_AdjustmentPos exception')
    print('RfF_HomePos done')
    print('_____________________________________________________________________________')
    return HOMEPos_Koord, HOMEPos_Angle 

 
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
        # BASEPos {X 82.815240, Y 100.194500, Z -11.291560, A(Z) 69.842480, B(Y) -2.680786, C(X) -3.097058}
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
            IndXA = zeilenliste[PathIndexAnf+i].index("X ", beg, len(zeilenliste[PathIndexAnf+i])) # Same as find(), but raises an exception if str not found 
            IndXE = zeilenliste[PathIndexAnf+i].index(", Y", beg, len(zeilenliste[PathIndexAnf+i]))
            PTPX = PTPX + [float(zeilenliste[PathIndexAnf+i][IndXA+2:IndXE])]
       
            IndYA = zeilenliste[PathIndexAnf+i].index("Y ", beg, len(zeilenliste[PathIndexAnf+i]))  
            IndYE = zeilenliste[PathIndexAnf+i].index(", Z", beg, len(zeilenliste[PathIndexAnf+i]))
            PTPY = PTPY + [float(zeilenliste[PathIndexAnf+i][IndYA+2:IndYE])]
       
            IndZA = zeilenliste[PathIndexAnf+i].index("Z ", beg, len(zeilenliste[PathIndexAnf+i])) 
            IndZE = zeilenliste[PathIndexAnf+i].index(", A", beg, len(zeilenliste[PathIndexAnf+i]))
            PTPZ = PTPZ + [float(zeilenliste[PathIndexAnf+i][IndZA+2:IndZE])]
       
            IndAA = zeilenliste[PathIndexAnf+i].index("A ", beg, len(zeilenliste[PathIndexAnf+i])) 
            IndAE = zeilenliste[PathIndexAnf+i].index(", B", beg, len(zeilenliste[PathIndexAnf+i]))
            PTPAngleA = PTPAngleA + [float(zeilenliste[PathIndexAnf+i][IndAA+2:IndAE])] # * (2*math.pi)/360 als rad einlesen!
            print('PTPAngleA' +str(PTPAngleA))
            IndBA = zeilenliste[PathIndexAnf+i].index("B ", beg, len(zeilenliste[PathIndexAnf+i]))  
            IndBE = zeilenliste[PathIndexAnf+i].index(", C", beg, len(zeilenliste[PathIndexAnf+i]))
            PTPAngleB = PTPAngleB + [float(zeilenliste[PathIndexAnf+i][IndBA+2:IndBE])]
            print('PTPAngleB' +str(PTPAngleB))
            IndCA = zeilenliste[PathIndexAnf+i].index("C ", beg, len(zeilenliste[PathIndexAnf+i]))  
            IndCE = len(zeilenliste[PathIndexAnf+i])-2 # }   " "+chr(125) funktioniert nicht?!
            PTPAngleC = PTPAngleC + [float(zeilenliste[PathIndexAnf+i][IndCA+2:IndCE])]
            print('PTPAngleC' +str(PTPAngleC))
        SkalierungPTP = 1000
        # XYZ = CBA - TEST: ABC, BAC
        BASEPos_Koord  = Vector([float(PTPX[0])/SkalierungPTP, float(PTPY[0])/SkalierungPTP, float(PTPZ[0])/SkalierungPTP])
        #BASEPos_Koord  = Vector([float(PTPY[0])/SkalierungPTP, float(PTPX[0])/SkalierungPTP, float(-PTPZ[0])/SkalierungPTP])
        # XYZ = CBA - TEST: ABC, BAC
        # A = -Z
        #BASEPos_Angle  = float(str(PTPAngleA[0])), float(str(PTPAngleB[0])), float(str(PTPAngleC[0])) # in Grad
        BASEPos_Angle  = float(str(PTPAngleC[0])), float(str(PTPAngleB[0])), float(str(PTPAngleA[0])) # in Grad
        
     
        
    except: 
        print('RfF_BasePos exception')
    print('RfF_BasePos done')
    print('_____________________________________________________________________________')
    return BASEPos_Koord, BASEPos_Angle    

def RfF_SafePos(filepath):
    print('_____________________________________________________________________________')
    print('Read from File - RfF_SafePos')
    
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
        # Einlesen der PTP Werte (X, Y, Z, A(Z), B(Y) C(X)) 
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
            IndXA = zeilenliste[PathIndexAnf+i].index("X ", beg, len(zeilenliste[PathIndexAnf+i])) # Same as find(), but raises an exception if str not found 
            IndXE = zeilenliste[PathIndexAnf+i].index(", Y", beg, len(zeilenliste[PathIndexAnf+i]))
            PTPX = PTPX + [float(zeilenliste[PathIndexAnf+i][IndXA+2:IndXE])]
       
            IndYA = zeilenliste[PathIndexAnf+i].index("Y ", beg, len(zeilenliste[PathIndexAnf+i]))  
            IndYE = zeilenliste[PathIndexAnf+i].index(", Z", beg, len(zeilenliste[PathIndexAnf+i]))
            PTPY = PTPY + [float(zeilenliste[PathIndexAnf+i][IndYA+2:IndYE])]
       
            IndZA = zeilenliste[PathIndexAnf+i].index("Z ", beg, len(zeilenliste[PathIndexAnf+i])) 
            IndZE = zeilenliste[PathIndexAnf+i].index(", A", beg, len(zeilenliste[PathIndexAnf+i]))
            PTPZ = PTPZ + [float(zeilenliste[PathIndexAnf+i][IndZA+2:IndZE])]
       
            IndAA = zeilenliste[PathIndexAnf+i].index("A ", beg, len(zeilenliste[PathIndexAnf+i])) 
            IndAE = zeilenliste[PathIndexAnf+i].index(", B", beg, len(zeilenliste[PathIndexAnf+i]))
            PTPAngleA = PTPAngleA + [float(zeilenliste[PathIndexAnf+i][IndAA+2:IndAE])]
       
            IndBA = zeilenliste[PathIndexAnf+i].index("B ", beg, len(zeilenliste[PathIndexAnf+i]))  
            IndBE = zeilenliste[PathIndexAnf+i].index(", C", beg, len(zeilenliste[PathIndexAnf+i]))
            PTPAngleB = PTPAngleB + [float(zeilenliste[PathIndexAnf+i][IndBA+2:IndBE])]
       
            IndCA = zeilenliste[PathIndexAnf+i].index("C ", beg, len(zeilenliste[PathIndexAnf+i]))  
            IndCE = len(zeilenliste[PathIndexAnf+i])-2 # }   " "+chr(125) funktioniert nicht?!
            PTPAngleC = PTPAngleC + [float(zeilenliste[PathIndexAnf+i][IndCA+2:IndCE])]
        
        SkalierungPTP  = 1000
        
        #SAFEPos_Koord  = Vector([float(PTPX[0])/SkalierungPTP, float(PTPY[0])/SkalierungPTP, float(PTPZ[0])/SkalierungPTP])
        SAFEPos_Koord  = Vector([float(PTPX[0])/SkalierungPTP, float(PTPY[0])/SkalierungPTP, float(PTPZ[0])/SkalierungPTP])
        print('SAFEPos_Koord' + str(SAFEPos_Koord))
        # XYZ = CBA
        # A = -Z
        #SAFEPos_Angle  = float(str(PTPAngleA[0])), float(str(PTPAngleB[0])), float(str(PTPAngleC[0])) # in Grad
        SAFEPos_Angle  = Vorz1 *float(str(PTPAngleC[0])), Vorz2 *float(str(PTPAngleB[0])), Vorz3 *float(str(PTPAngleA[0])) # in Grad
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
    
def RfF_PATHPTS(filepath, BASEPos_Koord, BASEPos_Angle):     
    print('_____________________________________________________________________________')
    print('RfF_PATHPTS')
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
        IndXA = zeilenliste[PathIndexAnf+1+i].index("X ", beg, len(zeilenliste[PathIndexAnf+1+i])) # Same as find(), but raises an exception if str not found 
        IndXE = zeilenliste[PathIndexAnf+1+i].index(", Y", beg, len(zeilenliste[PathIndexAnf+1+i]))
        PathPointX = PathPointX + [float(zeilenliste[PathIndexAnf+1+i][IndXA+2:IndXE])/SkalierungPTP]
   
        IndYA = zeilenliste[PathIndexAnf+1+i].index("Y ", beg, len(zeilenliste[PathIndexAnf+1+i]))  
        IndYE = zeilenliste[PathIndexAnf+1+i].index(", Z", beg, len(zeilenliste[PathIndexAnf+1+i]))
        PathPointY = PathPointY + [float(zeilenliste[PathIndexAnf+1+i][IndYA+2:IndYE])/SkalierungPTP]
   
        IndZA = zeilenliste[PathIndexAnf+1+i].index("Z ", beg, len(zeilenliste[PathIndexAnf+1+i])) 
        IndZE = zeilenliste[PathIndexAnf+1+i].index(", A", beg, len(zeilenliste[PathIndexAnf+1+i]))
        PathPointZ = PathPointZ + [float(zeilenliste[PathIndexAnf+1+i][IndZA+2:IndZE])/SkalierungPTP]
   
        IndAA = zeilenliste[PathIndexAnf+1+i].index("A ", beg, len(zeilenliste[PathIndexAnf+1+i])) 
        IndAE = zeilenliste[PathIndexAnf+1+i].index(", B", beg, len(zeilenliste[PathIndexAnf+1+i]))
        PathAngleA = PathAngleA + [float(zeilenliste[PathIndexAnf+1+i][IndAA+2:IndAE])]
   
        IndBA = zeilenliste[PathIndexAnf+1+i].index("B ", beg, len(zeilenliste[PathIndexAnf+1+i]))  
        IndBE = zeilenliste[PathIndexAnf+1+i].index(", C", beg, len(zeilenliste[PathIndexAnf+1+i]))
        PathAngleB = PathAngleB + [float(zeilenliste[PathIndexAnf+1+i][IndBA+2:IndBE])]
   
        IndCA = zeilenliste[PathIndexAnf+1+i].index("C ", beg, len(zeilenliste[PathIndexAnf+1+i]))  
        IndCE = len(zeilenliste[PathIndexAnf+1+i])-2 # }   " "+chr(125) funktioniert nicht?!
        PathAngleC = PathAngleC + [float(zeilenliste[PathIndexAnf+1+i][IndCA+2:IndCE]) ] # in Grad

    print('RfF_PATHPTS - Pathpositions und Angles initialisiert')
    # ==========================================    
    # Erstellen der Datenkontainer fuer location und rotation
    # ==========================================    
    
    # Korrektur der Punkte um die Tooljustierung:
    ADJUSTMENTPos_Koord, ADJUSTMENTPos_Angle = RfF_AdjustmentPos(filepath) 
    ADJUSTMENTPos_KoordB, ADJUSTMENTPos_AngleB = TransfRel(BASEPos_Koord, BASEPos_Angle, ADJUSTMENTPos_Koord, ADJUSTMENTPos_Angle)
    #ADJUSTMENTPos_KoordBD, ADJUSTMENTPos_AngleBD = DeltaFrom(BASEPos_Koord, BASEPos_Angle, ADJUSTMENTPos_Koord, ADJUSTMENTPos_Angle)
    
    mList= createMatrix(PATHPTSCount,1) # eigene Class "createMatrix" erstellt
    TList= createMatrix(PATHPTSCount,1) # eigene Class "createMatrix" erstellt
    dataPATHPTS_Loc = []
    dataPATHPTS_LocT = []
    # TODO: test, Vorzeichen an realen Kuka angepasst
    # Z-hoch = -Wert, X = - Wert, Y= -Wert  - TEST: ABC, BAC
    for i in range(0,PATHPTSCount,1):
        #mList[i][0:3] = [PathPointX[i], PathPointY[i], PathPointZ[i]]
        mList[i][0:3] = [PathPointX[i], PathPointY[i], PathPointZ[i]]
        dataPATHPTS_Loc = dataPATHPTS_Loc + [mList[i]] 
        TList[i][0:3] = [(PathPointX[i] + ADJUSTMENTPos_KoordB[0]) , (PathPointY[i] + ADJUSTMENTPos_KoordB[1]) , (PathPointZ[i] + ADJUSTMENTPos_KoordB[2]) ]
        dataPATHPTS_LocT  = dataPATHPTS_LocT + [TList[i]]
    # float(str(ADJUSTMENTPos_Koord[0])) 
    nList= createMatrix(PATHPTSCount,1)  
    UList= createMatrix(PATHPTSCount,1) 
    dataPATHPTS_Rot =[] 
    dataPATHPTS_RotT =[] 
    # XYZ = CBA
    # A = -Z
    for i in range(0,PATHPTSCount,1):
        #nList[i][0:3] = [PathAngleA[i], PathAngleB[i], PathAngleC[i]]
        
        nList[i][0:3] = [Vorz1 *PathAngleC[i], Vorz2 *PathAngleB[i], Vorz3 *PathAngleA[i]]
        
        # ... DAS SOLLTE JETZT SO OK SEIN: Die XYZ Verschiebung wird durch die Armature beruecksichtigt. D.h. Das Empty, bzw
        # die PATHPTS geben die TCP Position des Werkzeugs an. Es wird dann nur noch 'Vorverdrehung' beim Anschrauben des Werkzeugs
        # an das Flansch beruecksichtigt. (hier: -38�)
        # Achtung: TODO: noch nicht bei EXPORT beruecksichtigt... [Pruefung: nicht 100% OK, verworfen!!!!...]
        #nList[i][0:3] = [Vorz1 *(PathAngleC[i]-ADJUSTMENTPos_Angle[0]), Vorz2 *(PathAngleB[i]-ADJUSTMENTPos_Angle[1]), Vorz3 *(PathAngleA[i]-ADJUSTMENTPos_Angle[2])]
        
        dataPATHPTS_Rot = dataPATHPTS_Rot + [nList[i]]
        
        UList[i][0:3] = [(PathAngleC[i] + ADJUSTMENTPos_AngleB[0]) , (PathAngleB[i] + ADJUSTMENTPos_AngleB[1]) , (PathAngleA[i] + ADJUSTMENTPos_AngleB[2]) ]
        dataPATHPTS_RotT  = dataPATHPTS_RotT + [UList[i]]
        
    #dataPATHPTS_Loc = dataPATHPTS_LocT
    #dataPATHPTS_Rot = dataPATHPTS_RotT
    print('RfF_PATHPTS - Curve data - splines ersetzt')
    print('_____________________________________________________________________________')
    return dataPATHPTS_Loc, dataPATHPTS_Rot, PATHPTSCount, dataPATHPTS_LocT, dataPATHPTS_RotT

    
    
    
def TransfRel(BASEPos_Koord, BASEPos_Angle, ADJUSTMENTPos_Koord, ADJUSTMENTPos_Angle):
    print('_____________________________________________________________________________')
    print('TransfRel')
    print('BASEPos_Koord: ' +str(BASEPos_Koord))
    print('BASEPos_Angle: ' +str(BASEPos_Angle))
    print('ADJUSTMENTPos_Koord: ' +str(ADJUSTMENTPos_Koord))
    print('ADJUSTMENTPos_Angle: ' +str(ADJUSTMENTPos_Angle))  
    print('')
    matrix_world = mathutils.Matrix.Translation(BASEPos_Koord)
    point_local  = ADJUSTMENTPos_Koord
    point_world  = matrix_world * point_local
    print(' ADJUSTMENTPos_Koord local bezogen auf Base: point_local ' +str(point_local))
    print(' ADJUSTMENTPos_Koord local bezogen auf World: point_world ' +str(point_world))
    print('')
    print('Transformation von ADJUSTMENTPos auf GlobalKoordinaten...')
    
    
    
    #todo: evtl auf ZYX aendern???:
    eul = mathutils.Euler((math.radians(BASEPos_Angle[0]), math.radians(BASEPos_Angle[1]), math.radians(BASEPos_Angle[2])), RotationModeTransform) # XYZ
    print('eul: ' +str(eul))
    mat_rot = eul.to_matrix()
    mat_loc = point_local 
    mat = mat_rot * mat_loc 
    print('mat: ' +str(mat))
    
    #print('Rotation von ADJUSTMENTPos_Koord bezogen auf BaseKoordinaten...')
    #matrix_world = mathutils.Matrix.Translation(BASEPos_Koord)
    #print('matrix_world: ' +str(matrix_world))
    #point_local  = mat
    #point_world  = matrix_world * point_local
    #print('point_world2: ' +str(point_world))
    
    #print('BASEPos_Koord: ' +str(BASEPos_Koord))
    #print('BASEPos_Angle: ' +str(BASEPos_Angle))
    #print('ADJUSTMENTPos_Koord: ' +str(ADJUSTMENTPos_Koord))
    #print('ADJUSTMENTPos_Angle: ' +str(ADJUSTMENTPos_Angle)) 
    
    #SetOrigin(Obj, Obj)
    
    #ADJUSTMENTPos_KoordB = point_world
    ADJUSTMENTPos_KoordB = mat
    
    #print('Safe-Origin  = Obj auf point_world  gesetzt.')
    #-----------------------------------
    
    print('ADJUSTMENTPos_AngleB wieder dem Origin zuweisen unter Beruecksichtigung der BaseOrientierung:')
    ADJUSTMENTPos_AngleB = []
    # todo - test : vertauschen der Winkel... unklar... Import=Export, aber nicht = KUKA Film... 
    #ADJUSTMENTPos_AngleB[0] = list(BASEPos_Angle[0] +ADJUSTMENTPos_Angle[0])
    #ADJUSTMENTPos_AngleB[1] = list(BASEPos_Angle[1] +ADJUSTMENTPos_Angle[1])
    #ADJUSTMENTPos_AngleB[2] = list(BASEPos_Angle[2] +ADJUSTMENTPos_Angle[2])
    ADJUSTMENTPos_AngleB = [(BASEPos_Angle[0] + ADJUSTMENTPos_Angle[0]) , (BASEPos_Angle[1] + ADJUSTMENTPos_Angle[1]) , (BASEPos_Angle[2] + ADJUSTMENTPos_Angle[2]) ]     
    print('BASEPos_Koord: ' +str(BASEPos_Koord))
    print('BASEPos_Angle: ' +str(BASEPos_Angle))
    print('ADJUSTMENTPos_AngleB: ' +str(ADJUSTMENTPos_AngleB))    
    print('ADJUSTMENTPos_KoordB: ' +str(ADJUSTMENTPos_KoordB)) 
    
    print('TransfRel done')
    print('_____________________________________________________________________________')
    
    return ADJUSTMENTPos_KoordB, ADJUSTMENTPos_AngleB

def RfF_TIMEPTS(filepath):
    print('_____________________________________________________________________________')
    print('Read from File - TIMEPTS')
    # Besonderheit hier: dier erste ENDFOLD Marke muss uebersprungen werden.
    # ==========================================    
    # Import der TIMEPTS 
    # ==========================================    
    try:
        d = open(filepath)
        gesamtertext = d.read()
        d.close
        # Umwandeln in eine Liste
        zeilenliste =[]
        zeilenliste = gesamtertext.split(chr(10))
    
        # ==========================================
        # Suche nach "FOLD TIME DATA" 
        # ==========================================
        suchAnf = "FOLD TIME DATA"
        suchEnd = "ENDFOLD"
        Merker=[]
        TIMEPTSCount = len(zeilenliste)
        PathIndexAnf = 0
        PathIndexEnd = TIMEPTSCount
        for i in range(TIMEPTSCount):
            if zeilenliste[i].find(suchAnf)!=-1: 
                PathIndexAnf = i
                Merker=1
            if (zeilenliste[i].find(suchEnd)!=-1 and PathIndexAnf!=TIMEPTSCount and Merker==1): 
                PathIndexEnd = i
                break
        print("...")
        TIMEPTSCount = PathIndexEnd - (PathIndexAnf+1) # Achtung: hier wird 'zwischen' den Suchmarken ausgelesen
        # ==========================================
        # Einlesen der TIMEPTS Werte 
        # TIMEPTS[1]=0.2
        # TIMEPTS[1]=0.6
        # ==========================================
        TIMEPTS = []
        beg=0
        i=[]
        for i in range(0,TIMEPTSCount,1):
            IndXA = zeilenliste[PathIndexAnf+i+1].index("]=", beg, len(zeilenliste[PathIndexAnf+i+1])) # Same as find(), but raises an exception if str not found 
            IndXE = len(zeilenliste[PathIndexAnf+i+1])
            TIMEPTS = TIMEPTS + [float(zeilenliste[PathIndexAnf+i+1][IndXA+2:IndXE])]
        
    except: 
        print('TIMEPTS exception')
    print('TIMEPTS:' + str(TIMEPTS))
    print('RfF TIMEPTS done')
    print('_____________________________________________________________________________')
    return TIMEPTS, TIMEPTSCount   

 
def RfS_BasePos(objBase):    
    print('_____________________________________________________________________________')
    print('Read from Scene - RfS_BasePos')
    #objBase = bpy.data.objects['Sphere_BASEPos']
    
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
    BASEPos_Angle = BASEPos_Angle + [bpy.data.objects[objBase.name].rotation_euler.x * 360 / (2*math.pi)]# C(X)
    BASEPos_Angle = BASEPos_Angle + [bpy.data.objects[objBase.name].rotation_euler.y * 360 / (2*math.pi)]# B(Y)
    BASEPos_Angle = BASEPos_Angle + [bpy.data.objects[objBase.name].rotation_euler.z * 360 / (2*math.pi)]# A(Z)
    
    print('BASEPos_Koord: ' +str(BASEPos_Koord))
    print('BASEPos_Angle: ' +str(BASEPos_Angle))
    print('Read from Scene - RfS_BasePos done')
    print('_____________________________________________________________________________')
    return BASEPos_Koord, BASEPos_Angle

def RfS_HomePos(objHome):    
    print('_____________________________________________________________________________')
    print('Read from Scene - RfS_HomePos')
    #objHome = bpy.data.objects['Sphere_HOMEPos']
    
    print('bringe Base Origin to Center...')
    original_type = bpy.context.area.type
    bpy.context.area.type = "VIEW_3D" 
    bpy.ops.view3d.snap_cursor_to_center()
    objHome.select =True
    bpy.context.scene.objects.active = objHome
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    bpy.context.area.type = original_type
    
    HOMEPos_Koord = bpy.data.objects[objHome.name].location
    
    print('HOMEPos_Koord: ' +str(HOMEPos_Koord))
    
    #--------------------------
    # origin auf vert[0] setzten um die richtige Rotation zu bekommen
    # Origin der Base auf Vertex[0] setzen   (ohne die Base zu verschieben)
    
    SetOrigin(objHome, objHome)
    
    print('HOMEPos_Koord: ' +str(HOMEPos_Koord))
    
    # Achtung: Die Winkel HOMEPos_Angle werden in Grad benoetigt (wie auch im Import File angegeben):
    HOMEPos_Angle = []
    HOMEPos_Angle = HOMEPos_Angle + [bpy.data.objects[objHome.name].rotation_euler.x * 360 / (2*math.pi)]# C(X)
    HOMEPos_Angle = HOMEPos_Angle + [bpy.data.objects[objHome.name].rotation_euler.y * 360 / (2*math.pi)]# B(Y)
    HOMEPos_Angle = HOMEPos_Angle + [bpy.data.objects[objHome.name].rotation_euler.z * 360 / (2*math.pi)]# A(Z)
    
    print('HOMEPos_Koord: ' +str(HOMEPos_Koord))
    print('HOMEPos_Angle: ' +str(HOMEPos_Angle))
    print('Read from Scene - RfS_HomePos done')
    print('_____________________________________________________________________________')
    return HOMEPos_Koord, HOMEPos_Angle


def RfS_LocRot(objPATHPTS, dataPATHPTS_Loc, dataPATHPTS_Rot, BASEPos_Koord, BASEPos_Angle):
    # Aufruf von: create_PATHPTSObj, SetSafePos
    # Diese Funktion wird nur bei Export aufgerufen.
    # Wiedergabe von LOC/Rot bezogen auf Base
    
    # World2Local
    # dataPATHPTS_Loc = Global --> PATHPTS_Koord bezogen auf Base 
    # dataPATHPTS_Rot = Global --> PATHPTS_Angle bezogen auf Base
    print('_____________________________________________________________________________')
    print('Funktion: RfS_LocRotX - lokale Koordinaten bezogen auf Base!')
    
    objBase = bpy.data.objects['Sphere_BASEPos']
    PATHPTS_Angle = []
    
    matrix_world = mathutils.Matrix.Translation(objBase.location) #global
    point_local  = dataPATHPTS_Loc #global
    point_worldV = matrix_world.to_translation()
    point_worldR  = matrix_world.to_3x3() 
    
    print('point_local'+ str(point_local))  # neuer Bezugspunkt
    
    #--------------------------------------------------------------------------
    
    mat_rotX2 = mathutils.Matrix.Rotation(dataPATHPTS_Rot[0], 3, 'X') # Global
    mat_rotY2 = mathutils.Matrix.Rotation(dataPATHPTS_Rot[1], 3, 'Y')
    mat_rotZ2 = mathutils.Matrix.Rotation(dataPATHPTS_Rot[2], 3, 'Z')  
    Mrot2 = mat_rotZ2 * mat_rotY2 * mat_rotX2
    print('Mrot2'+ str(Mrot2))
    
    point_world2 = Mrot2.inverted()  * (point_worldV -point_local) 
    print('point_world2'+ str(point_world2))  # neuer Bezugspunkt
    
    #-----------------------------
    
    mat_rotX = mathutils.Matrix.Rotation(math.radians(BASEPos_Angle[0]), 3, 'X') # Global
    mat_rotY = mathutils.Matrix.Rotation(math.radians(BASEPos_Angle[1]), 3, 'Y')
    mat_rotZ = mathutils.Matrix.Rotation(math.radians(BASEPos_Angle[2]), 3, 'Z')
    Mrot = mat_rotZ * mat_rotY * mat_rotX
    print('Mrot :'+ str(Mrot))
    
    #point_world = matrix_world.inverted()  * (point_worldV -point_local) 
    point_world = Mrot.inverted()  * (point_local -point_worldV) 
    print('point_world (Base)'+ str(point_world))  # neuer Bezugspunkt
     
    PATHPTS_Koord = point_world
    
    matrix_1R0 = Mrot.inverted()  * Mrot2 # Falsche Vorzeichen f�r KUKA System  
    #matrix_1R0   =matrix_1R.inverted() 
    print('matrix_1R0'+ str(matrix_1R0))
    
    newR =matrix_1R0.to_euler('XYZ')
    print('newR'+ str(newR))
    print('newR[0] :'+ str(newR[0]*360/(2*3.14)))
    print('newR[1] :'+ str(newR[1]*360/(2*3.14)))
    print('newR[2] :'+ str(newR[2]*360/(2*3.14)))
        
    # todo - test - 23.12.13  PATHPTS_Angle = (-newR[0]*360/6.28, -newR[1]*360/6.28, -newR[2]*360/6.28)
    PATHPTS_Angle = (Vorz1* newR[0]*360/6.28, Vorz2*newR[1]*360/6.28, Vorz3*newR[2]*360/6.28)
    
    print('PATHPTS_Koord = point_local: ' + str(PATHPTS_Koord))
    print('PATHPTS_Angle: '+'C X {0:.3f}'.format(PATHPTS_Angle[0])+' B Y {0:.3f}'.format(PATHPTS_Angle[1])+' A Z {0:.3f}'.format(PATHPTS_Angle[2]))
    
    print('RfS_LocRotX done')
    print('_____________________________________________________________________________')
    return PATHPTS_Koord, PATHPTS_Angle 




def RfS_TIMEPTS(objEmpty_A6):
    
    # todo: objSafe -> action_name ...
    
    print('_____________________________________________________________________________')
    print('RfF TIMEPTS')
    
    #objEmpty_A6 = bpy.data.objects['Empty_Zentralhand_A6']
    action_name = bpy.data.objects[objEmpty_A6.name].animation_data.action.name
    print('RfF action_name' +str(action_name))
    action=bpy.data.actions[action_name] 
    locID, rotID = FindFCurveID(objEmpty_A6, action)
    
    
    #TIMEPTSCount = len(action.fcurves) # Anzahl der actions (locx, locy, ...)
    TIMEPTSCount = len(action.fcurves[0].keyframe_points) # Anzahl der KeyFrames
    print('RfF TIMEPTSCount' +str(TIMEPTSCount))
    # zum schreiben der PATHPTS verwenden:
    action.fcurves[locID[0]].keyframe_points[0].co # Ergebnis: Vector(Frame[0] Wert, x Wert)
    action.fcurves[locID[1]].keyframe_points[0].co # Ergebnis: Vector(Frame[0] Wert, y Wert)
    action.fcurves[locID[2]].keyframe_points[0].co # Ergebnis: Vector(Frame[0] Wert, z Wert)
    action.fcurves[rotID[0]].keyframe_points[1].co # Ergebnis: Vector(Frame[1] Wert, x Wert)
    action.fcurves[rotID[1]].keyframe_points[1].co # Ergebnis: Vector(Frame[1] Wert, x Wert)
    action.fcurves[rotID[2]].keyframe_points[1].co # Ergebnis: Vector(Frame[1] Wert, x Wert)
    
    
    action.fcurves[rotID[0]].keyframe_points[1].co # Ergebnis: Vector(Frame[1] Wert, x Wert)
    
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
    print('RfF TIMEPTS done')
    print('_____________________________________________________________________________')
    return TIMEPTS, TIMEPTSCount


def FindFCurveID(objEmpty_A6, action):
    print('_____________________________________________________________________________')
    print('FindFCurveID')
   
    #ob_target = objEmpty_A6
    # todo: Unklar: mehrere Actions moeglich?! -> fuehrt ggf. zu einer Liste als Rueckgabewert:
    
    print(action.name)
    
    locID=['xx',9999,9999]
    rotID=[9999,9999,9999]
    scaleID=[9999,9999,9999]
    dlocID =[9999,9999,9999]
         
    action_data =action.fcurves
    print(action_data)
    
    for v,action_data in enumerate(action_data):
        if action_data.data_path == "location":
            locID[action_data.array_index] = v
            #ob_target.delta_location[action_data.array_index]=v
            print("location[" + str(action_data.array_index) + "] to (" + str(v) + ").")
        elif action_data.data_path == "rotation_euler":
            rotID[action_data.array_index] = v
            #ob_target.delta_rotation_euler[action_data.array_index]=v
            print("rotation_euler[" + str(action_data.array_index) + "] to (" + str(v) + ").")
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
        bpy.data.objects[objBase.name].rotation_mode = RotationModeBase #n YXZ, XYZ
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
    bpy.data.objects[objCurve.name].rotation_mode =RotationModePATHPTS #n YXZ, XYZ
    objCurve.location = BASEPos_Koord.x,BASEPos_Koord.y ,BASEPos_Koord.z 
    objCurve.rotation_euler = BASEPos_Angle[0] *(2*math.pi)/360,  BASEPos_Angle[1] *(2*math.pi)/360,BASEPos_Angle[2] *(2*math.pi)/360
    print('SetCurvePos done')
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
    
    # Transformation Local2World
    
    objBase = bpy.data.objects['Sphere_BASEPos']
    bpy.data.objects[Obj.name].rotation_mode =RotationModeTransform
    # bpy.context.object.matrix_world 
    matrix_world = mathutils.Matrix.Translation(objBase.location)
    point_local  = Obj_Koord    
    point_worldV = matrix_world.to_translation()
    print('point_local'+ str(point_local))  # neuer Bezugspunkt
    mat_rotX = mathutils.Matrix.Rotation(math.radians(BASEPos_Angle[0]), 3, 'X') # C = -179 Global
    mat_rotY = mathutils.Matrix.Rotation(math.radians(BASEPos_Angle[1]), 3, 'Y') # B = -20
    mat_rotZ = mathutils.Matrix.Rotation(math.radians(BASEPos_Angle[2]), 3, 'Z') # A = -35
    Mrot = mat_rotZ * mat_rotY * mat_rotX
    print('Mrot'+ str(Mrot))
    mat_rotX2 = mathutils.Matrix.Rotation(math.radians(Obj_Angle[0]), 3, 'X') # Local (bez. auf Base)
    mat_rotY2 = mathutils.Matrix.Rotation(math.radians(Obj_Angle[1]), 3, 'Y') # 0,20,35 = X = -C, Y = -B, Z = -A
    mat_rotZ2 = mathutils.Matrix.Rotation(math.radians(Obj_Angle[2]), 3, 'Z')
    #Mrot2 = mat_rotX2 * mat_rotY2 * mat_rotZ2 # eigentliches Erg.
    Mrot2 = mat_rotZ2 * mat_rotY2 * mat_rotX2 # KUKA Erg.
    
    print('Mrot2'+ str(Mrot2))
    
    
    rot_matrix_world = Mrot2.transposed() * Mrot.transposed()       
    rot_matrix_world = rot_matrix_world.transposed()
    rotEuler =rot_matrix_world.to_euler('XYZ')
    Obj.rotation_euler = rotEuler

    print('rotEuler'+ str(rotEuler))
    print('rotEuler[0] :'+ str(rotEuler[0]*360/(2*3.14)))
    print('rotEuler[1] :'+ str(rotEuler[1]*360/(2*3.14)))
    print('rotEuler[2] :'+ str(rotEuler[2]*360/(2*3.14)))
    
    Vector_World = point_worldV - point_local # OK, ungenau!!!!?????
    point_world = (point_worldV -point_local) *matrix_world # OK, ungenau!!!!?????
        
    Obj.location = point_world #Vector_World
    print('Vector_World :'+ str(Vector_World))
       
    return

    
def SetObjRelToBaseX(Obj, Obj_Koord, Obj_Angle, BASEPos_Koord, BASEPos_Angle):
    # Diese Funktion wird nur bei Import aufgerufen.
    print('_____________________________________________________________________________')
    print('Funktion: SetObjRelToBase - lokale Koordinaten bezogen auf Base!')
    objBase = bpy.data.objects['Sphere_BASEPos']
    
    bpy.data.objects[Obj.name].rotation_mode =RotationModeTransform #n YXZ, XYZ
    
    #Obj = bpy.data.objects['Sphere_SAFEPos']
    print('BASEPos_Koord: ' +str(BASEPos_Koord))
    print('BASEPos_Angle: ' +str(BASEPos_Angle))
    print('Obj_Koord: ' +str(Obj_Koord))
    print('Obj_Angle: ' +str(Obj_Angle))  
    print('')
    matrix_world = mathutils.Matrix.Translation(BASEPos_Koord)
    point_local  = Obj_Koord
    point_world  = matrix_world * point_local
    #point_world  = point_local * matrix_world
    print(' Obj local bezogen auf Base: point_local ' +str(point_local))
    print(' Obj local bezogen auf World: point_world ' +str(point_world))
    print('')
    print('Transformation von Obj auf GlobalKoordinaten...')
    
    
    #todo: evtl auf ZYX aendern???:
    eul = mathutils.Euler((math.radians(BASEPos_Angle[0]), math.radians(BASEPos_Angle[1]), math.radians(BASEPos_Angle[2])), RotationModeTransform) # XYZ
    print('eul: ' +str(eul))
    mat_rot = eul.to_matrix()
    mat_loc = point_local 
    mat = mat_rot * mat_loc 
    #mat = mat_loc * mat_rot 
    print('mat: ' +str(mat))
    
    print('Rotation von SafeKood bezogen auf BaseKoordinaten...')
    matrix_world = mathutils.Matrix.Translation(BASEPos_Koord)
    print('matrix_world: ' +str(matrix_world))
    point_local  = mat
    point_world  = matrix_world * point_local
    #point_world  =  point_local *matrix_world
    
    print('point_world2: ' +str(point_world))
    
    print('BASEPos_Koord: ' +str(BASEPos_Koord))
    print('BASEPos_Angle: ' +str(BASEPos_Angle))
    print('Obj_Koord: ' +str(Obj_Koord))
    print('Obj_Angle: ' +str(Obj_Angle)) 
    
    SetOrigin(Obj, Obj)
    
    Obj.location = point_world
    print('Safe-Origin  = Obj auf point_world  gesetzt.')
    #-----------------------------------
    
    print('Obj_Angle wieder dem Origin zuweisen unter Beruecksichtigung der BaseOrientierung:')
    
    # todo - test : Fehler, Transformationsmatrix muss aufgeloest werden damit die Winkel auf die Achsen
    # der Base zerlegt werden.... Import=Export, aber nicht = KUKA Film... 
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
        
        # Wichtig: Verdrehung des Koordinaten Systems (TODO: vgl. Euler Winkel)
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
        
        ApplyScale(context.object) 
        #--------------------------------------------------------------------------------
        
        BASEPos_Koord, BASEPos_Angle = RfS_BasePos(objBase)
        ADJUSTMENTPos_Koord, ADJUSTMENTPos_Angle = (0,0,0), (0,0,0) #RfS_AdjustmentPos(aus GUI)
        HOMEPos_Koord, HOMEPos_Angle = RfS_HomePos(objHome)
        
        print('_________________CurveExport - BASEPos_Koord' + str(BASEPos_Koord))
        print('_________________CurveExport - BASEPos_Angle' +'X C {0:.3f}'.format(BASEPos_Angle[0])+' Y B {0:.3f}'.format(BASEPos_Angle[1])+' Z A {0:.3f}'.format(BASEPos_Angle[2]))
        
        SAFEPos_Koord, SAFEPos_Angle = RfS_LocRot(objSafe, objSafe.location, objSafe.rotation_euler, BASEPos_Koord, BASEPos_Angle)
        
        print('_________________CurveExport - BASEPos_Koord' + str(BASEPos_Koord))
        print('_________________CurveExport - BASEPos_Angle' +'X C {0:.3f}'.format(BASEPos_Angle[0])+' B Y {0:.3f}'.format(BASEPos_Angle[1])+' Z A {0:.3f}'.format(BASEPos_Angle[2]))
        print('_________________SAFEPos_Koord: ' + str(SAFEPos_Koord))
        print('_________________SAFEPos_Angle' +'A {0:.3f}'.format(SAFEPos_Angle[0])+' B {0:.3f}'.format(SAFEPos_Angle[1])+' C {0:.3f}'.format(SAFEPos_Angle[2]))
        
        
        WtF_KUKAdat(context.object, objEmpty_A6, PATHPTSObjName, self.filepath, BASEPos_Koord, BASEPos_Angle)
        
        print('_________________CurveExport - BASEPos_Koord' + str(BASEPos_Koord))
        print('_________________CurveExport - BASEPos_Angle' +'X C {0:.3f}'.format(BASEPos_Angle[0])+' B Y {0:.3f}'.format(BASEPos_Angle[1])+' Z A {0:.3f}'.format(BASEPos_Angle[2]))
        print('_________________SAFEPos_Koord: ' + str(SAFEPos_Koord))
        print('_________________SAFEPos_Angle' +'A {0:.3f}'.format(SAFEPos_Angle[0])+' B Y {0:.3f}'.format(SAFEPos_Angle[1])+' C {0:.3f}'.format(SAFEPos_Angle[2]))
        WtF_BasePos(BASEPos_Koord, BASEPos_Angle, self.filepath)
        WtF_AdjustmentPos(ADJUSTMENTPos_Koord, ADJUSTMENTPos_Angle, self.filepath)
        WtF_HomePos(HOMEPos_Koord, HOMEPos_Angle, self.filepath)
        print('_________________CurveExport - BASEPos_Koord' + str(BASEPos_Koord))
        print('_________________CurveExport - BASEPos_Angle' +'X C {0:.3f}'.format(BASEPos_Angle[0])+' X C {0:.3f}'.format(BASEPos_Angle[1])+' Z A {0:.3f}'.format(BASEPos_Angle[2]))
        print('_________________SAFEPos_Koord: ' + str(SAFEPos_Koord))
        print('_________________SAFEPos_Angle' +'A {0:.3f}'.format(SAFEPos_Angle[0])+' B Y {0:.3f}'.format(SAFEPos_Angle[1])+' C {0:.3f}'.format(SAFEPos_Angle[2]))
        WtF_SafePos(SAFEPos_Koord, SAFEPos_Angle, self.filepath)
        print('_________________CurveExport - BASEPos_Koord' + str(BASEPos_Koord))
        print('_________________CurveExport - BASEPos_Angle' +'X C {0:.3f}'.format(BASEPos_Angle[0])+' X C {0:.3f}'.format(BASEPos_Angle[1])+' Z A {0:.3f}'.format(BASEPos_Angle[2]))
        print('_________________SAFEPos_Koord: ' + str(SAFEPos_Koord))
        print('_________________SAFEPos_Angle' +'X C {0:.3f}'.format(SAFEPos_Angle[0])+' B Y {0:.3f}'.format(SAFEPos_Angle[1])+' Z A {0:.3f}'.format(SAFEPos_Angle[2]))
        #--------------------------------------------------------------------------------
        # Achtung: SetKukaToCurve funktioniert nur richtig, wenn das Parenting vorher geloest wurde!
        SetKukaToCurve(context.object)
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
        ApplyScale(context.object)
        #--------------------------------------------------------------------------------
        
        print("Erstellen der BezierCurve: done")
        BASEPos_Koord, BASEPos_Angle = RfF_BasePos(self.filepath)
        try:
            ADJUSTMENTPos_Koord, ADJUSTMENTPos_Angle = RfF_AdjustmentPos(self.filepath)
        except:
            print('failed to load AdjustmentPos')
        try:
            HOMEPos_Koord, HOMEPos_Angle = RfF_HomePos(self.filepath)
        except:
            
            print('failed to load HomePos')
        print('_________________CurveImport - BASEPos_Koord' + str(BASEPos_Koord))
        print('_________________CurveImport - BASEPos_Angle' +'X C {0:.3f}'.format(BASEPos_Angle[0])+' B Y {0:.3f}'.format(BASEPos_Angle[1])+' A Z {0:.3f}'.format(BASEPos_Angle[2]))
        
        # create Container (Location, Rotation) for each path point (PTP): dataPATHPTS_Loc, dataPATHPTS_Rot
        dataPATHPTS_Loc, dataPATHPTS_Rot, PATHPTSCountFile, dataPATHPTS_LocT, dataPATHPTS_RotT = RfF_PATHPTS(self.filepath, BASEPos_Koord, BASEPos_Angle) 
        
        
        
        #XYZ bei transformation nochmal zu zyx tauschen, bzw. YXZ ; Winkelverdrehung ergibt sich daraus, das die SAE Schale um 90 Grad 
        # verdreht montiert wird. dazu Kommt die HOMEPos von -128 -> -128 + 90 = -38 Grad Korrektur auf der Z Achse
        
        #todo: test ueber RfF_AdjustmentPos
        # wenn so richtig, dann muss f�r den Export alles ueber Adjustment Ruecktransformiert werden!
        # -> Diese Verdrehung +90 Grad bezieht sich nur auf die Montage des EndEffektors (SAE) Schale.
        # -> Die -128 Grad sind dem Roboter bekannt (da in der HOMEPos gespeichert.
        # -> Daraus folgt aber, das die Justageposition mit den CAD-World Winkeln Deckungsgleich ist!
        # --> Um die -178 aus HomePos zu ber�cksichtigen, muss ich die SAE Schale nochmal drehen!
        # --> Damit die PATHPTS die Ausrichtung der SAE Schale wiedergeben muss die Verdrehte Montage Verdrehung HOMEPos + Verdr. Tool (A -128.2708, B -0.4798438, C -178.1682)
        # bzgl. der Winkel und MES = {X -237, Y 0, Z 342, A (90), B 0, C 0 } bzgl der Verschiebung beruecksichtigt werden
        # Zus�tzlich: die PATHPTS haben ein rechtsdrehndes (linke HandRegel) System (YXZ) (Vg. Euler Winkel)
        
        
        # --> Die Verdrehungen werden ueber DeltaRotation angewandt, da diese nicht Teil des KUKA selbst sind.
        # D.h. nicht in den PATHPTS ber�cksichtigt werden.
        #SetBasePos(context.object, objBase, BASEPos_Koord, BASEPos_Angle)
        
        # TEST: warum verschieben sich die PATHPTS nicht mit der BASEPos?
        # Warum liegt die Kartesische HOMEPos nicht auf der Achsspez. HOMEPos?
        # Warum kann das Modell die Kartesische HOMEPos nicht einnehmen?
        # Achtung: Base = f(World) mit rechte Hand-Regel (links drehendes System)
        #          PATHPTS = f(Base) mit rechte/linke? Hand-Regel und links drehendem System -> entsteht dadurch das ZXY System???
        
        #ADJUSTMENTPos_Koord, ADJUSTMENTPos_Angle = RfF_AdjustmentPos(self.filepath) 
        #BASEPos_Koord[0] = BASEPos_Koord[0] + ADJUSTMENTPos_Koord[0]
        #BASEPos_Koord[1] = BASEPos_Koord[1] + ADJUSTMENTPos_Koord[1]
        #BASEPos_Koord[2] = BASEPos_Koord[2] + ADJUSTMENTPos_Koord[2]
        #liste1 = BASEPos_Angle[0] + ADJUSTMENTPos_Koord[0]
        #liste2 = BASEPos_Angle[1] + ADJUSTMENTPos_Koord[1]
        #liste3 = BASEPos_Angle[2] + ADJUSTMENTPos_Koord[2]
        #BASEPos_Angle = [liste1, liste2, liste3]
        
        SetBasePos(context.object, objBase, BASEPos_Koord, BASEPos_Angle)
        try:
            SetAdjustmentPos(guifeld)
        except:
            print('failed to set Adjustement Position....')
        SetBasePos(context.object, objHome, HOMEPos_Koord, HOMEPos_Angle)
        
        #SetObjRelToBase(objBase, BASEPos_Koord, BASEPos_Angle, ADJUSTMENTPos_Koord, ADJUSTMENTPos_Angle )
        
        
        #ADJUSTMENTPos_Koord, ADJUSTMENTPos_Angle = RfF_AdjustmentPos(self.filepath) 
        
        # todo - test: uebergebe um adjustement korrigierte werte f�r die pathpts...
        create_PATHPTSObj(dataPATHPTS_Loc, dataPATHPTS_Rot, PATHPTSCountFile, BASEPos_Koord, BASEPos_Angle)
        #create_PATHPTSObj(dataPATHPTS_LocT, dataPATHPTS_RotT, PATHPTSCountFile, BASEPos_Koord, BASEPos_Angle)
        
        #bezierCurve = bpy.data.curves[objCurve.name] #bpy.context.active_object #.data.name
        SetCurvePos(context.object, objBase, BASEPos_Koord, BASEPos_Angle)
        replace_CP(objCurve, PATHPTSObjName, dataPATHPTS_Loc, PATHPTSCountFile, BASEPos_Koord, BASEPos_Angle) 
        
        # Achtung: die Reihenfolge fon SetCurvePos und SetBasePos muss eingehalten werden! 
        # (da sonst die Curve nicht mit der Base mit verschoben wird!
       
        print('_________________CurveImport - BASEPos_Koord' + str(BASEPos_Koord))
        print('_________________CurveImport - BASEPos_Angle' + str(BASEPos_Angle))
        SAFEPos_Koord, SAFEPos_Angle = RfF_SafePos(self.filepath)
        print('_________________CurveImport - BASEPos_Koord' + str(BASEPos_Koord))
        print('_________________CurveImport - BASEPos_Angle' +'X C {0:.3f}'.format(BASEPos_Angle[0])+' B Y {0:.3f}'.format(BASEPos_Angle[1])+' A Z {0:.3f}'.format(BASEPos_Angle[2]))
        print('_________________SAFEPos_Koord: ' + str(SAFEPos_Koord))
        print('_________________SAFEPos_Angle' +'X C {0:.3f}'.format(SAFEPos_Angle[0])+' B Y {0:.3f}'.format(SAFEPos_Angle[1])+' A Z {0:.3f}'.format(SAFEPos_Angle[2]))
        # Achtung: Die Reihenfolge der Aufrufe von SetBasePos und SetObjRelToBase darf nicht vertauscht werden!
        SetObjRelToBase(objSafe, SAFEPos_Koord, SAFEPos_Angle, BASEPos_Koord, BASEPos_Angle )        
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
        SetKukaToCurve(context.object)
        #SetParenting() # hier wird ein Parenting hergestellt!
        # 2ter Aufruf notwendig, (wegen Kopie der Koordinaten vom parent to child objekt):
        SetKukaToCurve(context.object) 
        
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
        
        ApplyScale(context.object) 
        #--------------------------------------------------------------------------------
        
        BASEPos_Koord, BASEPos_Angle = RfS_BasePos(objBase)
        SAFEPos_Koord, SAFEPos_Angle = RfS_LocRot(objSafe, objSafe.location, objSafe.rotation_euler, BASEPos_Koord, BASEPos_Angle)
        PATHPTSObjList, countPATHPTSObj  = count_PATHPTSObj(PATHPTSObjName)
        #dataPATHPTS_Loc, dataPATHPTS_Rot, PATHPTSCountFile = RfS_LocRot(objSafe, objSafe.location, objSafe.rotation_euler, BASEPos_Koord, BASEPos_Angle)
        SetCurvePos(context.object, objBase, BASEPos_Koord, BASEPos_Angle)
        replace_CP(objCurve, PATHPTSObjName, '', countPATHPTSObj, BASEPos_Koord, BASEPos_Angle) 
        
        SetKukaToCurve(context.object)
        
        filepath ='none'
        GetRoute(objEmpty_A6, PATHPTSObjList, countPATHPTSObj, filepath)
        
                
        return {'FINISHED'} 
    print('- - -ClassRefreshButton done- - - - - - -')     

def GetRoute(objEmpty_A6, ObjList, countObj, filepath):
    # Diese Funktion wird erst interessant, wenn Routen ueber mehrere Objektgruppen erzeugt werden sollen.
    # in RefreshButton den Ablauf: [Ruhepos, n x (Safepos, PATHPTS, Safepos), Ruhepos] festlegen        
    
    # 1. Schritt: Umsetzung nur fuer einfache Reihenfolge
    
    # todo: GUI Liste abfragen (falls vorhanden) Reihenfolge der Objektgruppen/-Objekte zum erstellen der Route
    # n x [....] beruecksichtigen...???
        
    if filepath != 'none': # Aufruf von Button Import
        TIMEPTS_PATHPTS, TIMEPTS_PATHPTSCount = RfF_TIMEPTS(filepath)
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
                    # Zeit f�r eingef�gten PATHPTS mit dieser Geschw. ermitteln und einfuegen:
                    s = bpy.data.objects[PATHPTSObjList[i+1]].location - bpy.data.objects[PATHPTSObjList[i]].location
                elif (i+1) >= countPATHPTSObj:
                    s = bpy.data.objects[PATHPTSObjList[i-1]].location - bpy.data.objects[PATHPTSObjList[i-2]].location
                    v = s.length/(TIMEPTS[i-1]-TIMEPTS[i-2])
                    # Zeit f�r eingef�gten PATHPTS mit dieser Geschw. ermitteln und einfuegen:
                    s = bpy.data.objects[PATHPTSObjList[i-1]].location - bpy.data.objects[PATHPTSObjList[i-2]].location
                
                deltaT = abs(s.length /v)
                NewTIMEPTS = deltaT + TIMEPTS[i-1] # v=s/t -> t = s/v
                TIMEPTS.insert( i, NewTIMEPTS)
                # alle anderen TIMEPTS zeitlich um NewTIMEPTS verschieben:
                for n in range(i+1, len(TIMEPTS)):
                    TIMEPTS[n] = TIMEPTS[n] +  deltaT
             
    # Korrektur der TIMEPTS Werte, wenn groesser der Anzahl an PATHPTS    
    # Achtung: wird noch nicht ben�tigt, da in der Funktion erst alle KeyFrames geloescht werden. D.h. TIMEPTS Werte 
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
                SetObjRelToBase(bpy.data.objects[PATHPTSObjList[n]], Vector(dataPATHPTS_Loc[n]), dataPATHPTS_Rot[n], BASEPos_Koord, BASEPos_Angle)
                      
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
            
            # todo - test: .TIMEPTS einf�gen - eigene Class f�r PATHPTS erstellen!!!
            
            
            print('IF - uebertrage loc: ' + str(dataPATHPTS_Loc[n]) 
                      + ' und rot Daten:' + str(dataPATHPTS_Rot[n]) 
                      + ' vom File auf Objekt:' + str(PATHPTSObjList[n]))
            bpy.data.objects[PATHPTSObjList[n]].rotation_mode =RotationModePATHPTS
            SetObjRelToBase(bpy.data.objects[PATHPTSObjList[n]], Vector(dataPATHPTS_Loc[n]), dataPATHPTS_Rot[n], BASEPos_Koord, BASEPos_Angle)
                
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
                
                SetObjRelToBase(bpy.data.objects[PATHPTSObjList[n]], Vector(dataPATHPTS_Loc[n]), dataPATHPTS_Rot[n], BASEPos_Koord, BASEPos_Angle)
                      
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
            
            SetObjRelToBase(bpy.data.objects[PATHPTSObjList[n]], Vector(dataPATHPTS_Loc[n]), dataPATHPTS_Rot[n], BASEPos_Koord, BASEPos_Angle)
                
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
    
    for n in range(countPATHPTSObj):
        print(n)
        bpy.context.scene.frame_set(time_to_frame(TIMEPTS[n])) 
        ob.location = bpy.data.objects[TargetObjList[n]].location
        ob.rotation_euler = bpy.data.objects[TargetObjList[n]].rotation_euler
        ob.keyframe_insert(data_path="location", index=-1)
        # file:///F:/EWa_WWW_Tutorials/Scripting/blender_python_reference_2_68_5/bpy.types.bpy_struct.html#bpy.types.bpy_struct.keyframe_insert
        ob.keyframe_insert(data_path="rotation_euler", index=-1)
    
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
