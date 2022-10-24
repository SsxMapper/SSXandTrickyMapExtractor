from pathlib import Path
import struct
import numpy as np
import BezierSurface
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D



def ReadBlueBlock(wdfFileData, currentIndex):
    printOut=False
    if(printOut):
        print(f"==============  Blue Block ================== {currentIndex}")
    blueSectionOffset = 11*4 + 2
    blueSectionOffsetLength = 2
    blueSectionOffsetCheckNumber = 0xffff
    startIndex = currentIndex
    nineFloatSize = 9*4
    nineFloats = struct.unpack('fffffffff',wdfFileData[currentIndex:currentIndex+(nineFloatSize)])
    currentIndex+=nineFloatSize
    value1 = struct.unpack('H',wdfFileData[currentIndex:currentIndex+(2)])
    currentIndex+=2
    value2 = struct.unpack('H',wdfFileData[currentIndex:currentIndex+(2)])
    currentIndex+=2
    value3 = struct.unpack('H',wdfFileData[currentIndex:currentIndex+(2)])
    currentIndex+=2
    value4 = struct.unpack('H',wdfFileData[currentIndex:currentIndex+(2)])
    currentIndex+=2
    endBlockSize = struct.unpack('H',wdfFileData[currentIndex:currentIndex+(2)])
    currentIndex+=2
    blueFFFF = struct.unpack('H',wdfFileData[currentIndex:currentIndex+(2)])
    currentIndex+=2

    firstBlocksArray = []
    for firstBlocks in range(16):
        blockInfoSize = 12*2
        blockInfo = struct.unpack('HHHHHHHHHHHH',wdfFileData[currentIndex:currentIndex+(blockInfoSize)])
        currentIndex+=blockInfoSize    
        floatValuesFirstBlockSize = 6*4 
        floatValuesFirstBlock = struct.unpack('ffffff',wdfFileData[currentIndex:currentIndex+(floatValuesFirstBlockSize)])
        currentIndex+=floatValuesFirstBlockSize  
        firstBlocksArray.append([blockInfo,floatValuesFirstBlock])
    if(printOut):
        print(f"{nineFloats} {value1} {value2} {value3} {value4} {endBlockSize} {blueFFFF}")
        for block in firstBlocksArray:
            print(f"{block}")

    endBlocksArray = []
    for firstBlocks in range(endBlockSize[0]):
        endblockInfoSize = 2*2
        endblockInfo = struct.unpack('HH',wdfFileData[currentIndex:currentIndex+(endblockInfoSize)])    
        currentIndex+=endblockInfoSize  
        endBlocksArray.append(endblockInfo)
    if(printOut):
        for endblock in endBlocksArray:
            print(f"{endblock}", end = ' ')

    # blue block has to end on multiple of 32
    padFloat = 4 - (endBlockSize[0] % 4)
    if (padFloat == 4):
        padFloat = 0
    currentIndex+=(padFloat*4)  # pad floats
    if(printOut):
        print(f"BlueBlock Length: {currentIndex-startIndex} padBytes {padFloat}")
    return (currentIndex-startIndex, None)

def IsCheckValue(wdfFileData, currentIndex, offset, checkValue):
    offsetLength = 4
    offsetIndex = offset*4
    value = struct.unpack('L',wdfFileData[currentIndex+offsetIndex:currentIndex+offsetIndex+offsetLength])
    #print(f"IsCheckValue: {value[0]}=={checkValue}")
    return (value[0]==checkValue)

def IsFFFFFFFF(wdfFileData, currentIndex, offset):
    checkNumber = 0xffffffff
    return IsCheckValue(wdfFileData, currentIndex, offset,checkNumber)

def IsBlueBlock(wdfFileData, currentIndex, wdfFileDataLength):


    blueSectionOffset = 11*4 + 2
    blueSectionOffsetLength = 2
    blueSectionOffsetCheckNumber = 0xffff

    endIndex = currentIndex+blueSectionOffset+blueSectionOffsetLength
    if (wdfFileDataLength>endIndex):
        blueValue = struct.unpack('H',wdfFileData[currentIndex+blueSectionOffset:endIndex])
        #print(f"BlueValue : {blueValue[0]}")
        return (blueValue[0]== blueSectionOffsetCheckNumber)
    else:
        # not enough room left in file
        return False
        
