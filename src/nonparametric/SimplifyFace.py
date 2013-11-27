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
This Macro will take the currently selected (1) face and simplify by removing all
Cavities (or inlets) in the outside wire.

NOTE: sometimes FreeCAD will not select the correct wire when asking for the 
outside wire so you may need to edit the selection code near the end of this 
macro. 

e.g. with ............ produces
X----X   X----X     X-------------X
|    |   |    |  >  |             |
|    X---X    |  >  |             |
X-------------X     X-------------X
'''

import math
import FreeCADGui as Gui, FreeCAD

printfc = FreeCAD.Console.PrintMessage

class ListWrappingGenerator (object):
	'''Produces generators that start from an arbitory place in the list and 
	wrap around end to start.  The number of elements return may be shorter or
	longer than original list depending on settings'''
	
	def __init__(self, l):
		self.l = l
		self.le = len(l)
		
	def listAt(self, idx, repeat=0):
		'''Generator that yields items starting at idx and wrapping until 
		reaches idx again.  If repeat > 0 then that number of elements are
		repeated.'''
		l = self.l
		le = self.le
		if idx < 0:
			idx += le
		idx = idx % le
		for i in xrange(idx, le):
			yield l[i]
		for i in xrange(0, idx):
			yield l[i]
		i+=1
		repeated = 0
		while repeated < repeat:
			for i in xrange(i, le):
				repeated+=1
				yield l[i]
				if repeated >= repeat:
					return
			i = 0
			
	def lenListAt(self, idx, length=-1):
		'''Similar to listAt except you specify the number of elements to return.'''
		l = self.l
		le = self.le
		if length == -1:
			length = le
		c = 0
		for i in xrange(idx, le):
			c += 1
			if c > length:
				return
			yield l[i]
		for i in xrange(0, idx):
			c += 1
			if c > length:
				return
			yield l[i]
		i+=1
		while c <= length:
			for i in xrange(i, le):
				c+=1
				if c > length:
					return
				yield l[i]
			i = 0
## End ListWrappingGenerator Class ##
		
def getAngle3Point(a,b,c):
	'''Gets the angle between 3 (2D) points.  Points specified as 2-tuples.'''
	ab = (b[0] - a[0], b[1] - a[1])
	cb = (b[0] - c[0], b[1] - c[1])
	dot = ab[0] * cb[0] + ab[1] * cb[1]
	cross = ab[0] * cb[1] - ab[1] * cb[0]
	alpha = math.atan2(cross, dot)
	angle =  alpha * 180.0 / math.pi
	
	return angle

def sortVertexes(wire):
	'''Sorts the Vertices in a wire.  Returns a list of 3-tuples representing 
	the 3D coordinates of Vertices.'''
	edges = wire.Edges
	vertexConnections = {}
	
	# format the edges
	for edge in edges:
		v1 = edge.Vertexes[0]
		v2 = edge.Vertexes[1]
		t1 = (v1.X, v1.Y, v1.Z)
		t2 = (v2.X, v2.Y, v2.Z)
		
		if t1 in vertexConnections:
			vertexConnections[t1].append(t2)
		else:
			vertexConnections[t1] = [t2]
		if t2 in vertexConnections:
			vertexConnections[t2].append(t1)
		else:
			vertexConnections[t2] = [t1]
	
	# traverse edges
	cv = vertexConnections.keys()[0]
	result = [cv]
	visited = set([])
	while True:
		neighbours = vertexConnections[cv]
		found = False
		for n in neighbours:
			if n not in visited:
				visited.add(cv)
				cv = n
				result.append(cv)
				found = True
				break
		if not found:
			break
	
	return result

def Vectorise(vertlist):
	'''Converts a list of 3-tuples to list of vectors'''
	result = []
	for vert in vertlist:
		result.append(FreeCAD.Vector(*vert))
	return result

def makeFaceFromVectors(vectors):
	'''Makes a face from a list of vectors.  Note: it will add the first vector
	to end to make it complete'''
	copy = [v for v in vectors]
	copy.append(copy[0])
	w = Part.makePolygon(copy)
	return Part.Face(w)

def removeCavities(vertlist):
	'''Skips any inward protrusions in the vertlist.  Expects a list of 3-tuples.
	
	e.g. with ............ produces
	X----X   X----X     X-------------X
	|    |   |    |  >  |             |
	|    X---X    |  >  |             |
	X-------------X     X-------------X
	'''
	# convert to 2d
	vertlist2d = [(v[0], v[1]) for v in vertlist]
	listGenerator = ListWrappingGenerator(vertlist2d)
	
	# calcuate the direction of list
	lv = None
	llv = None
	angleSum = 0
	for v in listGenerator.listAt(0, 2):
		vt = (v[0], v[1])
		angle=0
		if llv:
			angle = getAngle3Point(llv,lv,vt)
		angleSum += angle
		llv = lv
		lv = vt
	dir = angleSum >= 0
	
	# find best vert to follow each vert
	lastVert = None
	idx = 0
	bestVerts = {}
	for vert in listGenerator.listAt(0,1):
		if lastVert:
			bestAngle = 0
			bestVert = None
			for cvert in listGenerator.lenListAt(idx + 2):
				angle = round(getAngle3Point(lastVert, vert, cvert), 6)
				if (dir and angle >= bestAngle) or ((not dir) and angle <= bestAngle):
					bestAngle = angle
					bestVert = cvert
			bestVerts[vert] = bestVert
			idx += 1
		lastVert = vert
	
	# produce best path
	consumed = set([])
	result = []
	currentVert = bestVert # should be a good one (but may not always be that way) TODO: check
	while True:
		if currentVert in consumed:
			break
		result.append(currentVert)
		consumed.add(currentVert)
		currentVert = bestVerts[currentVert]
	
	if currentVert != result[0]:
		FreeCAD.Console.PrintMessage("Error: incorrect starting point\n");
		# TODO: pop from front until we get to currentVert
	
	return result
		
# get face selection
face = Gui.Selection.getSelectionEx()[0].SubObjects[0]
### If this fails to select correct wire do it manually (example below). ###
wire = face.OuterWire
# wire = face.Wires[0]

# simplify face
sortedVertexes = sortVertexes(wire)
trimmedVertexes = removeCavities(sortedVertexes)

# make a face
face = makeFaceFromVectors(Vectorise(trimmedVertexes))
# printfc(face)
Part.show(face)
