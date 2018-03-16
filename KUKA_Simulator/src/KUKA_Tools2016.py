# -*- coding: utf-8 -*-    
#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# coding Angabe in Zeilen 1 und 2 fuer Eclipse Luna/ Pydev 3.9 notwendig
# cp1252


#  ***** BEGIN GPL LICENSE BLOCK ***** 
#  https://github.com/EWa74/KUKA_Simulator.git
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
# [ongoing] Abgleich mit KUKA und Definition der daraus folgenden GUI Panels
# code optimization: less parenting, more fcurve controlled objekts/bones
# naming convention
# gui panel (add/remove pathpoints, timepts
#


# Infos
# bpy.data.window_managers["WinMan"] ... propvalue
# bpy.app.handlers.frame_change_pre.append(bpy.ops.curve.cureexport('BezierCurve'))
# Window.GetScreenInfo(Window.Types.VIEW3D) 
# Beachte: x=(1,2,3) ist TUPEL, d.h. nicht veraenderbar; x = [1,2,3] ist Listse (veraenderbar)
# bpy.data.curves[bpy.context.active_object.data.name].splines[0].bezier_points[0].co.angle(bpy.data.curves[bpy.context.active_object.data.name].splines[0].bezier_points[1].co)    
# ARMATURE: Position und Winkel auf Plausibilitaet abfragen: bone constraints eingestellt; werden diese ueberschritten "springt" der Arm
# bpy.data.objects['OBJ_KUKA_Armature'].pose.bones['Bone_KUKA_Zentralhand_A4'].rotation_euler 
# Info: 
# 0. SAFE POSITION: muss immer von Hand im Menue angegeben werden. auch BASEPosition!
# 1. Kuka startet von HOMEPOSITION und faehrt zur BASEPosition
# 2. Kuka faehrt von der BASEPosition zum ersten Kurvenpunkt
# 3. Die Kurvenpunkte werden abgearbeitet 
# 4. Kuka faehrt zur SAFEPosition 
# 5. Keine Wiederholung: fahre zur HOMEPOSITION
# 6. Wiederholung: Wiederhole Punkte 2, 3, 4

# [done] todo: RefreshFunktion (wenn Boje oder Kurve +/- Punkte bekommt. Button Boje +/-; done, aber: inset keyframe fehlt noch
# [done] Listenfeld dazu verwenden um Obj +/-
# [done] TIMEPTS einlesen und I-Keys setzen -> Empty: follow path entfaellt dann: done
# handling vom POP UP window: alternativ *.src laden ODER default TP auswaehlen --> Panel(bpy_struct)
# [done] (refresh) button um nach editieren der Kurve das Kuka_Empty auf den ersten Kurvenpunkt zu setzen
# [done] obj. rename um 001.001 etc. zu vermeiden!!!
# [done] TODO: pruefen ob TIMEPTS = PATHPTS ist und ggf. neue keyframes und TIMEPTS setzen -> Funktion RefreshButton

# todo: geladenes File anzeigen
#git
# V-REP -> Roboter Simulation
# Phyton code aufraeumen
# Doku update 
# ToDo: ToolPosition (oder Baseposition) auslesen und offset beruecksichtigen MES ={ :  enthalten in *.dat -> OBJ_KUKA_EndEffector zuweisen
# BasePosition: (noch kein korrespondierender KUKA File bekannt !!! -> ALe
# todo: globale variablen definieren??..... --> Properties oder Klasse?
# todo: Verschiedene Import/ Export Funktionen beruecksichtigen (XYZ/ KUKA YXZ)
# Datenmodell und Funktionen beschreiben!!!
# TODO: Beschriftung der PATHPTS im 3D view
# TODO: GUI Feld um die Winkel bezogen auf Base oder Tool (bez. sich auf Base) editieren zu koennen
# writelog ueber Flag ein-/ausschalten

'''

${workspace_loc:KUKA_OT_Export/src/KUKA_Tools.py}

KUKA_Tools add-on
bpy.data.curves[bpy.context.active_object.data.name].splines[0].bezier_points[0].co=(0,1,1)
'''  
#--- ### Header 
bl_info = { 
    "name": "KUKA_OT_Export",
    "author": "Eric Wahl",
    "version": (1, 0, 3),
    "blender": (2, 7, 9),
    "api": 36147,
    "location": "View3D >Objects >KUKA_Tools",
    "category": "Curve",
    "description": "Import/ Editing/ Export Kuka Bahnkurve",
    "warning": "",
    "wiki_url": "http://...",
    "tracker_url": "http://..."
    }


#import pydevd;pydevd.settrace() # notwendig weil breakpoints uebersprungen werden. warum auch immer
     
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
from bpy.props import FloatProperty, IntProperty, CollectionProperty, EnumProperty, StringProperty
from mathutils import Vector  
from mathutils import *
import mathutils
import math
import re  # zum sortieren de Objektliste
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator, Panel, UIList
from symbol import except_clause
from copy import deepcopy # fuer OptimizeRotation
import fnmatch

#blender myscene.blend --background --python myscript.py

'''    
# Global Variables: 
To avoid _Restricted Data error by activating the Addon it is 
necessary to use a InitButton. -> KUKA_OT_InitBlendFile sets 
the global variables
'''
KUKAInitBlendFileExecuted = 'False'
print('\n KUKAInitBlendFileExecuted:  ' + KUKAInitBlendFileExecuted)
# import kuka_dat -> bug?: wird beim debuggen nicht aktualisiert....
# from kuka_dat import *
# import kuka_dat
# http://wiki.blender.org/index.php/Doc:2.6/Manual/Extensions/Python/Properties
# http://www.blender.org/documentation/blender_python_api_2_57_1/bpy.props.html



        

    
def writelog(text=''):
            
            
            FilenameLog = bpy.data.filepath
            FilenameLog = FilenameLog.replace(".blend", '.log')
            fout = open(FilenameLog, 'a')
            localtime = time.asctime( time.localtime(time.time()) )
            fout.write(localtime + " : " + str(text) + '\n')
            fout.close();



        
'''

Beschreibung:
Die location-Values des aktiven Objektes sollen in Abhaengigkeit des unter 'kuka.ORIGINType' ausgewaehlten Koordinatensystems 
a) richtig angezeigt werden
b) editierbar sein
Vorgehensweise:
1. ob = aktives Objekt der Szene

unterscheide zwischen Anzeige und Eingabe:
Anzeige:
die permanente Anzeige unter 'Panel' muss 'kuka.ORIGINType' beruecksichtigen. D.h. die Berechnung muss im Panel selber erfolgen.

Eingabe:
Bei Eingabe erfolgt der Ausruf der 'update_GUIloc' Funktion:
2. IF kuka.ORIGINType == z.B. BASEPos:
      > berechne die Positionswerte in Abhaengigkeit von 'kuka.ORIGINType'
      > uebergebe diese Werte dem GUI-Feld
      
'''
        

        
           
