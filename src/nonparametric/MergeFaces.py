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
Makes a single face from multiple (must be planer).  e.g. if you have two adjacent 
triangle faces that make up a square you can use this to macro to create a new object 
with a single square face.
'''

import FreeCADGui as Gui, FreeCAD, Part, math

printfc = FreeCAD.Console.PrintMessage

def tupleVert(tup):
    '''Converts a tuple representation of vertex into Vertex'''
    return Part.Vertex(*tup)

def vertTuple(vert):
    '''Makes a 3-tuple representing a vertex'''
    return (vert.X, vert.Y, vert.Z)

def edgeTuples(edge):
    '''Makes a 2-tuple of 3-tuples representing the edge (sorted)'''
    v1 = vertTuple(edge.Vertexes[0])
    v2 = vertTuple(edge.Vertexes[1])
    if v1 < v2:
        return (v1,v2)
    return (v2,v1)

def appendDict(d, k, v):
    '''Appends v to element k of dict d (safely)'''
    if k in d:
        d[k].append(v)
    else:
        d[k] = [v]

# count the edges
edgeCount = {}
faces = Gui.Selection.getSelection()
for face in faces:
    for edge in face.Shape.Edges:
        et = edgeTuples(edge)
        if et in edgeCount:
            edgeCount[et] += 1
        else:
            edgeCount[et] = 1

# printfc("Edge Counts: %s\n" % (edgeCount,))

# remove any that are duplicates
dirarcs = {}
start = None
for edge, c in edgeCount.items():
    if c == 1:
        appendDict(dirarcs, edge[0], edge[1])
        appendDict(dirarcs, edge[1], edge[0])
        start = edge[0]

# printfc("Directed Arcs: %s\n" % (dirarcs,))

# follow edges
vert = start
path = []
while True:
    nextVerts = dirarcs[vert]
    found = False
    for v in nextVerts:
        if v not in path:
            vert = v
            path.append(v)
            found = True
            break
    if not found:
        break
    
# printfc("Path: %s\n" % (path,))

# convert back to edges
edges = []
lastv = path[-1]
for v in path:
    edges.append(Part.Edge(Part.Vertex(*lastv),Part.Vertex(*v)))
    lastv = v

# printfc("Edges: %s\n" % (edges,))

# make new part
wire = Part.Wire(edges)
face = Part.Face(wire)
Part.show(face)

# hide the originals
for face in faces:
    face.ViewObject.hide()
