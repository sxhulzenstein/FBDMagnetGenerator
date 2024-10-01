from math import acos, pi, sin, radians, sqrt, floor
from itertools import pairwise
from cadquery import Workplane, exporters, Sketch, Plane, Vector
from util import Default, drawPolyLine
from joint import makeJoint, cutMagnetChamber, makeBottomHole
from uuid import uuid4

def makeComb( start: Vector, end: Vector, delta ) -> Workplane:
    lineLength = sin( radians( 60 ) ) * Default.supportEdgeLength / 3
    lineDirection = - Vector( 1, 1, 0 ) * lineLength * 1.15 / sqrt( 2 )
    combLine = drawPolyLine( Default.lineWidthDefault, [ Vector(), lineDirection ] )
    direction = ( end - start ).normalized()
    length = ( end - start ).Length
    nLines = floor( length / delta ) + 1
    combPoints = [ start + i * delta * direction for i in range( nLines ) ]
    comb = Workplane().pushPoints( combPoints ).eachpoint( lambda loc: combLine.val().located( loc ), combine = True )
    base = drawPolyLine( Default.lineWidthDefault, [ start, end, end + lineDirection, start + lineDirection ], True, True ).faces(">Z").workplane(
        offset = -Default.contourThickness ).split( keepBottom = True )
    return comb + base

def makeTriangle( width: float, height: float ) -> Workplane:
    points = [ ( 0, 0, 0), ( - width / 2 , -height, 0 ), ( width / 2 , -height, 0 ) ]
    outline = drawPolyLine( Default.lineWidthDefault, points, True, True)
    return outline

def makeBaseLine(start: Vector, end: Vector) -> Workplane:
    return drawPolyLine( Default.lineWidthBold, [ start, end ] )

def makeDoubleBaseLine( start: Vector, end: Vector, space: float = Default.linewidthThin ) -> Workplane:
    upperLine = drawPolyLine( Default.lineWidthBold, [ start, end ] )
    dy = Vector( 0, - Default.lineWidthBold - space, 0 )
    startLower, endLower = start + dy, end + dy
    lowerLine = drawPolyLine( Default.lineWidthBold, [ startLower, endLower ] )
    base = drawPolyLine( Default.lineWidthBold, [ start, end, endLower, startLower ], True, True ).faces(">Z").workplane(
        offset = -Default.contourThickness ).split( keepBottom = True )
    base += upperLine
    base += lowerLine
    return base

def makeFixedSupport() -> Workplane:
    h, b = sin( radians( 60 ) ) * Default.supportEdgeLength, Default.supportEdgeLength
    fixedSupport = makeTriangle( b, h )
    fixedSupport += makeBaseLine( Vector( - 1.25 * b / 2 , -h, 0 ), Vector( 1.25 * b / 2 , -h, 0 ) )
    dx = Default.supportEdgeLength / 3 * 1.15
    fixedSupport += makeComb( Vector( 1.25 * b / 2, -h, 0 ), Vector( 1.25 * b / 2, -h, 0 ) - Vector( Default.supportEdgeLength * 1.15, 0, 0 ), dx )
    additionalMagnetPoint =  Vector( 0, - ( 1 + 1 / 6 / sqrt( 2 ) ) * h, 0 )
    fixedSupport = cutMagnetChamber( additionalMagnetPoint, fixedSupport )
    fixedSupport = makeBottomHole( additionalMagnetPoint, fixedSupport )
    return makeJoint( model = fixedSupport )

def makeLooseSupport() -> Workplane:
    h, b = sin( radians( 60 ) ) * Default.supportEdgeLength, Default.supportEdgeLength
    looseSupport = makeTriangle( b, h )
    looseSupport += makeDoubleBaseLine( Vector( - 1.25 * b / 2 , -h, 0 ), Vector( 1.25 * b / 2 , -h, 0 ) )
    dx = Default.supportEdgeLength / 3 * 1.15
    looseSupport += makeComb( Vector( 1.25 * b / 2, -h - Default.lineWidthBold - Default.linewidthThin, 0 ), 
                              Vector( 1.25 * b / 2, -h - Default.lineWidthBold - Default.linewidthThin, 0 ) - Vector( Default.supportEdgeLength * 1.15, 0, 0 ), dx )
    additionalMagnetPoint =  Vector( 0, - ( 1 + 1 / 6 / sqrt( 2 ) ) * h - ( Default.linewidthThin + Default.lineWidthBold ), 0 )
    looseSupport = cutMagnetChamber( additionalMagnetPoint, looseSupport )
    looseSupport = makeBottomHole( additionalMagnetPoint, looseSupport )
    return makeJoint( model = looseSupport )

def generateSupport( specification: dict, directory: str ) -> None:
    generateSupportTypeMap = {
        "fixed" : makeFixedSupport,
        "loose" : makeLooseSupport
    }
    
    supportType = specification[ "type" ]
    name = specification[ "name" ] if "name" in specification else str(uuid4())
    support = generateSupportTypeMap[ supportType ]()
    exporters.export(support, f"{directory}/{name}.stl")