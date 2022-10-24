from pathlib import Path
import struct
import numpy as np
import BezierSurface
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import filehelpers




def IsCheckValue(pdbFileData, currentIndex, offset, checkValue):
    offsetLength = 4
    offsetIndex = offset*4
    value = struct.unpack('L',pdbFileData[currentIndex+offsetIndex:currentIndex+offsetIndex+offsetLength])
    #print(f"IsCheckValue: {value[0]}=={checkValue}")
    return (value[0]==checkValue)

def IsFFFFFFFF(pdbFileData, currentIndex, offset):
    checkNumber = 0xffffffff
    return IsCheckValue(pdbFileData, currentIndex, offset,checkNumber)


class SSXTrickyCurvedPatchBlock:
    def __init__(self):
        # patch file data
        self.numInitialPoints = 5
        self.InitialPoints = np.zeros((self.numInitialPoints,4)) # 5 of them - I dont use them, what are they? Translation, rotation?
        self.BezierControlPoints = np.zeros((4,4,4)) # 16 of them, x,y,z,1
        self.bezierSrf = None

        self.numOutlinePointsSet1 = 2
        self.OutlinePointsSet1 = np.zeros((self.numOutlinePointsSet1 ,3))   # it's probably the outline like SSX but they have shaved 8 bytes by leaving the 1 off the end so x,y,z

        self.numOutlinePointsSet2 = 4
        self.OutlinePointsSet2 = np.zeros((self.numOutlinePointsSet2 ,4))   # it's probably the outline too but x,y,z,1

        self.numEndDwords = 6
        self.EndDwords = np.zeros((self.numEndDwords))   
        
        
        # useful data I calculate
        self.blockSizeBytes = 112*4

        # self.Outline2TrianglesNumberPoints = 5
        # self.Outline2Triangles = np.zeros((self.Outline2TrianglesNumberPoints,3)) 
    
    def WriteHeaderToCsvFile(self, fileOut):
        if (fileOut is not None):
            fileOut.write(f"Curved Patch Index")
            coord = ["x","y","z","w"]
            for floatOut in range(self.numInitialPoints):
                for subFloatOut in range(4):
                    fileOut.write(f",InitialPoints_{floatOut}_{coord[subFloatOut]}")

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

            for dwordOut in range(self.numEndDwords):
                fileOut.write(f",EndDword_{dwordOut}")

            fileOut.write("\n")  

    def WriteToCsvFile(self, fileOut, indexNumCurvedPatchBlocks):
        if (fileOut is not None):
            #write to file
            fileOut.write(f"{indexNumCurvedPatchBlocks}")

            for floatOut in range(self.numInitialPoints):
                for subFloatOut in range(4):
                    fileOut.write(f",{self.InitialPoints[floatOut][subFloatOut]}")

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

            for dwordOut in range(self.numEndDwords):
                fileOut.write(f",{self.EndDwords[dwordOut]}")
    
            fileOut.write("\n")       

