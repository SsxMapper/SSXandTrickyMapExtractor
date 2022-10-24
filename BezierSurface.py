import numpy as np
import matplotlib.pyplot as plt
#from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D

def Combination(n, i):
    numerator = np.math.factorial(n)
    denomenator = np.math.factorial(i) * np.math.factorial(n - i)
    return numerator / denomenator

def BernsteinBasis(n, i, t):
    return Combination(n, i) * np.math.pow(t, i) * np.math.pow(1.0 - t, n - i)

def BezierCurve(T, Points):
    countPoints = np.size(Points, 0)
    n = countPoints - 1
    dim = np.size(Points, 1)
    rVal = []
    for t in T:
        point = np.zeros(dim)
        for i in range(0, countPoints):
            point += Points[i] * BernsteinBasis(n, i, t)
        rVal.append(point)
    return np.array(rVal)

def BezierSurface(Points, UV):
    pointsU = np.size(Points, 0)
    pointsV = np.size(Points, 1)
    dimension = np.size(Points, 2)

    n = pointsU - 1
    m = pointsV - 1

    countU = np.size(UV, 0)
    countV = np.size(UV, 1)

    Out = np.zeros([countU, countV, dimension])

    for u in range(countU):
        for v in range(countV):
            value = np.zeros(dimension)
            uv = UV[u, v, :]
            for i in range(pointsU):
                for j in range(pointsV):
                    value += Points[i, j, :] * BernsteinBasis(n, i, uv[0]) * BernsteinBasis(m, j, uv[1])
            Out[u, v, :] = value
    return Out

def PlotBezier(Points, showControlPoints):

    U = np.linspace(0., 1., 8)
    V = np.linspace(0., 1., 8)

    UV = np.transpose(np.asarray(np.meshgrid(U, V, sparse=False)))

    BezierSrf = BezierSurface(Points, UV)
    print(f" Bezier suface \n {BezierSrf}")
    fig = plt.figure()
    ax = Axes3D(fig)
    # show control points
    if (showControlPoints):
        ax.plot_wireframe(Points[:, :, 0], Points[:, :, 1], Points[:, :, 2])
    # show surface
    ax.plot_surface(BezierSrf[:, :, 0], BezierSrf[:, :, 1], BezierSrf[:, :, 2])
    plt.show()    

def PlotBoundBox(Points, Points2):
    fig = plt.figure()
    ax = Axes3D(fig)
    # show control points
    print(Points[:, 0])
    print(Points[:, 1])
    print(Points[:, 2])
    
    ax#.plot_wireframe(Points[:, 0], Points[:,  1], Points[:,  2])
    ax.plot_trisurf(Points[:, 0], Points[:,  1], Points[:,  2])
    ax.plot_trisurf(Points2[:, 0], Points2[:,  1], Points2[:,  2])
    plt.show() 


def BezierSurfaceFromPremultipledMatrix(resultX, resultY, resultZ, UV):

    countU = np.size(UV, 0)
    countV = np.size(UV, 1)

    Out = np.zeros([countU, countV, 3])

    for u in range(countU):
        for v in range(countV):
            uv = UV[u, v, :]
            uValue = uv[0]
            vValue = uv[1]
            uMatrix =  np.asarray([uValue*uValue*uValue,uValue*uValue, uValue,1])
            vMatrix =  np.asarray([[vValue*vValue*vValue],
                [vValue*vValue], 
                [vValue],
                [1]]
                )

            resultIntermediate = np.matmul(uMatrix,resultX)
            finalValueX = np.matmul(resultIntermediate,vMatrix)

            resultIntermediate = np.matmul(uMatrix,resultY)
            finalValueY = np.matmul(resultIntermediate,vMatrix)

            resultIntermediate = np.matmul(uMatrix,resultZ)
            finalValueZ = np.matmul(resultIntermediate,vMatrix)

            Out[u, v, :] = np.array([finalValueX[0],finalValueY[0],finalValueZ[0]])
    return Out


