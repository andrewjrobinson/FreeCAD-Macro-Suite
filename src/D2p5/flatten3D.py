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
Un-wraps a 3D model to produce a 2D representation that can be cut out and folded to
produce the 3D object.  Note: all faces need to be on the same shape for FreeCAD to report the selection order correctly.
To use it you need to:
.. 1. Select the reference face
.. 2. Select the bend edge (i.e. usually one that is incommon between reference and next face
.. 3. Select a face to un-fold
.. 4. Run macro
.. 5. Repeat step 1 to 4 for all faces you want to unfold.
.. * Note: you can repeat step 2 and 3 more than once to do an unfold with reference to an unfolded face.  e.g. 
the underside of a cube.
'''


import FreeCADGui as Gui, FreeCAD, Part, math
from itertools import izip_longest

printfc = FreeCAD.Console.PrintMessage



# definitions
def nearValue(src, dest):
	'''Checks if src is near dest'''
	return (src - 1e-14) < dest < (src + 1e-14)

def grouper(n, iterable, fillvalue=None):
	"Collect data into fixed-length chunks or blocks"
	# grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx
	args = [iter(iterable)] * n
	return izip_longest(fillvalue=fillvalue, *args)

def calculateBend(primface, bendedge, secoface):
	'''Calculates the reference point, axis, and angle (degrees) inorder to 
	rotate secoface around bend edge to be in plane of primface'''
	primnorm = primface.normalAt(0,0)
	seconorm = secoface.normalAt(0,0)
	bendvert1 = bendedge.Vertexes[0]
	bendvert2 = bendedge.Vertexes[1]
	bendvect1 = FreeCAD.Vector(bendvert1.X, bendvert1.Y, bendvert1.Z)
	bendvect2 = FreeCAD.Vector(bendvert2.X, bendvert2.Y, bendvert2.Z)
	bendangle = primnorm.getAngle(seconorm)
	return (bendvect1, bendvect1-bendvect2, bendangle*180/math.pi, primface.normalAt(0,0)) # (referencePoint, axis, angle, expectedNormal)

def flattenSelection(selection):
	result = []
	for sel in selection:
		result.extend(sel.SubObjects)
	return result

def notNear(v1, v2):
	'''Checks if two vectors are near each other'''
	return not (nearValue(v1.x, v2.x) and nearValue(v1.y, v2.y) and nearValue(v1.z, v2.z))

# extract features from selection
sel = Gui.Selection.getSelectionEx()
sel.reverse()
faces = flattenSelection(sel)

# trim off primary face
primface = faces[0]
faces = faces[1:]

# calculate each bend
bends = []
lastsecoface = primface
for bendedge,secoface in grouper(2,faces):
	bends.append(calculateBend(lastsecoface, bendedge, secoface))
	lastsecoface = secoface

# do bends on last face
bends.reverse()
for bend in bends:
	faces[-1].rotate(bend[0],bend[1], bend[2])
	printfc("%s\n" % (bend[3]))
	printfc("%s\n\n" % (faces[-1].normalAt(0,0)))
	if notNear(bend[3],faces[-1].normalAt(0,0)):
		faces[-1].rotate(bend[0],bend[1], bend[2]*-2)
Part.show(faces[-1])