class set_locrot (bpy.types.Operator):
    
    ''' set location/ rotation from GUI to Object '''
    bl_idname = "object.set_locrot"
    bl_label = "set loc/rot" #Toolbar - Label
    bl_description = "set location/ rotation" # Kommentar im Specials Kontextmenue
    bl_options = {'REGISTER', 'UNDO'} #Set this options, if you want to update  
    #                                  parameters of this operator interactively 
    #                                  (in the Tools pane) 
    
    # ToDo: Achtung: nur OK bei BasePosObj; am besten weitere Properties anlegen. z.B. PATHPTSlocBase, PATHPTSlocHome, ...
     
    def execute(self, context): 
        objActive = bpy.context.scene.objects.active
        orgType = bpy.context.scene.objects.active.kuka.ORIGINType
        
        if orgType == 'BASEPos':
            objBase = bpy.context.scene.objects['kukaBASEPosObj']
        elif orgType == 'HOMEPos':
            objBase = bpy.context.scene.objects['kukaHOMEPosObj']
        elif orgType == 'SAFEPos':
            objBase = bpy.context.scene.objects['kukaSAFEPosObj']
        else:
            objBase = bpy.context.scene.objects['kukaBASEPosObj'] # um Fehler abzufangen
        
        BASEPos_Koord = objBase.location
        BASEPos_Angle = objBase.rotation_euler
        
        dataPATHPTS_Loc = bpy.data.objects[objActive.name].kuka.PATHPTSloc 
        dataPATHPTS_Rot = bpy.data.objects[objActive.name].kuka.PATHPTSrot
        
        helperLoc, helperRot = get_absolute(dataPATHPTS_Loc, dataPATHPTS_Rot, objBase, BASEPos_Koord, BASEPos_Angle)
        
        objActive.location = helperLoc
        objActive.rotation_euler = helperRot
        return {'FINISHED'}

class get_rel_locrot (bpy.types.Operator):
    
    ''' get relative location/ rotation '''
    bl_idname = "object.get_rel_locrot"
    bl_label = "get relative loc/rot" #Toolbar - Label
    bl_description = "get relative location/ rotation" # Kommentar im Specials Kontextmenue
    bl_options = {'REGISTER', 'UNDO'} #Set this options, if you want to update  
    #                                  parameters of this operator interactively 
    #                                  (in the Tools pane) 
    
    # ToDo: Achtung: nur OK bei BasePosObj; am besten weitere Properties anlegen. z.B. PATHPTSlocBase, PATHPTSlocHome, ...
     
    def execute(self, context): 
        objActive = bpy.context.scene.objects.active
        orgType = bpy.context.scene.objects.active.kuka.ORIGINType
        
        if orgType == 'BASEPos':
            objBase = bpy.context.scene.objects['kukaBASEPosObj']
        elif orgType == 'HOMEPos':
            objBase = bpy.context.scene.objects['kukaHOMEPosObj']
        elif orgType == 'SAFEPos':
            objBase = bpy.context.scene.objects['kukaSAFEPosObj']
        else:
            objBase = bpy.context.scene.objects['kukaBASEPosObj'] # um Fehler abzufangen
        
        BASEPos_Koord = objBase.location
        BASEPos_Angle = objBase.rotation_euler
        
        dataPATHPTS_Loc = bpy.data.objects[objActive.name].location 
        dataPATHPTS_Rot = bpy.data.objects[objActive.name].rotation_euler
        
        helperLoc, helperRot = get_relative(dataPATHPTS_Loc, dataPATHPTS_Rot, BASEPos_Koord, BASEPos_Angle)
        
        bpy.data.objects[objActive.name].kuka.PATHPTSloc = helperLoc
        bpy.data.objects[objActive.name].kuka.PATHPTSrot = helperRot
        return {'FINISHED'}
        

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

def get_absolute(Obj_Koord, Obj_Angle, objBase, BASEPos_Koord, BASEPos_Angle):
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
    
    # 01012014 objBase = bpy.data.objects['kukaBASEPosObj']
    #bpy.data.objects[Obj.name].rotation_mode =RotationModeTransform
    writelog('_____________________________________________________________________________')
    writelog('get_absolute ')
    
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
    
    writelog('get_absolute done')
    writelog('_____________________________________________________________________________')
       
    return Vtrans_abs, rotEuler

                  
def count_PATHPTSObj(PATHPTSObjName):
    writelog('_____________________________________________________________________________')
    writelog('count_PATHPTSObj')
    countPATHPTSObj = 0
    countObj = 0
    PATHPTSObjList=[]
    
    '''
    diese 3 Zeilen koennten die for-if Schleife ersetzten:
    objects = bpy.data.objects
    PATHPTSObjList = fnmatch.filter( [objects [i].name for i in range(len(objects ))] , 'PTPObj_*')
    countPATHPTSObj = len(PATHPTSObjList)
    '''  
    
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
    
class ObjectSettings(bpy.types.PropertyGroup): # self, context, 
    
    # Access it e.g. like
    # bpy.context.object.kuka.PATHPTS
    
    
        
    ID = bpy.props.IntProperty()
    # type: BASEPos, PTP, HOMEPos, ADJUSTMENTPos
    #type = bpy.props.StringProperty()
    ORIGINType = bpy.props.EnumProperty(
        items=(
            ('BASEPos', "Base Position", "coordinates relative to Base-Position"),
            ('SAFEPos', "Safe Position", "coordinates relative to Safe-Position"),
            ('HOMEPos', "Home Position", "coordinates relative to Home-Position"),
            ('ADJUSTMENTPos', "Adjustment Position", "coordinates relative to Adjustment-Position"),
        )
    )
    
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
    
    PATHPTSloc = bpy.props.FloatVectorProperty(name="Location",
        default=(0.0, 0.0, 0.0),
        options={'ANIMATABLE'}, 
        subtype='TRANSLATION', 
        size=3,
        update=None)
        
    PATHPTSrot = bpy.props.FloatVectorProperty(name="Rotation",
        default=(0.0, 0.0, 0.0),
        #min=(-10.0,-10.0,-10.0, -180.0, -180.0, -180.0),
        #max=(+10.0,+10.0,+10.0, 180.0, 180.0, 180.0),
        options={'ANIMATABLE'}, 
        subtype='EULER', 
        size=3,
        update=None)
    
     

bpy.utils.register_class(ObjectSettings)

bpy.types.Object.kuka = \
    bpy.props.PointerProperty(type=ObjectSettings) 
    
        
def WtF_KeyPos(Keyword, KeyPos_Koord, KeyPos_Angle, filepath, FileExt, FileMode):            
    ''' 
    Write to File 
    Create a file for output
    KeyPos_Angle [rad]
    '''
    
    writelog('_____________________________________________________________________________')
    writelog('WtF_KeyPos :' + Keyword)  
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
    
        for i in range(0,Count-2,1):    
            fout.write(Keyword +"[" + str(i+1) + "]=" + 
                       "{0:.5f}".format(KeyPos_Koord[i+1] ) +
                       "\n")
        fout.write(";ENDFOLD" + "\n")
        
    writelog('close file.')
    fout.close();
        
    writelog('WtF_KeyPos :' + Keyword + ' geschrieben.')
    writelog('_____________________________________________________________________________')

