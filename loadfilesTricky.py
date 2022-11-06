from pathlib import Path
import struct
import numpy as np
import BezierSurface
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import filehelpers
import texturelightmaps





    
class SSXTrickyExportOptions:
    def __init__(self):
        self.writeCurvedPatchesToObjFile = True
        self.writeCurvedPatchesToCsvFile = True 
        self.writePdbHeaderToCsvFile = True
        self.writeTextures = True
        self.applyLightMapsToTextures = True


class SSXTrickyCurvedPatchBlock:
    def __init__(self):
        # patch file data

        # number 1 is the index into the lightmap image bitmap. Number 1 contains 4 floats x,y,w,h from 0 to 1.
        # multiple these numbers by the size of the lightmap image in the (mapname)_L.ssh file
        # the numbers are such that you always get a multiple of 8, so for example:
        # width and height of the lightmap is 128
        # x = 0.9375 * 120
        # y = 0.125	 * 16
        # w = 0.0625 * 128 = 8
        # h = 0.0625  * 128 = 8
        # so the light map is inside the light bitmap (indexed by another data point later) in a rect at x,y 120,16 w,h 8,8
        self.numLightMapUVPoints = 1
        self.LightMapUVPoints = np.zeros((self.numLightMapUVPoints,4)) 


        # number 2 to 5 are the UV co-ordinates for texture mapping https://en.wikipedia.org/wiki/UV_mapping

        self.numTextureUVPoints = 4
        self.TextureUVPoints = np.zeros((self.numTextureUVPoints,4)) 



        self.BezierControlPoints = np.zeros((4,4,4)) # 16 of them, x,y,z,1
        self.bezierSrf = None

        self.numOutlinePointsSet1 = 2
        self.OutlinePointsSet1 = np.zeros((self.numOutlinePointsSet1 ,3))   # it's probably the outline like SSX but they have shaved 8 bytes by leaving the 1 off the end so x,y,z

        self.numOutlinePointsSet2 = 4
        self.OutlinePointsSet2 = np.zeros((self.numOutlinePointsSet2 ,4))   # it's probably the outline too but x,y,z,1

        self.PatchStyleUint32 = 0
        self.Unknown1Uint32 = 0
        self.TextureAssigmentUint16 = 0
        self.LightmapIDUint16 = 0
        self.Unknown2Uint32 = 0
        self.Unknown3Uint32 = 0
        self.Unknown4Uint32 = 0 
                
        # useful data I calculate
        self.blockSizeBytes = 112*4

        # self.Outline2TrianglesNumberPoints = 5
        # self.Outline2Triangles = np.zeros((self.Outline2TrianglesNumberPoints,3)) 
    
    def WriteHeaderToCsvFile(self, fileOut):
        if (fileOut is not None):
            fileOut.write(f"Curved Patch Index")
            coord = ["x","y","z","w"]
            for floatOut in range(self.numLightMapUVPoints ):
                    for subFloatOut in range(4):
                        fileOut.write(f",LightMapUVPoint_{floatOut}_{coord[subFloatOut]}")

            for floatOut in range(self.numTextureUVPoints):
                    for subFloatOut in range(4):
                        fileOut.write(f",TextureUVPoints_{floatOut}_{coord[subFloatOut]}")

            for bezierPointsX in range(4):
                for bezierPointsY in range(4):
                    for subFloatOut in range(4):
                        fileOut.write(f",BezC_{bezierPointsX}_{bezierPointsY}_{coord[subFloatOut]}")

            for floatOut in range(self.numOutlinePointsSet1):
                for subFloatOut in range(3): # TODO use shape
                    fileOut.write(f",OutlineSet1_{floatOut}_{coord[subFloatOut]}")

            for floatOut in range(self.numOutlinePointsSet2):
                for subFloatOut in range(4): # TODO use shape
                    fileOut.write(f",OutlineSet2_{floatOut}_{coord[subFloatOut]}")

            fileOut.write(f",PatchStyleUint32")
            fileOut.write(f",Unknown1Uint32")
            fileOut.write(f",TextureAssigmentUint16")
            fileOut.write(f",LightmapIDUint16")
            fileOut.write(f",Unknown2Uint32")
            fileOut.write(f",Unknown3Uint32")
            fileOut.write(f",Unknown4Uint32")



            fileOut.write("\n")  

    def WriteToCsvFile(self, fileOut, indexNumCurvedPatchBlocks, fileName):
        if (fileOut is not None):
            if (fileName is not None):
                fileOut.write(f"{fileName},")

            #write to file
            fileOut.write(f"{indexNumCurvedPatchBlocks}")

            for floatOut in range(self.numLightMapUVPoints):
                for subFloatOut in range(4):
                    fileOut.write(f",{self.LightMapUVPoints[floatOut][subFloatOut]}")

            for floatOut in range(self.numTextureUVPoints):
                for subFloatOut in range(4):
                    fileOut.write(f",{self.TextureUVPoints[floatOut][subFloatOut]}")

            for bezierPointsX in range(4):
                for bezierPointsY in range(4):
                    for subFloatOut in range(4):
                        fileOut.write(f",{self.BezierControlPoints[bezierPointsX, bezierPointsY,subFloatOut]}")

            for floatOut in range(self.numOutlinePointsSet1):
                for subFloatOut in range(3): # TODO use shape
                    fileOut.write(f",{self.OutlinePointsSet1[floatOut][subFloatOut]}")

            for floatOut in range(self.numOutlinePointsSet2):
                for subFloatOut in range(4): # TODO use shape
                    fileOut.write(f",{self.OutlinePointsSet2[floatOut][subFloatOut]}")

            fileOut.write(f",{self.PatchStyleUint32}")
            fileOut.write(f",{self.Unknown1Uint32}")
            fileOut.write(f",{self.TextureAssigmentUint16}")
            fileOut.write(f",{self.LightmapIDUint16}")
            fileOut.write(f",{self.Unknown2Uint32}")
            fileOut.write(f",{self.Unknown3Uint32}")
            fileOut.write(f",{self.Unknown4Uint32}")
            
            fileOut.write("\n")       

