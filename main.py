
import convertbigfiles
import loadfilesTricky
import loadfilesSSX
import time
import pathlib
import convertsshfiles


def ConvertTrickyBigFileToObjFile(bigFileName, mapModelFileName, sshFileName, sshLightMapFileName):
    print(f"TRICKY BIG FILE {bigFileName}")
    convertedFilesDir = f'.\\output_files\\SSX Tricky\\dvdmodelfiles\\'
    pathlib.Path(convertedFilesDir).mkdir(parents=True, exist_ok=True)
    convertbigfiles.ConvertSSXTrickyBigFileToSeparateFiles(f'.\\input_files\\SSX_Tricky_DVD\\DATA\\MODELS\\{bigFileName}.BIG', convertedFilesDir)

    modelsDir = f"{convertedFilesDir}DATA\\MODELS\\"
    convertsshfiles.ConvertSSHFileToSeparateFiles(f"{modelsDir}{sshFileName}.ssh", f"{modelsDir}ssh_files\\{sshFileName}_ssh\\")

    convertsshfiles.ConvertSSHFileToSeparateFiles(f"{modelsDir}{sshLightMapFileName}.ssh", f"{modelsDir}ssh_files\\{sshLightMapFileName}_ssh\\")

    pdbOptions = loadfilesTricky.SSXTrickyExportOptions()
    pdbOptions.writeCurvedPatchesToObjFile = True
    pdbOptions.writeCurvedPatchesToCsvFile = True 
    pdbOptions.writePdbHeaderToCsvFile = True
    pdbOptions.writeTextures = True
    pdbOptions.applyLightMapsToTextures = True

    loadfilesTricky.Load_SSXTricky_pbd(mapModelFileName, sshFileName, sshLightMapFileName, convertedFilesDir, pdbOptions)

def ConvertAllSSXTrickyToObjFile():
    # convert all SSX Tricky map files to .obj files that can be imported into blender
    # on the cuved patches works at present 

    ConvertTrickyBigFileToObjFile("ALASKA","alaska", "alaska", "alaska_L")
    ConvertTrickyBigFileToObjFile("ALOHA","aloha","aloha","aloha_L")
    ConvertTrickyBigFileToObjFile("ELYSIUM","elysium", "elysium", "elysiu_L")
    ConvertTrickyBigFileToObjFile("GARI","gari","gari","gari_L")
    ConvertTrickyBigFileToObjFile("MEGAPLE","megaple","megaple","megapl_L")
    ConvertTrickyBigFileToObjFile("MERQUER","merquer","merquer","merque_L")
    ConvertTrickyBigFileToObjFile("MESA","mesa","mesa","mesa_L")
    ConvertTrickyBigFileToObjFile("PIPE","pipe","pipe","pipe_L")
    ConvertTrickyBigFileToObjFile("SNOW","snow","snow","snow_L")
    ConvertTrickyBigFileToObjFile("SSXFE","ssxfe","ssxfE","ssxfE_L")
    ConvertTrickyBigFileToObjFile("TRICK","trick","trick","trick_L")
    ConvertTrickyBigFileToObjFile("UNTRACK","untrack", "untrack", "untrac_L")

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
