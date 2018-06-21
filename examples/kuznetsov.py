from pylab import *
from numpy import *

dt = 5.e-2
s0 = [1.0,1.0]
d = 4
p = 2
boundaries = ones(2*d)
boundaries[0] = -1.0
boundaries[1] = -1.0
boundaries[3] = -1.0
T = 6.0
n_poincare = int(ceil(T/dt))

def Step(u0,s,n):
    u = copy(u0)
    for i in arange(n):
        x = u[0]
        y = u[1]
        z = u[2]
        r2 = x**2.0 + y**2.0 + z**2.0	
        r = sqrt(r2)
        
        sigma = diff_rot_freq(u[3])
        a = rot_freq(u[3])		

        coeff1 = sigma*pi*0.5*(z*sqrt(2) + 1)
        coeff2 = s[0]*(1. - sigma*sigma - a*a)
        coeff3 = s[0]*a*a*(1.0 - r)		

        u[0] += dt*(-1.0*coeff1*y - 
                        coeff2*x*y*y + 
                        0.5*a*pi*z + coeff3*x)

        u[1] += dt*(coeff1*0.5*x + 
                        coeff2*y*x*x + 
                        coeff3*y)

        u[2] += dt*(-0.5*a*pi*x + coeff3*z)

        u[3] = (u[3] + dt)%T

	 

        
    return u


def convert_to_spherical(u):
    x = u[0]	
    y = u[1]	
    z = u[2]
    r = sqrt(x**2 + y**2 + z**2)
    theta = arccos(z/r)
    phi = arctan2(y,x)	
    return r,theta,phi



def stereographic_projection(u):

    x = u[0]
    y = u[1]
    z = u[2]
    deno = x + z + sqrt(2.0)

    re_part = (x - z)/deno
    im_part = y*sqrt(2.0)/deno

    return re_part,im_part


def tangent_source(v0, u, s, ds):

    v = copy(v0)
    x = u[0]
    y = u[1]
    z = u[2]
    t = u[3]
    r2 = x**2 + y**2 + z**2	
    r = sqrt(r2)
    t = t%T
    sigma = diff_rot_freq(t)
    a = rot_freq(t)
    coeff2 = s[0]*(1. - sigma*sigma - a*a)
    coeff3 = s[0]*a*a*(1.0 - r)		
    dcoeff2_ds1 = coeff2/s[0]
    dcoeff3_ds2 = coeff3/s[0]


    v[0] += (-1.0*dcoeff2_ds1*ds[0]*x*y*y + 
                            dcoeff3_ds2*ds[0]*x)
    v[1] += (dcoeff2_ds1*ds[0]*y*x*x + 
                            dcoeff3_ds2*ds[0]*y)
    v[2] += dcoeff3_ds2*ds[0]*z
    
    return v


def DfDs(u,s):

    dfds = zeros(d,p)
    ds1 = [1.0, 0.0]
    ds2 = [0.0, 1.0]
    dfds[:,0] = tangent_source(zeros(d),u,s,ds1)
    dfds[:,1] = tangent_source(zeros(d),u,s,ds2)
    return dfds