def IsGreenBlock(wdfFileData, currentIndex, wdfFileDataLength):
    if currentIndex+(68*4)<=wdfFileDataLength:
        return (
            IsFFFFFFFF(wdfFileData, currentIndex, 65) and
            IsFFFFFFFF(wdfFileData, currentIndex, 66) and
            IsFFFFFFFF(wdfFileData, currentIndex, 67))
    else:
        # not enough room left in file
        return False

def IsCurvedPatchBlock(wdfFileData, currentIndex, wdfFileDataLength):
    if currentIndex+(112*4)<=wdfFileDataLength:
        return (IsFFFFFFFF(wdfFileData, currentIndex, 111) )
    else:
        # not enough room left in file
        return False

def IsRedBlock(wdfFileData, currentIndex, wdfFileDataLength):
    if currentIndex+(32*4)<=wdfFileDataLength:
        return (IsFFFFFFFF(wdfFileData, currentIndex, 31))
    else:
        # not enough room left in file
        return False

def IsOrangeBlock(wdfFileData, currentIndex, wdfFileDataLength):
    if currentIndex+(22*4)<=wdfFileDataLength:
        return (IsCheckValue(wdfFileData, currentIndex, 0,0x00000002) or
            IsCheckValue(wdfFileData, currentIndex, 0,0x00000001) or 

            (IsCheckValue(wdfFileData, currentIndex, 12,0xE4078678) and
            IsCheckValue(wdfFileData, currentIndex, 13,0xE4078678) and
            IsCheckValue(wdfFileData, currentIndex, 14,0xE4078678) and
            IsCheckValue(wdfFileData, currentIndex, 15,0x64078678) and
            IsCheckValue(wdfFileData, currentIndex, 16,0x64078678) and
            IsCheckValue(wdfFileData, currentIndex, 17,0x64078678) ) )
    else:
        # not enough room left in file
        return False        

