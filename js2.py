import numpy as np
import sympy as sp


## juliafunc checks if an iteration diverges
## take a function f and applies it to z n times 
## => returns z if it is smaller than 4 or puts the value to inf 
def juliafunc(f,z,n):
    for i in xrange(n):
        z = f(z)
        if abs(z) > 4:
            return float("inf")
    return z


## JS_gridsui makes a grid a values ready to plot a julia set
## takes a function f, Number of Pixels in x and y direction Nx/Ny
## and ranges for x and y axes in the form of arrays 
## => returns X,Y,Z where X and Y are a grid between the x and I*y limits and Z
## equals to juliafunc of all those points in the complex plane
def JS_gridsui(f,Nx=100,Ny=100,xlims=np.array([-2.,2]),ylims=np.array([-2.,2])):
    
    # Dummy number k we use to iterate over a one dim Z array
    k=0
    # number of times we run the juliafunc, when n is too big will 
    # cause juliafunc to diverge beacuse of comma errors of float
    n=30

    # 1-dim array Z where we will save all the values we get from juliafunc
    Z = np.zeros(Nx*Ny)
    # makes a grid X,Y between x and y limits in the complex plane
    X,Y = np.ogrid[xlims[0]:xlims[1]:Nx*1j, ylims[0]:ylims[1]:Ny*1j]

    # Dummy array z we use to call juliafunc
    z = np.zeros(2)      

    # Iteration over X and Y
    for x in X[:,0]:
        for y in Y[0,:]:
            x0 = complex(x, y)
            z = juliafunc(f,x0,n)
            #If our call converges we set Z[k] to 2
            if abs(z) < 4:
                    Z[k]= 2.
            #If it doesn't we set Z[k] to 0
            else:
                Z[k] = 0.
            k += 1

    
    # Reshape Z 
    Z = Z.reshape(Nx,Ny)

    # Make a meshgrid of X and Y values
    Xm,Ym = np.mgrid[xlims[0]:xlims[1]:Nx*1j,ylims[0]:ylims[1]:Ny*1j] # create start value domain mesh for plotting
    
    # Return the meshgrid of X,Y and Z values ready to plot with contourf
    return Xm,Ym,Z

