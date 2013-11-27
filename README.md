FreeCAD-Macro-Suite
===================

A collection of FreeCAD macro's

To make use of these macros (on linux/mac) you can symlink these files to your default macro directory with the extension changed to .FCMacro

## Cam

* __LinesToGCode__: converts the select edges (in selection order) to a gcode program.  Useful to convert a sketch on a face to a tool-path.
* __SketchLinesToGCode__: an older version of LinesToGCode that works on a sketch (in edit mode)

## 2.5D (D2p5)

Some macros for working with 2.5 Dimentions

* __flatten3D__: Un-wraps a 3D model to produce a 2D representation that can be cut out and folded to
produce the 3D object.  Note: all faces need to be on the same shape for FreeCAD to report the selection order correctly.
To use it you need to:
.. 1. Select the reference face
.. 2. Select the bend edge (i.e. usually one that is incommon between reference and next face
.. 3. Select a face to un-fold
.. 4. Run macro
.. 5. Repeat step 1 to 4 for all faces you want to unfold.
.. * Note: you can repeat step 2 and 3 more than once to do an unfold with reference to an unfolded face.  e.g. 
the underside of a cube.


## Non-parametric

A number of non-parametric macros (i.e. break the FreeCAD-way) but help enable productivity (and save sanity) when modeling complex parts.

* __MakeFace__: Makes a face (triangle) from 3 Vertexes.  You can select any number of sub-objects as-long-as the total unique vertexes is 3.  e.g. you could select 2 edges (as long as they have one vertex in common OR 1 vertex and 1 edge OR 3 vertexes etc.
* __MakeSolid__: Makes a solid from a bunch selected of faces.
* __MergeFaces__: Makes a single face from multiple (must be planer).  e.g. if you have two adjacent 
triangle faces that make up a square you can use this to macro to create a new object 
with a single square face.
* __PromoteSelected__: Promotes the selected sub-objects to first class objects.  It functions on all sub-
object types i.e. Face, Edge, Wire, etc.
e.g. if you select a face it will make a new shape with a single face (a clone of the 
one you selected).  If you select 2 faces it will create two shapes with 1 face.
* __SimplifyFace__: This Macro will take the currently selected (1) face and simplify by removing all
Cavities (or inlets) in the outside wire.
NOTE: sometimes FreeCAD will not select the correct wire when asking for the 
outside wire so you may need to edit the selection code near the end of this 
macro. 
> e.g. with ............ produces
> X----X   X----X     X-------------X
> |    |   |    |  >  |             |
> |    X---X    |  >  |             |
> X-------------X     X-------------X

## Utility

Some other macros.

* __ImportWing__: imports a airfoil profile (.dat file) into a face.  A work-around for a bug in my pivy/coil installation.