def ReadGreenBlock(wdfFileData, currentIndex, numGreenBlocks, fileGreenOut):
    #print(f"============== Green Block ================== {currentIndex}")
    if  fileGreenOut is not None:
        fileGreenOut.write(f"{numGreenBlocks},")  
      
    # TODO refactor  
    first48ColsFloats = []   
    for valueIndex in range(48):
        floatSize = 4
        floatValue = struct.unpack('f',wdfFileData[currentIndex:currentIndex+(floatSize)])        
        first48ColsFloats.append(floatValue)
        if  fileGreenOut is not None:
            fileGreenOut.write(f"{floatValue[0]},")  
        currentIndex+=floatSize
    #column 49
    for valueIndex in range(4):
        sizeShort = 2
        shortValue = struct.unpack('H',wdfFileData[currentIndex:currentIndex+(sizeShort)])        
        if  fileGreenOut is not None:
            fileGreenOut.write(f"0x{shortValue[0]:04x},")
        currentIndex+=sizeShort
    # column 53 (51)
    for valueIndex in range(1):
        longSize = 4
        longValue = struct.unpack('L',wdfFileData[currentIndex:currentIndex+(longSize)])        
        if  fileGreenOut is not None:
            fileGreenOut.write(f"0x{longValue[0]:08x},")
        currentIndex+=longSize
    #column 54 (52)
    for valueIndex in range(2):
        sizeShort = 2
        shortValue = struct.unpack('H',wdfFileData[currentIndex:currentIndex+(sizeShort)])        
        if  fileGreenOut is not None:
            fileGreenOut.write(f"0x{shortValue[0]:04x},")
        currentIndex+=sizeShort
    # column 56 (53) - world co-ordintes 
    worldCoordCol56Floats = []
    for valueIndex in range(6):
        floatSize = 4
        floatValue = struct.unpack('f',wdfFileData[currentIndex:currentIndex+(floatSize)])    
        worldCoordCol56Floats.append(floatValue)    
        if  fileGreenOut is not None:
            fileGreenOut.write(f"{floatValue[0]},")  
        currentIndex+=floatSize
    # column 60 (59) 
    for valueIndex in range(2):
        sizeShort = 2
        shortValue = struct.unpack('H',wdfFileData[currentIndex:currentIndex+(sizeShort)])        
        if  fileGreenOut is not None:
            fileGreenOut.write(f"0x{shortValue[0]:04x},")
        currentIndex+=sizeShort
    # column 64 (60)            
    for valueIndex in range(1):
        longSize = 4
        longValue = struct.unpack('L',wdfFileData[currentIndex:currentIndex+(longSize)])        
        if  fileGreenOut is not None:
            fileGreenOut.write(f"0x{longValue[0]:08x},") 
        currentIndex+=longSize
    # column 65 (61) 
    for valueIndex in range(4):
        sizeShort = 2
        shortValue = struct.unpack('H',wdfFileData[currentIndex:currentIndex+(sizeShort)])        
        if  fileGreenOut is not None:
            fileGreenOut.write(f"0x{shortValue[0]:04x},")
        currentIndex+=sizeShort 
    # column 67 (63)                        
    for valueIndex in range(1):
        floatSize = 4
        floatValue = struct.unpack('f',wdfFileData[currentIndex:currentIndex+(floatSize)])        
        if  fileGreenOut is not None:
            fileGreenOut.write(f"{floatValue[0]},")  
        currentIndex+=floatSize
    # column 68 (64) 
    for valueIndex in range(2):
        sizeShort = 2
        shortValue = struct.unpack('H',wdfFileData[currentIndex:currentIndex+(sizeShort)])        
        if  fileGreenOut is not None:
            fileGreenOut.write(f"0x{shortValue[0]:04x},")
        currentIndex+=sizeShort 
    # column 70 (65)                        
    for valueIndex in range(4):
        longSize = 4
        longValue = struct.unpack('L',wdfFileData[currentIndex:currentIndex+(longSize)])        
        if  fileGreenOut is not None:
            fileGreenOut.write(f"0x{longValue[0]:08x},")
        currentIndex+=longSize
    if  fileGreenOut is not None:
        fileGreenOut.write(f"\n")   

    Outline1Triangles = np.zeros((4,3)) 
    Outline1Triangles[0,0] = first48ColsFloats[12][0]
    Outline1Triangles[0,1] = first48ColsFloats[13][0]
    Outline1Triangles[0,2] = first48ColsFloats[14][0]
    Outline1Triangles[1,0] = worldCoordCol56Floats[0][0]
    Outline1Triangles[1,1] = worldCoordCol56Floats[1][0]
    Outline1Triangles[1,2] = worldCoordCol56Floats[2][0]
    Outline1Triangles[2,0] = worldCoordCol56Floats[3][0]
    Outline1Triangles[2,1] = worldCoordCol56Floats[4][0]
    Outline1Triangles[2,2] = worldCoordCol56Floats[5][0]
    Outline1Triangles[3,0] = first48ColsFloats[12][0]
    Outline1Triangles[3,1] = first48ColsFloats[13][0]
    Outline1Triangles[3,2] = first48ColsFloats[14][0]

    return (68*4, Outline1Triangles)

