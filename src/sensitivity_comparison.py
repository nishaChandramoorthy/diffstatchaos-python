import sys
sys.path.insert(0, '../examples/')
import kuznetsov_poincare as kmap
import kuznetsov as kode
import map_sens as map_sens
import flow_sens as flow_sens
from time import clock
if __name__ == "__main__":
    solver_ode = kode.Solver()
    solver_map = kmap.Solver()
    n_map = solver_ode.n_poincare
    n_steps_map = 50
    n_steps = n_map*n_steps_map
    plykin = flow_sens.Sensitivity(solver_ode,n_steps)
    t0 = clock()
    u_ode = plykin.solve_primal(solver_ode,solver_ode.u_init,\
            n_steps,
            solver_ode.s0)
    t1 = clock()
    print('{:<60s}{:>16.10f}'.format(\
            "Time to solve primal: ",\
        t1-t0))

    t2 = clock()
    plykin.precompute_sources(solver_ode,u_ode)
    t3 = clock()
    print('{:<60s}{:>16.10f}'.format(\
            "Time for flow precomputations: ",\
        t3-t2))

    poincare_plykin = map_sens.Sensitivity(solver_map,n_steps_map)
    #u_map = poincare_plykin.solve_primal(solver_map,\
     #       solver_map.u_init, n_steps_map, solver_map.s0)
    u_map = u_ode[::n_map]
   

    t4 = clock() 
    poincare_plykin.precompute_sources(solver_map,u_map)
    t5 = clock()
    print('{:<60s}{:>16.10f}'.format(\
            "Time for map precomputations: ",\
        t5-t4))

    # Comparison of pre-computations
    
    v0 = plykin.v0[::n_map]
    v0_map = poincare_plykin.v0
    w0 = plykin.w0[::n_map]
    w0_map = poincare_plykin.w0
    J = plykin.J[::n_map]
    J_map = poincare_plykin.J
    dJ = plykin.dJ[::n_map]
    dJ_map = poincare_plykin.dJ
    tan_src = plykin.source_tangent[::n_map]
    tan_src_map = poincare_plykin.source_tangent
    foradj_src = plykin.source_foradj[::n_map]
    foradj_src_map = poincare_plykin.source_foradj
    sens_src = plykin.source_sens[::n_map]
    sens_src_map = poincare_plykin.source_sens

    n_pad = 10 
    n_comp = n_steps_map - 2*n_pad
    v0 = v0[n_pad:-n_pad]
    v0_map = v0_map[n_pad:-n_pad]
    w0 = w0[n_pad:-n_pad]
    w0_map = w0_map[n_pad:-n_pad]
    tan_src = tan_src[n_pad:-n_pad]
    tan_src_map = tan_src_map[n_pad:-n_pad]
    foradj_src = foradj_src[n_pad:-n_pad]
    foradj_src_map = foradj_src_map[n_pad:-n_pad]
    sens_src = sens_src[n_pad:-n_pad]
    sens_src_map = sens_src_map[n_pad:-n_pad]





    diff_v0 = zeros(n_comp)
    diff_w0 = zeros(n_comp)
    diff_tan_src = zeros(n_comp)
    diff_foradj_src = zeros(n_comp)
    diff_sens_src = zeros(n_comp)
    
    for i in range(n_comp):
        diff_v0[i] = min(norm(v0[i]-v0_map[i]),\
                norm(v0[i]+v0_map[i]))
        diff_w0[i] = min(norm(w0[i]-w0_map[i]),\
                norm(w0[i]+w0_map[i]))




    print('{:<60s}{:>16.10f}'.format(\
        "l_infty norm of difference in tangent unstable direction: ",\
        max(diff_v0)))

    print('{:<60s}{:>16.10f}'.format(\
        "l_infty norm of difference in adjoint unstable direction: ",\
        max(diff_w0)))
    
   
    g_flow = plykin.compute_timeseries_unstable_sensitivity(solver_ode)
    g_map = poincare_plykin.compute_timeseries_unstable_sensitivity(solver_map)
    g_flow = g_flow[::n_map]
    print('{:<60s}{:>16.10f}'.format(\
        "l_infty norm of unstable time series: ",\
        max(abs(g_flow - g_map))))

    
    dJds_stable_flow = plykin.compute_stable_sensitivity(solver_ode,u_ode)
    dJds_stable_map = poincare_plykin.compute_stable_sensitivity(solver_map,u_map)
    dJds_unstable_flow = plykin.compute_unstable_sensitivity(solver_ode)
    dJds_unstable_map = poincare_plykin.compute_unstable_sensitivity(solver_map)
    
    dtheta = pi/(solver_map.n_theta -1)
    dphi = 2*pi/(solver_map.n_phi -1)
    theta_bin_centers = linspace(dtheta/2.0,pi - dtheta/2.0, \
            solver_map.n_theta)
    phi_bin_centers = linspace(-pi-dphi/2.0,pi - dphi/2.0,\
            solver_map.n_phi)
    contourf(phi_bin_centers,theta_bin_centers\
            ,dJds_stable_map,100)
    
    figure()
    contourf(phi_bin_centers,theta_bin_centers\
            ,dJds_stable_flow,100)

    figure()
    contourf(phi_bin_centers,theta_bin_centers\
            ,dJds_unstable_map,100)

    figure()
    contourf(phi_bin_centers,theta_bin_centers\
            ,dJds_unstable_flow,100)


    '''
    
    u = zeros((n_steps,state_dim))
    random.seed(0)
    u_init = rand(state_dim)
    u_init[3] = 0
    u_init = poincare_step(u_init,s0,n_runup)
    param_dim = s0.size
    ds0 = zeros(param_dim)
    ds1 = copy(ds0)
    ds1[0] = 1.0
    dJ0 = zeros(state_dim)
    
    w0 = zeros((n_steps,state_dim))
    w0_init = rand(state_dim)
    w0_init /= linalg.norm(w0_init)
    
    v0_init = rand(state_dim)
    v0_init /= linalg.norm(v0_init)
    
    J_theta_phi = zeros((n_steps,n_points_theta,n_points_phi))
    DJ_theta_phi = zeros((n_steps,n_points_theta,n_points_phi,state_dim))  
    theta_bin_centers = linspace(dtheta/2.0,pi - dtheta/2.0, n_points_theta)
    phi_bin_centers = linspace(-pi-dphi/2.0,pi - dphi/2.0, n_points_phi)
    v = zeros(state_dim)
    w_inv = zeros(state_dim)
    dfds = zeros((n_steps,param_dim,state_dim))
    source_forward_adjoint = zeros((n_steps,state_dim))
    source_tangent = zeros((n_steps,param_dim,state_dim))
    dJds_stable = zeros((n_points_theta,n_points_phi))
    dJds_unstable = zeros((n_points_theta,n_points_phi))
    divdfds = zeros(n_steps)

    source_tangent = compute_poincare_source_tangent(u,n_steps,s0)[:,0,:] 
    t3 = clock()
#    J_theta_phi = compute_objective(u,s0,n_steps,n_points_theta,n_points_phi)
    t4 = clock()
 #   DJ_theta_phi = compute_gradient_objective(u,s0,n_steps,n_points_theta,n_points_phi)
    t5 = clock()
    source_forward_adjoint = compute_poincare_source_inverse_adjoint(u,n_steps,s0)
    t6 = clock()
    unstable_sensitivity_source = (compute_poincare_source_sensitivity(u,n_steps,s0))
    t7 = clock()
    w0, log_w_mag = solve_poincare_unstable_adjoint_direction(u, w0_init, n_steps, s0)
    t8 = clock()

    
    print('='*50)
    print("Pre-computation times for {:>10d} steps".format(n_samples))
    print('='*50)
    print('{:<35s}{:>16.10f}'.format("primal", t1-t0))
    print('{:<35s}{:>16.10f}'.format("tangent",t2 - t1)) 
    print('{:<35s}{:>16.10f}'.format("tangent source", t3 - t2))
    print('{:<35s}{:>16.10f}'.format("inverse adjoint source", t6 - t5))
    print('{:<35s}{:>16.10f}'.format("objective ", t4 - t3)) 
    print('{:<35s}{:>16.10f}'.format("gradient objective ", t5 - t4))
    print('{:<35s}{:>16.10f}'.format("sensitivity source ", t7 - t6))
    print('{:<35s}{:>16.10f}'.format("adjoint ", t8 - t7))
    print('*'*50)
    print("End of pre-computation")
    print('*'*50)

    stop
    ds1 = copy(ds0)
    ds1[0] = 1.0
    print('Starting stable-(adjoint-unstable) split evolution...')
    t13 = clock()
    unstable_sensitivity_source = unstable_sensitivity_source[:,0]
    dJds_stable, dJds_unstable, w0_inv, gsum_history = compute_sensitivity(u,s0,v0,w0,J_theta_phi,\
            DJ_theta_phi,\
            source_tangent,\
            unstable_sensitivity_source, \
            source_forward_adjoint,\
            n_steps,n_runup_forward_adjoint)
    t14 = clock()
    print('{:<35s}{:>16.10f}'.format("time taken",t14-t13))
    print('End of computation...')

    dJds = dJds_stable + dJds_unstable
    theta = linspace(0,pi,n_points_theta)
    phi = linspace(-pi,pi,n_points_phi)
    figure()
    contourf(phi,theta,dJds_stable,100)
    xlabel(r"$\phi$")
    ylabel(r"$\theta$")
    colorbar()
    figure()
    #visualize_tangent_3D(u,w0_inv)
    savefig("../examples/plots/plykin_poincare_main_stable")
    #figure()
    contourf(phi,theta,dJds_unstable,100)
    xlabel(r"$\phi$")
    ylabel(r"$\theta$")
    colorbar()
    savefig("../examples/plots/plykin_poincare_main_unstable")
    figure()
    contourf(phi,theta,dJds_unstable+dJds_stable,100)
    xlabel(r"$\phi$")
    ylabel(r"$\theta$")
    colorbar()
    savefig("../examples/plots/plykin_poincare_main_total")
    '''
