

import cv2 as cv2
import sys
import numpy as np
import time
from pathlib import Path

def ShowImageAndWaitForKey(imgShow, displayName, showImage):
    if(showImage):
        cv2.imshow(displayName, imgShow)
        k = cv2.waitKey(0)

def LoadImageFromDir(directory, fileName, loadAlpha = False):
    if (loadAlpha):
        img = cv2.imread(directory+fileName, cv2.IMREAD_UNCHANGED)
    else:
        img = cv2.imread(directory+fileName)
    if img is None:
        sys.exit("Could not read the image.")

    return img

def SaveImageToDir(directory, fileName, image):
    fileToWrite = directory+fileName
    Path(directory).mkdir(parents=True, exist_ok=True)
    cv2.imwrite(fileToWrite, image)

def SpecialRounding(floatToRound):
    # for SSX Tricky everything can be rounded to 1 dp except -0.35, makes the patches align with the texture boundaries
    if round(floatToRound,2)==-0.35:
        return -0.35
    return round(floatToRound,1)

def LookupBoundsType(textureBounds):
    # I categorise the texture UV into different types to adjust accordingly
    xySubset = textureBounds[0:4,0:2]
    if np.array_equal(xySubset, np.array([[0,0],[-1,0],[0,-2],[-1,-2]])): return 1
    if np.array_equal(xySubset, np.array([[0,0],[-1,0],[0,-1],[-1,-1]])): return 2
    if np.array_equal(xySubset, np.array([[0,0],[-1,0],[0,1],[-1,1]])): return 3
    if np.array_equal(xySubset, np.array([[0,0],[0.5,0],[0,-0.5],[0.5,-0.5]])): return 4
    if np.array_equal(xySubset, np.array([[0,0],[1,0],[0,-6],[1,-6]])): return 5
    if np.array_equal(xySubset, np.array([[0,0],[1,0],[0,-2],[1,-2]])): return 6
    if np.array_equal(xySubset, np.array([[0,-1],[1,-1],[0,-2],[1,-2]])): return 7
    if np.array_equal(xySubset, np.array([[0,0],[1,0],[0,-1],[1,-1]])): return 8
    if np.array_equal(xySubset, np.array([[0,0],[1,0],[0,-0.7],[1,-0.7]])): return 9
    if np.array_equal(xySubset, np.array([[0,0],[1,0],[0,-0.35],[1,-0.35]])): return 10
    if np.array_equal(xySubset, np.array([[0,0],[1,0],[0,1],[1,1]])): return 11
    if np.array_equal(xySubset, np.array([[0,0],[2,0],[0,-3],[2,-3]])): return 12
    if np.array_equal(xySubset, np.array([[0,0],[2,0],[0,-2],[2,-2]])): return 13
    if np.array_equal(xySubset, np.array([[0,0],[2,0],[0,-1],[2,-1]])): return 14
    if np.array_equal(xySubset, np.array([[0,0],[3,0],[0,-6],[3,-6]])): return 15
    if np.array_equal(xySubset, np.array([[0,0],[3,0],[0,-3],[3,-3]])): return 16
    if np.array_equal(xySubset, np.array([[0,0],[3,0],[0,-1],[3,-1]])): return 17
    if np.array_equal(xySubset, np.array([[0,0],[4,0],[0,-1],[4,-1]])): return 18
    if np.array_equal(xySubset, np.array([[0,0],[4,0],[0,-0.5],[4,-0.5]])): return 19
    if np.array_equal(xySubset, np.array([[0,0],[7,0],[0,-1],[7,-1]])): return 20
    if np.array_equal(xySubset, np.array([[0,0],[16,0],[0,-15],[16,-15]])): return 21
    if np.array_equal(xySubset, np.array([[0,0],[30,0],[0,-1],[30,-1]])): return 22
    if np.array_equal(xySubset, np.array([[1,-1],[0,-1],[1,0],[0,0]])): return 23
    if np.array_equal(xySubset, np.array([[1,-1],[0,-1],[1,-2],[0,-2]])): return 24
    if np.array_equal(xySubset, np.array([[1,0],[1,-1],[0,0],[0,-1]])): return 25
    if np.array_equal(xySubset, np.array([[0,-1],[0,0],[1,-1],[1,0]])): return 26
    if np.array_equal(xySubset, np.array([[1,0],[1,-1],[2,0],[2,-1]])): return 27

    assert False


