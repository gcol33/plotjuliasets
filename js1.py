import numpy as np
from numpy import pi
import sympy as sp

# Definition of a function that returns meshgrids X, Y, Z read to use with contourfplot 
# to plot Julia sets for the vectorized Newton iteration z->f(z) that solves 
# the equation z^n-1 for a user input exponent n
# note: roots are identified by their angles

def JS_grids(n,tol,maxit,Nx=100,Ny=100,xlims=np.array([-2,2]),ylims=np.array([-2,2])):
    # n = exponent of z^n-1=0 
    # tol = tolerance criterium to decide if the Newton iteration has converged
    # maxit = maximal number of iterations
    # xlims/ylims = an array that contain minimal x/y coordinates

    # we use symbolic calculations to find F and the Jacobian
    x = sp.Symbol("x",real = True)
    y = sp.Symbol("y",real = True)

    # expand (x+Iy)^3 and return real and imaginary part and create
    # symbolic functions
    F1 = sp.utilities.lambdify( (x,y), sp.re(sp.expand((x+sp.I*y)**n)-1))
    F2 = sp.utilities.lambdify( (x,y), sp.im(sp.expand((x+sp.I*y)**n)-1))

    # compute symbolically components of Jacobian and create symbolic
    # functions
    DF11 =sp.utilities.lambdify( (x,y),  sp.diff(F1(x,y),x))
    DF12 =sp.utilities.lambdify( (x,y),  sp.diff(F1(x,y),y))
    DF21 =sp.utilities.lambdify( (x,y),  sp.diff(F2(x,y),x))
    DF22 =sp.utilities.lambdify( (x,y),  sp.diff(F2(x,y),y))

    # create inline (lambda) definitions
    F = lambda x,y: np.array([F1(x,y),F2(x,y)]) 
    detDF = lambda x,y: DF11(x,y)*DF22(x,y) - DF21(x,y)*DF12(x,y) 

    # set x and y imits for the axis. x is the real plane, y the complex plane
    xmin = float(xlims[0])
    xmax = float(xlims[1])
    ymin = float(ylims[0])
    ymax = float(ylims[1])


    # mesh 
    X,Y = np.ogrid[xmin:xmax:Nx*1j, ymin:ymax:Ny*1j]

    # vectorized Newton iteration with vectorized termination criterium
    # maximal number of iterations is set by the variable maxit
    X1 = X
    Y1 = Y
    for i in np.r_[0:maxit]:
        X0 = X1
        Y0 = Y1
        X1 = X0 - 1./detDF(X0,Y0)*DF22(X0,Y0)*F1(X0,Y0) + 1./detDF(X0,Y0)*DF12(X0,Y0)*F2(X0,Y0)  
        Y1 = Y0 + 1./detDF(X0,Y0)*DF21(X0,Y0)*F1(X0,Y0) - 1./detDF(X0,Y0)*DF11(X0,Y0)*F2(X0,Y0)

        if np.max(((X1-X0)**2+(Y1-Y0)**2)/(X1**2+Y1**2))<tol:
            break


    # create X,Y,Z read to use with contourf 
    Xm,Ym = np.mgrid[xmin:xmax:Nx*1j, ymin:ymax:Ny*1j]
    Z = np.angle(X1+Y1*1j) 
    levels = np.linspace(0+pi/n,2*pi+pi/n,n*2)

    return Xm, Ym, Z, levels, i





