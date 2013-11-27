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
A macro to convert selected sketcher lines (in selection-order) into Basic GCode.

The output is printed to the FreeCAD console (which you can copy to a file of your 
choice).  NOTE: Ctrl-C keyboard shortcut doesn't work from the console.

Note: this macro doesn't yet know how to tell the direction of an arc so it assumes 
Clockwise.  You will need to change the G02 to G03 of incorrect ones.
'''

import FreeCADGui as Gui, FreeCAD, Part, math
from itertools import izip_longest

## Begin Settings ##
# basic configuration groups.  Use the useConfig setting below to select which is used.
config = {"pocket":  {"slowAtCorners": True,    # Use slow movement speed near end of lines
                      "slowLen": 4,             # The number of units from end points to enter slow speed 
                                                #  (note: if lines total length is less than 2.5x this number then it will slow for whole line)
                      "feedRate": 200,          # Rate of movement for regular feed movements
                      "slowRate": 100,          # rate of movement for slow movements (approaching end of lines)
                      "useZDepth": True,        # if False, replaces Z coord with Zcut for feed movements
                      },
          "contour": {"slowAtCorners": False,
                      "feedRate": 200,
                      "useZDepth": True,
                      },
          }

# selects which of the above setting group is used
useConfig = "pocket"

# some constants for starting points and rapid movements
Zrapid = 1.0
Zsurface = 0.0
Zcut = -3.0

# offset all gcode coordinates by a given X, Y, Z amount.  This point is considered to origin
G54 = (0, -3, 20)

## end settings ##

# extract required settings
defaultSettings = {"slowAtCorners": True, "slowLen": 4, "feedRate": 200, "slowRate": 100, "useZDepth": True,}
defaultSettings.update(config[useConfig])
slowAtCorners = defaultSettings['slowAtCorners']
slowLen = defaultSettings['slowLen']
feedRate = defaultSettings['feedRate']
slowRate = defaultSettings['slowRate']
useZDepth = defaultSettings['useZDepth']

# definitions
printfc = FreeCAD.Console.PrintMessage

def vertexString(vert):
    return "%s|%s|%s" % (vert.X, vert.Y, vert.Z)
def vectorString(vect):
    return "%s|%s|%s" % (vect.x, vect.y, vect.z)

def toStr(line):
    return "Line [%s -> %s]" % (vertexString(line.Vertexes[0]),vertexString(line.Vertexes[1]))

def feed(edge, currentVert, nextVert):
    X = round(nextVert.X,3)
    Y = round(nextVert.Y,3)
    if type(edge.Curve) == Part.Line:
        if slowAtCorners:
            if edge.Length >= 2.5*slowLen:
                Xd = (currentVert.X - nextVert.X) / edge.Length * slowLen
                Yd = (currentVert.Y - nextVert.Y) / edge.Length * slowLen
                printfc("G01 X%s Y%s F%s\n" % (X + Xd - G54[0], Y + Yd - G54[1], feedRate))
                printfc("G01 X%s Y%s F%s\n" % (X - G54[0], Y - G54[1], slowRate))
            else:
                printfc("G01 X%s Y%s F%s\n" % (X - G54[0], Y - G54[1], slowRate))
        else:
            printfc("G01 X%s Y%s F%s\n" % (X - G54[0], Y - G54[1], feedRate))
    elif type(edge.Curve) == Part.Circle:
        cen = edge.Curve.Center
        I = round(cen.x - currentVert.X,3)
        J = round(cen.y - currentVert.Y,3)
        printfc("G02 X%s Y%s I%s J%s\n" % (X - G54[0], Y - G54[1], I, J))

# start GCode
printfc("\n----------\n%\nG54 G21 G90 G40\n\n")


sel = Gui.Selection.getSelectionEx()[0]


# process from line to line
lastEdge = None
lastVerts = []
doneFirst = False
for edge in sel.SubObjects:
    if lastEdge:
        if vertexString(edge.Vertexes[0]) in lastVerts:
            currentVert = edge.Vertexes[0]
            nextVert = edge.Vertexes[1]
        elif vertexString(edge.Vertexes[1]) in lastVerts:
            currentVert = edge.Vertexes[1]
            nextVert = edge.Vertexes[0]
        else:
            printfc("Lines don't join\nEdge: %s\nLast edge: %s\n" % (toStr(edge), toStr(lastEdge)))
            break
        
        if not doneFirst:
            # find other end of first line
            if vertexString(lastEdge.Vertexes[0]) == vertexString(currentVert):
                startVert = lastEdge.Vertexes[1]
            else:
                startVert = lastEdge.Vertexes[0]
            
            # setup
            X = round(startVert.X,3)
            Y = round(startVert.Y,3)
            printfc("(Move to start)\n")
            printfc("G00 Z%s\n" % (Zrapid,))
            printfc("G00 X%s Y%s\n" % (X - G54[0], Y - G54[1]))
            if useZDepth:
                Z = round(startVert.Z,3)
                printfc("G01 Z%s F100 (Plunge)\n" % (Z - G54[2],))
            else:
                printfc("G01 Z%s F100 (Plunge)\n" % (Zcut,))
                
            printfc("(Program)\n")
            
            # do first line
            feed(lastEdge, startVert, currentVert)
            doneFirst = True
        
        # do current line
        feed(edge, currentVert, nextVert)
        
    lastVerts = [vertexString(edge.Vertexes[0]), vertexString(edge.Vertexes[1])]
    lastEdge = edge

printfc("G00 Z1.0 (Retract)\n\nM30 (Program End)\n%\n")
    