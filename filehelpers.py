import struct

class Unpacker:
    # all routines force little endian as PS2 file is little endian
    def __init__(self, startIndex, dataFile):
        self._index = startIndex
        self._dataFile = dataFile
    
    def GetCurrentIndex(self):
        return self._index

    def ReadByte(self):
        byteRead = struct.unpack('<B',self._dataFile[self._index:self._index+1])
        self._index+=1
        return byteRead[0]

    def ReadUint32(self):
        uint32Read = struct.unpack('<L',self._dataFile[self._index:self._index+4])
        self._index+=4
        return uint32Read[0]

    # unpacking files needs some big endian reading

    def BigEndianReadUint16(self):
        byte1 = self.ReadByte()
        byte2 = self.ReadByte()
        uint16 =  (byte1<< 8) + byte2
        return uint16

    def BigEndianReadUint24(self):
        byte1 = self.ReadByte()
        byte2 = self.ReadByte()
        byte3 = self.ReadByte()
        uint24 = (byte1 << 16) + (byte2 << 8) + byte3
        return uint24

    def BigEndianReadUint32(self):
        byte1 = self.ReadByte()
        byte2 = self.ReadByte()
        byte3 = self.ReadByte()
        byte4 = self.ReadByte()
        uint32 = (byte1 << 24) + (byte2 << 16) + (byte3 << 8) + byte4
        return uint32

if __name__ == "__main__":
    # tests
    testData = b'\x29\xbf\xd0'
    unpack = Unpacker(0, testData)
    readUint24BigEndian = unpack.BigEndianReadUint24()
    assert readUint24BigEndian == 2736080


