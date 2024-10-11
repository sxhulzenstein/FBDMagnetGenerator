from math import acos, cos, floor
from itertools import pairwise
from cadquery import Workplane, exporters, Vector, Plane
from util import Default, drawPolyLine
from joint import makeJoint
from uuid import uuid4

def centerLine(model: Workplane, p0: Vector, p1: Vector ) -> Workplane:
    longLineLength = Default.linewidthThin * 3
    shortLineLength = Default.linewidthThin * 0.5
    segmentLength = longLineLength + 5 * shortLineLength
    directon = ( p1 - p0 ).normalized()

    actuaLength = ( p1 - p0 ).Length
    
    numberOfSegments = floor( actuaLength / segmentLength )

    for i in range( numberOfSegments ):
        initialPosition = p0 + i * segmentLength * directon
        model += drawPolyLine( Default.linewidthThin, [ initialPosition, initialPosition + longLineLength * directon ]  )
        model += drawPolyLine( Default.linewidthThin, [ initialPosition + ( longLineLength + 2 * shortLineLength ) * directon , initialPosition + ( longLineLength + 3 * shortLineLength ) * directon ] )
    else:
        model += drawPolyLine( Default.linewidthThin, [ p0 + ( numberOfSegments ) * segmentLength * directon, p1 ] )
    
    return model

def addText( start: Vector, end: Vector, beam: Workplane ) -> Workplane: 
    plane = Plane( origin = ( start + end ) / 2 + Vector( 0, 0, Default.jointHeight / 2 - Default.contourThickness ), normal = Vector( 0, 0, 1 ), xDir = ( end -  start ).normalized() )
    length = ( end - start ).Length
    text = Workplane( plane ).text( f"{length:.0f}", 7, Default.contourThickness, font="Arial", kind="bold" )
    return beam + text

def generatePoints( normals: list[ Vector ], directions: list[ Vector ], points, invert = False ) -> list[ Vector ]:
    sign = -1 if invert else 1
    polyLinePoints = []
    beamWidth = Default.jointDiameter - Default.lineWidthDefault

    for i in range( len( points ) ):
        if i == 0:
            polyLinePoints.append( points[ 0 ] - sign * directions[ 0 ] * beamWidth / 2 + sign * normals[ 0 ] * beamWidth / 2 )
        elif i == len( points ) - 1:
            polyLinePoints.append( points[ -1 ] + sign * directions[ -1 ] * beamWidth / 2 + sign * normals[ -1 ] * beamWidth / 2 )
        else:
            cosAlpha = cos(  acos( normals[ i ].dot( normals[ i - 1 ] ) ) / 2 )
            polyLinePoints.append( points[ i ] + sign * ( normals[ i ] + normals[ i - 1 ] ).normalized() * beamWidth / 2 / cosAlpha )
    return polyLinePoints

def makeBeam( points: list[ Vector ] ) -> Workplane:
    # determining the segment normals
    # A beam is given only by a polyline. But the resulting object is a polygon. Thus, calculating the corner nodes is necessary.
    segmentNormals: list[ Vector ] = []
    segmentDirections = [ ( pointsPair[ 1 ] - pointsPair[ 0 ] ).normalized() for pointsPair in pairwise( points ) ]
    segmentNormals = [ Vector( - dir.y, dir.x, dir.z ) for dir in segmentDirections ]

    polyLinePoints = generatePoints( segmentNormals, segmentDirections, points )
    polyLinePoints.extend( generatePoints( list( reversed( segmentNormals ) ), list( reversed( segmentDirections ) ), list( reversed( points ) ), True ) )

    polygon = drawPolyLine( Default.lineWidthDefault, polyLinePoints, True, True )

    for pair in pairwise( points ):
         polygon = addText( pair[ 0 ], pair[ 1 ], polygon )

    for point in points:
        polygon = makeJoint( point, polygon )
    
    return polygon

def generateBeam( specification: dict, directory: str ) -> None:
    name = specification[ "name" ] if "name" in specification else str(uuid4())
    points = [ Vector( ( p[ 0 ], p[ 1 ], 0 ) ) for p in specification[ "points" ] ]
    support = makeBeam( points )
    exporters.export(support, f"{directory}/{name}.stl")