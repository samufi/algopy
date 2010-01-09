import numpy
from numpy.testing import *
from prettyplotting import *
from algopy.utp.utpm import *

# STEP 0: setting parameters and general problem definition
############################################################

# Np = number of parameters p
# Nq = number of control variables q
# Nm = number of measurements
# P  = number of vectorized operations at once (SPMD)

D,Nq,Np,Nm = 2,1,2,10
P = Np
q = UTPM(numpy.zeros((D,P,Nq)))
q0 = 1.
q.data[0,:,0] = q0
p = UTPM(numpy.zeros((D,P,Np)))
p0 = numpy.random.rand(Np)
p.data[0,0,:] = p0
p.data[0,1,:] = p0
p.data[1,:,:] = numpy.eye(P)

B = UTPM(numpy.zeros((D,P,Nm, Np)))
B0 = numpy.random.rand(Nm,Np)
B.data[0,0] = B0
B.data[0,1] = B0


# STEP 1: compute push forward
############################################################

G = UTPM.dot(B, p)
F  = G * q[0]
J = F.FtoJT().T

Q,R = UTPM.qr(J)
Id = numpy.eye(Np)
Rinv = UTPM.solve(R,Id)
C2 = UTPM.dot(Rinv,Rinv.T)

E = UTPM.dot(J.T,J)
C = UTPM.inv(E)

print C - C2

l,U = UTPM.eigh(C)
arg = UTPM.argmax(l)

# check correctness of the push forward
tmp1 = q0**-2* numpy.linalg.inv(numpy.dot(B0.T,B0))
l0, U0 = numpy.linalg.eigh( tmp1 )

assert_array_almost_equal( J.data[0,0], B0)
assert_array_almost_equal( C.data[0,0], tmp1)
assert_array_almost_equal(l.data[0,0], l0)
assert_array_almost_equal(U.data[0,0], U0)



# STEP 2: compute pullback
############################################################

lbar = UTPM(numpy.zeros(l.data.shape))
lbar.data[0,0, arg] = 1.
Ubar = UTPM(numpy.zeros(U.data.shape))

Cbar = UTPM.eigh_pullback(lbar, Ubar, C, l, U)

# # Qbar = UTPM(numpy.zeros(Q.data.shape))
# # Jbar = UTPM.qr_pullback(Qbar, Rbar, J, Q, R)

# print Cbar

Ebar = UTPM.inv_pullback(Cbar, E, C)
JTbar, Jbar = UTPM.dot_pullback(Ebar, J.T, J, E)

Jbar += JTbar.T

Fbar = Jbar.T.JTtoF()
qbars = UTPM.dot(G.T,Fbar)

# accumulate over the different directions
qbar = UTPM(numpy.zeros((D,1)))
qbar.data[:,0] = qbars.data[:,0] + qbars.data[:,1]

#############################################
# compare with analytical solution
#############################################
c = numpy.max(numpy.linalg.eig( numpy.linalg.inv(numpy.dot(B0.T, B0)))[0])
dPhidq = - 2* c * q0**-3

assert_almost_equal( dPhidq, qbar.data[1,0])

print 'symbolical - UTPM pullback = %e'%( numpy.abs(dPhidq - qbar.data[1,0]))










