The utility extracts the curved patches from the SSX and SSX Tricky PS2 game maps and converted them to Wavefront .obj files that can be loaded into blender. See video at:
https://youtu.be/uE_oahOPU5Y

Note this is only the curved surfaces, other objects such as buildings and rails are missing. 

Latest version also gets all textures from SSX Tricky and lightmap adjusts them (not SSX).

Requires numpy, matplotlib, opencv to be installed. Tested with Python 3.10.6.

Copy the contents of the PS2 games discs:
- SSX CD to input_files\SSX_DVD
- SSX Tricky DVD to input_files\SSX_Tricky_DVD

Run main.py to convert all DVDs, takes about 12 mins on my computer, and produces 1.6 GB of files.

Output will be in the output_files directory. These directories contain obj files that can be imported into Blender using File/Import/Wavefront (.obj):
- output_files\SSX\curved patch beizer
- output_files\SSX Tricky\curved patch beizer

The 'csv files' directory in output_files contains exports of some data which can be loaded in excel.
The converted game files are in dvdmodelfiles directory. The ssh files have been extracted into separate files.

The documentation folder contains some details about how the Bi-cubic Bézier surfaces work in SSX.

Note that I cannot publish the exported files as the game is copyright, but you can use the utility to extract from your own game discs.

Todo:
- SSX textures
- export SSX Tricky model positions.
