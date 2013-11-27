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
Makes a solid from a bunch of faces.

@see: MakeFace.py, to make triangles to fill in gaps between other objects
@see: MergeFaces.py, to reduce the number of faces

@todo: This macro currently doesn't produce a proper solid.  It looks ok but doesn't cooperate with the boolean operators.
'''

import FreeCADGui as Gui, FreeCAD, Part, math

printfc = FreeCAD.Console.PrintMessage

faces = []

for sel in Gui.Selection.getSelectionEx():
    if len(sel.Object.Shape.Faces):
        faces.extend(sel.Object.Shape.Faces)
    else:
        faces.extend(sel.SubObjects)
    

shell=Part.makeShell(faces)
solid=Part.makeSolid(shell)
Part.show(solid)


