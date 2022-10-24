import filehelpers
from pathlib import Path

def ReadPackFile(sourceData, filesize):
    # files in SSX are compressed
    unpack = filehelpers.Unpacker(0, sourceData)
    # big endian for some reason
    packCodeHiByte = unpack.ReadByte()
    packCode = ((packCodeHiByte&0xfe)*256)+unpack.ReadByte()
    if (packCode != 0x10fb):
        print(f"Error in unpack, pack code not correct: 0x{packCode:04x}")
        return None
    expandedFilelengthToRead = unpack.BigEndianReadUint24()
    if (packCodeHiByte & 0x01):
        # align if necessary
        unpack.ReadByte()
        unpack.ReadByte()
        unpack.ReadByte()
    expandedData = bytearray()


    targetOffset = 0
    pack_byte = 0
    while(unpack.GetCurrentIndex()<filesize):
        pack_byte = unpack.ReadByte()
        if  pack_byte >= 0xfc:
            break
        if (not (pack_byte & 0x80)):
            lengthToRead = pack_byte & 0x03
            aByte = unpack.ReadByte()
            # copy short section
            while (lengthToRead>0):
                unpackByte = unpack.ReadByte()
                expandedData.append(unpackByte)
                targetOffset+=1
                lengthToRead-=1
            # copy again section already copied (uncompress)
            lengthToRead = ((pack_byte & 0x1c)>>2) + 3
            offset = ((pack_byte >> 5)<<8) + aByte + 1
            copyIndex = targetOffset - offset
            while (lengthToRead>0):
                expandedData.append(expandedData[copyIndex])
                copyIndex+=1
                targetOffset+=1
                lengthToRead-=1            
        elif(not (pack_byte & 0x40)):
            aByte = unpack.ReadByte()
            bByte = unpack.ReadByte() 
            lengthToRead = (aByte >> 6) & 0x03
            # copy short section
            while (lengthToRead>0):
                unpackByte = unpack.ReadByte()
                expandedData.append(unpackByte)
                targetOffset+=1
                lengthToRead-=1
            # copy again section already copied (uncompress)
            lengthToRead = (pack_byte & 0x3f)+4
            offset = (aByte & 0x3f)*256 + bByte + 1
            copyIndex = targetOffset - offset
            while (lengthToRead>0):
                expandedData.append(expandedData[copyIndex])
                copyIndex+=1
                targetOffset+=1
                lengthToRead-=1            
        elif(not (pack_byte & 0x20)):
            aByte = unpack.ReadByte()
            bByte = unpack.ReadByte() 
            cByte = unpack.ReadByte() 
            lengthToRead = (pack_byte & 0x03)
            # copy short section
            while (lengthToRead>0):
                unpackByte = unpack.ReadByte()
                expandedData.append(unpackByte)
                targetOffset+=1
                lengthToRead-=1
            # copy again section already copied (uncompress)
            lengthToRead = ((pack_byte >> 2)&0x03)*256+cByte+5;
            offset = ((pack_byte & 0x10)<<0x0c) + 256*aByte + bByte + 1;
            copyIndex = targetOffset - offset
            while (lengthToRead>0):
                expandedData.append(expandedData[copyIndex])
                copyIndex+=1
                targetOffset+=1
                lengthToRead-=1
        else:
            lengthToRead = ((pack_byte & 0x1f)*4)+4
            # copy short section
            while (lengthToRead>0):
                unpackByte = unpack.ReadByte()
                expandedData.append(unpackByte)
                targetOffset+=1
                lengthToRead-=1
    if (unpack.GetCurrentIndex() < filesize and targetOffset < expandedFilelengthToRead):

        lengthToRead = pack_byte & 0x03
        while (lengthToRead>0):
            unpackByte = unpack.ReadByte()
            expandedData.append(unpackByte)
            targetOffset+=1
            lengthToRead-=1
    # check output size
    if (len(expandedData) != expandedFilelengthToRead):
        print(f"file expand error!!! Expected lengthToRead: {expandedFilelengthToRead} actual lengthToRead {len(expandedData)}")
    return expandedData

class bigFileFileDetail:
    def __init__(self):
        self.fileOffset = 0
        self.fileSize = 0
        self.fileName = ""



