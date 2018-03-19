# KUKA_Simulator
Based on a bezier curve in Blender 3D a path can be imported/ exported/ edited for KUKA Occubot robot arm.
In case of Gimbal-lock problem a second push on 'refresh' normaly fix it.
Pathpoints are animated.

Following steps are planned:
- time input per GUI (currently automated time calculation running)
- Force input per GUI
- Force/ Physics simulation/ calculation
- currently the pathpoints are 1:1 between Blender and real KUKA. The way from Point to Point is not implemented e.g.: Point to Point, HandMode/ 'Teachen'
, SchrittMmode, AutomatikMode: die Folgepunkte werden mit berücksichtigt 'Vorlauf' and Überschleifen
- XBox 3D-Cam to be mounted on robot arm to scann the 'Werkstück'

KUKA

New Project created for next updates: [KUKA-Tools2018] with .blend file