def gradfs(u,s):

	x = u[0]
	y = u[1]
	z = u[2]
	t = u[3]	
	r2 = x**2 + y**2 + z**2	
	r = sqrt(r2)
	
	t = t%T

	sigma = diff_rot_freq(t)
	a = rot_freq(t)
	dsigma_dt = ddiff_rot_freq_dt(t)
	da_dt = drot_freq_dt(t)

	coeff1 = sigma*pi*0.5*(z*sqrt(2) + 1)
	coeff2 = s[0]*(1. - sigma*sigma - a*a)
	coeff3 = s[1]*a*a*(1.0 - r)		

	dcoeff1_dt = pi*0.5*(z*sqrt(2) + 1)*dsigma_dt
	dcoeff2_dt = s[0]*(-2.0)*(sigma*dsigma_dt + a*da_dt)
	dcoeff3_dt = s[1]*(1.0 - r)*2.0*a*da_dt


	dcoeff1_dz = sigma*pi*0.5*sqrt(2)
	dcoeff2_ds1 = coeff2/s[0]
	dcoeff3_ds2 = coeff3/s[1]
	dcoeff3_dx = s[1]*a*a*(-x)/r
	dcoeff3_dy = s[1]*a*a*(-y)/r
	dcoeff3_dz = s[1]*a*a*(-z)/r
			
	dFdu = zeros(d,d)

	dFdu[0,0] = (-coeff2*y*y +
				 coeff3 + dcoeff3_dx*x)

	dFdu[0,1] = (-1.0*coeff1 - 
				coeff2*2.0*y*x + 
				dcoeff3_dy*x)

	dFdu[0,2] = (-1.0*dcoeff1_dz*y + 
				0.5*a*pi + dcoeff3_dz*x)


	dFdu[0,3] = (-1.0*dcoeff1_dt*y - 
				 dcoeff2_dt*x*y*y + 
				 0.5*pi*z*da_dt + 
				 dcoeff3_dt*x)

	dFdu[1,0] = (coeff1*0.5 + 	
				coeff2*y*2.0*x + 
				dcoeff3_dx*y)	 
							 
	dFdu[1,1] = (coeff2*x*x + 
				coeff3 + dcoeff3_dy*y)	

	dFdu[1,2] = (dcoeff1_dz*0.5*x + 
				dcoeff3_dz*y)

	dFdu[1,3] = (dcoeff1_dt*0.5*x + 
				 dcoeff2_dt*y*x*x + 
				 dcoeff3_dt*y)	

	dFdu[2,0] = (-0.5*a*pi + dcoeff3_dx*z)

	dFdu[2,1] = dcoeff3_dy*z

	dFdu[2,2] = coeff3 + dcoeff3_dz*z

	dFdu[2,3] = (-0.5*pi*x*da_dt + dcoeff3_dt*z)

	dFdu[3,3] = 1.0

	return dFdu


def divGradfs(u,s):

	epsi = 1.e-8			
	dgf = zeros(d)
	v = zeros(d)
	tmp_matrix = zeros(d,d)
	for i in range(d):
		v = zeros(d)
		v[i] = 1.0
		tmp_matrix = (gradfs(u + epsi*v,s) - 
		 gradfs(u - epsi*v,s))/(2*epsi)
		dgf += tmp_matrix[i,:]

	
	return dgf
	



def tangent_step(v0,u,s,ds):

	x = u[0]
	y = u[1]
	z = u[2]
	t = u[3]
	dx = v0[0]
	dy = v0[1]
	dz = v0[2]
	dtime = v0[3]
	v = copy(v0)

	
	r2 = x**2 + y**2 + z**2	
	r = sqrt(r2)
		
	t = t%T
	
	sigma = diff_rot_freq(t)
	a = rot_freq(t)
	dsigma_dt = ddiff_rot_freq_dt(t)
	da_dt = drot_freq_dt(t)


	
	coeff1 = sigma*pi*0.5*(z*sqrt(2) + 1)
	coeff2 = s[0]*(1. - sigma*sigma - a*a)
	coeff3 = s[1]*a*a*(1.0 - r)		

	dcoeff1_dt = pi*0.5*(z*sqrt(2) + 1)*dsigma_dt
	dcoeff2_dt = s[0]*(-2.0)*(sigma*dsigma_dt + a*da_dt)
	dcoeff3_dt = s[1]*(1.0 - r)*2.0*a*da_dt


	dcoeff1_dz = sigma*pi*0.5*sqrt(2)
	dcoeff2_ds1 = coeff2/s[0]
	dcoeff3_ds2 = coeff3/s[1]
	dcoeff3_dx = s[1]*a*a*(-x)/r
	dcoeff3_dy = s[1]*a*a*(-y)/r
	dcoeff3_dz = s[1]*a*a*(-z)/r
		


	v[1] += dt*(-1.0*dcoeff1_dz*y*dz - 1.0*
				coeff1*dy - dcoeff2_ds1*ds[0]*x*y*y - 
				coeff2*y*y*dx - coeff2*x*2.0*y*dy + 
				0.5*a*pi*dz + dcoeff3_ds2*ds[1]*x + 
				dcoeff3_dx*x*dx + 
				dcoeff3_dy*x*dy + 
				dcoeff3_dz*x*dz +
				coeff3*dx - 1.0*dcoeff1_dt*y*dtime - 
				dcoeff2_dt*x*y*y*dtime + 
				0.5*da_dt*pi*z*dtime + 
				dcoeff3_dt*x*dtime)

	v[2] += dt*(coeff1*0.5*dx + 
				dcoeff1_dz*0.5*x*dz + 
				dcoeff2_ds1*y*x*x*ds[0] + 
				coeff2*dy*x*x + 
				coeff2*2.0*x*dx*y + 
				dcoeff3_ds2*ds[1]*y + 
				dcoeff3_dx*y*dx + 
				dcoeff3_dy*y*dy +
		 		dcoeff3_dz*y*dz +
			 	coeff3*dy + dcoeff1_dt*0.5*x*dtime +
				dcoeff2_dt*y*x*x*dtime + 
				dcoeff3_dt*y*dtime) 

	v[3] += dt*(-0.5*a*pi*dx + 
				dcoeff3_ds2*z*ds[1] + 
				dcoeff3_dx*z*dx + 
				dcoeff3_dy*z*dy + 
				dcoeff3_dz*z*dz + 
				coeff3*dz - 
				0.5*pi*x*da_dt*dtime + 
				dcoeff3_dt*z*dtime)
	 

	return v





