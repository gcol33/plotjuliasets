# plotjuliasets

Description

The code runs with Python 2.x since its uses wxpython (not
yet officially ported to Python 3).
The code has been developed on Mac Os Sierra.

This code lets you plot Julia sets for the vectorial newton iteration that solves the equation z^n = 1 
for a user input number n. Each root is made a different color by identifying the different angles to 
where our points converged to. The code also lets you enter some custom iteration (but without a differential 
opeator like the one we need in the newton iteration) f(z) which is parsed by scipy and then transformed 
into a function with lambdify- to see where it converges if we apply it "infinitely many times" 
(in the code it applies it 30 times). You can change the real and imaginary range (default is 
(-2,2)x(-2,2)*i) and also the number of steps which I called precision. Finally you can update 
the graph after zooming in with the entered precision (the default is 100).

How to use:
- buttons:
    1. newton iteration
        this button lets you put in a number n for the equation z^n-1=0 that is then solved with a vectorized newton iteration. Each root is colored differently
    2. enter iteration
        this button lets you enter an iteration f(z) and plot the corresponding julia set. f cannot depend on any derivates. Any constants can 
        be entered as a+bi or a+bj or complex(a,b) or a or bi or bj.
    3. update
        updates the graph after you changed the precsion or if you zoomed in
    4. precision
        lets you input a number of points in the real and the imaginary direction you want to have in your grid
    5. range
        lets you select your range for the initial plot
- toolbar:
    the default matplotlib toolbar
- statusbar (bottom of the window):
    shows the current status
- menu:
    let's you save a picture quickly with Crtl+s as pic.png in the current folder


INSTALLATION NOTES

To install the code in your computer, you need first to install the anaconda
python (https://www.continuum.io/downloads).
You will have to use the Python 2.x distribution since the code
uses wxpython which is still not ported to Python 3.


Then clone the repository:
git clone https://github.com/gcol33/plotjuliasets.git

Build the conda package:
conda build plotjuliasets

And install it locally:

conda install --use-local sospex

At this point you can start the code everywhere by
typing:

plotjuliasets

since the executable is in the ~/anaconda/bin directory.