def ReadCurvedPatchBlockSSXTricky(pdbFileData, currentIndex):
    #print(f"========= Curved Patch Block ================ {currentIndex}")
    curvedBlock = SSXTrickyCurvedPatchBlock()

    # actual loading of data to structs
    for header in range(curvedBlock.numLightMapUVPoints):
        somethingFloatSize = 4*4
        somethingFloats = struct.unpack('ffff',pdbFileData[currentIndex:currentIndex+(somethingFloatSize)])
        curvedBlock.LightMapUVPoints[header,0:4] = somethingFloats
        currentIndex+=somethingFloatSize

    for header in range(curvedBlock.numTextureUVPoints):
        somethingFloatSize = 4*4
        somethingFloats = struct.unpack('ffff',pdbFileData[currentIndex:currentIndex+(somethingFloatSize)])
        curvedBlock.TextureUVPoints[header,0:4] = somethingFloats
        currentIndex+=somethingFloatSize

    for bezierPointsX in range(4):
        for bezierPointsY in range(4):
            bezierControlPointSize = 4*4
            bezierControlPoint = struct.unpack('ffff',pdbFileData[currentIndex:currentIndex+(bezierControlPointSize)])
            currentIndex+=bezierControlPointSize
            curvedBlock.BezierControlPoints[bezierPointsX, bezierPointsY,0:4] = bezierControlPoint[0:4]

    numSegments = 8 # TODO - the rest of the code does not work unless this is 8...
    curvedBlock.bezierSrf = BezierSurface.CalcBezierUsingMatrixMethod(curvedBlock.BezierControlPoints, True, numSegments)    

    
    for pointsIndex in range(curvedBlock.numOutlinePointsSet1):
        outlinePointsSize = 4*3
        outlinePoints = struct.unpack('fff',pdbFileData[currentIndex:currentIndex+(outlinePointsSize)])
        currentIndex+=outlinePointsSize
        curvedBlock.OutlinePointsSet1[pointsIndex, 0:3] = outlinePoints[0:3]

    for pointsIndex in range(curvedBlock.numOutlinePointsSet2):
        outlinePointsSize = 4*4
        outlinePoints = struct.unpack('ffff',pdbFileData[currentIndex:currentIndex+(outlinePointsSize)])
        currentIndex+=outlinePointsSize
        curvedBlock.OutlinePointsSet2[pointsIndex, 0:4] = outlinePoints[0:4]


    # TODO figure out the outlines like SSX
    # curvedBlock.Outline2Triangles[0,0:3] = curvedBlock.OutlinePoints[0,0:3]
    # curvedBlock.Outline2Triangles[1,0:3] = curvedBlock.OutlinePoints[1,0:3]
    # curvedBlock.Outline2Triangles[2,0:3] = curvedBlock.OutlinePoints[3,0:3] 
    # curvedBlock.Outline2Triangles[3,0:3] = curvedBlock.OutlinePoints[2,0:3] 
    # curvedBlock.Outline2Triangles[4,0:3] = curvedBlock.OutlinePoints[0,0:3]


    longSize = 4

    curvedBlock.PatchStyleUint32 = struct.unpack('L',pdbFileData[currentIndex:currentIndex+(longSize)])[0] 
    currentIndex+=longSize

    curvedBlock.Unknown1Uint32 = struct.unpack('L',pdbFileData[currentIndex:currentIndex+(longSize)])[0] 
    currentIndex+=longSize

    uint16Size = 2
    curvedBlock.TextureAssigmentUint16 = struct.unpack('H',pdbFileData[currentIndex:currentIndex+(uint16Size)])[0] 
    currentIndex+=uint16Size

    curvedBlock.LightmapIDUint16 = struct.unpack('H',pdbFileData[currentIndex:currentIndex+(uint16Size)])[0] 
    currentIndex+=uint16Size

    curvedBlock.Unknown2Uint32 = struct.unpack('L',pdbFileData[currentIndex:currentIndex+(longSize)])[0] 
    currentIndex+=longSize

    curvedBlock.Unknown3Uint32 = struct.unpack('L',pdbFileData[currentIndex:currentIndex+(longSize)])[0] 
    currentIndex+=longSize

    curvedBlock.Unknown4Uint32     = struct.unpack('L',pdbFileData[currentIndex:currentIndex+(longSize)])[0] 
    currentIndex+=longSize
    
    return (curvedBlock.blockSizeBytes, curvedBlock)

    