def RfF_KeyPos(Keyword, filepath, FileExt):
    '''
    Read from File
    [Grad] Werte werden eingelesen und in [rad] umgewandelt
    '''
    
    writelog('_____________________________________________________________________________')
    writelog('RfF_KeyPos :' + Keyword)  
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
            #LOADPTS[2]={FX NAN, FY NAN, FZ -120, TX NAN, TY NAN, TZ NAN }
            pass
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
            pass
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
    '''
    Read from Scene
    
    todo: objSafe -> action_name ...
    
    '''
    
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
    '''
    find F-curve ID
    
    todo: Unklar: mehrere Actions moeglich?! -> fuehrt ggf. zu einer Liste als Rueckgabewert:
    '''
    
    
    writelog('_____________________________________________________________________________')
    writelog('FindFCurveID')
   
    #ob_target = objEmpty_A6
    
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
            pass
    
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

    '''
    todo: Sicherheitsabfrage/bug: 'EDIT' Mode line 919, in SetOrigin
    TypeError: Converting py args to operator properties:  enum "EDIT" not found in ('OBJECT')
    -> Verwendung minimieren durch ersetzen der Transformation durch Ueberlagerung der FCurve Werte!
    Fehler scheint aufzutreten, wenn z.B. kukaBASEPosObjekt "ge-Hidded" (ausgeblendet) wird....pruefen
    oder der Layer auf dem BASEPos, SAFEPos liegen ausgeblendet ist
    Die Funktion hier ist sch...; Achtung: wenn im Editmode nicht Vertex select aktive ist sondern z.B. Faces oder Edges gibt Probleme...
    '''
    
    writelog('_____________________________________________________________________________')
    writelog('SetOrigin')
    
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
    
    # Sicherstellen das wir uns im Object Mode befinden:
    #original_mode = bpy.context.mode
    #if original_mode!= 'OBJECT':
    #    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        
    bpy.context.scene.objects.active = sourceObj
    
    # Sicherstellen das wir uns im Object Mode befinden:
    #original_mode = bpy.context.mode
    #if original_mode!= 'OBJECT':
    #    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    
    # Sicherstellen das wir uns im Object Mode befinden:
    #original_mode = bpy.context.mode
    #if original_mode!= 'OBJECT':
    #    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        
    bpy.ops.object.select_all(action='DESELECT')
    
    bpy.context.area.type = original_type 
    writelog('Origin von '+ str(sourceObj.name) + ' auf vertex 0 von ' + str(targetObj.name) + ' gesetzt.')
    
    if original_mode!= 'OBJECT':
        bpy.ops.object.mode_set(mode='EDIT', toggle=True)
    
    writelog('SetOrigin done')
    writelog('_____________________________________________________________________________')



 
def OptimizeRotation(ObjList):
    writelog('_____________________________________________________________________________')
    writelog('OptimizeRotation ')
    
    
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
    # wenn zum erreichen des folgenden Winkels mehr als 180Grad (PI) zurueckzulegen ist, 
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
        
        
        # Quaternation-Flip disabled
        # ohne OptimRotation: Quaternion(( 0.1570675 9691238403, -0.639445 6028938293,  0.7424664497375488,  -0.1232177 3916482925))
        # ohne flip:          Quaternion(( 0.1570675 3730773926, -0.639445 7221031189,  0.742466 390132904,  -0.1232177 9131889343))
        # nach 1. flip (OK) : Quaternion((-0.1570675 0750541687,  0.639445 6624984741, -0.742466 4497375488,  0.1232177 7641773224)) auch ohne flip
        # nach 2. flip (NOK): Quaternion(( 0.1570675 9691238403, -0.639445 6028938293,  0.742466 4497375488, -0.1232177 3916482925))
        
        
        rF = 16
        new = [round(Rot2.to_quaternion()[0],rF), round(Rot2.to_quaternion()[1],rF),round(Rot2.to_quaternion()[2],rF), round(Rot2.to_quaternion()[3],rF)]
        old = [-round(Rot2old.to_quaternion()[0],rF), -round(Rot2old.to_quaternion()[1],rF),-round(Rot2old.to_quaternion()[2],rF), -round(Rot2old.to_quaternion()[3],rF)]
        
        if new[:] == old[:]: # notwendig um Quaternion flip zu vermeiden
            Rot2.x = Rot2old.x
            Rot2.y = Rot2old.y
            Rot2.z = Rot2old.z
        
        print('')
    writelog('OptimizeRotation done')
    writelog('_____________________________________________________________________________')
    
                               
def OptimizeRotationQuaternion(ObjList, countObj):
    writelog('_____________________________________________________________________________')
    writelog('OptimizeRotationQuaternion ')
    
    
    # ToDo: Status: on hold...
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
    
    writelog('OptimizeRotationQuaternion done')
    writelog('_____________________________________________________________________________')
        
    return QuaternionList    


# ________________________________________________________________________________________________________________________



def renamePATHObj(PATHPTSObjList):
    writelog('_____________________________________________________________________________')
    writelog('renamePATHObj')
         
    for n in range(len(PATHPTSObjList)-1,0, -1): 
        bpy.data.objects[PATHPTSObjList[n]].name = PATHPTSObjName + str("%03d" %(n+1)) # "%03d" % 2
        PATHPTSObjList[n] = PATHPTSObjName + str("%03d" %(n+1)) # "%03d" % 2  
        writelog(PATHPTSObjList[n])
    writelog('renamePATHObj done')
    writelog('_____________________________________________________________________________')
    return PATHPTSObjList

def ValidateTIMEPTS(PATHPTSObjList, TIMEPTS):
    writelog('_____________________________________________________________________________')
    writelog('ValidateTIMEPTS')
    countPATHPTSObj = len(PATHPTSObjList)
        
    # Korrektur der TIMEPTS Werte, wenn kleiner der Anzahl an PATHPTS
    if len(TIMEPTS)<countPATHPTSObj: # while
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
    
    # Korrektur der TIMEPTS Werte, wenn Werte gleich sind (z.B. durch kopieren eines PATHPTS) oder Zeit zu kurz:
    
    v_max = 0.5 # 1m/s= 3,6km/h => 1/3,6m/s = 0,00027777m/s = 1km/h
    
    for i in range(countPATHPTSObj-1):
        s = bpy.data.objects[PATHPTSObjList[i]].location - bpy.data.objects[PATHPTSObjList[i+1]].location
        if (round(TIMEPTS[i+1],1) -round(TIMEPTS[i],1)) == 0:
            TIMEPTS[i+1] = TIMEPTS[i] + 0.001
        v = abs(s.length/(TIMEPTS[i+1]-TIMEPTS[i]))
        
        if v>= v_max: 
            time_old = deepcopy(TIMEPTS[i+1])
            TIMEPTS[i+1] = TIMEPTS[i] + s.length/v_max
            deltaT = TIMEPTS[i+1] - time_old
            # alle anderen TIMEPTS zeitlich um das deltaT verschieben:
            for n in range(i+1, len(TIMEPTS)):
                TIMEPTS[n] = TIMEPTS[n] +  deltaT
        
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
    


