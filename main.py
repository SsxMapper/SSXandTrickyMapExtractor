
import convertbigfiles
import loadfilesTricky
import loadfilesSSX
import time
import pathlib

def ConvertTrickyBigFileToObjFile(bigFileName, mapModelFileName):
    print(f"TRICKY BIG FILE {bigFileName}")
    convertedFilesDir = f'.\\output_files\\SSX Tricky\\dvdmodelfiles\\'
    pathlib.Path(convertedFilesDir).mkdir(parents=True, exist_ok=True)
    convertbigfiles.ConvertSSXTrickyBigFileToSeparateFiles(f'.\\input_files\\SSX_Tricky_DVD\\DATA\\MODELS\\{bigFileName}.BIG', convertedFilesDir)
    writeCurvedPatchesToObjFile = True
    writeCurvedPatchesToCsvFile = True 
    writePdbHeaderToCsvFile = True

    loadfilesTricky.Load_SSXTricky_pbd(mapModelFileName, convertedFilesDir, writeCurvedPatchesToObjFile, writeCurvedPatchesToCsvFile, writePdbHeaderToCsvFile)

def ConvertAllSSXTrickyToObjFile():
    # convert all SSX Tricky map files to .obj files that can be imported into blender
    # on the cuved patches works at present 

    ConvertTrickyBigFileToObjFile("ALASKA","alaska")
    ConvertTrickyBigFileToObjFile("ALOHA","aloha")
    ConvertTrickyBigFileToObjFile("ELYSIUM","elysium")
    ConvertTrickyBigFileToObjFile("GARI","gari")
    ConvertTrickyBigFileToObjFile("MEGAPLE","megaple")
    ConvertTrickyBigFileToObjFile("MERQUER","merquer")
    ConvertTrickyBigFileToObjFile("MESA","mesa")
    ConvertTrickyBigFileToObjFile("PIPE","pipe")
    ConvertTrickyBigFileToObjFile("SNOW","snow")
    ConvertTrickyBigFileToObjFile("SSXFE","ssxfe")
    ConvertTrickyBigFileToObjFile("TRICK","trick")
    ConvertTrickyBigFileToObjFile("UNTRACK","untrack")

def ConvertSSXBigFileToObjFile(bigFileName, mapModelFileName):
    print(f"BIG FILE {bigFileName}")
    convertedFilesDir = f'.\\output_files\\SSX\\dvdmodelfiles\\'
    pathlib.Path(convertedFilesDir).mkdir(parents=True, exist_ok=True)
    convertbigfiles.ConvertSSXBigFileToSeparateFiles(f'.\\input_files\\SSX_DVD\\DATA\\MODELS\\{bigFileName}.BIG', convertedFilesDir)
    writeCurvedPatchesToObjFile = True
    writeCurvedPatchesToCsvFile = True 
    writePdbHeaderToCsvFile = True

    loadfilesSSX.LoadSSXWdf(mapModelFileName, convertedFilesDir, writeCurvedPatchesToObjFile, writeCurvedPatchesToCsvFile, writePdbHeaderToCsvFile)

def ConvertAllSSXtoObjFile():
    # convert all SSX Tricky map files to .obj files that can be imported into blender
    # on the cuved patches works at present 

    ConvertSSXBigFileToObjFile("ALOHA","aloha_ice_jam")
    ConvertSSXBigFileToObjFile("ELYSIUM", "elysium_alps")
    ConvertSSXBigFileToObjFile("MEGAPLEX", "tokyo_megaplex")
    ConvertSSXBigFileToObjFile("MERQUERY", "merquery_city")
    ConvertSSXBigFileToObjFile("MESA", "mesablanca")
    ConvertSSXBigFileToObjFile("PIPE", "pipedream")
    ConvertSSXBigFileToObjFile("SNOW", "snowdream")
    ConvertSSXBigFileToObjFile("UNTRACK", "untracked")
    # TODO fix warmup.big
    # ConvertSSXBigFileToObjFile("WARMUP", "warmup")


# main
start = time.time()
print(f"============== SSX ==================")
ConvertAllSSXtoObjFile()
print(f"============== SSX Tricky ==================")
ConvertAllSSXTrickyToObjFile()
end = time.time()
print(f"Time to process all files (seconds): {end - start}")
