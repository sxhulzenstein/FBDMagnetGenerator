# FBDMagnetGenerator
A tool to generate whiteboard magnets using the style of a free body diagram

# Motivation

This project aims to provide a simple tool to generate magnets for assembling various free body diagrams directly onto a black board or a withe board. The main goals are:
* avoiding creating sketches manually
* having a sense for the kinematics of mechanisms

# Generatable objects ...so far
* fixed support
* loose support with fixed upper and lower part (triangle and comb)
* rod with multisection, stiffening representation over intermediate joints and length imprint
* torsion spring
* tensile spring
* joint (spacer)
* joint (cap)

# Planned objects
* loose support with moveable upper and lower part
* sliding joint
* beam
* arbitrary polygon
* damper with moveable parts
* arrows (circular/ linear)

# Getting started

## 0. Preconditions
To perform the following steps, there are some precontistions that need to be fullfilled. Please make sure to have [Git]("https://git-scm.com/downloads") and [Python]("https://www.python.org/downloads") installed. Add the directory to the python installation to your PATH system environment variable. The python installation can be found roughly at `C:\Users\<Username>\AppData\Local\Programs\Python\Python312`. However, the exact path can differ from your case. Also, the AppData-folder is commonly hidden by default so you need to make it visible. Packages can be installed using pip, which should be installed together with python by default.

## 1. Cloning the directory
First, you should clone the directory anywhere you want on your local mschine. If you have git installed and added it to your PATH you can simply open a terminal, head to the location where you want the files to be stored and then executing
```
git clone https://github.com/sxhulzenstein/FBDMagnetGenerator
```
If you are not using Git or something similair, you can also simply download all files directly.

## 2. Setting up a virtual environment
If you are working with python frequently this part might not be new to you. To do this, head to the location of the source files of this project on your maschine. Then, you can type 
```
python -m venv .venv
```
into the command window. Here, it is assumed that the python executable is added to PATH already.

## 3. Activating the virtual environment
This may sound complicated, but this is very simple to perform. If your machine is running Windows, the activaton file can be found in the `.venv` folder we already created.
```
.venv\Scripts\activate.bat
``` 
If you are executing the commands from Powershell, you need to type
```
.venv\Scripts\activate.ps1
```

## 4. Installing the required packages
This generator uses the CADQuery library (which I am a huge fan of) and is also making use of some tkinter features to improve usability. To install all packages, you need to execute
```
pip install -r requirements.txt --upgrade
```

## 5. Configuring the objects
Now you are almost ready to go. Now, the most important step is to define the objects we want to generate. Here we are using `.json`-files to communicate with the program. You can find an example on how a config-file can look like.
```json
{
    "objects": [
        [ "spring", { "type": "torsion", "name": "torsionSpring" } ],
        [ "spring", { "type": "tensile", "name": "tensileSpring" } ],
        [ "rod", { "points": [ [ 0, 0 ], [ 50, 0 ], [ 100, 50 ] ], "name" : "rod_50_100"} ],
        [ "support", { "type" : "loose" } ],
        [ "support", { "type" : "fixed" } ],
        [ "joint", { "type" : "cap", "name" : "cap1" } ],
        [ "joint", { "type" : "space", "name" : "space1" } ],
        [ "beam", { "points": [ [ 0, 0 ], [ 20, 0 ], [ 60, 0 ] ], "name": "beam_20_60" } ]
    ]
}
```
You can see that it contains a field `objects` which holds a list of object-discribing-lists. The first entry in these lists indicate the type of object such as spring, rod, joint and support. The second entry specifies how the object is shaped.

## 6. Running the application
If you have created a configuration file, you can type
```
python generate.py
```
into your command terminal. If everything works as intended, a file dialog should open. There, you can choose the configuration file you just created. In the end, a new folder `parts` should appear in the same location where your configuration file is located. This new folder holds all the generated models.

## 7. Printing the parts
Printing advice can be found here. Sharing your make and the experiences you made while printing is very welcome.

## Trouble Shooting
* Make sure to have the `numpy` and `nlopt` versions installed which are listed in the `requirements.txt`. A numpy verion of 2 and higher might cause errors.   
```
pip install numpy==1.26.0, nlopt==2.7.1 --upgrade
``` 