def AddStandardUVCoordinatesToObjFile(fileCurvedPatchObj):
    # the UV co-ordinates are in the PDB file and normally would  put those in the object file
    # but I used them already and manipulated the texture image to be transformed, mirror, duplicated and light adjusted, 
    # so the same UV co-ordinates will work for all mapping 
    # TODO make function to generate this
    fileCurvedPatchObj.write(f"vt 0 0  \n")
    fileCurvedPatchObj.write(f"vt 0 0.14285 \n")
    fileCurvedPatchObj.write(f"vt 0 0.28571 \n")
    fileCurvedPatchObj.write(f"vt 0 0.42857 \n")
    fileCurvedPatchObj.write(f"vt 0 0.57142 \n")
    fileCurvedPatchObj.write(f"vt 0 0.71428 \n")
    fileCurvedPatchObj.write(f"vt 0 0.85714 \n")
    fileCurvedPatchObj.write(f"vt 0 1  \n")
    fileCurvedPatchObj.write(f"vt 0.14285 0  \n")
    fileCurvedPatchObj.write(f"vt 0.14285 0.14285  \n")
    fileCurvedPatchObj.write(f"vt 0.14285 0.28571  \n")
    fileCurvedPatchObj.write(f"vt 0.14285 0.42857 \n")
    fileCurvedPatchObj.write(f"vt 0.14285 0.57142 \n")
    fileCurvedPatchObj.write(f"vt 0.14285 0.71428 \n")
    fileCurvedPatchObj.write(f"vt 0.14285 0.85714 \n")
    fileCurvedPatchObj.write(f"vt 0.14285 1 \n")
    fileCurvedPatchObj.write(f"vt 0.28571 0 \n")
    fileCurvedPatchObj.write(f"vt 0.28571 0.14285 \n")
    fileCurvedPatchObj.write(f"vt 0.28571 0.28571 \n")
    fileCurvedPatchObj.write(f"vt 0.28571 0.42857 \n")
    fileCurvedPatchObj.write(f"vt 0.28571 0.57142 \n")
    fileCurvedPatchObj.write(f"vt 0.28571 0.71428 \n")
    fileCurvedPatchObj.write(f"vt 0.28571 0.85714 \n")
    fileCurvedPatchObj.write(f"vt 0.28571 1 \n")
    fileCurvedPatchObj.write(f"vt 0.42857 0 \n")
    fileCurvedPatchObj.write(f"vt 0.42857 0.14285 \n")
    fileCurvedPatchObj.write(f"vt 0.42857 0.28571 \n")
    fileCurvedPatchObj.write(f"vt 0.42857 0.42857 \n")
    fileCurvedPatchObj.write(f"vt 0.42857 0.57142 \n")
    fileCurvedPatchObj.write(f"vt 0.42857 0.71428 \n")
    fileCurvedPatchObj.write(f"vt 0.42857 0.85714 \n")
    fileCurvedPatchObj.write(f"vt 0.42857 1 \n")
    fileCurvedPatchObj.write(f"vt 0.57142 0 \n")
    fileCurvedPatchObj.write(f"vt 0.57142 0.14285 \n")
    fileCurvedPatchObj.write(f"vt 0.57142 0.28571 \n")
    fileCurvedPatchObj.write(f"vt 0.57142 0.42857 \n")
    fileCurvedPatchObj.write(f"vt 0.57142 0.57142 \n")
    fileCurvedPatchObj.write(f"vt 0.57142 0.71428 \n")
    fileCurvedPatchObj.write(f"vt 0.57142 0.85714 \n")
    fileCurvedPatchObj.write(f"vt 0.57142 1 \n")
    fileCurvedPatchObj.write(f"vt 0.71428 0 \n")
    fileCurvedPatchObj.write(f"vt 0.71428 0.14285 \n")
    fileCurvedPatchObj.write(f"vt 0.71428 0.28571 \n")
    fileCurvedPatchObj.write(f"vt 0.71428 0.42857 \n")
    fileCurvedPatchObj.write(f"vt 0.71428 0.57142 \n")
    fileCurvedPatchObj.write(f"vt 0.71428 0.71428 \n")
    fileCurvedPatchObj.write(f"vt 0.71428 0.85714 \n")
    fileCurvedPatchObj.write(f"vt 0.71428 1 \n")
    fileCurvedPatchObj.write(f"vt 0.85714 0 \n")
    fileCurvedPatchObj.write(f"vt 0.85714 0.14285 \n")
    fileCurvedPatchObj.write(f"vt 0.85714 0.28571 \n")
    fileCurvedPatchObj.write(f"vt 0.85714 0.42857 \n")
    fileCurvedPatchObj.write(f"vt 0.85714 0.57142 \n")
    fileCurvedPatchObj.write(f"vt 0.85714 0.71428 \n")
    fileCurvedPatchObj.write(f"vt 0.85714 0.85714 \n")
    fileCurvedPatchObj.write(f"vt 0.85714 1 \n")
    fileCurvedPatchObj.write(f"vt 1 0 \n")
    fileCurvedPatchObj.write(f"vt 1 0.14285 \n")
    fileCurvedPatchObj.write(f"vt 1 0.28571 \n")
    fileCurvedPatchObj.write(f"vt 1 0.42857 \n")
    fileCurvedPatchObj.write(f"vt 1 0.57142 \n")
    fileCurvedPatchObj.write(f"vt 1 0.71428 \n")
    fileCurvedPatchObj.write(f"vt 1 0.85714 \n")
    fileCurvedPatchObj.write(f"vt 1 1 \n")