def DefRoute(objEmpty_A6, filepath):
    # Diese Funktion wird erst interessant, wenn Routen ueber mehrere Objektgruppen erzeugt werden sollen.
    # in RefreshButton den Ablauf: [HomePos, n x (Safepos, PATHPTS, Safepos), HomePos] festlegen        
    
    # 1. Schritt: Umsetzung nur fuer einfache Reihenfolge
    
    # [done] todo: GUI Liste abfragen (falls vorhanden) Reihenfolge der Objektgruppen/-Objekte zum erstellen der Route
    # [open] n x [....] beruecksichtigen...???
    
    # todo: Bei Bearbeitung und Konkatonierung per GUI Ablauf (Object.RouteNbr)
    
    # Festlegen der TIMEPTS fuer jedes beteiligte Objekt:
    PATHPTSObjList, countPATHPTSObj  = count_PATHPTSObj(PATHPTSObjName)
    PATHPTSObjList =  renamePATHObj(PATHPTSObjList)
        
    if filepath != 'none': # Aufruf von Button Import
        # Achtung: ueberarbeiten!!
        TIMEPTS_PATHPTS, NAN = RfF_KeyPos('TIMEPTS', filepath, '.dat')
        TIMEPTS_PATHPTSCount = len (TIMEPTS_PATHPTS)
        
        '''
        # Korrektur der TIMEPTS Werte, wenn kleiner der Anzahl an PATHPTS:
         '''
        TIMEPTS_PATHPTS = ValidateTIMEPTS(PATHPTSObjList, TIMEPTS_PATHPTS) # TODO: Fehler!! PATHPTSObjList hat noch die'alten' Objekte!
       
        for i in range(len (TIMEPTS_PATHPTS)):    
            bpy.data.objects[PATHPTSObjList[i]].kuka.TIMEPTS = TIMEPTS_PATHPTS[i]
        
    elif filepath == 'none': # Aufruf von Button RefreshButton
        #TIMEPTS_PATHPTS, TIMEPTS_PATHPTSCount = RfS_TIMEPTS(objEmpty_A6)
        TIMEPTS_PATHPTS = []
        for i in range(countPATHPTSObj):
            TIMEPTS_PATHPTS = TIMEPTS_PATHPTS + [bpy.data.objects[PATHPTSObjList[i]].kuka.TIMEPTS]
            if TIMEPTS_PATHPTS[i] == 0: # besser: werte der fcurve zuruecklesen....
                TIMEPTS_PATHPTS[i] = TIMEPTS_PATHPTS[i-1]+1
                bpy.data.objects[PATHPTSObjList[i]].kuka.TIMEPTS = TIMEPTS_PATHPTS[i]
        TIMEPTS_PATHPTS = ValidateTIMEPTS(PATHPTSObjList, TIMEPTS_PATHPTS)
        for i in range(len (TIMEPTS_PATHPTS)):    
            bpy.data.objects[PATHPTSObjList[i]].kuka.TIMEPTS = TIMEPTS_PATHPTS[i]
       
            
    # Korrektur der TIMEPTS Werte, wenn kleiner der Anzahl an PATHPTS:  
    #TIMEPTS_PATHPTS = ValidateTIMEPTS(PATHPTSObjList, TIMEPTS_PATHPTS)
    
    
    TIMEPTS_Safe = TIMEPTS_PATHPTS[len (TIMEPTS_PATHPTS)-1] + 2 # Sekunden
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
    '''
    # Achtung: verfaelscht einen Winkel????
    Route_TIMEPTS  = ValidateTIMEPTS(Route_ObjList, Route_TIMEPTS)
    for i in range(len (Route_TIMEPTS)):    
                bpy.data.objects[Route_ObjList[i]].kuka.TIMEPTS = Route_TIMEPTS[i]
    
    '''
    if filepath == 'none': # Aufruf von Button RefreshButton
        OptimizeRotation(Route_ObjList) 
     
    # todo: Validierung der Objekte.TIMEPTS (ob jedes Objekt einen plausiblen Wert hat)
    
    SetKeyFrames(objEmpty_A6, Route_ObjList, Route_TIMEPTS)
    return Route_ObjList
    

def AnimateOBJScaling(TargetObjList):
    
    # TODO: TargetObjList um Basepos erweitern
    
    # Funktion soll die PathPoints die gerade vom KUKA angefahren werden per Scaling der Objekte
    # fruehzeitig ausblenden und danach wieder einblenden
    # evtl. spaeter verschiedene Modi einstellbar (z.B. nur PTP vor dem Empty/ bzw. vor- & nach/ etc..)
    
    
    # Ort & Zeit von Empty_A6 ueber seine Keyframes bekannt
    # PTPs bekommen eigene keyframes mit entsprechender Scaling-Angabe zugewiesen:
    # Ziel: die noechsten 3 PTPs einblenden
    
    original_type         = bpy.context.area.type
    bpy.context.area.type = "VIEW_3D"
    bpy.ops.object.select_all(action='DESELECT')
    
    
        
    # 1. alle vorhandenen Keyframes fuer das Objekt loeschen bevor neue gesetzt werden:
    for n in range(len(TargetObjList)):
        bpy.data.objects[TargetObjList[n]].select = True #objEmpty_A6.select = True
        bpy.ops.anim.keyframe_clear_v3d() #Remove all keyframe animation for selected objects
        bpy.data.objects[TargetObjList[n]].select = False
    
    # 1. alle Objekte im scaling minimieren:
    for n in range(len(TargetObjList)):
        bpy.context.scene.objects.active = bpy.data.objects[TargetObjList[n]]
        ob = bpy.context.active_object
        ob.scale =   (0.2, 0.2, 0.2) 
        ob.keyframe_insert(data_path="scale", index=-1, frame=1) #startframe
        
    # 2. 
    for n in range(len(TargetObjList)):
        
        bpy.context.scene.objects.active = bpy.data.objects[TargetObjList[n]]
        ob = bpy.context.active_object
                
        #wann:
        bpy.context.scene.frame_set(time_to_frame(bpy.data.objects[TargetObjList[n]].kuka.TIMEPTS))
        
        # welche Eigenschaft:      
        # bpy.data.objects['PTPObj_016'].scale -> Vector((1.0, 1.0, 1.0))
        #bpy.data.objects[TargetObjList[n]].scale
        #keyframe fuer scaling setzen:
        ob.scale =   (0.2, 0.2, 0.2)
        ob.keyframe_insert(data_path="scale", index=-1, frame=(bpy.context.scene.frame_current -25))
        ob.scale =   (1.0, 1.0, 1.0)
        ob.keyframe_insert(data_path="scale", index=-1, frame=(bpy.context.scene.frame_current -15))
        ob.scale =   (0.2, 0.2, 0.2)
        ob.keyframe_insert(data_path="scale", index=-1, frame=bpy.context.scene.frame_current)
        #ob.scale =   (1.0, 1.0, 1.0)
        #ob.keyframe_insert(data_path="scale", index=-1, frame=(bpy.context.scene.frame_current +25))
        #ob.scale =   (0.2, 0.2, 0.2)
        #ob.keyframe_insert(data_path="scale", index=-1, frame=(bpy.context.scene.frame_current +30))
        
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.area.type = original_type 
    
    
    
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
    ob.rotation_mode = 'QUATERNION' #'XYZ'
    
       
    '''
    BGEActionCount = bpy.data.actions.find('BGEAction')
    if BGEActionCount == -1:
        bpy.data.actions.new('BGEAction')
    bpy.data.actions['BGEAction'].fcurves.new(data_path = 'location', index=0, action_group="")
    bpy.data.actions['BGEAction'].fcurves.new(data_path = 'location', index=1, action_group="")
    bpy.data.actions['BGEAction'].fcurves.new(data_path = 'location', index=2, action_group="")
    bpy.data.actions['BGEAction'].fcurves.new(data_path = 'rotation_euler', index=0, action_group="")
    bpy.data.actions['BGEAction'].fcurves.new(data_path = 'rotation_euler', index=1, action_group="")
    bpy.data.actions['BGEAction'].fcurves.new(data_path = 'rotation_euler', index=2, action_group="")
    '''
    
    #QuaternionList = OptimizeRotationQuaternion(TargetObjList, TIMEPTSCount)
    
    for n in range(len(TargetObjList)):
        writelog(n)
        #bpy.context.scene.frame_set(time_to_frame(TIMEPTS[n])) 
        bpy.context.scene.frame_set(time_to_frame(bpy.data.objects[TargetObjList[n]].kuka.TIMEPTS))
        ob.location = bpy.data.objects[TargetObjList[n]].location
        # todo - done: keyframes auf quaternion um gimbal lock zu vermeiden
                
        ob.rotation_quaternion = bpy.data.objects[TargetObjList[n]].rotation_euler.to_quaternion()
        
        #obQuaternion = bpy.data.objects[TargetObjList[n]].rotation_euler.to_quaternion()
        #ob.rotation_euler = obQuaternion.to_euler('XYZ')
        #ob.rotation_euler = bpy.data.objects[TargetObjList[n]].rotation_euler
           
        ob.keyframe_insert(data_path="location", index=-1)
        
        #bpy.data.actions['BGEAction'].keyframe_insert(data_path="location", index=-1)
        
        # --->>>> ggf. das eigentliche action wieder von quaternion nach euler zuroecktransformieren (dann evtl. GimbalLock noch OK?!)
        # bpy.data.actions['BGEAction'].fcurves.data.keyframe_insert(data_path="X_Location")    fcurve.data _path
        
        # file:///F:/EWa_WWW_Tutorials/Scripting/blender_python_reference_2_68_5/bpy.types.bpy_struct.html#bpy.types.bpy_struct.keyframe_insert
        
        ob.keyframe_insert(data_path="rotation_quaternion", index=-1)
        
        #ob.keyframe_insert(data_path="rotation_euler", index=-1)
        
        #bpy.data.actions['BGEAction'].keyframe_insert(data_path="rotation_euler", index=-1)
        
            
    if len(TIMEPTS)> len(TargetObjList):
        writelog('Achtung: mehr TIMEPTS als PATHPTS-Objekte vorhanden')
        pass
    # todo: end frame not correct if PATHPTS added....
    bpy.context.scene.frame_end = time_to_frame(TIMEPTS[len(TIMEPTS)-1])
    bpy.context.scene.frame_preview_end = time_to_frame(TIMEPTS[len(TIMEPTS)-1])
    
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
        pass
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
        
        # http://blenderscripting.blogspot.de/2012/03/deleting-objects-from-scene.html
        candidate_list = PATHPTSObjList[PATHPTSCountFile: PATHPTSCountFile+zuViel]
        # select them only.
        for object_name in candidate_list:
            bpy.data.objects[object_name].select = True 
        # remove all selected.
        bpy.ops.object.delete(use_global=True)     # True, damit das Objekt auch aus dem DATABLOCK geloescht wird.
        
        
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
                '''
                writelog('IF - uebertrage loc: ' + str(dataPATHPTS_Loc[n]) 
                      + ' und rot Daten:' + str(dataPATHPTS_Rot[n]) 
                      + ' vom File auf Objekt:' + str(PATHPTSObjList[n]))
                '''
                bpy.data.objects[PATHPTSObjList[n]].rotation_mode =RotationModePATHPTS
                
                #get_absolute(bpy.data.objects[PATHPTSObjList[n]], Vector(dataPATHPTS_Loc[n]), dataPATHPTS_Rot[n], BASEPos_Koord, BASEPos_Angle) #Transformation Local2World
                bpy.data.objects[PATHPTSObjList[n]].location, bpy.data.objects[PATHPTSObjList[n]].rotation_euler = get_absolute(Vector(dataPATHPTS_Loc[n]), dataPATHPTS_Rot[n], objBase, BASEPos_Koord, BASEPos_Angle) #Transformation Local2World
                
                      
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
            
            '''
            writelog('IF - uebertrage loc: ' + str(dataPATHPTS_Loc[n]) 
                      + ' und rot Daten:' + str(dataPATHPTS_Rot[n]) 
                      + ' vom File auf Objekt:' + str(PATHPTSObjList[n]))
            '''
            bpy.data.objects[PATHPTSObjList[n]].rotation_mode =RotationModePATHPTS
            
            #get_absolute(bpy.data.objects[PATHPTSObjList[n]], Vector(dataPATHPTS_Loc[n]), dataPATHPTS_Rot[n], BASEPos_Koord, BASEPos_Angle) #Transformation Local2World
            bpy.data.objects[PATHPTSObjList[n]].location, bpy.data.objects[PATHPTSObjList[n]].rotation_euler = get_absolute(Vector(dataPATHPTS_Loc[n]), dataPATHPTS_Rot[n], objBase, BASEPos_Koord, BASEPos_Angle) #Transformation Local2World
               
    bpy.context.area.type = original_type 
    writelog('create_PATHPTSObj done')
    writelog('_____________________________________________________________________________')


                
