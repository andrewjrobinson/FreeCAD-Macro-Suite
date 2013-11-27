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
Makes a face (triangle) from 3 Vertexes.  You can select any number of sub-objects as-
long-as the total unique vertexes is 3.  e.g. you could select 2 edges (as long as 
they have one vertex in common OR 1 vertex and 1 edge OR 3 vertexes etc.

@see: MergeFaces.py for a macro to join 2 (or more) planar faces.
'''

import FreeCADGui as Gui, FreeCAD, Part, math

printfc = FreeCAD.Console.PrintMessage



def tupleVert(tup):
    '''Converts a tuple representation of vertex into Vertex'''
    return Part.Vertex(*tup)

def vertTuple(vert):
    '''Makes a 3-tuple representing a vertex'''
    return (vert.X, vert.Y, vert.Z)


# 3 unique verts (from any sub-object selection)
verts = set([])
for sel in Gui.Selection.getSelectionEx():
    for obj in sel.SubObjects:
        for vert in obj.Vertexes:
            verts.add(vertTuple(vert))

if len(verts) != 3:
    printfc("You must only select 3 vertexes\n")
else:
    vertexes = []
    for v in verts:
        vertexes.append(tupleVert(v))
    edges = [Part.Edge(vertexes[0], vertexes[1]), Part.Edge(vertexes[1], vertexes[2]), Part.Edge(vertexes[2], vertexes[0])]
    wire = Part.Wire(edges)
    face = Part.Face(wire)
    Part.show(face)