def rot_freq(t): 
    a0 = -1.0
    a1 = 0.0
    a2 = 1.0

    c0 = 2.0
    c1 = 3.0
    c2 = 5.0
    c3 = 6.0 
    c4 = 0.0

    slope = 20.0
    est = exp(slope*t)
    esc0 = exp(slope*c0)
    esc1 = exp(slope*c1)
    esc2 = exp(slope*c2)
    esc3 = exp(slope*c3)
    esc4 = exp(slope*c4)

    fn0 = (a1*esc0 + a0*est)/(esc0 + est)	
    fn1 = (a0*esc1 + a1*est)/(esc1 + est)
    fn2 = (a1*esc2 + a2*est)/(esc2 + est)
    fn3 = (a2*esc3 + a1*est)/(esc3 + est)
    fn4 = (a2*esc4 + a1*est)/(esc4 + est)

    return fn0 + fn1 + fn2 + fn3 + fn4






def diff_rot_freq(t):
    a0 = -1.0
    a1 = 0.0
    a2 = 1.0
    c0 = 1.0
    c1 = 2.0
    c2 = 4.0
    c3 = 5.0 

    slope = 20.0
    est = exp(slope*t)
    esc0 = exp(slope*c0)
    esc1 = exp(slope*c1)
    esc2 = exp(slope*c2)
    esc3 = exp(slope*c3)
	
    fn0 = (a1*esc0 + a0*est)/(esc0 + est)	
    fn1 = (a0*esc1 + a1*est)/(esc1 + est)
    fn2 = (a1*esc2 + a2*est)/(esc2 + est)
    fn3 = (a2*esc3 + a1*est)/(esc3 + est)

    return fn0 + fn1 + fn2 + fn3


def ddiff_rot_freq_dt(t):

    a0 = -1.0
    a1 = 0.0
    a2 = 1.0

    c0 = 1.0
    c1 = 2.0
    c2 = 4.0
    c3 = 5.0 

    slope = 20.0
    est = exp(slope*t)
    esc0 = exp(slope*c0)
    esc1 = exp(slope*c1)
    esc2 = exp(slope*c2)
    esc3 = exp(slope*c3)


    dfn0 = esc0*est*slope*(a0-a1)/(esc0 + est)/(esc0 + est)
    dfn1 = esc1*est*slope*(a1-a0)/(esc1 + est)/(esc1 + est)
    dfn2 = esc2*est*slope*(a2-a1)/(esc2 + est)/(esc2 + est)
    dfn3 = esc3*est*slope*(a1-a2)/(esc3 + est)/(esc3 + est)

    return dfn0 + dfn1 + dfn2 + dfn3 




