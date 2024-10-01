import tkinter.filedialog
from json import loads
from rod import generateRod
from joint import generateJoint
from support import generateSupport
from pathlib import Path
from spring import generateSpring

if __name__ == "__main__":
    fileTypes: tuple[ tuple[ str, str], ... ] = ( ( "JSON-File", ".json" ), ( "Text-File", ".txt" ) )
    with tkinter.filedialog.askopenfile( title = "Select a configuration file", mode="r", filetypes = fileTypes ) as file:
        content: dict = loads( file.read() )
        directory: Path = Path( file.name ).parent.joinpath("parts")
        directory.mkdir() 

    objectCallerBinding: dict[ str, callable ] = {
        "rod" : generateRod,
        "support" : generateSupport,
        "joint" : generateJoint,
        "spring" : generateSpring
    }

    for object in content[ "objects" ]:
        typeOfObject: str = object[ 0 ]
        objectSpecification: dict = object[ 1 ]
        objectCallerBinding[ typeOfObject ]( objectSpecification, str ( directory ) )