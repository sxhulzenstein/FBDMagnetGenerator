from math import acos, pi, sin, radians, sqrt, cos
from itertools import pairwise
from cadquery import Workplane, exporters, Sketch, Plane, Vector
from util import Default, drawPolyLine
from joint import makeJoint, cutMagnetChamber, makeBottomHole
from uuid import uuid4

def makeTorsionSpring() -> Workplane:
    nWinds = 2.25
    r = 20 / nWinds / ( 2 * pi )

    def _spiral( angle: float ) -> tuple[ float, float, float ]:
        return ( r * angle * cos( angle ), r * angle * sin( angle ), 0 )

    spiral = Workplane("XY").parametricCurve( _spiral, 100, start = 0, stop = 2 * nWinds * pi )
    spring = Workplane("YZ").rect(1, Default.jointHeight).sweep(spiral)
    spring = makeJoint( model = spring )
    spring = makeJoint( Vector( 0, 20, 0 ), spring )
    return spring

def makeTensileSpring() -> Workplane:
    width = Default.jointDiameter
    windHeight = 5
    nWinds = 4
    points = [ ( 0, Default.jointDiameter, 0 ), ( 0, 0, 0 ) ]
    for i in range(nWinds):
        points.append((  - width / 2, - ( i + 0.5 ) * windHeight, 0 ) )
        points.append( ( width / 2, - ( i + 1.0 ) * windHeight, 0 ) )
    points.append( ( 0, - ( nWinds + 0.5 ) * windHeight, 0 ) )
    points.append( ( 0, - ( nWinds + 0.5 ) * windHeight - Default.jointDiameter, 0 ) )
    path = Workplane().polyline( points )
    spring = Workplane("XZ").rect(1, Default.jointHeight).sweep(path, transition = "round")
    spring = makeJoint( Vector(points[ 0 ]), spring )
    spring = makeJoint( Vector(points[ -1 ]), spring )
    return spring


def generateSpring( specification: dict, directory: str ) -> None:
    generateSpringTypeMap = {
        "torsion" : makeTorsionSpring,
        "tensile" : makeTensileSpring
    }
    
    springType = specification[ "type" ]
    name = specification[ "name" ] if "name" in specification else str(uuid4())
    spring = generateSpringTypeMap[ springType ]()
    exporters.export(spring, f"{directory}/{name}.stl")