class SSXCurvedPatchBlock:
    def __init__(self):
        # patch file data
        self.numInitialPoints = 5
        self.InitialPoints = np.zeros((self.numInitialPoints,4)) # 5 of them - I dont use them, what are they? Translation, rotation?
        self.BezierControlPoints = np.zeros((4,4,4)) # 16 of them, x,y,z,1
        self.bezierSrf = None

        self.numOutlinePoints = 6
        self.OutlinePoints = np.zeros((self.numOutlinePoints ,4))   # the first 4 are a bounding rectangle for the patch, the last 2 are maybe lighting normals (although SSX Game developer conference notes say the lighting is pre calculated)

        self.TextureBlockIdUint32 = 0  # maybe but does not match up with (mapname).ssh file images
        # I suspect given other reading about SSX that lighting textures are stored in large bitmaps of 128x128 in 
        # (mapname)l.ssh, and then use an sub id to reference a smalled 16x16 or 8x8 block 
        self.LightBlockTextureIndexBlockIdUint32 = 0  
        self.LightBlockTextureSubblockIndexUint32 = 0  # maybe
        
        self.TerminatorUint32 = 0  # should always be 0xffffffff
        
        # useful data I calculate
        self.blockSizeBytes = 112*4
        self.Outline2TrianglesNumberPoints = 5
        self.Outline2Triangles = np.zeros((self.Outline2TrianglesNumberPoints,3)) 

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

            for floatOut in range(self.numOutlinePoints):
                for subFloatOut in range(4): # TODO use shape
                    fileOut.write(f",OutlineSet_{floatOut}_{coord[subFloatOut]}")

            fileOut.write(f",TextureBlockIdUint32")
            fileOut.write(f",LightBlockTextureIndexBlockIdUint32")
            fileOut.write(f",LightBlockTextureSubblockIndexUint32")
            fileOut.write(f",TerminatorUint32")

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

            for floatOut in range(self.numOutlinePoints):
                for subFloatOut in range(4):
                    fileOut.write(f",{self.OutlinePoints[floatOut][subFloatOut]}")


            fileOut.write(f",{self.TextureBlockIdUint32}")
            fileOut.write(f",{self.LightBlockTextureIndexBlockIdUint32}")
            fileOut.write(f",{self.LightBlockTextureSubblockIndexUint32}")
            fileOut.write(f",{self.TerminatorUint32}")
    
            fileOut.write("\n")       

def ReadCurvedPatchBlock(wdfFileData, currentIndex):
    #print(f"========= Curved Patch Block ================ {currentIndex}")
    curvedBlock = SSXCurvedPatchBlock()

    # actual loading of data to structs
    for header in range(5):
        somethingFloatSize = 4*4
        somethingFloats = struct.unpack('ffff',wdfFileData[currentIndex:currentIndex+(somethingFloatSize)])
        curvedBlock.InitialPoints[header,0:4] = somethingFloats
        currentIndex+=somethingFloatSize

    for bezierPointsX in range(4):
        for bezierPointsY in range(4):
            bezierControlPointSize = 4*4
            bezierControlPoint = struct.unpack('ffff',wdfFileData[currentIndex:currentIndex+(bezierControlPointSize)])
            currentIndex+=bezierControlPointSize
            curvedBlock.BezierControlPoints[bezierPointsX, bezierPointsY,0:4] = bezierControlPoint[0:4]

    numSegments = 8 # TODO - the rest of the code does not work unless this is 8...
    curvedBlock.bezierSrf = BezierSurface.CalcBezierUsingMatrixMethod(curvedBlock.BezierControlPoints, True, numSegments)    

    # 2 triangles to make a rectangle? 6 vectices?
    pointsIndex=0
    for outlinePointsX in range(curvedBlock.numOutlinePoints):
        outlinePointsSize = 4*4
        outlinePoints = struct.unpack('ffff',wdfFileData[currentIndex:currentIndex+(outlinePointsSize)])
        currentIndex+=outlinePointsSize
        curvedBlock.OutlinePoints[pointsIndex, 0:4] = outlinePoints[0:4]
        pointsIndex+=1

    
    curvedBlock.Outline2Triangles[0,0:3] = curvedBlock.OutlinePoints[0,0:3]
    curvedBlock.Outline2Triangles[1,0:3] = curvedBlock.OutlinePoints[1,0:3]
    curvedBlock.Outline2Triangles[2,0:3] = curvedBlock.OutlinePoints[3,0:3] 
    curvedBlock.Outline2Triangles[3,0:3] = curvedBlock.OutlinePoints[2,0:3] 
    curvedBlock.Outline2Triangles[4,0:3] = curvedBlock.OutlinePoints[0,0:3]


    longSize = 4
    curvedBlock.TextureBlockIdUint32 = struct.unpack('L',wdfFileData[currentIndex:currentIndex+(longSize)])[0] 
    currentIndex+=longSize
    curvedBlock.LightBlockTextureIndexBlockIdUint32 = struct.unpack('L',wdfFileData[currentIndex:currentIndex+(longSize)])[0] 
    currentIndex+=longSize
    curvedBlock.LightBlockTextureSubblockIndexUint32 = struct.unpack('L',wdfFileData[currentIndex:currentIndex+(longSize)])[0] 
    currentIndex+=longSize
    curvedBlock.TerminatorUint32 = struct.unpack('L',wdfFileData[currentIndex:currentIndex+(longSize)])[0] 
    currentIndex+=longSize
    return (curvedBlock.blockSizeBytes, curvedBlock)