class createMatrix(object):
            
            def __init__(self, rows, columns, default=0):
                writelog('_____________________________________________________________________________')
                writelog('createMatrix')
                
                self.m = []
                for i in range(rows):
                    self.m.append([default for j in range(columns)])
                
                writelog('createMatrix done')
                writelog('_____________________________________________________________________________')  
        
            def __getitem__(self, index):
                return self.m[index]
                           
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
    
    @classmethod
    def poll(cls, context):
        return (KUKAInitBlendFileExecuted =='False') # Test, ob InitBlendFile ausgefuehrt wurde.
    
    def execute(self, context):  
        global PATHPTSObjName, objBase, objSafe, objCurve, objHome, objEmpty_A6
        global Mode, RotationModeBase, RotationModePATHPTS, RotationModeEmpty_Zentralhand_A6, RotationModeTransform
        global Vorz1, Vorz2, Vorz3
        global CalledFrom, filepath 
        global KUKAInitBlendFileExecuted 
        
        
        # Global Variables:
        KUKAInitBlendFileExecuted = 'True'
        PATHPTSObjName = 'PTPObj_'
        objBase     = bpy.data.objects['kukaBASEPosObj']
        objSafe     = bpy.data.objects['kukaSAFEPosObj']
        
        #bpy.types.Scene.pathname       = StringProperty(name="PathName")
        #bpy.context.scene.pathname = 'BezierCircle'
        objCurve    = bpy.data.objects[bpy.context.scene.pathname]
        #objCurve     = bpy.data.objects['BezierCircle']
        #bpy.context.scene.pathname = 'BezierCircle'
        #objCurve    = bpy.data.objects[bpy.context.scene.pathname]
        #bpy.types.Scene.pathname = StringProperty(name="HelloWorld")
        #objCurve    = bpy.data.objects[bpy.types.Scene.pathname[1]['name']] # ToDo: Listenfeld mit concatonate of several curves
        #      objCurve    = bpy.data.objects[str(bpy.context.scene.pathname)] # ToDo: Listenfeld mit concatonate of several curves
        
        
        
        
        print('\n InitButton - objCurve.name: ' + str(objCurve.name))
        # --> doch an KUKA-Klasse haengen damit jedes PTPObj einer Kurve zugeordnet ist (fuer mehrere Kurven)!
        
        
        objHome     = bpy.data.objects['kukaHOMEPosObj']
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
        
        PATHPTSObjList, countPATHPTSObj  = count_PATHPTSObj(PATHPTSObjName)
        
        print('\n KUKA_OT_initBlendFile')
        return {'FINISHED'} 
    





  
