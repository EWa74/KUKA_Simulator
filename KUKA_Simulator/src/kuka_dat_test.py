# http://wiki.blender.org/index.php/Doc:2.6/Manual/Extensions/Python/Properties
# http://www.blender.org/documentation/blender_python_api_2_57_1/bpy.props.html


import bpy


class ObjectSettings(bpy.types.PropertyGroup):
    ID = bpy.props.IntProperty()
    TIMEPTS = bpy.props.FloatProperty()
    ACTIONMSK = bpy.props.FloatProperty()
    STOP = bpy.props.StringProperty()

bpy.utils.register_class(ObjectSettings)


print('Hallo kuka_dat 023')
def Eric():
    print('Hallo kuka_dat Funktion Eric')
    
# http://pythonhosted.org/ete2/tutorial/tutorial_trees.html
    

class kuka: 
   'Common base class for all employees' 
   empCount = 0 
 
   def __init__(self, PATHPTS, TIMEPTS): 
      self.name = name 
      self.PATHPTS = [] 
      self.PATHPTS.TIMEPTS = []
      Employee.empCount += 1 
    
   def displayCount(self): 
     print "Total Employee %d" % Employee.empCount 
 
   def displayEmployee(self): 
      print "Name : ", self.name,  ", Salary: ", self.salary 
   
   