def WriteTextureToMaterialFile(fileCurvedPatchObj, materialFile, patchNumber, objTextureDirectory):
    textureName = f"texture_{patchNumber}"
    fileCurvedPatchObj.write(f"usemtl {textureName}\n")

    materialFile.write(f"newmtl {textureName}\n")
    materialFile.write("Ka 1.000 1.000 1.000 \n")
    materialFile.write("Kd 1.000 1.000 1.000 \n")
    materialFile.write("Ks 0.000 0.000 0.000 \n")
    materialFile.write("d 1.0 \n")
    materialFile.write("Tr 1.000000 \n")
    materialFile.write("illum 0 \n")
    materialFile.write("Ns 0.000000 \n")
    patchFile = f"{objTextureDirectory}LitTexture_{patchNumber:04d}.png"
    materialFile.write(f"map_Ka {patchFile} \n")
    materialFile.write(f"map_Kd {patchFile}  \n")

            
def ConvertTextureToLightMapTexture(curveRead : SSXTrickyCurvedPatchBlock, patchNum, applyLightMap, dirTextures, dirLightMaps, outputTextureDirectory):
    applyLightMap = True
  
    texturelightmaps.CreateLightmapAdjustedTexture(dirTextures, dirLightMaps, outputTextureDirectory, 
        applyLightMap,patchNum, curveRead.LightmapIDUint16, curveRead.TextureAssigmentUint16,
        curveRead.TextureUVPoints,
        curveRead.LightMapUVPoints[0])