def ReadRedBlock(wdfFileData, currentIndex):
    #print(f"============== Red Block ================== {currentIndex}")
    return (32*4, None)

def ReadOrangeBlock(wdfFileData, currentIndex):
    offset=22
    #print(f"============== Orange Block ===============++=== {currentIndex}")
    #print(f"Type: {wdfFileData[0]}  magic number: {IsCheckValue(wdfFileData, currentIndex, 12,0xE4078678)}")

    return (offset*4, None)

def LoadSSXWdf(fileName, convertedFilesDir, writeCurvedPatchesToObjFile, writeCurvedPatchesToCsvFile, writeCurvedPatchesOutlinesToObjFile):

    # this code finds the different blocks in the map by looking for certain markers in the data to guess the block.

    print(f"=============== Loading Wdf file: {fileName} ==================")
    wdfFileFileandPath = f"{convertedFilesDir}data\\models\\{fileName}.wdf"
    wdfFileData = Path(wdfFileFileandPath).read_bytes()   
    
    FilesToClose = []


    # for expermenting, get a 3d plot in python, but very slow for entire map
    showCurvedPatchBlocksOn3dPlot = False
    # for expermenting, get a 3d plot in python, but very slow for entire map
    showCurvedPatchOutlineOn3dPlot  = False

    # experimental , some other numbers are the patch outlines

    if(writeCurvedPatchesOutlinesToObjFile):
        curvedOutlinesDir = '.\\output_files\\SSX\\curved patch outlines\\'
        Path(curvedOutlinesDir).mkdir(parents=True, exist_ok=True)
        fileCurvedPatchOutlinesObj = open(f'{curvedOutlinesDir}{fileName}_curvedpatch_outlines.obj', 'w') 
        FilesToClose.append(fileCurvedPatchOutlinesObj)
    else:
        fileCurvedPatchOutlinesObj = None

    # experimental, green blocks are objects in the map, like buildings
    showGreenBlocks = False
    addGreenBlocksToObjFile = False
    writeGreenBlocksToCSVFile = True
    if (writeGreenBlocksToCSVFile):
        csvFileDir = '.\\output_files\\SSX\\csv files\\'
        Path(csvFileDir).mkdir(parents=True, exist_ok=True)        
        fileGreenOut = open(f'{csvFileDir}{fileName}_green.csv', 'w') 
        FilesToClose.append(fileGreenOut)
    else:
        fileGreenOut = None

    # output to csv file for loading into excel etc for analysis
    if(writeCurvedPatchesToCsvFile):
        curvedPatchCsvDir = '.\\output_files\\SSX\\csv files\\'
        Path(curvedPatchCsvDir).mkdir(parents=True, exist_ok=True)     
        fileCurvedPatchCsvOut = open(f'{curvedPatchCsvDir}{fileName}_curvedpatch.csv', 'w')      
        FilesToClose.append(fileCurvedPatchCsvOut)
    else:
        fileCurvedPatchCsvOut = None

    # output to obj file for loading into blender
    if writeCurvedPatchesToObjFile:
        curvedPatchDir = '.\\output_files\\SSX\\curved patch beizer\\'
        Path(curvedPatchDir).mkdir(parents=True, exist_ok=True) 
        fileCurvedPatchObj = open(f'{curvedPatchDir}{fileName}_curvedpatch.obj', 'w')  
        FilesToClose.append(fileCurvedPatchObj)
    else:
        fileCurvedPatchObj = None


    wdfFileDataLength = len(wdfFileData)
    print(f"wdf File Length : {wdfFileDataLength}")
    index = 0
    numBlueBlocks = 0
    numGreenBlocks = 0
    greenBlocksList = []

    numCurvedPatchBlocks = 0
    curvedPatchList = []
    # curved block filter (for loading small sections and testing)
    useCurvedBlockFilter = False
    firstCurvedBlockFilter = 1
    lastCurvedBlockFilter = 100
    
    
    numOrangeBlocks = 0
    numRedBlocks = 0
    
    fig = plt.figure()
    ax = Axes3D(fig)
    
    wasOrange=False
    


    while index < wdfFileDataLength: #TODO or equal?
        foundBlockCount = 0
        foundBlueBlock = IsBlueBlock(wdfFileData, index, wdfFileDataLength)
        if (foundBlueBlock):
            foundBlockCount+=1
            numBlueBlocks+=1

        foundGreenBlock = IsGreenBlock(wdfFileData, index, wdfFileDataLength)
        if (foundGreenBlock):
            foundBlockCount+=1
            numGreenBlocks+=1

        foundCurvedPatchBlock = IsCurvedPatchBlock(wdfFileData, index, wdfFileDataLength)
        if (foundCurvedPatchBlock):
            foundBlockCount+=1
            numCurvedPatchBlocks+=1

        foundRedBlock = IsRedBlock(wdfFileData, index, wdfFileDataLength)
        if (foundRedBlock):
            foundBlockCount+=1
            numRedBlocks+=1

        foundOrangeBlock = IsOrangeBlock(wdfFileData, index, wdfFileDataLength)
        if (foundOrangeBlock):
            foundBlockCount+=1
            wasOrange=True
            numOrangeBlocks+=1

        if (foundBlockCount==1):
            if (foundBlueBlock):
                (blockSize, blueBlock) = ReadBlueBlock(wdfFileData, index) 
                index += blockSize
                wasOrange=False

            if (foundGreenBlock):
                (blockSize, greenBlock) = ReadGreenBlock(wdfFileData, index, numGreenBlocks, fileGreenOut) 
                index += blockSize
                wasOrange=False
                firstGreenBlock = 1
                lastGreenblock = 500000
                if (showGreenBlocks and numGreenBlocks>=firstGreenBlock and numGreenBlocks<=lastGreenblock):
                        # draw the outline
                        ax.plot3D(greenBlock[:, 0], greenBlock[:,  1], greenBlock[:,  2])
                        greenBlocksList.append(greenBlock)
                if (numGreenBlocks==lastGreenblock):
                    break

            if (foundCurvedPatchBlock):
                (blockSize, curvedBlock) = ReadCurvedPatchBlock(wdfFileData, index) 
                #print(f"Yellow Block Index: {numCurvedPatchBlocks}")
                if (useCurvedBlockFilter== False or (useCurvedBlockFilter== True and numCurvedPatchBlocks>=firstCurvedBlockFilter and numCurvedPatchBlocks<=lastCurvedBlockFilter)):
                    curvedPatchList.append(curvedBlock)           
                if (useCurvedBlockFilter== True and numCurvedPatchBlocks==lastCurvedBlockFilter):
                    # finish early if using filter 
                    break
                

                index += blockSize
                wasOrange=False
            if (foundRedBlock):
                (blockSize, redBlock) = ReadRedBlock(wdfFileData, index) 
                index += blockSize
                wasOrange=False            
            if (foundOrangeBlock):
                (blockSize, orangeBlock) = ReadOrangeBlock(wdfFileData, index) 
                index += blockSize
            percentProgress= index/wdfFileDataLength*100.0
            percentProgressInt = int(percentProgress*100)
            if percentProgressInt% 1000==0 and percentProgress > 5.0:
                print(f"Percent Progress: {percentProgress:.1f}")
        else:
            #  when orange finishes, need to pad it
            if (wasOrange):
                #try to pad and start again
                wasOrange=False
                padLength = 16
                padBytes = padLength - (index % padLength)
                if (padBytes==padLength):
                    padBytes=0
                index+=padBytes
                #break
            else:
                print(f"ERROR UNFINISHED at index: {index}")
                break
    print(f"Number of blocks: Blue {numBlueBlocks} Green: {numGreenBlocks} Yellow: {numCurvedPatchBlocks} Orange: {numOrangeBlocks} Red: {numRedBlocks} percent: {index/wdfFileDataLength*100.0}")
    
    if fileCurvedPatchCsvOut is not None:
        curvedBlock = SSXCurvedPatchBlock()
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




    objVertexIndex = 1
    for curveRead in curvedPatchList:
        if (showCurvedPatchOutlineOn3dPlot):
            ax.plot3D(curveRead.Outline2Triangles[:, 0], curveRead.Outline2Triangles[:,  1], curveRead.Outline2Triangles[:,  2])
            #ax.scatter3D(curveRead.Outline2Triangles[:, 0], curveRead.Outline2Triangles[:,  1], curveRead.Outline2Triangles[:,  2])
        if (fileCurvedPatchOutlinesObj is not None):
            for vertex in range(4):
                fileCurvedPatchOutlinesObj.write(f"v {curveRead.Outline2Triangles[vertex,0]/scaleFactor}  {curveRead.Outline2Triangles[vertex,1]/scaleFactor}  {curveRead.Outline2Triangles[vertex,2]/scaleFactor}  1 \n")
            fileCurvedPatchOutlinesObj.write(f"f {objVertexIndex} {objVertexIndex+1} {objVertexIndex+2} {objVertexIndex+3} \n")
            objVertexIndex+=4


    if (addGreenBlocksToObjFile):
        # adds the green blocks to the curved patch obj file to see where they appear
        if (fileCurvedPatchObj is not None):
            for greenBlk in greenBlocksList:
                for vertex in range(3):
                    fileCurvedPatchObj.write(f"v {greenBlk[vertex,0]/scaleFactor}  {greenBlk[vertex,1]/scaleFactor}  {greenBlk[vertex,2]/scaleFactor}  1 \n")
                fileCurvedPatchObj.write(f"f {objVertexIndex} {objVertexIndex+1} {objVertexIndex+2}  \n")
                objVertexIndex+=3

    for fileHandle in FilesToClose:
        fileHandle.close()

    if (showCurvedPatchBlocksOn3dPlot or showCurvedPatchOutlineOn3dPlot):
        plt.show() 
    