def convertUVBoundsToPixels(textureBounds, imgh, imgw):
# textureBounds is 
#    ((texture1x, texture1y)
#    (texture2x, texture2y),
#    (texture3x, texture3y),
#    (texture4x, texture4y))

    textureBounds[0][0] = SpecialRounding(textureBounds[0][0]) 
    textureBounds[1][0] = SpecialRounding(textureBounds[1][0])
    textureBounds[2][0] = SpecialRounding(textureBounds[2][0])
    textureBounds[3][0] = SpecialRounding(textureBounds[3][0])
    textureBounds[0][1] = SpecialRounding(textureBounds[0][1])
    textureBounds[1][1] = SpecialRounding(textureBounds[1][1])
    textureBounds[2][1] = SpecialRounding(textureBounds[2][1])
    textureBounds[3][1] = SpecialRounding(textureBounds[3][1])

    typeBounds = LookupBoundsType(textureBounds)

    if (textureBounds[0][1] == -1.0 and 
        textureBounds[1][1] == -1.0 and
        textureBounds[2][1] == -2.0 and
        textureBounds[3][1] == -2.0):
        # fix up to make less combinations to adjust as y -1 to -2 is the same as 0 to -1
        textureBounds[0][1] = 0.0
        textureBounds[1][1] = 0.0
        textureBounds[2][1] = -1.0
        textureBounds[3][1] = -1.0

    if (textureBounds[0][0] == 1.0 and 
        textureBounds[1][0] == 1.0 and
        textureBounds[2][0] == 2.0 and
        textureBounds[3][0] == 2.0):
        # fix up to make less combinations to adjust as x 1 to 2 to 0 to 1
        textureBounds[0][0] = 0.0
        textureBounds[1][0] = 0.0
        textureBounds[2][0] = 1.0
        textureBounds[3][0] = 1.0


    texture1xp = int(round(imgw *textureBounds[0][0], 0)) 
    texture2xp = int(round(imgw *textureBounds[1][0], 0)) 
    texture3xp = int(round(imgw *textureBounds[2][0], 0)) 
    texture4xp = int(round(imgw *textureBounds[3][0], 0)) 
    texture1yp = int(round(imgh *textureBounds[0][1], 0)) 
    texture2yp = int(round(imgh *textureBounds[1][1], 0)) 
    texture3yp = int(round(imgh *textureBounds[2][1], 0)) 
    texture4yp = int(round(imgh *textureBounds[3][1], 0)) 
    result = ((texture1xp, texture1yp),
        (texture2xp, texture2yp),
        (texture3xp, texture3yp),
        (texture4xp, texture4yp))
    return result, typeBounds

def CalculateInclusiveDistance(point1, point2):
    if (point2>point1 ):
        result = point2-point1 
    else:
        result = point1-point2 
    return result

def ResizeTextureAccordingToMappingUVBounds(imgTexture,
    textureBounds):