class SSX_Tricky_MapPdbFileHeader:
    def __init__(self):
        # this is a guess based on internet information, from https://github.com/SSXModding/splinebruty/blob/master/pbdtypes.h
        self.version1                = 0 
        self.version2                = 0 
        self.version3                = 0 
        self.eDataFormatType         = 0 
        self.NumPlayerStarts         = 0 
        self.NumPatches              = 0 
        self.NumInstances            = 0 
        self.NumParticleInstances    = 0 
        self.NumMaterials            = 0 
        self.NumMaterialBlocks       = 0 
        self.NumLights               = 0 
        self.NumSplines              = 0 
        self.NumSplineSegments       = 0 
        self.NumTextureFlips         = 0 
        self.NumModels               = 0 
        self.Unknown                 = 0 
        self.NumTextures             = 0 
        self.NumCameras              = 0 
        self.LightMapSize            = 0 
        self.PlayerStartOffset       = 0 
        self.PatchOffset             = 0 
        self.InstanceOffset          = 0 
        self.Unknown2                = 0 
        self.MaterialOffset          = 0 
        self.MaterialBlocksOffset    = 0 
        self.LightsOffset            = 0 
        self.SplineOffset            = 0 
        self.SplineSegmentOffset     = 0 
        self.TextureFlipOffset       = 0 
        self.ModelPointerOffset      = 0 
        self.ModelsOffset            = 0 
        self.ParticleModelPointerOffset = 0 
        self.ParticleModelsOffset    = 0 
        self.CameraPointerOffset     = 0 
        self.CamerasOffset           = 0 
        self.HashOffset              = 0 

    def LoadHeaderBlock(self, loadedFileData):
        unpack = filehelpers.Unpacker(0, loadedFileData)
        self.version1                = unpack.ReadByte()
        self.version2                = unpack.ReadByte()
        self.version3                = unpack.ReadByte()
        self.eDataFormatType         = unpack.ReadByte()
        self.NumPlayerStarts         = unpack.ReadUint32()
        self.NumPatches              = unpack.ReadUint32()  # this field is correct
        self.NumInstances            = unpack.ReadUint32()
        self.NumParticleInstances    = unpack.ReadUint32()
        self.NumMaterials            = unpack.ReadUint32()
        self.NumMaterialBlocks       = unpack.ReadUint32()
        self.NumLights               = unpack.ReadUint32()
        self.NumSplines              = unpack.ReadUint32()
        self.NumSplineSegments       = unpack.ReadUint32()
        self.NumTextureFlips         = unpack.ReadUint32()
        self.NumModels               = unpack.ReadUint32()
        self.Unknown                 = unpack.ReadUint32()
        self.NumTextures             = unpack.ReadUint32()
        self.NumCameras              = unpack.ReadUint32()
        self.LightMapSize            = unpack.ReadUint32()
        self.PlayerStartOffset       = unpack.ReadUint32()
        self.PatchOffset             = unpack.ReadUint32() # this field is correct
        self.InstanceOffset          = unpack.ReadUint32()
        self.Unknown2                = unpack.ReadUint32()
        self.MaterialOffset          = unpack.ReadUint32()
        self.MaterialBlocksOffset    = unpack.ReadUint32()
        self.LightsOffset            = unpack.ReadUint32()
        self.SplineOffset            = unpack.ReadUint32()
        self.SplineSegmentOffset     = unpack.ReadUint32()
        self.TextureFlipOffset       = unpack.ReadUint32()
        self.ModelPointerOffset      = unpack.ReadUint32()
        self.ModelsOffset            = unpack.ReadUint32()
        self.ParticleModelPointerOffset  = unpack.ReadUint32()
        self.ParticleModelsOffset    = unpack.ReadUint32()
        self.CameraPointerOffset     = unpack.ReadUint32()
        self.CamerasOffset           = unpack.ReadUint32()
        self.HashOffset              = unpack.ReadUint32()

    def WriteHeaderBlock(self, fileOut):
        fileOut.write(f",{self.version1                }")
        fileOut.write(f",{self.version2                }")
        fileOut.write(f",{self.version3                }")
        fileOut.write(f",{self.eDataFormatType         }")
        fileOut.write(f",{self.NumPlayerStarts         }")
        fileOut.write(f",{self.NumPatches              }")
        fileOut.write(f",{self.NumInstances            }")
        fileOut.write(f",{self.NumParticleInstances    }")
        fileOut.write(f",{self.NumMaterials            }")
        fileOut.write(f",{self.NumMaterialBlocks       }")
        fileOut.write(f",{self.NumLights               }")
        fileOut.write(f",{self.NumSplines              }")
        fileOut.write(f",{self.NumSplineSegments       }")
        fileOut.write(f",{self.NumTextureFlips         }")
        fileOut.write(f",{self.NumModels               }")
        fileOut.write(f",{self.Unknown                 }")
        fileOut.write(f",{self.NumTextures             }")
        fileOut.write(f",{self.NumCameras              }")
        fileOut.write(f",{self.LightMapSize            }")
        fileOut.write(f",{self.PlayerStartOffset       }")
        fileOut.write(f",{self.PatchOffset             }")
        fileOut.write(f",{self.InstanceOffset          }")
        fileOut.write(f",{self.Unknown2                }")
        fileOut.write(f",{self.MaterialOffset          }")
        fileOut.write(f",{self.MaterialBlocksOffset    }")
        fileOut.write(f",{self.LightsOffset            }")
        fileOut.write(f",{self.SplineOffset            }")
        fileOut.write(f",{self.SplineSegmentOffset     }")
        fileOut.write(f",{self.TextureFlipOffset       }")
        fileOut.write(f",{self.ModelPointerOffset      }")
        fileOut.write(f",{self.ModelsOffset            }")
        fileOut.write(f",{self.ParticleModelPointerOffset}")
        fileOut.write(f",{self.ParticleModelsOffset    }")
        fileOut.write(f",{self.CameraPointerOffset     }")
        fileOut.write(f",{self.CamerasOffset           }")
        fileOut.write(f",{self.HashOffset              }")
       

    