class KUKA_OT_Export (bpy.types.Operator, ExportHelper):
    
    # bpy.ops.curve.KUKA_OT_Export(                          
    # Export selected curve of the mesh
    bl_idname = "object.kuka_export"
    bl_label = "KUKA_OT_Export (TBxxx)" #Toolbar - Label
    bl_description = "Export selected Curve1" # Kommentar im Specials Kontextmenue
    bl_options = {'REGISTER', 'UNDO'} #Set this options, if you want to update  
    #                                  parameters of this operator interactively 
    #                                  (in the Tools pane) 
    
    
    # check poll() to avoid exception.
    '''
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='EDIT')
    '''  
    print('\n KUKA_OT_Export - KUKAInitBlendFileExecuted:  ' + KUKAInitBlendFileExecuted)
    @classmethod
    def poll(cls, context):
        return (KUKAInitBlendFileExecuted =='True') # Test, ob InitBlendFile vorher ausgefuehrt wurde.
    
    
    
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
        
        # nur fuer Scaling, da Location, Rotatation (mit Hilfe des Mesh-Objektes 'kukaBASEPosObj') beim Export in *.src file geschrieben wird:
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
        writelog('KUKA_OT_Export done')
        return {'FINISHED'}
     

class KUKA_OT_Import (bpy.types.Operator, ImportHelper): # OT fuer Operator Type
    ''' Import selected curve '''
    bl_idname = "object.kuka_import"
    bl_label = "KUKA_OT_Import (TB)" #Toolbar - Label
    bl_description = "Import selected Curve2" # Kommentar im Specials Kontextmenue
    bl_options = {'REGISTER', 'UNDO'} #Set this options, if you want to update  
    #                                  parameters of this operator interactively 
    #                                  (in the Tools pane)
            
    # check poll() to avoid exception.
    @classmethod
    def poll(cls, context):
        return (KUKAInitBlendFileExecuted =='True') # Test, ob InitBlendFile vorher ausgefuehrt wurde.
    
     

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
            pass
        try:
            HOMEPos_Koord, HOMEPos_Angle = RfF_KeyPos('HOMEPos', self.filepath, '.cfg')
        except:
            writelog('failed to load HomePos')
            pass
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
        
        # Achtung: die Reihenfolge von SetCurvePos und SetBasePos muss eingehalten werden! 
        # (da sonst die Curve nicht mit der Base mit verschoben wird!
       
        writelog('_________________KUKA_OT_Import - BASEPos_Koord' + str(BASEPos_Koord))
        writelog('_________________KUKA_OT_Import - BASEPos_Angle' + str(BASEPos_Angle))
        SAFEPos_Koord, SAFEPos_Angle = RfF_KeyPos('PTP', self.filepath, '.src') # PTP = SAFEPos
        writelog('_________________KUKA_OT_Import - BASEPos_Koord' + str(BASEPos_Koord))
        writelog('_________________KUKA_OT_Import - BASEPos_Angle' +'X C {0:.3f}'.format(BASEPos_Angle[0])+' B Y {0:.3f}'.format(BASEPos_Angle[1])+' A Z {0:.3f}'.format(BASEPos_Angle[2]))
        writelog('_________________SAFEPos_Koord: ' + str(SAFEPos_Koord))
        writelog('_________________SAFEPos_Angle' +'X C {0:.3f}'.format(SAFEPos_Angle[0])+' B Y {0:.3f}'.format(SAFEPos_Angle[1])+' A Z {0:.3f}'.format(SAFEPos_Angle[2]))
        # Achtung: Die Reihenfolge der Aufrufe von SetBasePos und get_absolute darf nicht vertauscht werden!
        
        objSafe.location, objSafe.rotation_euler = get_absolute(SAFEPos_Koord, SAFEPos_Angle, objBase, BASEPos_Koord, BASEPos_Angle )        #Transformation Local2World
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
        writelog('KUKA_OT_Import done')
        return {'FINISHED'} 
    
    
class KUKA_OT_SelectPath(bpy.types.Operator):
    bl_idname = "object.kuka_select_path"
    bl_label = "kuka_select_path" #Toolbar - Label
    bl_description = "select curve object" # Kommentar im Specials Kontextmenue
    bl_options = {'REGISTER', 'UNDO'} 
   
    def execute(self, context):  
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects.active = bpy.context.scene.objects[bpy.context.scene.pathname]
        bpy.context.scene.objects.active.select=True
        objCurve    = bpy.data.objects[bpy.context.scene.pathname]
        print('\n objCurve.name: ' + str(objCurve.name))
        info = 'pathname Button: %s selected' % (bpy.context.scene.pathname)
        self.report({'INFO'}, info)
        return {'FINISHED'}     

class KUKA_OT_RefreshButton (bpy.types.Operator):
    ''' Import selected curve '''
    bl_idname = "object.refreshbutton"
    bl_label = "Refresh (TB)" #Toolbar - Label
    bl_description = "Set Animation Data" # Kommentar im Specials Kontextmenue
    bl_options = {'REGISTER', 'UNDO'} #Set this options, if you want to update  
    #                                  parameters of this operator interactively 
    #                                  (in the Tools pane) 
    
    # check poll() to avoid exception.
    @classmethod
    def poll(cls, context):
        return (KUKAInitBlendFileExecuted =='True') # Test, ob InitBlendFile vorher ausgefuehrt wurde.
    
    
 
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
        #PATHPTSObjList =  renamePATHObj(PATHPTSObjList) # wird von DefRoute aufgerufen
        
        
        
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
        
        # PATHPTSObjList an create_PATHPTSObj uebergeben
        # ToDo Okt 2016:
        #PATHPTSCountFile = countPATHPTSObj
        #create_PATHPTSObj(PathPoint, PathPoint, PATHPTSCountFile, BASEPos_Koord, BASEPos_Angle) # relative Koordinaten
        
        
        
        replace_CP(objCurve, PathPoint)  #relativ, weil Origin der Kurve auf BasePos liegt!
        
        bpy.ops.object.select_all(action='DESELECT')
        objEmpty_A6.select=True
        bpy.context.scene.objects.active = objEmpty_A6
        writelog('- - -KUKA_OT_RefreshButton done- - - - - - -') 
        return {'FINISHED'} 
        



class KUKA_OT_animateptps (bpy.types.Operator):
    ''' Import selected curve '''
    bl_idname = "object.animateptps"
    bl_label = "animatePTPs (TB)" #Toolbar - Label
    bl_description = "Set Animation Data for PathPoints (PTPs)" # Kommentar im Specials Kontextmenue
    bl_options = {'REGISTER', 'UNDO'} #Set this options, if you want to update  
    #                                  parameters of this operator interactively 
    #                                  (in the Tools pane) 
    
    # check poll() to avoid exception.
    '''
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='EDIT')
      
    @classmethod
    def poll(cls, context):
        return (bpy.context.active_object.type == 'CURVE') # Test, ob auch wirklich ein 'CURVE' Objekt aktiv ist.
    '''
    @classmethod
    def poll(cls, context):
        return (KUKAInitBlendFileExecuted =='True') # Test, ob InitBlendFile vorher ausgefuehrt wurde.
    
 
    def execute(self, context):  
        writelog('- - -animatePTPs - - - - - - -')
        writelog('Testlog von KUKA_OT_animatePTPs')
        PATHPTSObjList, countPATHPTSObj  = count_PATHPTSObj(PATHPTSObjName)
        
        # TODO: TargetObjList um Basepos erweitern ggf defroute funktion ueberarbeiten/ ueberbehmen
        filepath ='none'
        Route_ObjList = DefRoute(objEmpty_A6, filepath)
        
        #TargetObjList= PATHPTSObjList
        #AnimateOBJScaling(TargetObjList)
        
        AnimateOBJScaling(Route_ObjList)
        writelog('- - -KUKA_OT_animatePTPs done- - - - - - -') 
        return {'FINISHED'} 
    