# textureBounds is 
#    ((texture1x, texture1y)
#    (texture2x, texture2y),
#    (texture3x, texture3y),
#    (texture4x, texture4y))
    imgh, imgw, _ = imgTexture.shape
 
    # this function is doing my own texture mapping using UV co-ordinate the same as blender would. The reason I do it is so
    # that i can apply the light map to the texture and save together, and wavefront obj does not support a separate lightmap
    # the lightmap is applied after the texture mapping transformation included duplication

    textureBoundsPixels, boundsType = convertUVBoundsToPixels(textureBounds, imgh, imgw)
    texture1xp = textureBoundsPixels[0][0] 
    texture2xp = textureBoundsPixels[1][0] 
    texture3xp = textureBoundsPixels[2][0] 
    texture4xp = textureBoundsPixels[3][0] 
    texture1yp = textureBoundsPixels[0][1] 
    texture2yp = textureBoundsPixels[1][1] 
    texture3yp = textureBoundsPixels[2][1] 
    texture4yp = textureBoundsPixels[3][1] 

    # 
    #  For all the SSX tricky curved patch data point 4 is covered by the other points
    # new texture width is always 1 to 2
    # new texture height is always 1 to 3
 
    if (texture1xp == texture2xp):
        texture1xpTo2xpDirectionYDirection = True 
    else:
        texture1xpTo2xpDirectionYDirection = False 
 
    if (texture1xp == texture3xp):
        texture1xpTo3xpDirectionYDirection = True 
    else:
        texture1xpTo3xpDirectionYDirection = False 
    assert(texture1xpTo2xpDirectionYDirection == True or texture1xpTo3xpDirectionYDirection ==  True)
    # calculate final size
    if (texture1xpTo2xpDirectionYDirection):

        newImageWidth = CalculateInclusiveDistance(texture1yp, texture2yp)
        startDestXPos = texture1yp
        endDestXPos = texture2yp
    else:

        newImageWidth = CalculateInclusiveDistance(texture1xp, texture2xp)
        startDestXPos = texture1xp
        endDestXPos = texture2xp

    if (texture1xpTo3xpDirectionYDirection):
        newImageHeight = CalculateInclusiveDistance(texture1yp, texture3yp)
        startDestYPos = texture1yp
        endDestYPos = texture3yp

    else:
        newImageHeight =CalculateInclusiveDistance(texture1xp,texture3xp)
        startDestYPos = texture1xp
        endDestYPos = texture3xp

    
    #textureMappingDirection = ((texture1xpTo2xpDirectionYDirection, texture1xpTo3xpDirectionYDirection), (DestXIncrement,DestYIncrement), (mirroredX, mirroredY))
    # I was using textureMappingDirection to also flip the lightmap but then I found that the lightmap is not ever flipped, 
    # it is applied as is with no transformation other than scaling to the texture after the texture is flipped (if it is)
    #return (newImageTexture, textureMappingDirection)

    flipVertical = 0
    # flip the texture - not sure why, seems to work, matches sign of texture co-ordinate maybe
    imgTexture = cv2.flip(imgTexture, flipVertical)

    #start = time.time() 
    rotateImage = False
    if (boundsType<=22):
        # these types image runs 1xp to 2xp, and 1yp to 3yp
        assert texture1xp == 0
        assert texture3xp == 0
        assert texture1yp == 0
        assert texture2yp == 0
        assert texture2xp == texture4xp
        assert texture3yp == texture4yp
        if (texture2xp < 0.0):
            # flip image in x
            doFlipXAxis = True
        else:
            doFlipXAxis = False
        if (texture3yp < 0.0):
            # flip image in Y 
            doFlipYAxis = True
        else:
            doFlipYAxis = False

        # tile the image to a whole number of tiles
        xDirectionNumTiles =  int(abs(round(textureBounds[1][0],1)))
        yDirectionNumTiles =  int(abs(round(textureBounds[2][1],1)))

    elif  (boundsType==23):
        doFlipXAxis = True
        doFlipYAxis = False
        xDirectionNumTiles =  1
        yDirectionNumTiles =  1
    elif  (boundsType==24):
        doFlipXAxis = True
        doFlipYAxis = True
        xDirectionNumTiles =  1
        yDirectionNumTiles =  1
    elif  (boundsType==25):
        rotateImage = True
        doFlipXAxis = True
        doFlipYAxis = True
        xDirectionNumTiles =  1
        yDirectionNumTiles =  1
    elif  (boundsType==26):
        rotateImage = True
        doFlipXAxis = True
        doFlipYAxis = False
        xDirectionNumTiles =  1
        yDirectionNumTiles =  1
    elif  (boundsType==27):
        rotateImage = True
        doFlipXAxis = False
        doFlipYAxis = False
        xDirectionNumTiles =  1
        yDirectionNumTiles =  1

    if (rotateImage):
        # rotate because the co-ordinates go x1 to x3 instead of x1 to x2
        rotateDirection = cv2.ROTATE_90_COUNTERCLOCKWISE
        imgTexture = cv2.rotate(  imgTexture, rotateDirection)

    if (doFlipXAxis == True):
        # flip image in X 
        flipHorizontal = 1
        imgTexture = cv2.flip(imgTexture, flipHorizontal)
    if (doFlipYAxis == True):
        # flip image in y 
        flipVertical = 0
        imgTexture = cv2.flip(imgTexture, flipVertical)
    if xDirectionNumTiles < 1: 
        xDirectionNumTiles = 1
    if yDirectionNumTiles < 1: 
        yDirectionNumTiles = 1

    # tile the image, a mapped texture gets repeated if the co-ordinate is greater than 1 or -1
    tileImg = np.tile(imgTexture,(yDirectionNumTiles, xDirectionNumTiles,1))
    #extract part of tiled image (as the texture co-ordinates are fractions sometimes)
    extractStartXpos = abs(startDestXPos)
    extractEndXpos = abs(endDestXPos)
    if (extractEndXpos<extractStartXpos):
        temp = extractEndXpos
        extractEndXpos = extractStartXpos
        extractStartXpos = temp
    extractStartYpos = abs(startDestYPos)
    extractEndYpos = abs(endDestYPos)
    if (extractEndYpos<extractStartYpos):
        temp = extractEndYpos
        extractEndYpos = extractStartYpos
        extractStartYpos = temp
    assert (extractEndYpos-extractStartYpos) == newImageHeight
    assert (extractEndXpos-extractStartXpos) == newImageWidth
    finalImage = tileImg[extractStartYpos:extractEndYpos, extractStartXpos:extractEndXpos, 0:3 ]
    # Test
    # if xDirectionNumTiles > 5 or yDirectionNumTiles > 6:
    #     #ShowImageAndWaitForKey(tileImg, "tile Img", True)   
    #     ShowImageAndWaitForKey(finalImage, "tile Img", True)   
    # cv2.putText(finalImage, #target image
    #             f"{boundsType}", #text
    #             (24, 24), #top-left position
    #             cv2.FONT_HERSHEY_DUPLEX,
    #             1.0,
    #             (255, 255, 0),  2) #font color
    #PrintElapsedTime(start) 


    return finalImage, boundsType

