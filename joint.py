from uuid import uuid4
from cadquery import Workplane, exporters, Plane, Vector
from util import Default, halfCrossSection, crossSection

def cutMagnetChamber( p: Vector, model: Workplane ) -> Workplane:
    return model.cut( Workplane( origin = ( p.x, p.y, - Default.jointHeight / 2 + 0.6 ) ).circle( 
        ( Default.magnetDiameter + Default.magnetDiameterTol ) / 2 ).extrude( Default.magnetHeight + Default.magnetDiameterTol ) )

def makeBottomHole( p: Vector, model: Workplane ) -> Workplane:
    return model - Workplane().moveTo( p.x, p.y ).circle( 4.0 ).extrude( - Default.jointHeight / 2 ) 


def makeJoint( p: Vector = Vector( 0, 0, 0 ), model: Workplane | None = None ) -> Workplane:
    plane = Plane( origin = p, normal = (1, 0, 0), xDir = (0, 1, 0) )
    base = halfCrossSection( Workplane( plane ), Default.jointDiameter ).revolve( 
         axisStart = ( 0, 0, 0 ), axisEnd = ( 0, 1, 0 ) ).faces( ">Z" ).workplane().circle( 3.7 ).extrude( 0.7, taper = 15 )
    if model is None:
        return makeBottomHole( p, cutMagnetChamber( p, base ) )
    return makeBottomHole( p, cutMagnetChamber( p, model + base ) )

def makeCap() -> Workplane:
    path = Workplane().circle( ( Default.jointDiameter - Default.lineWidthBold ) / 2 )
    torus = crossSection( Workplane( "YZ", origin = Vector( 0, ( Default.jointDiameter - Default.lineWidthBold ) / 2, 0 ) ), 
                          Default.lineWidthBold ).sweep( path )
    fill = Workplane( "XY", origin = Vector( 0, 0, - Default.jointHeight / 2 ) ).circle( 
        ( Default.jointDiameter - Default.lineWidthBold ) / 2 ).extrude( Default.jointHeight - Default.contourThickness )
    return makeBottomHole( Vector() , cutMagnetChamber( Vector() , torus +  fill ) )

def generateJoint( specification: dict, directory: str) -> None:
    generateJointMap = {
        "cap" : makeCap,
        "space" : makeJoint
    }
    
    jointType = specification["type"]
    j = generateJointMap[jointType]()
    name = specification[ "name" ] if "name" in specification else str(uuid4())
    exporters.export( j, f"{directory}/{name}.stl" )
