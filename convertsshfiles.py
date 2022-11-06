# convert ssh files to png

import filehelpers
from pathlib import Path
import numpy as np
import cv2 as cv2

def ShowImageAndWaitForKey(imgShow, displayName, showImage):
    if(showImage):
        cv2.imshow(displayName, imgShow)
        k = cv2.waitKey(0)

def LoadPalette(unpackPalette: filehelpers.Unpacker):
    palette = np.empty((256,4),dtype='uint8')
    # see https://ssx.computernewb.com/wiki/Formats/Common:SSH
    entryType = unpackPalette.ReadByte()   
    sizePalette = unpackPalette.ReadUint24()
    widthPalette = unpackPalette.ReadUint16()
    HeightPalette = unpackPalette.ReadUint16()
    TotalPalette = unpackPalette.ReadUint16()
    Unknown1Palette = unpackPalette.ReadUint16()
    SwizzledPalette = unpackPalette.ReadUint16()
    Unknown2Palette = unpackPalette.ReadUint16()
    diagnostics = False
    if (diagnostics):
        print(f"Palette Info: {entryType=} {sizePalette=} {widthPalette=} {HeightPalette=} {TotalPalette=} {Unknown1Palette=} {SwizzledPalette=} {Unknown2Palette=}")
    # only support this:
    assert entryType == 33
    assert sizePalette == 1040
    assert widthPalette == 256
    assert HeightPalette == 1
    assert TotalPalette == 256
    for index in range (256):
        blue = unpackPalette.ReadByte()      
        green = unpackPalette.ReadByte()      
        red = unpackPalette.ReadByte()      
        alpha = unpackPalette.ReadByte()      
        assert alpha <= 128
        alpha = alpha*2-1
        palette[index,0] = blue
        palette[index,1] = green
        palette[index,2] = red
        palette[index,3] = alpha

    return palette

def LoadPaletteBitmap(palette, unpackBitmap: filehelpers.Unpacker, widthBitmap, heightBitmap):
    bitmap = np.empty((heightBitmap, widthBitmap, 4),dtype='uint8')  # opencv style rows, cols, BGRA
    for yIndex in range(heightBitmap):
        for xIndex in range(widthBitmap):
            data = unpackBitmap.ReadByte()  
            red = palette[data][0]
            green = palette[data][1]
            blue = palette[data][2]
            alpha = palette[data][3]

            bitmap[yIndex, xIndex,0] = blue
            bitmap[yIndex, xIndex,1] = green
            bitmap[yIndex, xIndex,2] = red
            bitmap[yIndex, xIndex,3] = alpha

    return bitmap

def LoadBitmap(unpackBitmap: filehelpers.Unpacker, widthBitmap, heightBitmap):
    bitmap = np.empty((heightBitmap, widthBitmap, 4),dtype='uint8')  # opencv style rows, cols, BGRA
    for yIndex in range(heightBitmap):
        for xIndex in range(widthBitmap):
            red = unpackBitmap.ReadByte()
            green = unpackBitmap.ReadByte()
            blue = unpackBitmap.ReadByte()
            alpha = unpackBitmap.ReadByte()

            bitmap[yIndex, xIndex,0] = blue
            bitmap[yIndex, xIndex,1] = green
            bitmap[yIndex, xIndex,2] = red
            bitmap[yIndex, xIndex,3] = alpha
 
    return bitmap

def SaveTexture(outputDirectory, saveFileName, sourceData, fileOffset):
    unpack = filehelpers.Unpacker(fileOffset, sourceData)


    bitmapType = unpack.ReadByte()
    if (bitmapType == 2 or bitmapType == 5):
        
        # load bitmap size - sometimes this is bigger than width * height!!
        bitmapSizeInBytes = unpack.ReadUint24()
        widthBitmap = unpack.ReadUint16()
        heightBitmap = unpack.ReadUint16()
        unknown1 = unpack.ReadUint32()
        assert unknown1 == 0
        unknown2 = unpack.ReadUint32()
        assert unknown2 == 0
        bitampFileOffset = fileOffset + 0x10
        unpackBitmap = filehelpers.Unpacker(bitampFileOffset, sourceData)
        if (bitmapType == 2):
            paletteFileOffset = fileOffset + bitmapSizeInBytes
            unpackPalette = filehelpers.Unpacker(paletteFileOffset, sourceData)
            palette = LoadPalette(unpackPalette)
            bitmap = LoadPaletteBitmap(palette, unpackBitmap, widthBitmap, heightBitmap)
        else:
            # type 5 RGBA 32 bit bitmap
            bitmap = LoadBitmap(unpackBitmap, widthBitmap, heightBitmap)
        outputFilename = f'{outputDirectory}{saveFileName}.png'
        output_file = Path(outputFilename)
        output_file.parent.mkdir(exist_ok=True, parents=True)   
        cv2.imwrite(outputFilename,bitmap)
        diagnostics = False
        if (diagnostics):
            print(f"Bitmap: {saveFileName} file wrote successfully")
        showImage = False
        ShowImageAndWaitForKey(bitmap,saveFileName, showImage)
    else:
        print(f"File: {saveFileName} type not supported {bitmapType}")
        assert False


def ConvertSSHFileToSeparateFiles(sshFileName, outputDirectory):
    sourceData = Path(sshFileName).read_bytes()   
    unpack = filehelpers.Unpacker(0, sourceData)

    idString = unpack.ReadMagicWord()
    if(not (idString == "SHPS")):
        print(f"Error in reading SSH file, id not correct: {idString}") 
        assert False
        return False
    fileSize = unpack.ReadUint32()
    numFiles = unpack.ReadUint32() # number of image files
    print(f"Ssh file number files: 0x{numFiles:04x} fileSize: 0x{fileSize:08x}")
    idGimex = unpack.ReadMagicWord() #Gimex Version/Creator Code
    if (not ((idGimex == "GIMX") or (idGimex == "G278") )):
        print(f"Error in reading SSH file, id Gimex not correct: {idGimex}") 
        return False


    for index in range (numFiles):
        sshFilename = ""
        sshFilename += chr(unpack.ReadByte())
        sshFilename += chr(unpack.ReadByte())
        sshFilename += chr(unpack.ReadByte())
        sshFilename += chr(unpack.ReadByte())
        fileOffset = unpack.ReadUint32()
        diagnostics = False
        if (diagnostics):
            print(f"File name: {sshFilename} offset: 0x{fileOffset:06x} ")
        SaveTexture(outputDirectory, sshFilename, sourceData, fileOffset)
    print(f"Number of bitmaps: {numFiles} wrote successfully")

    return True

if __name__ == "__main__":
    # tests
    modelsDir = ".\\output_files\\SSX Tricky\\dvdmodelfiles\\data\\models\\"
    fileName = "merquer"
    #ConvertSSHFileToSeparateFiles(f"{modelsDir}{fileName}.ssh", f"{modelsDir}ssh_files\\{fileName}_ssh\\")
    fileName = "merque"
    #ConvertSSHFileToSeparateFiles(f"{modelsDir}{fileName}_L.ssh", f"{modelsDir}ssh_files\\{fileName}_ssh_L\\")

    fileName = "elysium"
    ConvertSSHFileToSeparateFiles(f"{modelsDir}{fileName}.ssh", f"{modelsDir}ssh_files\\{fileName}_ssh\\")
    fileName = "elysiu"
    ConvertSSHFileToSeparateFiles(f"{modelsDir}{fileName}_L.ssh", f"{modelsDir}ssh_files\\{fileName}_ssh_L\\")