def ResizeLightmapToTexture(imgLightSegment,imgh, imgw): 
     
    # I have to rotate all lightmaps by 90 degrees counterclockwise, no idea why
    rotate1to2Direction = cv2.ROTATE_90_COUNTERCLOCKWISE
    imgLightSegment = cv2.rotate(  imgLightSegment, rotate1to2Direction)
    
    # resize to fix texture lightmap is mapped onto
    imgLightSegment = cv2.resize(imgLightSegment,(imgw, imgh))
    return imgLightSegment

def ExtractLightSegmentAndAlphaMap(imgLight, lightBounds):
    # lightBounds = light_x, light_y,  light_w, light_h,
    # we don't use the whole light map texture. we just use the part specified by the curved patch information
    # this is usually an 8x8 part of the whole bitmap
    # light_x,light_y, light_w,light_h are uv co-ordinates into the bitmap, so multiple by the width
    # so if light_x = 0.6875 and the width is 128 then the x in the light map is 88

    (light_x, light_y,  light_w, light_h) = lightBounds
    lightHeight, lightWidth, _ = imgLight.shape
    slice_x1 = int(light_x*lightWidth)
    slice_y1 = int(light_y*lightHeight)
    slice_x2 = int(slice_x1 + (light_w*lightWidth))
    slice_y2 = int(slice_y1 + (light_h*lightHeight))
    
    # how to crop opencv: cropped = img[start_row:end_row, start_col:end_col]  so y pair is first, then x pair
    
    # take  the rbg part for the light texture to subtract
    imgLightSegment = imgLight[slice_y1:slice_y2, slice_x1:slice_x2,0:3 ] 
    
    # take the alpha channel and turn into a matrix to mutliple by the image, fill in each R,G,B with alpha value repeated
    imgLightAlphaSegment = np.empty_like(imgLightSegment)
    
    imgLightAlphaSegment[:,:,0] = imgLight[slice_y1:slice_y2, slice_x1:slice_x2,3 ] 
    imgLightAlphaSegment[:,:,1] = imgLight[slice_y1:slice_y2, slice_x1:slice_x2,3 ] 
    imgLightAlphaSegment[:,:,2] = imgLight[slice_y1:slice_y2, slice_x1:slice_x2,3 ] 

    return (imgLightSegment, imgLightAlphaSegment)