def ConvertSSXTrickyBigFileToSeparateFiles(bigFileName, outputDirectory):
    sourceData = Path(bigFileName).read_bytes()   
    unpack = filehelpers.Unpacker(0, sourceData)
    # Big files are big endian
    idCode1 = unpack.ReadByte()
    idCode2 = unpack.ReadByte()
    if(not (idCode1 == 0xc0 and idCode2 == 0xfb)):
        print(f"Error in reading SSX Tricky Big file, id not correct: 0x{idCode1:02x}{idCode2:02x}") 
        return None

    tableSize = unpack.BigEndianReadUint16()
    numFiles = unpack.BigEndianReadUint16()
    print(f"Big file tablesize: 0x{tableSize:04x} size: 0x{numFiles:04x}")
    filelist = []
    for index in range (numFiles):

        fileDetails = bigFileFileDetail()
        fileDetails.fileOffset = unpack.BigEndianReadUint24()
        fileDetails.fileSize = unpack.BigEndianReadUint24()
        while(True):
            letter = unpack.ReadByte()
            if (letter == 0):
                break
            fileDetails.fileName += chr(letter)
        filelist.append(fileDetails)
    for convertFileDetail in filelist:
        print(f"File offset: 0x{convertFileDetail.fileOffset:06x} size: 0x{convertFileDetail.fileSize:06x} name: {convertFileDetail.fileName}")
        outputData = ReadPackFile(sourceData[convertFileDetail.fileOffset:(convertFileDetail.fileOffset + convertFileDetail.fileSize)], convertFileDetail.fileSize)
        if (outputData is not None):        
            outputFilename = f'{outputDirectory}{convertFileDetail.fileName}'
            output_file = Path(outputFilename)
            output_file.parent.mkdir(exist_ok=True, parents=True)
            fileOut = open(outputFilename, 'wb')      
            if (fileOut==None):
                print("Error opening output file: {outputFilename}")  
            else:
                
                fileOut.write(outputData) 
                fileOut.close()
                print("File wrote successfully")

def ConvertSSXBigFileToSeparateFiles(bigFileName, outputDirectory):
    sourceData = Path(bigFileName).read_bytes()   
    unpack = filehelpers.Unpacker(0, sourceData)
    # Big files are big endian
    idString = ""
    idString += chr(unpack.ReadByte())
    idString += chr(unpack.ReadByte())
    idString += chr(unpack.ReadByte())
    idString += chr(unpack.ReadByte())
    if(not (idString == "BIGF")):
        print(f"Error in reading SSX Big file, id not correct: {idString}") 
        return None
    dummy = unpack.BigEndianReadUint32()
    numFiles = unpack.BigEndianReadUint32()
    offsetX = unpack.BigEndianReadUint32()
    print(f"Big file numberfiles: 0x{numFiles:04x} offsetX: 0x{offsetX:04x}")
    filelist = []
    for index in range (numFiles):

        fileDetails = bigFileFileDetail()
        fileDetails.fileOffset = unpack.BigEndianReadUint32()
        fileDetails.fileSize = unpack.BigEndianReadUint32()
        while(True):
            letter = unpack.ReadByte()
            if (letter == 0):
                break
            fileDetails.fileName += chr(letter)
        filelist.append(fileDetails)
    for convertFileDetail in filelist:
        print(f"File offset: 0x{convertFileDetail.fileOffset:06x} size: 0x{convertFileDetail.fileSize:06x} name: {convertFileDetail.fileName}")
        outputData = ReadPackFile(sourceData[convertFileDetail.fileOffset:(convertFileDetail.fileOffset + convertFileDetail.fileSize)], convertFileDetail.fileSize)
        if (outputData is not None):        
            outputFilename = f'{outputDirectory}{convertFileDetail.fileName}'
            output_file = Path(outputFilename)
            output_file.parent.mkdir(exist_ok=True, parents=True)
            fileOut = open(outputFilename, 'wb')      
            if (fileOut==None):
                print("Error opening output file: {outputFilename}")  
            else:
                
                fileOut.write(outputData) 
                fileOut.close()
                print("File wrote successfully")

if __name__ == "__main__":
    # tests
    testUnpack =  False
    if (testUnpack): 
        unconvertedFileData = Path(f'.\\testdata\\ssxtrickybig\\alaskaunconverted.pbd').read_bytes()  
        convertedFileData = Path(f'.\\testdata\\ssxtrickybig\\alaskaconverted.pbd').read_bytes()  
        unpackedData = ReadPackFile(unconvertedFileData, len(unconvertedFileData))
        for index in range (len(convertedFileData)):
            if (convertedFileData[index] != unpackedData[index]):
                print(f"Failed")
                break

        fileConvertedOut = open(f'.\\testdata\\ssxtrickybig\\alaskaconvertedtest.pbd', 'wb') 
        fileConvertedOut.write(convertedFileData)
        fileConvertedOut.close()
    testSSXTrickyBigFile = False
    if(testSSXTrickyBigFile):
        ConvertSSXTrickyBigFileToSeparateFiles(f'.\\testdata\\ssxtrickybig\\ALASKA.BIG', f'.\\testdata\\ssxtrickybig\\bigfileout\\')
    testSSXBigFile = True
    if(testSSXBigFile):
        ConvertSSXBigFileToSeparateFiles(f'.\\testdata\\ssxbig\\ALOHA.BIG', f'.\\testdata\\ssxbig\\bigfileout\\')