def drot_freq_dt(t):
    
    a0 = -1.0
    a1 = 0.0
    a2 = 1.0

    c0 = 2.0
    c1 = 3.0
    c2 = 5.0
    c3 = 6.0 
    c4 = 0.0

    slope = 20.0
    est = exp(slope*t)
    esc0 = exp(slope*c0)
    esc1 = exp(slope*c1)
    esc2 = exp(slope*c2)
    esc3 = exp(slope*c3)
    esc4 = exp(slope*c4)

    fn0 = (a1*esc0 + a0*est)/(esc0 + est)	
    fn1 = (a0*esc1 + a1*est)/(esc1 + est)
    fn2 = (a1*esc2 + a2*est)/(esc2 + est)
    fn3 = (a2*esc3 + a1*est)/(esc3 + est)
    fn4 = (a2*esc4 + a1*est)/(esc4 + est)

    dfn0 = esc0*est*slope*(a0-a1)/(esc0 + est)/(esc0 + est)
    dfn1 = esc1*est*slope*(a1-a0)/(esc1 + est)/(esc1 + est)
    dfn2 = esc2*est*slope*(a2-a1)/(esc2 + est)/(esc2 + est)
    dfn3 = esc3*est*slope*(a1-a2)/(esc3 + est)/(esc3 + est)
    dfn4 = esc4*est*slope*(a1-a2)/(esc4 + est)/(esc4 + est)

    return dfn0 + dfn1 + dfn2 + dfn3 + dfn4



def adjoint_step(y1,u,s,dJ):


	y0 = copy(y1)

	x = u[0]
	y = u[1]
	z = u[2]
	t = u[3]
	
	r2 = x**2 + y**2 + z**2
	r = sqrt(r2)
	sigma = diff_rot_freq(t)
	a = rot_freq(t)	
	dsigmadt = ddiff_rot_freq_dt(t)
	dadt = drot_freq_dt(t)
	coeff1 = sigma*pi*0.5*(z*sqrt(2) + 1)
	coeff2 = s[0]*(1. - sigma*sigma - a*a)
	coeff3 = s[1]*a*a*(1.0 - r)		

	dcoeff1dt = pi*0.5*(z*sqrt(2) + 1)*dsigmadt
	dcoeff2dt = s[0]*(-2.0)*(sigma*dsigmadt + a*dadt)
	dcoeff3dt = s[1]*(1.0 - r)*2.0*a*dadt

	dcoeff1dz = sigma*pi*0.5*sqrt(2)
	dcoeff3dx = s[1]*a*a*(-x)/r 
	dcoeff3dy = s[1]*a*a*(-y)/r
	dcoeff3dz = s[1]*a*a*(-z)/r 

	y0[0] += (y1[0]*dt*(-1.0*coeff2*y*y) + 
			y1[0]*dt*coeff3 + 
			y1[0]*dt*x*dcoeff3dx + 
			y1[1]*dt*coeff1*0.5 + 
			y1[1]*dt*coeff2*y*2.0*x + 
			y1[1]*dt*dcoeff3dx*y + 
			y1[2]*dt*(-0.5)*a*pi + 
			y1[2]*dt*z*dcoeff3dx) 	

	y0[1] += (y1[0]*dt*(-1.0)*coeff1 - 
			y1[0]*dt*(-1.0)*coeff2*x*2.0*y + 
			y1[0]*dt*dcoeff3dy*x + 
			y1[1]*dt*coeff2*x*x + 
			y1[1]*dt*coeff3 + 
			y1[1]*dt*dcoeff3dy*y + 
			y1[2]*dt*dcoeff3dy*z)

	
	y0[2] += (y1[0]*dt*(-1.0)*dcoeff1dz*y + 
			y1[0]*dt*0.5*a*pi + 
			y1[0]*dt*dcoeff3dz*x + 
			y1[1]*dt*dcoeff1dz*0.5*x + 
			y1[1]*dt*y*dcoeff3dz + 
			y1[2]*dt*z*dcoeff3dz + 
			y1[2]*dt*coeff3)


	y0[3] += (-1.0*y1[0]*dt*dcoeff1dt*y - 
			 y1[0]*dt*x*y*y*dcoeff2dt + 
			 y1[0]*dt*x*dcoeff3dt +
			 y1[0]*dt*0.5*pi*z*dadt +  
			 y1[1]*dt*0.5*x*dcoeff1dt + 
			 y1[1]*dt*y*x*x*dcoeff2dt +
			 y1[1]*dt*y*dcoeff3dt + 
			 y1[2]*dt*dcoeff3dt*z + 
			 y1[2]*dt*(-0.5)*pi*x*dadt) 
			 

	y0 += dJ		

	return y0