def BezierSurfaceUsingMatrixMethod(Points, UV):

    BezierMatrix = np.asarray([
        [-1, 3,	 -3, 1],
        [3,  -6, 3,	 0],
        [-3, 3,	 0,	 0],
        [1,	 0,	 0,	 0],
   ])

    resultIntermediate = np.matmul(BezierMatrix, Points[:, :, 0])
    resultX = np.matmul(resultIntermediate, BezierMatrix)
    resultIntermediate = np.matmul(BezierMatrix, Points[:, :, 1])
    resultY = np.matmul(resultIntermediate, BezierMatrix)
    resultIntermediate = np.matmul(BezierMatrix, Points[:, :, 2])
    resultZ = np.matmul(resultIntermediate, BezierMatrix)

    return BezierSurfaceFromPremultipledMatrix(resultX, resultY, resultZ, UV)

def CalcBezierUsingMatrixMethod(Points, isPremultiplied, numSegments):
    # Points is 4x4x(x,y,z) 
    U = np.linspace(0., 1., numSegments)
    V = np.linspace(0., 1., numSegments)

    UV = np.transpose(np.asarray(np.meshgrid(U, V, sparse=False)))

    if (isPremultiplied):
        resultX = Points[:, :, 0]
        resultY = Points[:, :, 1]
        resultZ = Points[:, :, 2]       
        BezierSrf = BezierSurfaceFromPremultipledMatrix(resultX, resultY, resultZ, UV)
    else:
        BezierSrf = BezierSurfaceUsingMatrixMethod(Points, UV)
    return BezierSrf

def PlotBezierUsingMatrixMethod(Points, showControlPoints, isPremultiplied):
    
    BezierSrf = CalcBezierUsingMatrixMethod(Points, isPremultiplied, 8)
    
    fig = plt.figure()
    subplot = fig.add_subplot(projection='3d')
    # show control points
    if (showControlPoints):
        subplot.plot_wireframe(Points[:, :, 0], Points[:, :, 1], Points[:, :, 2])
    # show surface
    subplot.plot_wireframe(BezierSrf[:, :, 0], BezierSrf[:, :, 1], BezierSrf[:, :, 2])
    #ax.plot_surface(BezierSrf[:, :, 0], BezierSrf[:, :, 1], BezierSrf[:, :, 2])
    plt.show()    


def ReversePrecomputedBezier(PreComputedPoints):
    #  reverse a pre computed bezier back to a non pre-computed form
    BezierMatrix = np.asarray([
        [-1, 3,	 -3, 1],
        [3,  -6, 3,	 0],
        [-3, 3,	 0,	 0],
        [1,	 0,	 0,	 0],
   ])
    InverseBezierMatrix = np.linalg.inv(BezierMatrix)
    # pre compute is BezierMatrix * controlPoints * BezierMatrix
    # general solution is (https://math.stackexchange.com/questions/1681654/axb-c-find-the-x-matrice):
    # AXB=C (C = Points, A and B = BezierMatrix)
    # A−1×(AXB)=A−1×C
    # (A−1A)(XB)=A−1C
    # I(XB)=A−1C
    # XB=A−1C
    # but A and B are the Bezier matrix
    # control points x Bezier matrix () = Inverse Beizer X pre comptued points
    controlPointsByBezierMaxtrixX = np.matmul(InverseBezierMatrix, PreComputedPoints[:, :, 0])
    controlPointsByBezierMaxtrixY = np.matmul(InverseBezierMatrix, PreComputedPoints[:, :, 1])
    controlPointsByBezierMaxtrixZ = np.matmul(InverseBezierMatrix, PreComputedPoints[:, :, 2])
    # now solve equation
    # XA=B ⟹
    # XAA−1=BA−1 ⟹
    # X=BA−1
    # so control points = last result X Inverse Beizer
    controlPointsX = np.matmul(controlPointsByBezierMaxtrixX,InverseBezierMatrix)    
    controlPointsY = np.matmul(controlPointsByBezierMaxtrixY,InverseBezierMatrix)    
    controlPointsZ = np.matmul(controlPointsByBezierMaxtrixZ,InverseBezierMatrix)    


    controlPoints = np.empty_like(PreComputedPoints)
    controlPoints[:, :, 0] = controlPointsX
    controlPoints[:, :, 1] = controlPointsY
    controlPoints[:, :, 2] = controlPointsZ
    return controlPoints


