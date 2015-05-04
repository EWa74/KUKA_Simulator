import bpy
import mathutils
import math
'''
{1}    action = context.blend_data.actions.new("anumation_action")
{2}    obj.animation_data.action = action
{3}    path = obj.path_from_id('property_to_animate')
{4}    fcurve = action.fcurves.new(path, index=0)
'''

def generate_keyframes():
    context = bpy.context
    scene = bpy.context.scene

    # create action (container for the folowing fcurves)
    # link the action to the "Cube" object
    # create fcurves to animate the "Cube" object
    action_cube = context.blend_data.actions.new("myActionCube")
    obj_cube = bpy.context.scene.objects.get("Cube")
    if not obj_cube.animation_data:
        obj_cube.animation_data_create()
    obj_cube.animation_data.action = action_cube
    #path_rotation = obj.path_from_id("rotation_quaternion")
    #fcurve_rotation_w = action.fcurves.new(path_rotation, index=0)
    #fcurve_rotation_x = action.fcurves.new(path_rotation, index=1)
    #fcurve_rotation_y = action.fcurves.new(path_rotation, index=2)
    #fcurve_rotation_z = action.fcurves.new(path_rotation, index=3)
    path_rotation = obj_cube.path_from_id("rotation_euler")
    fcurve_rotation_x = action_cube.fcurves.new(path_rotation, index=0)
    fcurve_rotation_y = action_cube.fcurves.new(path_rotation, index=1)
    fcurve_rotation_z = action_cube.fcurves.new(path_rotation, index=2)

    # create fcurves to animate the "Cube" material diffuse color
    # link the action to the material
    # create action (container for the folowing fcurves)
    action_material = context.blend_data.actions.new("myActionMaterial")
    obj_material = obj_cube.material_slots.get("Material")
    if not obj_material.material.animation_data:
        obj_material.material.animation_data_create()
    obj_material.material.animation_data.action = action_material
    path_color = obj_material.material.path_from_id('diffuse_color')
    fcurve_color_r = action_material.fcurves.new(path_color, index=0)
    fcurve_color_g = action_material.fcurves.new(path_color, index=1)
    fcurve_color_b = action_material.fcurves.new(path_color, index=2)

    # create action (container for the folowing fcurves)
    # link the action to the "Lamp" object
    # create fcurves to animate the "Lamp" object
    action_lamp = context.blend_data.actions.new("myActionLamp")
    obj_lamp = bpy.context.scene.objects.get("Lamp")
    if not obj_lamp.animation_data:
        obj_lamp.animation_data_create()
    obj_lamp.animation_data.action = action_lamp
    path_location = obj_lamp.path_from_id('location')
    fcurve_location_x = action_lamp.fcurves.new(path_location, index=0)
    fcurve_location_y = action_lamp.fcurves.new(path_location, index=1)
    fcurve_location_z = action_lamp.fcurves.new(path_location, index=2)

    frame_time_total = (scene.frame_end - scene.frame_start) / (scene.render.fps / scene.render.fps_base)

    for frame in range(scene.frame_start, scene.frame_end + 1, scene.frame_step):
        frame_time = (frame - scene.frame_start) / (scene.render.fps / scene.render.fps_base)
        print(frame, frame_time, frame_time_total)

        angle360 = math.radians(360 / frame_time_total * frame_time)

        # animate the lamp
        radius = 6.0
        x = math.sin(angle360) * radius
        y = math.cos(angle360) * radius
        z = math.sin(angle360 * 2.0) * radius
        fcurve_location_x.keyframe_points.insert(frame, x)
        fcurve_location_y.keyframe_points.insert(frame, y)
        fcurve_location_z.keyframe_points.insert(frame, z)

        # animate the material
        r = (1.0 + math.sin(angle360)) * 0.5
        g = (1.0 + math.cos(angle360)) * 0.5
        b = (1.0 + math.sin(angle360 * 2.0)) * 0.5
        fcurve_color_r.keyframe_points.insert(frame, r)
        fcurve_color_g.keyframe_points.insert(frame, g)
        fcurve_color_b.keyframe_points.insert(frame, b)

        # animate the cube
        x = angle360 * 0.25
        y = angle360 * 0.5
        z = angle360
        fcurve_rotation_x.keyframe_points.insert(frame, x)
        fcurve_rotation_y.keyframe_points.insert(frame, y)
        fcurve_rotation_z.keyframe_points.insert(frame, z)


generate_keyframes()






import bpy
print('start....')
ob = bpy.data.objects['Empty_Zentralhand_A6']


action=bpy.data.actions['Empty_Zentralhand_A6Action.025']
    
len(action.fcurves) # Anzahl der keyframes

