testName="kuznetsov"
import sys
sys.path.insert(0, '../')
from kuznetsov import *
from matplotlib.pyplot import *
from pylab import *
from numpy import *


def plot_attractor():

	n_testpoints = 5000
	n_times = 6
	n_steps = n_poincare*100
	u0 = rand(d,n_testpoints)
	u0 = (u0.T*(boundaries[d:2*d]-boundaries[0:d])).T
	u0 = (u0.T + boundaries[0:d]).T
	u = zeros((d,n_testpoints,n_times))
	for j in arange(n_times):
		u[:,:,j] = copy(u0)
	subplot(331)
	plot(u0[0,:],u0[1,:],"o")
	for i in arange(n_testpoints):
		u[:,i,1] = Step(u[:,i,1],s0,n_steps)
		for n in arange(1,n_times):
			u[:,i,n] = Step(u[:,i,n-1],s0,n_steps)
	
	subplot(332)
	plot(u[0,:,1],u[1,:,1],"o")
		
	subplot(333)
	plot(u[0,:,2],u[1,:,2],"o")

	subplot(334)
	plot(u[0,:,3],u[1,:,3],"o")

	subplot(335)
	plot(u[0,:,4],u[1,:,4],"o")
		
	subplot(336)
	plot(u[0,:,5],u[1,:,5],"o")


	r = zeros(n_testpoints)
	theta = zeros(n_testpoints)
	phi = zeros(n_testpoints)
	x = zeros(n_testpoints)
	y = zeros(n_testpoints)
	for i in range(n_testpoints):
		r[i],theta[i],phi[i] = convert_to_spherical(u[:,i,5]) 
		x[i],y[i] = stereographic_projection(u[:,i,5])
	figure()		
	subplot(121)		
	plot(phi,theta,"ko")
	xlim([-pi,pi])
	ylim([0.,pi])
	subplot(122)
	plot(x,y,"ro")


def test_tangent():

	n_testpoints = 100
	n_epsi = 8
	
	u0 = rand(d,n_testpoints)
	epsi = logspace(-n_epsi,-1.0,n_epsi)
	vu_fd = zeros((d,n_testpoints,n_epsi))
	vs_fd = zeros((d,n_testpoints,n_epsi))
	vu_ana = zeros((d,n_testpoints))
	vs_ana = zeros(d,n_testpoints)
	u0next = zeros(d)
	v0 = rand(4)
	ds0 = array([1.,1.])
	for i in arange(n_testpoints):
		u0[:,i] = Step(u0[:,i],s0,n_poincare)	
		for k in arange(n_epsi):		
			u0next = Step(u0[:,i],s0,1)
			vu_fd[:,i,k] = (Step(u0[:,i] + epsi[k]*v0,
						 s0,1)-u0next)/epsi[k]
			
			vs_fd[:,i,k] = (Step(u0[:,i],s0 + epsi[k]*ds0,1) - 
						u0next)/epsi[k]

		end

		vu_ana[:,i] = tangent_step(v0,u0[:,i],s0,zeros(p))
		vs_ana[:,i] = tangent_step(zeros(d),u0[:,i],s0,ds0)

	
	end		

	erru = zeros(n_epsi)
	errs = zeros(n_epsi)

	for k in arange(n_epsi):
		erru[k] = norm(vu_ana[:,:]-vu_fd[:,:,k])
		errs[k] = norm(vs_ana[:,:]-vs_fd[:,:,k])

	figure()
	loglog(epsi,erru)
	figure()
	loglog(epsi,errs)





def test_jacobian():


	u0 = rand(d)
	u0[3] *= T
	epsi = 1.e-8
	Jacu = zeros((d,d))
	Jacu[:,0] = ((Step(u0 + epsi*array([1.0,0.0,0.0,0.0]),s0,1) - 
				Step(u0 - epsi*array([1.0,0.0,0.0,0.0]),s0,1))/
				(2.0*epsi))

  	Jacu[:,1] = ((Step(u0 + epsi*array([0.0,1.0,0.0,0.0]),s0,1) - 
				Step(u0 - epsi*array([0.0,1.0,0.0,0.0]),s0,1))/
				(2.0*epsi))

	Jacu[:,2] = ((Step(u0 + epsi*array([0.0,0.0,1.0,0.0]),s0,1) - 
				Step(u0 - epsi*array([0.0,0.0,1.0,0.0]),s0,1))/
				(2.0*epsi))

	Jacu[:,3] = ((Step(u0 + epsi*array([0.0,0.0,0.0,1.0]),s0,1) - 
				Step(u0 - epsi*array([0.0,0.0,0.0,1.0]),s0,1))/
				(2.0*epsi))

	dFds1 = (Step(u0,s0 + epsi*array([1.0,0.0]),1)-Step(u0,s0
			- epsi*array([1.0,0.0]),1))/(2.0*epsi)	


	dFds2 = (Step(u0,s0 + epsi*array([0.0,1.0]),1)-Step(u0,s0
			- epsi*array([0.0,1.0]),1))/(2.0*epsi)	


	Jacana = dt*gradfs(u0,s0) + eye(d,d)
	print(norm(Jacu-Jacana))
	print(Jacu)
	
	v0 = rand(4)
	v0_fd = dot(Jacu,v0) 
	print(v0_fd)
	v0_hand = tangent_step(v0,u0,s0,zeros(2))
	print(norm(v0_fd - v0_hand))


	v1_fd = v0_fd + dFds1 
	v1_hand = tangent_step(v0,u0,s0,[1.0,0.0])
	print(norm(v1_fd - v1_hand))

	v2_fd = v0_fd + dFds2 
	v2_hand = tangent_step(v0,u0,s0,[0.0,1.0])
	print(norm(v2_fd - v2_hand))



def test_adjoint():

	u0 = rand(4)
	u0[3] *= T
	u1 = Step(u0,s0,1)
	epsi = 1.e-8

	y1 = [0.0,1.,0.,0.]
	y0_ana = adjoint_step(y1,u0,s0,y1)

	y0_fd = zeros(d)
	v0 = zeros(d)
	for i in arange(d):
		v0 = zeros(d)
		v0[i] = 1.0
		u0pert = u0 + epsi*v0
		u1pert =  Step(u0pert,s0,1)
		obj2 = u0pert[1] + u1pert[1]

		u0pert = u0 - epsi*v0
		u1pert =  Step(u0pert,s0,1)
		obj1 = u0pert[1] + u1pert[1]

		y0_fd[i] = (obj2 - obj1)/(2.0*epsi) 
	print(norm(y0_fd-y0_ana))



def test_tangentadjoint():
	u = rand(4)
	u[3] *= T
	y1 = rand(4)
	v0 = rand(4)
	v1 = tangent_step(v0,u,s0,zeros(2))
	y0 = adjoint_step(y1,u,s0,zeros(4))
	print(dot(v1,y1))
	print(dot(v0,y0))	