def Load_SSXTricky_pbd(fileName, sshFileName, sshLightMapFileName, convertedFilesDir, 
    exportOptions: SSXTrickyExportOptions):
    #  , writePdbHeaderToCsvFile):

    print(f"=============== Loading Pdb file: {fileName} ==================")
    pdbFileData = Path(f'{convertedFilesDir}data\\models\\{fileName}.pbd').read_bytes()

    FilesToClose = []

    dirNameTextures = f'{convertedFilesDir}data\\models\\ssh_files\\{sshFileName}_ssh\\'
    dirNameLightMaps = f'{convertedFilesDir}data\\models\\ssh_files\\{sshLightMapFileName}_ssh\\'

    # for expermenting, get a 3d plot in python, but very slow for entire map
    showCurvedPatchBlocksOn3dPlot = False
    if(exportOptions.writePdbHeaderToCsvFile):
        fileHeaderDir = '.\\output_files\\SSX Tricky\\csv files\\'
        Path(fileHeaderDir).mkdir(parents=True, exist_ok=True)
        fileHeader = open(f'{fileHeaderDir}Tricky_{fileName}_headerblock.csv', 'w')
    else:
        fileHeader = None


    # output to csv file for loading into excel etc for analysis
    consolidateAllCurvedPatchesToCsv = False


    if(exportOptions.writeCurvedPatchesToCsvFile):
        fileCurvedPatchCsvDir = '.\\output_files\\SSX Tricky\\csv files\\'
        Path(fileCurvedPatchCsvDir).mkdir(parents=True, exist_ok=True)
        fileCurvedPatchCsvOut = open(f'{fileCurvedPatchCsvDir}Tricky_{fileName}_curvedpatch.csv', 'w') 
        FilesToClose.append(fileCurvedPatchCsvOut)

        if (consolidateAllCurvedPatchesToCsv):
            # dump all to the same file for testing
            fileCurvedPatchTestingCsvOut = open(f'{fileCurvedPatchCsvDir}X_Test_curvedpatch.csv', 'a')      
            FilesToClose.append(fileCurvedPatchTestingCsvOut)
    else:
        fileCurvedPatchCsvOut = None

    # output to obj file for loading into blender
    
    if exportOptions.writeCurvedPatchesToObjFile:
        CurvedPatchDir = '.\\output_files\\SSX Tricky\\curved patch beizer\\'
        Path(CurvedPatchDir).mkdir(parents=True, exist_ok=True)
        fileCurvedPatchObj = open(f'{CurvedPatchDir}Tricky_{fileName}_curvedpatch.obj', 'w')  
        FilesToClose.append(fileCurvedPatchObj)
        mtlFileName = f"Tricky_{fileName}_curvedpatch.mtl"
        materialFile = open(f'{CurvedPatchDir}{mtlFileName}', 'w') 
        fileCurvedPatchObj.write(f"mtllib {mtlFileName}\n")
        objTextureDirectory = f"Tricky_{fileName}_curvedpatch_textures\\"
        textureOutputDirectory = f"{CurvedPatchDir}{objTextureDirectory}"

    else:
        fileCurvedPatchObj = None


    pdbFileDataLength = len(pdbFileData)
    print(f"pdb File Length : {pdbFileDataLength}")

    header = SSX_Tricky_MapPdbFileHeader() 
    header.LoadHeaderBlock(pdbFileData)
    if showCurvedPatchBlocksOn3dPlot:
        fig = plt.figure()
        ax = Axes3D(fig)

    numCurvedPatchBlocks = 0
    curvedPatchList = []
    # curved block filter (for loading small sections and testing)
    useCurvedBlockFilter = False
    firstCurvedBlockFilter = 1 
    lastCurvedBlockFilter = 760
    
    

    
    if (fileHeader is not None):
        header.WriteHeaderBlock(fileHeader)
        fileHeader.close   

    index = header.PatchOffset
    while numCurvedPatchBlocks < header.NumPatches: # end of yellows    


        numCurvedPatchBlocks+=1
        (blockSize, curvedBlock) = ReadCurvedPatchBlockSSXTricky(pdbFileData, index) 
        #print(f"Curved Block Index: {numCurvedPatchBlocks}")
        if (useCurvedBlockFilter== False or (useCurvedBlockFilter== True and numCurvedPatchBlocks>=firstCurvedBlockFilter and numCurvedPatchBlocks<=lastCurvedBlockFilter)):
            curvedPatchList.append(curvedBlock)           
        if (useCurvedBlockFilter== True and numCurvedPatchBlocks==lastCurvedBlockFilter):
            # finish early if using filter 
            break
        index += blockSize

        percentProgress= numCurvedPatchBlocks/header.NumPatches*100.0
        percentProgressInt = int(percentProgress*100)
        if percentProgressInt% 1000==0 and percentProgress > 5.0:
            print(f"Percent Progress: {percentProgress:.1f}")

    print(f"Number of blocks:  Curved: {numCurvedPatchBlocks}  percent curved blocks: {numCurvedPatchBlocks/header.NumPatches*100.0}")     

    if fileCurvedPatchCsvOut is not None:
        curvedBlock = SSXTrickyCurvedPatchBlock()
        curvedBlock.WriteHeaderToCsvFile(fileCurvedPatchCsvOut)

    # ====== write object file ======
    scaleFactor = 10000.0 # blender does not handle large numbers....
    numCurvedPatchBlocks = 0
    objVertexIndex = 1
    if fileCurvedPatchObj is not None:
        AddStandardUVCoordinatesToObjFile(fileCurvedPatchObj)   
    for curveRead in curvedPatchList:
        numCurvedPatchBlocks += 1

        if fileCurvedPatchCsvOut is not None:
            curveRead.WriteToCsvFile(fileCurvedPatchCsvOut, numCurvedPatchBlocks, None)
            if (consolidateAllCurvedPatchesToCsv):
                curveRead.WriteToCsvFile(fileCurvedPatchTestingCsvOut, numCurvedPatchBlocks, fileName)


        if showCurvedPatchBlocksOn3dPlot:
            ax.plot_surface(curveRead.bezierSrf[:, :, 0], curveRead.bezierSrf[:, :, 1], curveRead.bezierSrf[:, :, 2])

        if fileCurvedPatchObj is not None:
            # TODO - refactor with SSX to common code
            # make obj file of curved patches
            fileCurvedPatchObj.write(f"o patch_{numCurvedPatchBlocks} \n")
            numSegments = 8 # breaks if not 8
            for x in range(0,numSegments):
                for y in range(0,numSegments):
                    fileCurvedPatchObj.write(f"v {curveRead.bezierSrf[x,y,0]/scaleFactor}  {curveRead.bezierSrf[x,y,1]/scaleFactor}  {curveRead.bezierSrf[x,y,2]/scaleFactor}  1 \n")

            # add textures to material file
            WriteTextureToMaterialFile(fileCurvedPatchObj, materialFile, numCurvedPatchBlocks, objTextureDirectory)
            if (exportOptions.writeTextures):
                ConvertTextureToLightMapTexture(curveRead, numCurvedPatchBlocks, exportOptions.applyLightMapsToTextures, dirNameTextures, dirNameLightMaps, textureOutputDirectory)

            # it's a grid of 8 x 8 rectangles so make triangles for each rectangle
            vextexIndex = objVertexIndex
            textureIndex = 1
            for x in range(0,numSegments-1):
                for y in range(0,numSegments-1):
                    fileCurvedPatchObj.write(f"f {vextexIndex}/{textureIndex} {vextexIndex+1}/{textureIndex+1} {vextexIndex+8}/{textureIndex+8} \n")
                    fileCurvedPatchObj.write(f"f {vextexIndex+1}/{textureIndex+1} {vextexIndex+8}/{textureIndex+8} {vextexIndex+9}/{textureIndex+9} \n")
                    vextexIndex +=1
                    textureIndex+=1
                vextexIndex +=1 # skip the last one.
                textureIndex+=1
            objVertexIndex+=64

        percentProgress= numCurvedPatchBlocks/header.NumPatches*100.0
        percentProgressInt = int(percentProgress*100)
        if percentProgressInt% 1000==0 and percentProgress > 5.0:
            print(f"Percent Progress Textures: {percentProgress:.1f}")


    for fileHandle in FilesToClose:
        fileHandle.close()

    if (showCurvedPatchBlocksOn3dPlot):
        plt.show() 
    