action.fcurves[0].keyframe_points[0].co # Ergebnis: Vector(Frame[0] Wert, x Wert)
action.fcurves[1].keyframe_points[0].co # Ergebnis: Vector(Frame[0] Wert, y Wert)
action.fcurves[2].keyframe_points[0].co # Ergebnis: Vector(Frame[0] Wert, z Wert)
action.fcurves[0].keyframe_points[1].co # Ergebnis: Vector(Frame[1] Wert, x Wert)
    
'''
for curve in bpy.context.object.animation_data.action.fcurves:
    print("%s[%i]" % (curve.data_path, curve.array_index))
    print("%s[%i]" % (curve.data_path, curve.array_index))
'''    
print(" Keyframe points (x):")

timeframes = bpy.context.object.animation_data.action.fcurves[0].keyframe_points
for p in timeframes:
    print(" %f" % p.co.x)

print('....')
    

# action.fcurves[0].data_path

# Transfer the DATA action.
action_name = ""
da_source = ob.data
if da_source != None:
    ad = ob.animation_data
else:
    print("Action is None.")
if ad != None:
    ac = ad.action
else:
    print ("Animation data for [%s] is None." % ob.name)
if ac != None:
    action_name = ac.name
    #print(action_name)
    can_proceed = True   
else:
    print ("Object data is None.")
try:
    action = bpy.data.actions[action_name]
    can_proceed = True
except:
    print("ERROR: Can not proceed! [%s]." % action_name)
    can_proceed = False
if can_proceed == True:
    da_target = ob_target.data
for i,fcurve in enumerate(action.fcurves):
    v = fcurve.evaluate(offset_frame)
    # Construct a string that will set the value directly when executed.
s = "da_target." + fcurve.data_path + " = " + str(v)
name_space = {}
code = compile(s, '<string>', 'exec')
try:
    exec (code) in name_space
except:
    print ("Target datablock [" + current_target + "] can not accept data for [" +     str(fcurve.data_path) + "].")

# Transfer the OBJECT action.
try:
    action_name = ob.animation_data.action.name
except:
    action_name = ""
try:
    action = bpy.data.actions[action_name]
    can_proceed = True
except:
    can_proceed = False
if can_proceed == True:
    print("Transfering action [" + action_name + "] to [" + current_target + "].")
# New approach, read f-curve directly.
loc = [0.0,0.0,0.0] #ob_target.location #[0.0,0.0,0.0]
rot = [0.0,0.0,0.0] #ob_target.rotation_euler #[0.0,0.0,0.0]
scale = [1.0,1.0,1.0] #ob_target.scale #[1.0,1.0,1.0]
for i,fcurve in enumerate(action.fcurves):
    
    try:
        v = fcurve.evaluate(offset_frame)
        if fcurve.data_path == "location":
            loc[fcurve.array_index] = v
            ob_target.delta_location[fcurve.array_index]=v
            print("Assigning delta_location[" + str(fcurve.array_index) + "] to (" + str(v) + ").")
        elif fcurve.data_path == "rotation_euler":
            rot[fcurve.array_index] = v
            ob_target.delta_rotation_euler[fcurve.array_index]=v
            print("Assigning delta_rotation_euler[" + str(fcurve.array_index) + "] to (" + str(v) + ").")
        elif fcurve.data_path == "scale":
            scale[fcurve.array_index] = v
            ob_target.delta_scale[fcurve.array_index]=v
            print("Assigning delta_scale[" + str(fcurve.array_index) + "] to (" + str(v) + ").")
        else:
            print("Unsupported data_path [" + fcurve.data_path + "].")
    except:
        print("refresh problem operating upon bpy.data.")
'''
To read an f-curve use the evalute method and the frame you which to retireve the value from. This does not have to be the frame # you are currently on. You can fetch vaues from any point in the timeline.

To write to the f-curve, the above technique construct a string which is a valid Blender python command then executes the string to issue the assignment.

I have also used this single point f-curve approach as well. Basically create a single key f-curve on frame #1. Then it does not matter what frame # you are on. Just change the value on frame #1. This is for controlling an f-curve programmatically.
'''

################################################## ##########################
# f-Curve code.
################################################## ##########################
def makeSinglePointFCurve(passedName,passedDataPath, passedTarget, passedValue):
    # Use code generated f-curve solution.
    # Check for presence of f-curve.
    try:
        action = bpy.data.actions[passedName]
        can_proceed = True
    except:
        can_proceed = False
    if can_proceed == False:
    # Perform this one type setup of an f-curve.
    # Create a single point f-curve to act as a constant.
        print("Creating action [" + passedName + "] to control " + passedDataPath + ".")
        action = bpy.data.actions.new(passedName)

        action.fcurves.new(passedDataPath, action_group="managed by code")
        action.fcurves[0].keyframe_points.insert(1, 0.0) #frame, value,       option=set('FAST')

        passedTarget.animation_data_create()
        passedTarget.animation_data.action=action
    else:
        #print (action)
        pass

    # Assign value by changing frame #1 of the fcurve.
    print("Assigning " + passedDataPath + " " +str(passedValue) + " to particle [" + passedName +"].")
    action.fcurves[0].keyframe_points.insert(1, passedValue)
    action.fcurves[0].color_mode = 'CUSTOM'
    action.fcurves[0].extrapolation = 'LINEAR'
    action.fcurves[0].color = (0.6,0.0, 1.0) # Code managed f-curves will have their own custom color.
    action.fcurves[0].lock = False
    
