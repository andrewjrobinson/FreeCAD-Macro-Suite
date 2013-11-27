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
Makes an airfoil profile (.dat file) into a face.

This is a method that work's around some problems my pivy/coin installation has.
'''

import FreeCADGui as Gui, FreeCAD, Part, math
from IN import INTMAX_C, INTMAX_MIN, INTMAX_MAX

printfc = FreeCAD.Console.PrintMessage

# targetLen = 340
targetLen = 260
Xcoord = 0
filename = '/home/arobinson/Documents/RC Plane/E214 profile.dat'


# extract 2D points (and save in 3D)
f = open(filename)
f.readline() # remove header
points = []
maxlen = INTMAX_MIN
minlen = INTMAX_MAX
minheight = INTMAX_MAX
for line in f:
    nums = line.split()
    if len(nums) > 0:
        pa = float(nums[0])
        pb = float(nums[1])
        points.append((pa, pb))
        if pa > maxlen:
            maxlen = pa
        if pa < minlen:
            minlen = pa
        if pb < minheight:
            minheight = pb
    
printfc("Points: %s\n"%(points,))

# scale and translate
scaledpoints = []
factor = targetLen / (maxlen - minlen)
hfactor = factor * (35) / (27.34 + 11.99)
for p in points:
    scaledpoints.append((Xcoord, p[0] * factor - minlen, p[1] * hfactor - minheight))

printfc("Scaled points: %s\n"%(scaledpoints,))

# convert to Edges
edges = []
lastv = None
for v in scaledpoints:
    vert = Part.Vertex(*v)
    if lastv:
        edges.append(Part.Edge(lastv, vert))
    lastv = vert

# make face
wire = Part.Wire(edges)
face = Part.Face(wire)
Part.show(face)