def ReadCurvedPatchBlockSSXTricky(pdbFileData, currentIndex):
    #print(f"========= Curved Patch Block ================ {currentIndex}")
    curvedBlock = SSXTrickyCurvedPatchBlock()

    # actual loading of data to structs
    for header in range(5):
        somethingFloatSize = 4*4
        somethingFloats = struct.unpack('ffff',pdbFileData[currentIndex:currentIndex+(somethingFloatSize)])
        curvedBlock.InitialPoints[header,0:4] = somethingFloats
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

    for dwordOut in range(curvedBlock.numEndDwords):
        longSize = 4
        curvedBlock.EndDwords[dwordOut] = struct.unpack('L',pdbFileData[currentIndex:currentIndex+(longSize)])[0] 
        currentIndex+=longSize
    
    return (curvedBlock.blockSizeBytes, curvedBlock)

    





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
       

    
def Load_SSXTricky_pbd(fileName, convertedFilesDir, writeCurvedPatchesToObjFile, writeCurvedPatchesToCsvFile, writePdbHeaderToCsvFile):

    print(f"=============== Loading Pdb file: {fileName} ==================")
    pdbFileData = Path(f'{convertedFilesDir}data\\models\\{fileName}.pbd').read_bytes()

    FilesToClose = []


    # for expermenting, get a 3d plot in python, but very slow for entire map
    showCurvedPatchBlocksOn3dPlot = False
    if(writePdbHeaderToCsvFile):
        fileHeaderDir = '.\\output_files\\SSX Tricky\\csv files\\'
        Path(fileHeaderDir).mkdir(parents=True, exist_ok=True)
        fileHeader = open(f'{fileHeaderDir}Tricky_{fileName}_headerblock.csv', 'w')
    else:
        fileHeader = None


    # output to csv file for loading into excel etc for analysis
    if(writeCurvedPatchesToCsvFile):
        fileCurvedPatchCsvDir = '.\\output_files\\SSX Tricky\\csv files\\'
        Path(fileCurvedPatchCsvDir).mkdir(parents=True, exist_ok=True)
        fileCurvedPatchCsvOut = open(f'{fileCurvedPatchCsvDir}Tricky_{fileName}_curvedpatch.csv', 'w')      
        FilesToClose.append(fileCurvedPatchCsvOut)
    else:
        fileCurvedPatchCsvOut = None

    # output to obj file for loading into blender
    if writeCurvedPatchesToObjFile:
        CurvedPatchDir = '.\\output_files\\SSX Tricky\\curved patch beizer\\'
        Path(CurvedPatchDir).mkdir(parents=True, exist_ok=True)
        fileCurvedPatchObj = open(f'{CurvedPatchDir}Tricky_{fileName}_curvedpatch.obj', 'w')  
        FilesToClose.append(fileCurvedPatchObj)
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
    lastCurvedBlockFilter = 100
    
    

    
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

    print(f"Number of blocks:  Yellow: {numCurvedPatchBlocks}  percent curved blocks: {numCurvedPatchBlocks/header.NumPatches*100.0}")     

    if fileCurvedPatchCsvOut is not None:
        curvedBlock = SSXTrickyCurvedPatchBlock()
        curvedBlock.WriteHeaderToCsvFile(fileCurvedPatchCsvOut)

    scaleFactor = 10000.0 # blender does not handle large numbers....
    numCurvedPatchBlocks = 0
    objVertexIndex = 1
    for curveRead in curvedPatchList:
        numCurvedPatchBlocks += 1

        if fileCurvedPatchCsvOut is not None:
            curveRead.WriteToCsvFile(fileCurvedPatchCsvOut, numCurvedPatchBlocks)

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

            # it's a grid of 8 x 8 rectangles so make triangles for each rectangle
            vextexIndex = objVertexIndex
            for x in range(0,numSegments-1):
                for y in range(0,numSegments-1):
                    fileCurvedPatchObj.write(f"f {vextexIndex} {vextexIndex+1} {vextexIndex+8} \n")
                    fileCurvedPatchObj.write(f"f {vextexIndex+1} {vextexIndex+8} {vextexIndex+9} \n")
                    vextexIndex +=1
                vextexIndex +=1 # skip the last one.
            objVertexIndex+=64




    for fileHandle in FilesToClose:
        fileHandle.close()

    if (showCurvedPatchBlocksOn3dPlot):
        plt.show() 
    


if __name__ == "__main__":
    # testing
    writeCurvedPatchesToObjFile = True
    writeCurvedPatchesToCsvFile = True 
    writePdbHeaderToCsvFile = True
    
    # D:\\SSX Tricky dvd\\convertedmodels\\

    convertedFilesDir = f'.\\output_files\\SSX\\dvdmodelfiles\\'

    Load_SSXTricky_pbd("alaska", convertedFilesDir, writeCurvedPatchesToObjFile, writeCurvedPatchesToCsvFile, writePdbHeaderToCsvFile)
    Load_SSXTricky_pbd("aloha", convertedFilesDir, writeCurvedPatchesToObjFile, writeCurvedPatchesToCsvFile, writePdbHeaderToCsvFile)
    Load_SSXTricky_pbd("elysium", convertedFilesDir, writeCurvedPatchesToObjFile, writeCurvedPatchesToCsvFile, writePdbHeaderToCsvFile)
    Load_SSXTricky_pbd("gari", convertedFilesDir, writeCurvedPatchesToObjFile, writeCurvedPatchesToCsvFile, writePdbHeaderToCsvFile)
    Load_SSXTricky_pbd("megaple", convertedFilesDir, writeCurvedPatchesToObjFile, writeCurvedPatchesToCsvFile, writePdbHeaderToCsvFile)
    Load_SSXTricky_pbd("merquer", convertedFilesDir, writeCurvedPatchesToObjFile, writeCurvedPatchesToCsvFile, writePdbHeaderToCsvFile)
    Load_SSXTricky_pbd("mesa", convertedFilesDir, writeCurvedPatchesToObjFile, writeCurvedPatchesToCsvFile, writePdbHeaderToCsvFile)
    Load_SSXTricky_pbd("pipe", convertedFilesDir, writeCurvedPatchesToObjFile, writeCurvedPatchesToCsvFile, writePdbHeaderToCsvFile)
    Load_SSXTricky_pbd("snow", convertedFilesDir, writeCurvedPatchesToObjFile, writeCurvedPatchesToCsvFile, writePdbHeaderToCsvFile)
    Load_SSXTricky_pbd("ssxfe", convertedFilesDir, writeCurvedPatchesToObjFile, writeCurvedPatchesToCsvFile, writePdbHeaderToCsvFile)
    Load_SSXTricky_pbd("trick", convertedFilesDir, writeCurvedPatchesToObjFile, writeCurvedPatchesToCsvFile, writePdbHeaderToCsvFile)
    Load_SSXTricky_pbd("untrack", convertedFilesDir, writeCurvedPatchesToObjFile, writeCurvedPatchesToCsvFile, writePdbHeaderToCsvFile)