def PrintElapsedTime(start):
    end = time.time()
    print(f"Time elasped (ms): {(end - start)*1000.0}")

def CreateLightmapAdjustedTexture(dirNameTextures, dirNameLightMaps, dirNameLightMapsComputed, applyLightMap, patchIndex, lightId,  textureId,  
    textureBounds, lightBounds ):
 

    # lightBounds = light_x, light_y,  light_w, light_h,
    showImages = False
    textureFile = f"{textureId:04d}.png"
    lightFile = f"{lightId:04d}.png"
    imgTexture = LoadImageFromDir(dirNameTextures,textureFile)
 
 
    # do my own texture mapping using UV co-ordinate the same as blender would. The reason I do it is so
    # that i can apply the light map to the texture and save together, and wavefront obj does not support a separate lightmap
    # the lightmap is applied after the texture mapping transformation included duplication   
    imgTexture, boundsType = ResizeTextureAccordingToMappingUVBounds(imgTexture, textureBounds)


 
    textureHeight, textureWidth, textureChannels = imgTexture.shape
    assert textureChannels == 3

    ShowImageAndWaitForKey(imgTexture, textureFile, showImages)
    if applyLightMap:
        loadAlpha = True
        imgLightRGBA = LoadImageFromDir(dirNameLightMaps,lightFile, loadAlpha)

        (imgLightSegment, imgLightAlphaSegment)= ExtractLightSegmentAndAlphaMap(imgLightRGBA, lightBounds)
        
        # I am manually applying the lightmap to the texture because Wavefront .obj does not support baked lightmaps in a separate texture file
        # so  I manually resize the texture correctly then apply the lightmap
        imgLightSegment = ResizeLightmapToTexture(imgLightSegment, textureHeight, textureWidth)

        ShowImageAndWaitForKey(imgLightSegment, lightFile, showImages)

        # in SSX and Tricky the lightmap uses a performance feature of the PS2, which is:
        # (Cd - Cs) * As
        # Cd is destination texture
        # Cs is the lighting converted to a form to subtract from the texture
        # As is the lighting converted to a form to multiply by the texture
        # so instead of just texture x lighting (which I think is normal and supported by things like unity and blender) 
        # there is a convoluted system because of ps2 hardware optimisations.
        ImgSubtracted = cv2.subtract(imgTexture, imgLightSegment)
        
        ShowImageAndWaitForKey(ImgSubtracted, lightFile, showImages)

        imgLightAlphaSegment = ResizeLightmapToTexture(imgLightAlphaSegment, textureHeight, textureWidth)

        # change to range 0 to 1.0
        imgLightAlphaSegmenNormalised = imgLightAlphaSegment / 255.0
        ShowImageAndWaitForKey(imgLightAlphaSegmenNormalised, lightFile, showImages)

        # change to range 0 to 1.0
        imgNormalised = ImgSubtracted / 255.0
        ShowImageAndWaitForKey(imgNormalised, lightFile, showImages)

        ImgMultipliedNormalised = cv2.multiply(imgNormalised, imgLightAlphaSegmenNormalised)
        ShowImageAndWaitForKey(ImgMultipliedNormalised, lightFile, showImages)
        ImgMultipliedNormalised = ImgMultipliedNormalised * 255

        finalImage = ImgMultipliedNormalised

    else:
        finalImage = imgTexture

    saveFileName = f"LitTexture_{patchIndex:04d}.png"
    SaveImageToDir(dirNameLightMapsComputed, saveFileName, finalImage)
    debugPatches =False
    if debugPatches:
        fileCurvedPatchCsvDir = '.\\output_files\\SSX Tricky\\csv files\\'
        Path(fileCurvedPatchCsvDir).mkdir(parents=True, exist_ok=True)
        # dump all to the same file for testing
        fileCurvedPatchTestingCsvOut = open(f'{fileCurvedPatchCsvDir}X_Test_curvedpatch_types.csv', 'a')   
        fileCurvedPatchTestingCsvOut.write(f"{dirNameTextures},{patchIndex}, {boundsType}\n")
        fileCurvedPatchTestingCsvOut.close()



