from math import acos, pi
from itertools import pairwise
from cadquery import Workplane, exporters, Sketch, Plane, Vector
from util import Default, crossSection
from joint import makeJoint
import logging
from uuid import uuid4

def makeRodBase(p0: Vector, p1: Vector) -> Workplane:
    n = ( p1 - p0 ).normalized()
    length = ( p1 - p0 ).Length
    
    if length < Default.jointDiameter:
        raise Exception()
    
    plane = Plane( origin = p0, 
                   normal = n, xDir = ( -n.y, n.x, 0 ) )
    rod = crossSection( Workplane(plane), Default.lineWidthBold * 1.5 ).extrude( length )
    return rod 

def addText( start: Vector, end: Vector, rod: Workplane ) -> Workplane: 
    plane = Plane( origin = ( start + end ) / 2 + Vector( 0, 0, Default.jointHeight / 2 ), normal = Vector( 0, 0, 1 ), xDir = ( end -  start ).normalized() )
    length = ( end - start ).Length
    text = Workplane( plane ).text( f"{length:.0f}", 7, -1, font="Arial", kind="bold" )
    return rod - text


def polyLineRod( points: list[ Vector ] ) -> Workplane:
    rod = Workplane()
    for pair in pairwise( points ):
        rod += makeRodBase( *pair )
    
    if rod.val().Volume() == 0:
        logging.critical("rods cannot be created")
    
    if len( points ) > 2:
        for i in range( 1, len( points ) - 1):
            p0, p1, p2 = points[ i-1 : i+2 ]
            v10, v12 = ( p0 - p1 ).normalized(), ( p2 - p1 ).normalized()
            angle = acos(v10.dot(v12))
            
            if angle == pi:
                t = [ -v10, v12 ,v12 ]
                perpendicular = Vector( -v12.y, v12.x, 0 )
                p = ( p1 + 1 * Default.jointDiameter * v10, p1 + Default.jointDiameter / 2 * perpendicular, p1 + 1 * Default.jointDiameter * v12 )
            else:
                v123 = ( v10 + v12 ).normalized()
                perpendicular = Vector(-v123.y, v123.x, 0)
                t = [ -v10, Vector(-v123.y, v123.x, 0), v12 ]
                p = ( p1 + 1 * Default.jointDiameter * v10, p1 + Default.jointDiameter / 2 * v123, p1 + 1 * Default.jointDiameter * v12 )
            
            path = (Workplane("XY")
                 .spline( listOfXYTuple=p, tangents = t))
            plane = Plane( origin = p1 + 1 * Default.jointDiameter * v10, normal = -v10, xDir = ( v10.y, -v10.x, 0 ) )
            rod += crossSection(Workplane(plane), Default.lineWidthBold * 1.5 ).sweep(path)
    
    for point in points:
        rod = makeJoint( point, rod )
    
    try:
        rod = rod.edges("|Z").fillet(Default.jointDiameter/4)
    except:
        logging.warn("Fillet could not be applied. Continuing without.")

    for pair in pairwise( points ):
        rod = addText( *pair, rod )

    return rod


def generateRod( specification: dict, directory: str ) -> None:
    points = [ Vector( ( p[ 0 ], p[ 1 ], 0 ) ) for p in specification[ "points" ] ]
    name = specification[ "name" ] if "name" in specification else str(uuid4())
    rod = polyLineRod( points )
    exporters.export( rod, f"{directory}/{name}.stl" )
