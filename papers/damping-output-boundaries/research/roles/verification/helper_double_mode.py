"""Independent, standard-library audit of two-mode damping formulas."""
from fractions import Fraction as Q
from itertools import product
from math import sqrt
import hashlib
from pathlib import Path

def coeff(w1,w2,o,r1,r2):
    d1,d2=w1*w1-o*o,w2*w2-o*o
    b1,b2=2*w1*o,2*w2*o
    return ((r1*d2+r2*d1)**2,(r1*b2+r2*b1)**2,
            d1*d1*d2*d2,d1*d1*b2*b2+d2*d2*b1*b1,b1*b1*b2*b2)

def F(c,x):
    a,b,c0,d,e=c
    return (a+b*x)/(c0+d*x+e*x*x)

count=0
max_identity_error=0.0
for w1,w2 in [(Q(1),Q(2)),(Q(1),Q(3)),(Q(2),Q(3))]:
    for o,r1,r2,(z0,z1) in product([Q(1,2),Q(1),Q(3,2),Q(2),Q(3)],range(-2,3),range(-2,3),[(Q(1,20),Q(2,25)),(Q(1,5),Q(2,5)),(Q(1),Q(2))]):
        if r1==r2==0: continue
        a,b,c,d,e=co=coeff(w1,w2,o,Q(r1),Q(r2))
        x0,x1=z0*z0,z1*z1
        assert a+b*x0>0 and e>0
        den=(c+d*x0+e*x0*x0)*(c+d*x1+e*x1*x1)
        s=b*c-a*d-a*e*(x0+x1)-b*e*x0*x1
        assert F(co,x1)-F(co,x0)==(x1-x0)*s/den
        xc=(b*c-a*d-a*e*x0)/(e*(a+b*x0))
        assert s==e*(a+b*x0)*(xc-x1)
        assert F(co,x1)/F(co,x0)<x1/x0
        # Independent direct complex transfer (not using the rational F formula).
        h=sum(complex(float(r))/complex(float(w*w-o*o),float(2*z* w*o)) for w,r in [(w1,Q(r1)),(w2,Q(r2))] for z in [z0])
        err=abs(abs(h)**2-float(F(co,x0)))/max(1.0,float(F(co,x0)))
        max_identity_error=max(max_identity_error,err)
        assert err<1e-12
        if b>0 and b*c>a*d:
            # Stable rationalization of manuscript (12).
            xp=float((b*c-a*d)/e)/(sqrt(float(a*a+(b/e)*(b*c-a*d)))+float(a))
            derivative=float(b*c-a*d)-2*float(a*e)*xp-float(b*e)*xp*xp
            assert abs(derivative)<1e-9*max(1.0,abs(float(b*c-a*d)))
        count+=1
print('exact two-mode cases:',count)
print('rational difference/crossing/strict-upper assertions: PASS')
print('max relative direct-complex F discrepancy:',format(max_identity_error,'.3e'))

# Positive residues, exact undamped antiresonance at Omega^2=2.
a,b,c,d,e=Q(0),Q(128),Q(4),Q(64),Q(256)
x0,x1=Q(1,400),Q(4,625)
print('same-sign antiresonance ratio (zeta 0.05 -> 0.08):',sqrt(float(F((a,b,c,d,e),x1)/F((a,b,c,d,e),x0))))
print('same-sign antiresonance x_peak:',sqrt(float(c/e)))

# Both effective residues vanish despite a nonzero measurement vector.
# M=I, K=diag(1,4), input=(1,0), output=(0,1).
print('nonzero measurement but unexcited output: residues=(0,0), H=0, ratio=undefined, x_cross=0/0')
print('script_sha256:',hashlib.sha256(Path(__file__).read_bytes()).hexdigest())

print('fixed-frequency model sharpness: w=(1,2), r=(1,-1), zeta=(0.05,0.08)')
for o in [10,100,1000,10000]:
    co=coeff(Q(1),Q(2),Q(o),Q(1),Q(-1))
    print('Omega=',o,'ratio=',sqrt(float(F(co,Q(4,625))/F(co,Q(1,400)))))
