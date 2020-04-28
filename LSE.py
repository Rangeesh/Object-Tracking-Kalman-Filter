# initial y - y_1
# Y at every instant - y
# initial x - x_1
# X at every instant - x

# A is summation of A
# B is summation of B
# AC is a summation of (AC)

# ---------------------------------------------------------------------------- #
#                                      LSE.py                                  #
# ---------------------------------------------------------------------------- #

import csv
import matplotlib.pyplot as plt
from math import sqrt
import numpy as np
import time

# ------------------------------ Importing Files ----------------------------- #

rdx = csv.reader(open("x2d_1.csv","r"),delimiter = ",")
X=[]
for r in rdx:
    X.append(float(r[0]))

rdy = csv.reader(open("y2d_1.csv","r"),delimiter = ",")
Y=[]
for r in rdy:
    Y.append(float(r[0]))

x_1 = X[0]
y_1 = Y[0]


A = 0
B = 0
C = 0
Bc = 0
Ab = 0
Ac = 0
C2 = 0
B2 = 0
g = 979.343


# print(len(X))

ran = len(X)



print(ran)
# time.sleep(2)

# -------------------- Computing the Closed Form Solution -------------------- #

for i in range(ran):
    A = A + (Y[i] - y_1)
    B = B - (X[i] - x_1)
    C = C + (g*(X[i]-x_1)**2)/2
    Bc = Bc  - (X[i] - x_1)*g/2.0*(X[i]-x_1)**2
    Ab = Ab - (Y[i] - y_1)*(X[i] - x_1)
    Ac = Ac + (Y[i] - y_1)*g/2.0*(X[i]-x_1)**2
    C2 = C2 + g/2.0*(X[i]-x_1)**2*g/2.0*(X[i]-x_1)**2
    B2 = B2 + (X[i] - x_1)*(X[i] - x_1)


D = -Ab/B2
E = -Bc/B2

a = B2*D**2 + Ab*D # This will turn out to be 0, which I noticed later
b = 2*B2*D*E+Ab*E+2*Ac+3*Bc*D
c = B2*E**2 + 2*C2 + 3*Bc*E
# x1 = (-b + sqrt(b**2 - 4*a*c))/(2*a)
# x2 = (-b - sqrt(b**2 - 4*a*c))/(2*a)

xwq = - c/b 

# X11 = sqrt(x1)
# X12 = -sqrt(x1)

# X21 = sqrt(x2)
# X22 = -sqrt(x2)

# xx = X22

# -------------------------------- X Velocity -------------------------------- #

xx = - sqrt(xwq)
print(xx)

# -------------------------------- Y Velocity -------------------------------- #

yy = D*xx + E/xx

print(yy)

# ----------------------------------- Plot ----------------------------------- #

tir = np.linspace(0,0.4,40)
xr = np.array([x_1 + xx*n for n in tir])
yr = np.array([y_1 + yy*n - 0.5*979.343*(n**2) for n in tir])
plt.scatter(xr,yr)


# ------------------------------ Saving CSV File ----------------------------- #

np.savetxt("xd_33.csv",xr,delimiter=",")
np.savetxt("yd_33.csv",yr,delimiter=",")


plt.show()  