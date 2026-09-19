# UV_Flatten_Panel
Remap Tool Cleanup + New UI

I finally fixed up the bugs of and combined a set of plugins on things I use

Future Roadmap:
- Merge all connected vertices representing UV Islands in the outputted geometry
- Detect compatible topology in a more robust way than face count
- Better materials support
- Documentation

**Installation**

Github will handle all the zip file stuff under the green button. Once you get UV_Flatten_Panel-blender-5_1_2.zip Keep the files zipped up in order to install the plugin in Blender User Preferences > Addons. Plugin is intended for use with blender 5.1.2+, since that is what I use.

**Steps to use:**

1) Make an identical geometry copy of the original model first (copy-paste, keep both, rename the copy to something memorable like "copy" and the original model to "target")
2) add your new texture to the copy with a new material
3) align the UV on the copy to look the exact way you want it 
4) select the copied model and the original at once, and in the plugin window click the "pin" next to the original model name ("target")
5) press the flatten button, it will flatten/align your new texture to the original UV, creating a new plane under it with the texture remapped to it

**Steps to export the resulting texture:**

1) Select "flat" lighting for the scene and turn on textures (alternatively select the "diffuse color only" pass on the rendering view -- it's more computationally expensive for the same result though)
2) Click the "fix colors" button in the plugin to use the correct color space
3) Add a camera to your scene
4) Change the expected size of the texture in the plugin settings
5) Select both the camera and the blank square plane created in step five of the last set of steps and press "align to camera" button
6) deselect everything then select the camera and right click and then "align view to camera"
7) turn off viewing of both the axis and overlays (you should not see the 3D cursor, etc)
    8) in the view dropdown options in the header of the window select "render viewport" and then save the image if gives you as a png 

﻿
