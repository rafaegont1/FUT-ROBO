import numpy as np

def coef_calc(uv_points, xy_points):
    #Montando a matriz A:
    uvarray = np.array(uv_points)
    uvec = uvarray[:,0][:, np.newaxis]
    vvec = uvarray[:,1][:, np.newaxis]
    A = np.block([np.ones((len(uv_points),1)), uvarray, (uvec**2), (vvec**2)])

    #Montando as matrizes B:
    Bx = np.array(xy_points)[:,0][:, np.newaxis]
    By = np.array(xy_points)[:,1][:, np.newaxis]

    #Calculando a pseudo-inversa:
    A_ = np.linalg.inv(A.T@A)@A.T

    #Calculando os coeficientes:
    alpha = (A_@Bx).T
    beta = (A_@By).T

    return alpha[0], beta[0]

def uv_to_xy(uv, consts):
    coefs = np.vstack([consts[0], consts[1]])
    imag = np.hstack((np.ones(1), np.array(uv), np.array(uv[0]**2), np.array(uv[1]**2)))[:, np.newaxis]
    out = (coefs@imag).T
    return np.array(out[0].round(0), dtype=np.int_).tolist()
    

uv = [[322,246], [17,40], [614,55], [616,453], [10,447]]
xy = [[0,0], [-1190,800], [1190,800], [1190,-800], [-1190,-800]]

cte = coef_calc(uv, xy)

print(uv_to_xy((10,447), cte))