def TryReversePrecomputedBezier(PreComputedPoints):
    # try to reverse a pre computed bezier back to a non pre-computed form
    controlPoints = ReversePrecomputedBezier(PreComputedPoints)
    
    #print(controlPoints)
    PlotBezierUsingMatrixMethod(controlPoints, False, False) 
    # compare to original        
    PlotBezierUsingMatrixMethod(PreComputedPoints, False, True)   

if __name__ == "__main__":

    #testing


    PointsBounds = np.asarray(
    

        [
        [-29981.29883,	-29593.90039,	-32033.30078],
        [-29981.29883,	-29593.90039,	-32033.30078],
        [-29979.09766,	-29594.69922,	-31883.59961],
        [-20338.5,	-31197.10156,	-34574.5],
        [-20337.90039,	-31196.79883,	-34425],
        [-29981.29883,	-31197.10156,	-34574.5],
        [-20337.90039,	-29512.60156,	-31873.09961]])
    print(PointsBounds.shape)
    PointsBounds2 = np.asarray([
        [-20338.5,	-31197.10156,	-34574.5],
        [-20338.5,	-31197.10156,	-34574.5],
        [-20337.90039,	-31196.79883,	-34425],
        [-10571,	-29757.50195,	-37249.69922],
        [-10573.5,	-29758.30078,	-37099.10156],
        [-20339.40039,	-31231.40039,	-37249.69922],
        [-10571,	-29676.80078,	-34415.39844]
            ])

    #PlotBoundBox(PointsBounds, PointsBounds2)

    PointsOld = np.asarray([
        [[0, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0]],
        [[0, 1, 0], [1, 1, 1], [2, 1, 1], [3, 1, 0]],
        [[0, 2, 0], [1, 2, 1], [2, 2, 1], [3, 2, 0]],
        [[0, 3, 0], [1, 3, 0], [2, 3, 0], [3, 3, 0]],
    ])








    PointsTest1 = np.asarray([
        [[-1.5, 1.5, 0], [-0.5, 1.5, 0], [0.5, 1.5, 0], [1.5, 1.5, 0]],
        [[-1.5, 0.5, 0], [-0.5, 0.5, 0.5], [0.5, 0.5, 0.5], [1.5, 0.5, 0]],
        [[-1.5, -0.5, 0], [-0.5, -0.5, 0.5], [0.5, -0.5, 0.5], [1.5, -0.5, 0]],
        [[-1.5, -1.5, 0], [-0.5, -1.5, 0], [0.5, -1.5, 0], [1.5, -1.5, 0]],
    ])

    PointsTest2 = np.asarray([
        [        [0.31,	0.65,	1],        [0.61,	0.65,	1],        [0.31,	0.35,	1],        [0.61,	0.35,	1]],
        [        [0.88501	,1.817322	,-1.998901],        [2.124023	,-10.523987	,6.280518 ],        [-6.619263	,12.011719	,-1.18103 ],        [-4.290771	,3.69873	,-289.306641  ] ],
        [        [-3.579712	  ,-1.528931	  ,     3.909302       ],        [8.953857	  ,23.442078	  ,     -9.887695      ],        [60.342407	  ,-88.220215	  ,  0.878906       ],        [-209.115601  ,-158.097839	  , 431.707764 ]        ],
        [[1.794434	,-1.789856	,-0.604248 ],        [-11.672974	,-6.317139	,0         ],        [-50.427246	,69.309998	,0.906372  ],        [215.707397	,152.398682	,11.096191 ]],
    ])
    print(PointsTest2.shape)
    #PointsTest = np.zeros((4,4,3))
    #PlotBezier(PointsTest1, False)
    #PlotBezierUsingMatrixMethod(PointsTest1, False, False)   
    BezierMatrix = np.asarray([
        [-1, 3,	 -3, 1],
        [3,  -6, 3,	 0],
        [-3, 3,	 0,	 0],
        [1,	 0,	 0,	 0],
   ])

    resultIntermediate = np.matmul(BezierMatrix, PointsTest1[:, :, 0])
    resultX = np.matmul(resultIntermediate, BezierMatrix)
    resultIntermediate = np.matmul(BezierMatrix, PointsTest1[:, :, 1])
    resultY = np.matmul(resultIntermediate, BezierMatrix)
    resultIntermediate = np.matmul(BezierMatrix, PointsTest1[:, :, 2])
    resultZ = np.matmul(resultIntermediate, BezierMatrix)
    PointsTest2 = np.empty_like(PointsTest1)
    PointsTest2[:,:,0] = resultX
    PointsTest2[:,:,1] = resultY
    PointsTest2[:,:,2] = resultZ    
    #PlotBezierUsingMatrixMethod(PointsTest2, False, True)
    TryReversePrecomputedBezier(PointsTest2)

    # sample pre-multipled texture
    PreMultipledTexture1 = np.asarray([

        [[0.000572205,0.389862,-0.895691,1],
        [-0.00143051,0.0160217,1.19934,1],
        [0.00114441,-0.608826,-0.302124,1],
        [-0.000286102,0.202179,0.00152588,1]],

        [[-0.000286102,-0.58136,0.888062,1],
        [0.000858307,-0.0274658,-0.892639,1],
        [-0.000858307,0.913239,0,1],
        [0.000286102,-0.304413,0,1]],

        [[-162.69,154.788,1469.71,1],
        [229.861,-693.883,-2669.4,1],
        [243.9,774.893,1008.9,1],
        [-789.9,495.602,-113.402,1]],

        [[-134.41,-521.997,-229.9,1],
        [244.56,1288.5,505.499,1],
        [-126.18,-708.298,464.099,1],
        [-1121.61,-13124.2,13043.2,1]],
    ])

    #PlotBezierUsingMatrixMethod(PreMultipledTexture1, False, True)

    PreMultipledTexture2 = np.asarray([

        [[-0.0058651,0.505829,0.315857,1],[0.005579,-0.613403,-0.334168,1],
        [0.000286102,0.00915527,0.315857,1],[0.00295639,-0.00305176,-0.102234,1]],
        [[0.00901222,-0.908661,-0.325012,1],[0,0.920105,0.0549316,1],
        [-0.00901222,-0.0137329,-0.0274658,1],[0.00300407,0.00457764,0.00457764,1]],
        [[-647.277,319.805,-323.991,1],[1287.4,-606.61,887.38,1],
        [-826.272,-24.2935,-1480.49,1],[-486.699,37.7976,185.999,1]],
        [[512.864,-841.399,94.101,1],[-1042.84,1894.8,-381.601,1],
        [700.101,-684,1944.3,1],[-634.917,-13162,12857.3,1]],


    ])
    #PlotBezierUsingMatrixMethod(PreMultipledTexture2, False, True)
    # sample  texture which is pre-computed
    PreMultipledTexture4 = np.asarray([

    [[-0.209426879882812,0.27008056640625,0],[1.31921768188476,-1.959228515625,0],[-1.70974731445312,1.98898315429687,0],[-2.53009796142578,5.328369140625,0]],
    [[2.0390510559082,1.80130004882812,0],[-17.4579620361328,-17.4476623535156,0],[20.518684387207,20.1461791992187,0],[42.7803039550781,45.5429077148437,0]],
    [[4.77046966552734,2.51998901367187,0],[-43.2912826538085,-21.9657897949218,0],[-116.81900024414,317.525482177734,0],[610.379760742187,-821.52099609375,0]],
    [[-6.70032501220703,-4.80117797851562,-0.01068115234375],[60.4505538940429,43.1121826171875,-39.6583557128906],[769.619750976562,824.279052734375,363.658905029296],[-2671.68994140625,-7847.2998046875,5502.0302734375]],
    ])

    #PlotBezierUsingMatrixMethod(PreMultipledTexture4, False, True)
    #TryReversePrecomputedBezier(PreMultipledTexture4)