#class CURVE_OT_RefreshButtonButton(bpy.types.Operator):
# ToDo: ?
# ________________________________________________________________________________________________________________________
 

# return name of selected object
def get_activeSceneObject():
    return bpy.context.scene.objects.active.name

# duplicate selected object
def duplicate_activeSceneObject():
    # used for Pathpoints in the list field
    scene = bpy.context.scene
    src_obj = bpy.context.active_object
    
    new_obj = src_obj.copy()
    new_obj.data = src_obj.data.copy()
    new_obj.animation_data_clear()
    new_obj.location = src_obj.location + Vector((0.05, 0.05, 0.05))
    scene.objects.link(new_obj)
    print('duplicate_activeSceneObject')
    return bpy.ops.object.duplicate(linked=0,mode='TRANSLATION') 


# ui list item actions
class Uilist_actions(bpy.types.Operator):
    bl_idname = "custom.list_action"
    bl_label = "List Action"

    action = bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", ""),
        )
    )
    
        
    

    def invoke(self, context, event):
        print("\n Start execute")
        #ToDo: nach jeder Aenderung muss die Refreshfunktion aufgerufen werden.
        #ToDo: bei 'REMOVE': akutell muss noch nach jeder aktion zuerst 'load PTPs from Scene' gedrueckt werden. Dann erst 'Refresh'

        scene = context.scene
        idx = scene.custom_index
        
        objects = bpy.data.objects
        PATHPTSObjList = fnmatch.filter( [objects [i].name for i in range(len(objects ))] , 'PTPObj_*')
        
        bpy.ops.object.select_all(action='DESELECT')
        n = bpy.data.objects.find(PATHPTSObjList[idx])
        scene.objects.active = objects[n]
        
        try:
            item = scene.custom[idx]
        except IndexError:
            pass

        else:
            if self.action == 'UP' and idx >= 1:
                #Itemliste aendern:
                stack = scene.custom[idx-1].name
                scene.custom[idx-1].name = scene.custom[idx].name
                scene.custom[idx].name = stack
                
                #Objektnamen / TIMEPTS aendern:
                # https://blenderartists.org/forum/showthread.php?235702-How-to-make-a-property-pointing-to-an-object
                '''
-> index keine Feste groesse zum Identifizieren!!!
Even worse: The object index is in alphabetic order and therefore it may change even if another object is renamed... that makes it even worse than using the object name.
--> Meine Loesung geht nur auf Grund der Namenskonvention.
--> Fehler moeglich, wenn Objekte mit anderen Namen hinzukommen!!                
                '''
                n = bpy.data.objects.find(PATHPTSObjList[idx])
                stackObjName1= deepcopy(bpy.data.objects[n].name)     
                stackTimePTSName1= deepcopy(bpy.data.objects[bpy.data.objects[n].name].kuka.TIMEPTS)
                stackObjName2= deepcopy(bpy.data.objects[n-1].name)         
                stackTimePTSName2= deepcopy(bpy.data.objects[bpy.data.objects[n-1].name].kuka.TIMEPTS)      
                bpy.data.objects[n].name = stackObjName2
                bpy.data.objects[bpy.data.objects[n].name].kuka.TIMEPTS = stackTimePTSName2
                bpy.data.objects[n].name = stackObjName1
                bpy.data.objects[bpy.data.objects[n].name].kuka.TIMEPTS = stackTimePTSName1
                bpy.data.objects[n-1].name = stackObjName2 
                bpy.data.objects[bpy.data.objects[n-1].name].kuka.TIMEPTS = stackTimePTSName2
                       
                item_prev = scene.custom[idx-1].name
                scene.custom_index -= 1
                info = 'Object %d moved up' % (scene.custom_index + 1)
                
                
            elif self.action == 'DOWN' and idx < len(scene.custom) - 1:
                
                #Itemliste aendern:
                stack = scene.custom[idx+1].name
                scene.custom[idx+1].name = scene.custom[idx].name
                scene.custom[idx].name = stack
                
                #Objektliste / TIMEPTS aendern:
                n = bpy.data.objects.find(PATHPTSObjList[idx])
                stackObjName1= deepcopy(bpy.data.objects[n].name)    
                stackTimePTSName1= deepcopy(bpy.data.objects[bpy.data.objects[n].name].kuka.TIMEPTS) 
                stackObjName2= deepcopy(bpy.data.objects[n+1].name)    
                stackTimePTSName2= deepcopy(bpy.data.objects[bpy.data.objects[n+1].name].kuka.TIMEPTS)  
                           
                bpy.data.objects[n].name = stackObjName2
                bpy.data.objects[bpy.data.objects[n].name].kuka.TIMEPTS = stackTimePTSName2
                bpy.data.objects[n].name = stackObjName1
                bpy.data.objects[bpy.data.objects[n].name].kuka.TIMEPTS = stackTimePTSName1
                bpy.data.objects[n+1].name = stackObjName2 
                bpy.data.objects[bpy.data.objects[n+1].name].kuka.TIMEPTS = stackTimePTSName2
                                
                item_prev = scene.custom[idx+1].name
                scene.custom_index += 1
                info = 'Object %d moved up' % (scene.custom_index + 1)
                
            elif self.action == 'REMOVE':
                
                # ToDo: verhindern das andere objekte dupliziert/ geloescht werden!
                
                # min. 1 Objekt muss erhalten bleiben!
                if (len(PATHPTSObjList)>1):
                    # selection
                    bpy.data.objects[scene.custom[scene.custom_index].name].select = True
                    # remove it
                    bpy.ops.object.delete() 
                    info = 'Item %s removed from list' % \
                    (scene.custom[scene.custom_index].name)
                    scene.custom_index -= 1
                    self.report({'INFO'}, info)
                    scene.custom.remove(idx)
                else:
                    info = 'Minimum one PTPObj needed!'
                    self.report({'INFO'}, info)
                    
                
                #ToDo: akutell muss noch nach jeder aktion zuerst 'load PTPs from Scene' gedrueckt werden. Dann erst 'Refresh'
                
        if self.action == 'ADD':
            # ToDo: verhindern das andere objekte dupliziert/ geloescht werden!
            
            idx = scene.custom_index 
            duplicate_activeSceneObject()
            #bpy.ops.object.duplicate_move() funktioniert nicht
            # http://blender.stackexchange.com/questions/45099/duplicating-a-mesh-object
            
            # refresh aufrufen:
            bpy.ops.custom.get_pathpts()
            scene.custom_index = idx+1
            # ToDo: scene.custom.get_pathpts() warum nicht??
            # ToDo: rename aufrufen
            
            info = '%s added to list' % (item.name)
            self.report({'INFO'}, info)
        
        

        
        return {"FINISHED"}


# -------------------------------------------------------------------
# draw
# -------------------------------------------------------------------

# select_list_item_in_scene
class Uilist_selectListItemInScene(bpy.types.Operator):
    bl_idname = "custom.select_list_item_in_scene"
    bl_label = "Select List Item in Scene"
    bl_description = "Select List Item in Scene"

    def execute(self, context):
        scn = context.scene
        bpy.ops.object.select_all(action='DESELECT')
        obj = bpy.data.objects[scn.custom[scn.custom_index].name]
        obj.select = True
        bpy.context.scene.objects.active = obj

        return{'FINISHED'}