if __name__ == "__main__":
    #testing
    
    # control files what you want written
    writeCurvedPatchesToObjFile = True
    writeCurvedPatchesToCsvFile = True
    writeCurvedPatchesOutlinesToObjFile = True

    convertedFilesDir = '.\\output_files\\SSX\\dvdmodelfiles\\'

    LoadSSXWdf("aloha_ice_jam", convertedFilesDir, writeCurvedPatchesToObjFile, writeCurvedPatchesToCsvFile, writeCurvedPatchesOutlinesToObjFile) 
    # LoadSSXWdf("elysium_alps", writeCurvedPatchesToObjFile, writeCurvedPatchesToCsvFile, writeCurvedPatchesOutlinesToObjFile)
    # LoadSSXWdf("merquery_city" , writeCurvedPatchesToObjFile, writeCurvedPatchesToCsvFile, writeCurvedPatchesOutlinesToObjFile)
    # LoadSSXWdf("mesablanca", writeCurvedPatchesToObjFile, writeCurvedPatchesToCsvFile, writeCurvedPatchesOutlinesToObjFile)
    # LoadSSXWdf("pipedream", writeCurvedPatchesToObjFile, writeCurvedPatchesToCsvFile, writeCurvedPatchesOutlinesToObjFile)
    # LoadSSXWdf("snowdream", writeCurvedPatchesToObjFile, writeCurvedPatchesToCsvFile, writeCurvedPatchesOutlinesToObjFile)
    # LoadSSXWdf("tokyo_megaplex", writeCurvedPatchesToObjFile, writeCurvedPatchesToCsvFile, writeCurvedPatchesOutlinesToObjFile)
    # LoadSSXWdf("untracked", writeCurvedPatchesToObjFile, writeCurvedPatchesToCsvFile, writeCurvedPatchesOutlinesToObjFile)
    # LoadSSXWdf("warmup", writeCurvedPatchesToObjFile, writeCurvedPatchesToCsvFile, writeCurvedPatchesOutlinesToObjFile)
