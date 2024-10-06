from cadquery import Workplane, Plane, Vector
from copy import deepcopy

class Default:
    jointDiameter = 15.0
    magnetDiameter = 10
    magnetHeight = 3
    magnetDiameterTol = 0.16
    magnetHeightTol = 0.0
    jointHeight = 5.4
    linewidthThin = 3
    lineWidthDefault = 4
    lineWidthBold = 5
    supportEdgeLength = 30
    contourThickness = 1

def upperCurve( model: Workplane, width: float ) -> Workplane:
    return model.moveTo( width / 2, 0 ).lineTo( width / 2, Default.jointHeight / 6 ).tangentArcPoint( 
        ( - 0.5, 1 / 3 * Default.jointHeight ) ).lineTo( 0, Default.jointHeight / 2 )

def halfCrossSection( model: Workplane, width: float ) -> Workplane:
     return upperCurve( model, width ).lineTo( 0, 0 ).mirrorX()

def crossSection( model: Workplane, width: float ) -> Workplane:
    return upperCurve( model, width ).mirrorX().mirrorY()

def drawPolyLine( width: float, points: list[ Vector | tuple[ float, float, float ] ], close = False, fill = False) -> Workplane:
    pts = points
    
    if len( pts ) < 2:
        raise Exception()
    if close:
        pts.append( pts[ 0 ] )
    
    normal = ( Vector( pts[ 1 ] ) - Vector( pts[ 0 ] ) ).normalized()
    origin = Vector( pts[ 0 ] )
    plane: Plane = Plane( origin = origin, normal = normal, xDir = Vector( -normal.y, normal.x, 0 ) )
    line = crossSection( Workplane( plane ), width ).sweep( Workplane().polyline( pts ), transition = 'round' )

    if not close:
        cap = halfCrossSection( Workplane("YZ"), width ).revolve( axisStart = ( 0, 0, 0 ), axisEnd = ( 0, 1, 0 ) )
        line += Workplane().pushPoints( [ pts[ 0 ], pts[ -1 ] ] ).eachpoint( lambda loc: cap.val().located( loc ), combine = True )

    if fill and close:
        line += Workplane().polyline( pts ).close().extrude( Default.jointHeight / 2, both = True ).faces( ">Z" ).workplane( offset = - Default.contourThickness ).split( keepBottom = True )

    return line