# select_scene_item_in_list
class Uilist_selectSceneItemInList(bpy.types.Operator):
    bl_idname = "custom.select_scene_item_in_list"
    bl_label = "Select Scene Item in List"
    bl_description = "Select Scene Item in List"

    def execute(self, context):
        scn = context.scene
        
        PATHPTSObjList = fnmatch.filter( [bpy.data.objects[i].name for i in range(len(bpy.data.objects))] , 'PTPObj_*')
        if PATHPTSObjList!="":
            
            for i in range(len(PATHPTSObjList)):
                if PATHPTSObjList[i] == bpy.context.scene.objects.active.name:
                    bpy.context.scene.custom_index = i

        return{'FINISHED'}

# custom list
class UL_items(UIList):
    
     
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout.split(0.3)
        split.label("Index: %d" % (index))
        split.prop(item, "name", text="", emboss=False, translate=False, icon='MANIPUL')
    
    print('\n UL_items')
    


# draw the panel
class KUKA_PT_Panel(bpy.types.Panel):
#class UIListPanelExample(Panel):
    """Creates a Panel in the Object properties window"""
    bl_idname = 'OBJECT_PT_my_panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "KUKA Tools"
    bl_label = "KUKA Tools"
    
    def draw(self, context):
        
        '''
        writelog('_____________________________________________________________________________')
        writelog('FUNKTIONSAUFRUF - KUKA_PT_Panel')
        '''
        ob = context.object
        layout = self.layout
        scene = context.scene
        
        kuka = bpy.data.objects # bpy.types.Object.kuka
        # kuka['Cube'].kuka.
        
        obj = bpy.context.scene.objects.active
        
        # Liste initialisieren:
        # PATHPTSObjName ist erst nach druecken des InitBlendFile Button bekannt
        # prop_search(data, property, search_data, search_property, text="", text_ctxt="", translate=True, icon='NONE')
        # pruefen ob PATHPTSObjList als Obj vorhanden ist.
        
        # Init variable from blendFile:
        row = layout.row(align=True)
        sub = row.row()
        sub.scale_x = 1.0
        sub.operator("object.kuka_init_blendfile", text="init .blend")  
        
        sub.operator("object.kuka_select_path", text="Path") 
        layout.prop_search(context.scene, "pathname", bpy.data, "curves", "Path Name")
        
        # ToDo: Beziercurve auswaehlen (vorher mit GreacePencil gezeichnet und konvertiert)
        # --> OK. aber: die Kurve orientiert sich an den PTPObj
        # --> d.h. die PTPObj muessen erst an Hand der neuen Kurve erstellt werden,
        # 2 Moeglichkeiten:
        # a): PTPObj von alter Kurve auf neue verschieben/ Anzahl anpassen
        # b): neue PTPObj Gruppe erstellen 
        # ToDo: Listenfeld mit concatonate of several curves
        
        row = layout.row(align=True)
        row.prop(kuka[ob.name].kuka, "ORIGINType", text="Origin:")
        #print(kuka[ob.name].kuka.ORIGINType)
        
        props = row.operator("object.set_locrot", text="set Position")
        props = row.operator("object.get_rel_locrot", text="get Position")
                
        # Create two columns, by using a split layout.
        row = layout.row()
        #row.column().prop(ob, "delta_location")
        row.column().prop(kuka[obj.name].kuka, "PATHPTSloc", text="Location") 
        row.column().prop(kuka[obj.name].kuka, "PATHPTSrot", text="Rotation")
                
        #ob.rotation_mode ='rotation_euler'
        
        rows = 2
        row = layout.row()
        row.template_list("UL_items", "", scene, "custom", scene, "custom_index", rows=rows)
        
        
        col = row.column(align=True)
        col.operator("custom.list_action", icon='ZOOMIN', text="").action = 'ADD'
        col.operator("custom.list_action", icon='ZOOMOUT', text="").action = 'REMOVE'
        col.separator()
        col.operator("custom.list_action", icon='TRIA_UP', text="").action = 'UP'
        col.operator("custom.list_action", icon='TRIA_DOWN', text="").action = 'DOWN'

        row = layout.row()
        col = row.column(align=True)
        
        col.operator("custom.select_list_item_in_scene", icon="PASTEDOWN")
        col.operator("custom.select_scene_item_in_list", icon="COPYDOWN")
        col.operator("custom.get_pathpts", icon="FILE_REFRESH")
        col.operator("custom.get_filelist", icon="FILESEL")
        
        # Import/ Export Button:
        layout.label(text="Curvepath Import/ Export:")
        row = layout.row(align=True)        
        sub = row.row()
        sub.scale_x = 1.0
        sub.operator("object.kuka_import", icon='IMPORT')  
        row.operator("object.kuka_export", icon='EXPORT') 
        
        # Set KeyFrames Button:
        layout.label(text="Refresh Button:")
        row = layout.row(align=True)
        
        row.operator("object.refreshbutton", icon='FILE_REFRESH')  
        
        # Animate PTPs Button:
        layout.label(text="Animate PTPs:")
        row = layout.row(align=True)
         
        row.operator("object.animateptps")  
        
        
        
class Uilist_getPTPsFromScene(bpy.types.Operator):
    bl_idname = "custom.get_pathpts"
    bl_label = "load PTPs from Scene"
    bl_description = "load PTPs from Scene"

    def execute(self, context):
        # get PTPObj- Objects from scene:
        
        # die folgenden beiden Zeilen koennen das KUKATool optimieren
        # beachte: 'imort fnmatch' benoetigt
        objects = bpy.data.objects
        PATHPTSObjList = fnmatch.filter( [objects [i].name for i in range(len(objects ))] , 'PTPObj_*')
        
        print('\n\n PATHPTSObjList' + str(PATHPTSObjList))
        scene = context.scene    
        scene.custom.clear() 
        for i in range(len(PATHPTSObjList)):
            
            item = scene.custom.add()
            item.id = len(scene.custom)
            item.name = PATHPTSObjList[i]
            scene.custom_index = (len(scene.custom)-1)
            
        info = '%s added to list' % (item.name)
        self.report({'INFO'}, info)
        return{'FINISHED'}
 
class Uilist_loadFileList(bpy.types.Operator):
    bl_idname = "custom.get_filelist"
    bl_label = "load .blend file list"
    bl_description = "load file list from disc"

    def execute(self, context):     
        scene = context.scene  
        mylist = [] # empty the list    
        scene.custom.clear()  
        start_path = 'D:\OneDrive\_EWa_KUKA-Tutorial' # current directory. Change to your needs. Do NOT use backslashes here.
        for path,dirs,files in os.walk(start_path):
            for filename in files:
                if filename.endswith(".blend"):
                    mylist.append(os.path.join(filename))
        print (mylist) # debugging. The content in the console.
        
        for i in range(len(mylist)):
            item = scene.custom.add()
            item.id = len(scene.custom)
            item.name = mylist[i]
            scene.custom_index = (len(scene.custom)-1)
            
        info = '%s added to list' % (item.name)
        self.report({'INFO'}, info)
        return{'FINISHED'}             

# Create custom property group
class CustomProp(bpy.types.PropertyGroup):
    #'''name = StringProperty() '''
    id = IntProperty()



    



# ________________________________________________________________________________________________________________________


   
def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.custom = CollectionProperty(type=CustomProp)
    bpy.types.Scene.custom_index = IntProperty()
    bpy.types.Scene.pathname = StringProperty()
    
    
def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.custom
    del bpy.types.Scene.custom_index
    del bpy.types.Scene.pathname

if __name__ == "__main__":
    register()


    