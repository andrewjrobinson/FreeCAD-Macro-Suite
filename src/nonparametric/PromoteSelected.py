######################################################################################
#    This file is part of the FreeCAD Macro Suite                                    #
#                                                                                    #
#    Copyright (C) 2013 Andrew Robinson (andrewjrobinson@gmail.com)                  #
#                                                                                    #
#    This library is free software; you can redistribute it and/or                   #
#    modify it under the terms of the GNU Lesser General Public                      #
#    License as published by the Free Software Foundation; either                    #
#    version 2.1 of the License, or (at your option) any later version.              #
#                                                                                    #
#    This library is distributed in the hope that it will be useful,                 #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of                  #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU               #
#    Lesser General Public License for more details.                                 #
#                                                                                    #
#    You should have received a copy of the GNU Lesser General Public                #
#    License along with this library; if not, write to the Free Software             #
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA  #
######################################################################################

'''
Promotes the selected sub-objects to first class objects.  It functions on all sub-
object types i.e. Face, Edge, Wire, etc.
e.g. if you select a face it will make a new shape with a single face (a clone of the 
one you selected).  If you select 2 faces it will create two shapes with 1 face.
'''


import FreeCADGui as Gui, FreeCAD, Part, math

printfc = FreeCAD.Console.PrintMessage


for sel in Gui.Selection.getSelectionEx():
    for so in sel.SubObjects:
        Part.show(so)

