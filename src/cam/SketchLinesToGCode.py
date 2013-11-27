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
A macro to convert selected sketcher lines (in-order) into Basic GCode
Note: this is an older version
@see: LinesToGCode.py for a more advanced version
'''

import FreeCADGui as Gui, FreeCAD, Part, math
from itertools import izip_longest
from pivy import coin

printfc = FreeCAD.Console.PrintMessage

def vertexString(vert):
    return "%s|%s|%s" % (vert.X, vert.Y, vert.Z)
def vectorString(vect):
    return "%s|%s|%s" % (vect.x, vect.y, vect.z)

def toStr(line):
    return "Line [%s -> %s]" % (vertexString(line.Vertexes[0]),vertexString(line.Vertexes[1]))

printfc("starting\n")

Zval = -3.0


sel = Gui.Selection.getSelectionEx()[0]
sketch = Gui.Selection.getSelection()[0]
edgeNames = sel.SubElementNames

# get first point
startName = edgeNames[0]
if startName.startswith("Vertex"):
    nextVert = sketch.Shape.Vertexes[int(startName[6:])]
    printfc("G01 X%s Y%s Z%s\n" % (round(nextVert.X,3), round(nextVert.Y,3), Zval))
    edgeNames = edgeNames[1:]

# process from line to line
lastEdge = None
lastVerts = []
for edgeName in edgeNames:
    if edgeName.startswith("Edge"):
        edge = sketch.Geometry[int(edgeName[4:])]
        if lastEdge:
            if vectorString(edge.StartPoint) in lastVerts:
                nextVert = edge.StartPoint
                currentVert = edge.EndPoint
            elif vectorString(edge.EndPoint) in lastVerts:
                nextVert = edge.EndPoint
                currentVert = edge.StartPoint
            else:
                printfc("Lines don't join\nEdge: %s\nLast edge: %s\n" % (toStr(edge), toStr(lastEdge)))
                break
            
            X = round(nextVert.x,3)
            Y = round(nextVert.y,3)
            if type(edge.Curve) == Part.Line:
                printfc("G01 X%s Y%s Z%s\n" % (X, Y, Zval))
            elif type(edge.Curve) == Part.Circle:
                cen = edge.Curve.Center
                I = round(currentVert.x - cen.x,3)
                J = round(currentVert.y - cen.y,3)
                printfc("G02 X%s Y%s Z%s I%s J%s\n" % (X, Y, Zval, I, J))
            
        lastVerts = [vectorString(edge.StartPoint), vectorString(edge.EndPoint)]
        lastEdge = edge
    else:
        printfc( "skipping %s\n" % edgeName)

if currentVert:
    printfc("G01 X%s Y%s Z%s\n" % (round(currentVert.x,3), round(currentVert.y,3), Zval))