if __name__ == "__main__":
    # testing

    pdbOptions = SSXTrickyExportOptions()
    pdbOptions.writeCurvedPatchesToObjFile = True
    pdbOptions.writeCurvedPatchesToCsvFile = True 
    pdbOptions.writePdbHeaderToCsvFile = True
    pdbOptions.writeTextures = True
    pdbOptions.applyLightMapsToTextures = True


    convertedFilesDir = f'.\\output_files\\SSX Tricky\\dvdmodelfiles\\'

  
    # sshFileName, sshLightMapFileName
    # dirNameTexturesTest = '.\\output_files\\SSX Tricky\\dvdmodelfiles\\data\\models\\ssh_files\\elysium_ssh\\'
    # dirNameLightMapsTest = '.\\output_files\\SSX Tricky\\dvdmodelfiles\\data\\models\\ssh_files\\elysiu_ssh_L\\'
    # dirNameLightMapsComputedTest = '.\\output_files\\SSX Tricky\\curved patch beizer\\Tricky_elysium_curvedpatch_textures\\'
    # dirNameTexturesTest = f'{convertedFilesDir}data\\models\\ssh_files\\{sshFileName}_ssh\\'
    # dirNameLightMapsTest = f'{convertedFilesDir}data\\models\\ssh_files\\{sshLightMapFileName}_L\\'
    # dirNameLightMapsComputedTest = '.\\output_files\\SSX Tricky\\curved patch beizer\\Tricky_elysium_curvedpatch_textures\\'

    # texturelightmaps.CreateLightmapAdjustedTexture(dirNameTexturesTest, dirNameLightMapsTest, dirNameLightMapsComputedTest, applyLightMap,1,0,57,((0.00799998641014099,-0.00799998641014099),(0.991999983787536,-0.00799998641014099),(0.00799998641014099,-0.991999983787536),(0.991999983787536,-0.991999983787536)),(0,0,0.0625,0.0625))


    Load_SSXTricky_pbd("alaska", "alaska", "alaska_L", convertedFilesDir,  pdbOptions)
    Load_SSXTricky_pbd("aloha","aloha","aloha_L", convertedFilesDir, pdbOptions)
    Load_SSXTricky_pbd("elysium", "elysium", "elysiu_L", convertedFilesDir,  pdbOptions)
    Load_SSXTricky_pbd("gari","gari","gari_L", convertedFilesDir,  pdbOptions)
    Load_SSXTricky_pbd("megaple","megaple","megapl_L", convertedFilesDir,  pdbOptions)
    Load_SSXTricky_pbd("merquer","merquer","merque_L", convertedFilesDir,  pdbOptions)
    Load_SSXTricky_pbd("mesa","mesa","mesa_L", convertedFilesDir,  pdbOptions)
    Load_SSXTricky_pbd("pipe","pipe","pipe_L", convertedFilesDir,  pdbOptions)
    Load_SSXTricky_pbd("snow","snow","snow_L", convertedFilesDir,  pdbOptions)
    Load_SSXTricky_pbd("ssxfe","ssxfE","ssxfE_L", convertedFilesDir,  pdbOptions)
    Load_SSXTricky_pbd("trick","trick","trick_L", convertedFilesDir,  pdbOptions)
    Load_SSXTricky_pbd("untrack", "untrack", "untrac_L", convertedFilesDir,  pdbOptions)