def TestTile():
    imgTexture = LoadImageFromDir('.\\output_files\\SSX Tricky\\dvdmodelfiles\\data\\models\\ssh_files\\elysium_ssh\\','0051.png')   
    tile = np.tile(imgTexture,(2,5,1))
    ShowImageAndWaitForKey(tile, "tile test", True)

def TestFlip():
    imgTexture = LoadImageFromDir('.\\output_files\\SSX Tricky\\dvdmodelfiles\\data\\models\\ssh_files\\elysium_ssh\\','0015.png')   
    ShowImageAndWaitForKey(imgTexture, "normal", True)
    flipVertical = 0
    imgVert = cv2.flip(imgTexture, flipVertical)
    ShowImageAndWaitForKey(imgVert, "flip vertical", True)
    flipHori = 1
    imgHori = cv2.flip(imgTexture, flipHori)
    ShowImageAndWaitForKey(imgHori, "flip horizontal", True)

if __name__ == "__main__":
    #testing
    #TestTile()
    #TestFlip()

    testHeight = 128
    testWidth = 128
    textureBounds1 = np.array([[0.00799998641014099,-0.00799998641014099],[0.991999983787536,-0.00799998641014099],[0.00799998641014099,-0.991999983787536],[0.991999983787536,-0.991999983787536]])
    textureBounds1Pixels, _ = convertUVBoundsToPixels(textureBounds1, testHeight, testWidth)
    assert textureBounds1Pixels[0][0] == 0
    assert textureBounds1Pixels[0][1] == 0
    assert textureBounds1Pixels[1][0] == 128
    assert textureBounds1Pixels[1][1] == 0
    assert textureBounds1Pixels[2][0] == 0
    assert textureBounds1Pixels[2][1] == -128
    assert textureBounds1Pixels[3][0] == 128
    assert textureBounds1Pixels[3][1] == -128

    textureBounds1 = np.array([[0,-1.00399994850158],[1,-1.00399994850158],[0,-1.99599993228912],[1,-1.99599993228912]])
    textureBounds1Pixels, _ = convertUVBoundsToPixels(textureBounds1, testHeight, testWidth)
    # testadjust -1 to -2 to 0 to -1
    assert textureBounds1Pixels[0][0] == 0
    assert textureBounds1Pixels[0][1] == 0
    assert textureBounds1Pixels[1][0] == 128
    assert textureBounds1Pixels[1][1] == 0
    assert textureBounds1Pixels[2][0] == 0
    assert textureBounds1Pixels[2][1] == -128
    assert textureBounds1Pixels[3][0] == 128
    assert textureBounds1Pixels[3][1] == -128

    textureBounds1 = np.array([[1.0080018043518,-0.00800177454948425],[1.00799822807312,-0.992001771926879],[1.99200177192687,-0.00800523161888122],[1.99199831485748,-0.992005228996276]])
    textureBounds1Pixels, _ = convertUVBoundsToPixels(textureBounds1, testHeight, testWidth)
    # testadjust x 1 to 2 to 0 to 1
    assert textureBounds1Pixels[0][0] == 0
    assert textureBounds1Pixels[0][1] == 0
    assert textureBounds1Pixels[1][0] == 0
    assert textureBounds1Pixels[1][1] == -128
    assert textureBounds1Pixels[2][0] == 128
    assert textureBounds1Pixels[2][1] == 0
    assert textureBounds1Pixels[3][0] == 128
    assert textureBounds1Pixels[3][1] == -128



    textureBounds1 = np.array([[-0.008000016,-0.007999986],[-0.992000103,-0.007999986],[-0.008000016,-2.007999897],[-0.992000103,-2.007999897]])
    textureBounds1Pixels, _ = convertUVBoundsToPixels(textureBounds1, testHeight, testWidth)

    assert textureBounds1Pixels[0][0] == 0
    assert textureBounds1Pixels[0][1] == 0
    assert textureBounds1Pixels[1][0] == -128
    assert textureBounds1Pixels[1][1] == 0
    assert textureBounds1Pixels[2][0] == 0
    assert textureBounds1Pixels[2][1] == -256
    assert textureBounds1Pixels[3][0] == -128
    assert textureBounds1Pixels[3][1] == -256

    textureBounds1 = np.array([[0,0],[1.0,0],[0.0,-0.348],[1.0,-0.348]])
    textureBounds1Pixels, _ = convertUVBoundsToPixels(textureBounds1, testHeight, testWidth)
    assert textureBounds1Pixels[0][0] == 0
    assert textureBounds1Pixels[0][1] == 0
    assert textureBounds1Pixels[1][0] == 128
    assert textureBounds1Pixels[1][1] == 0
    assert textureBounds1Pixels[2][0] == 0
    assert textureBounds1Pixels[2][1] == -45
    assert textureBounds1Pixels[3][0] == 128
    assert textureBounds1Pixels[3][1] == -45

    assert CalculateInclusiveDistance(0, 128) == 128
    assert CalculateInclusiveDistance(127, 1) == 126
    assert CalculateInclusiveDistance(-1, -129) == 128
    assert CalculateInclusiveDistance(-128, 0) == 128
    assert CalculateInclusiveDistance(-127, 1) == 128
    assert CalculateInclusiveDistance(127, -1) == 128


    applyLightMap = True


    dirNameTexturesTest = '.\\output_files\\SSX Tricky\\dvdmodelfiles\\data\\models\\ssh_files\\gari_ssh\\'
    dirNameLightMapsTest = '.\\output_files\\SSX Tricky\\dvdmodelfiles\\data\\models\\ssh_files\\gari_L_ssh\\'
    dirNameLightMapsComputedTest = '.\\output_files\\SSX Tricky\\curved patch beizer\\Tricky_gari_curvedpatch_textures\\'


    CreateLightmapAdjustedTexture(dirNameTexturesTest, dirNameLightMapsTest, dirNameLightMapsComputedTest, applyLightMap,28,0,12,np.array([[-4.29153442382812E-06,-0.999995708465576],[4.29153442382812E-06,4.29153442382812E-06],[0.999995708465576,-1.00000429153442],[1.00000429153442,-4.29153442382812E-06]]),(0.6875,0.0625,0.0625,0.0625))