import bpy
print('---------------- START -----------------------')
ob_target = bpy.data.objects['Empty_Zentralhand_A6']
action=bpy.data.actions['Empty_Zentralhand_A6Action.025'] 
print(action)
# action.fcurves[0].data_path
loc=['xx',9999,9999]
rot=[9999,9999,9999]
scale=[9999,9999,9999]
dloc =[9999,9999,9999]
#v = fcurve.evaluate(offset_frame)
 
action_data =action.fcurves
print(action_data)
#for v in action_data:
for v,action_data in enumerate(action_data):
    if action_data.data_path == "location":
        loc[action_data.array_index] = v
        #ob_target.delta_location[action_data.array_index]=v
        print("location[" + str(action_data.array_index) + "] to (" + str(v) + ").")
    elif action_data.data_path == "rotation_euler":
        rot[action_data.array_index] = v
        #ob_target.delta_rotation_euler[action_data.array_index]=v
        print("rotation_euler[" + str(action_data.array_index) + "] to (" + str(v) + ").")
    elif action_data.data_path == "scale":
         scale[action_data.array_index] = v
         #ob_target.delta_scale[action_data.array_index]=v
         print("scale[" + str(action_data.array_index) + "] to (" + str(v) + ").")
    elif action_data.data_path == "delta_location":
         dloc[action_data.array_index] = v
         #ob_target.delta_scale[action_data.array_index]=v
         print("delta_location[" + str(action_data.array_index) + "] to (" + str(v) + ").")
    else:
         print("Unsupported data_path [" + action_data.data_path + "].")

print("fcurves ID from location [" + str(loc) + "].")
print("fcurves ID from rotation_euler [" + str(rot) + "].")
print("fcurves ID from scale [" + str(scale) + "].")
print("fcurves ID from delta_location [" + str(dloc) + "].")

print('---------------- END -----------------------')

















        


class ClassSetKeyFrames (bpy.types.Operator):
    print('ClassSetKeyFrames- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ') 
    print('- - - - - - - - - - - - -  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')
    ''' Import selected curve '''
    bl_idname = "curve.setkeyframes"
    bl_label = "Set KeyFrames (TB)" #Toolbar - Label
    bl_description = "Set Animation Data" # Kommentar im Specials Kontextmenue
    bl_options = {'REGISTER', 'UNDO'} #Set this options, if you want to update  
    #                                  parameters of this operator interactively 
    #                                  (in the Tools pane) 
 
    def execute(self, context):  
        print('- - -SetKeyFrames - - - - - - -')
        
        objBase = bpy.data.objects['Sphere_BASEPos']
        objSafe = bpy.data.objects['Sphere_SAFEPos']
        objCurve = bpy.data.objects['BezierCircle']
        objEmpty_A6 = bpy.data.objects['Empty_Zentralhand_A6']
        PATHPTSObjName = 'PTPObj_'
        
        ApplyScale(context.object) 
        #--------------------------------------------------------------------------------
        
        BASEPos_Koord, BASEPos_Angle = RfS_BasePos(context.object, self.filepath)
        SAFEPos_Koord, SAFEPos_Angle = RfS_LocRot(objSafe, objSafe.location, objSafe.rotation_euler, BASEPos_Koord, BASEPos_Angle)
        PATHPTSObjList, countPATHPTSObj  = count_PATHPTSObj(PATHPTSObjName)
        #dataPATHPTS_Loc, dataPATHPTS_Rot, PATHPTSCountFile = RfS_LocRot(objSafe, objSafe.location, objSafe.rotation_euler, BASEPos_Koord, BASEPos_Angle)
        SetCurvePos(context.object, objBase, BASEPos_Koord, BASEPos_Angle)
        replace_CP(objCurve, PATHPTSObjName, '', countPATHPTSObj, BASEPos_Koord, BASEPos_Angle) 
        
        SetKukaToCurve(context.object)
        
        filepath ='none'
        GetRoute(objEmpty_A6, PATHPTSObjList, countPATHPTSObj, filepath)
        
        return {'FINISHED'} 
    print('- - -SetKeyFrames class done- - - - - - -')     