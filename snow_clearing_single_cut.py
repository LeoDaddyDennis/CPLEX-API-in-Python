# -*- coding: utf-8 -*-
"""
ISE 6290 Homework 3
Snow Clearing Problem
Single-Cut Formulation and Solution
"""

import cplex as cpx

# deterministic and stochastic data
summer_cost = {'salt': 20.0, 'fuel': 70.0}
truck_days = 5000.0
salv_price = {'salt': 15.0, 'fuel': 65.0}
winter_cost = {'cold': {'salt': 32.0, 'fuel': 73.0},
                'warm':{'salt': 30.0, 'fuel': 73.0}}
operating_cost = {'cold': 120.0, 'warm': 110.0}
winter_prob = {'cold': 0.6, 'warm': 0.4}
salting_efficiency = {'cold': 1.1, 'warm': 1.2}
plowing_req = {'cold': 5100.0, 'warm': 3500.0}

init_salt = 0
init_fuel = 0


# Solution Algorithm
# step 0: initialize variables and set up problem
tolerance = .0000005
m = 1_000_000
upper_bound = cpx.infinity

# initialize dicts to keep track of 1st stage information
salt_x_hat = {0: 0}
fuel_x_hat = {0: 0}
theta_hat = {0: 'NA'}
lower_bounds = {0: -cpx.infinity}
potential_upper_bounds = {0: 'NA'}
upper_bounds = {0: cpx.infinity}
relative_error = {0: 'NA'}
cut_gradients = {}
cut_intercepts = {}

# Set up stage 1 master.
stg1_snow_clearing = cpx.Cplex()
stg1_snow_clearing.objective.set_sense(
        stg1_snow_clearing.objective.sense.minimize)
stg1_var_names = ['sum salt', 'sum fuel', 'theta']
stg1_objective = [summer_cost['salt'], summer_cost['fuel'], 1]
stg1_lower_bounds = [0.0, 0.0, -m]
stg1_upper_bounds = len(stg1_var_names)*[cpx.infinity]

stg1_snow_clearing.variables.add(obj = stg1_objective,
                      lb = stg1_lower_bounds,
                      ub = stg1_upper_bounds,
                      names = stg1_var_names)

# Set up stage 2 subproblems for warm and cold sceanrios.
# Stage 2 cold scenario
stg2_cold_snow_clearing = cpx.Cplex()
stg2_cold_snow_clearing.objective.set_sense(
        stg2_cold_snow_clearing.objective.sense.minimize)
stg2_cold_var_names = ['salting cold', 'plowing cold', 'short salt cold', 
                       'short fuel cold', 'exc salt cold', 'exc fuel cold']
# objective coefficients for variable names
stg2_cold_objective = [operating_cost['cold'], operating_cost['cold'],
                       winter_cost['cold']['salt'], winter_cost['cold']['fuel'],
                       -salv_price['salt'], -salv_price['fuel']] 
stg2_cold_lower_bounds = len(stg2_cold_var_names)*[0.0]
stg2_cold_upper_bounds = len(stg2_cold_var_names)*[cpx.infinity]

stg2_cold_snow_clearing.variables.add(obj = stg2_cold_objective,
                                      lb = stg2_cold_lower_bounds,
                                      ub = stg2_cold_upper_bounds,
                                      names = stg2_cold_var_names)


stg2_cold_constr_names = ['total truck days cold', 'all snow cleared cold', 
                          'salt cold', 'fuel cold']
stg2_cold_td_constr = [['salting cold', 'plowing cold'], [1.0, 1.0]]
# this constraint causing infeasibility
stg2_cold_work_constr = [['salting cold', 'plowing cold'], 
                         [salting_efficiency['cold'], 1.0]]
# something wrong with this constraint
stg2_salt_cold_constr = [['exc salt cold', 'short salt cold', 'salting cold'], 
                         [1.0, -1.0, 1.0]]
stg2_fuel_cold_constr = [['exc fuel cold', 'short fuel cold', 'salting cold', 
                          'plowing cold'], 
                        [1.0, -1.0, 1.0, 1.0]]
stg2_cold_constraints = [stg2_cold_td_constr, stg2_cold_work_constr, 
                         stg2_salt_cold_constr, stg2_fuel_cold_constr]
stg2_cold_rhs = [truck_days, plowing_req['cold'], init_salt, init_fuel]
stg2_cold_constraint_senses = ['L', 'G', 'E', 'E']

stg2_cold_snow_clearing.linear_constraints.add(lin_expr = stg2_cold_constraints,
                               senses = stg2_cold_constraint_senses,
                               rhs = stg2_cold_rhs,
                               names = stg2_cold_constr_names)

# Stage 2 warm scenario
stg2_warm_snow_clearing = cpx.Cplex()
stg2_warm_snow_clearing.objective.set_sense(
        stg2_warm_snow_clearing.objective.sense.minimize)
stg2_warm_var_names = ['salting warm', 'plowing warm', 'short salt warm', 
                       'short fuel warm', 'exc salt warm', 'exc fuel warm']
stg2_warm_objective = [operating_cost['warm'], operating_cost['warm'],
                       winter_cost['warm']['salt'], winter_cost['warm']['fuel'],
                       -salv_price['salt'], -salv_price['fuel']]
stg2_warm_lower_bounds = len(stg2_warm_var_names)*[0.0]
stg2_warm_upper_bounds = len(stg2_warm_var_names)*[cpx.infinity]

stg2_warm_snow_clearing.variables.add(obj = stg2_warm_objective,
                                      lb = stg2_warm_lower_bounds,
                                      ub = stg2_warm_upper_bounds,
                                      names = stg2_warm_var_names)

warm_constr_names = ['total truck days warm', 'all snow cleared warm',
                     'salt warm', 'fuel warm']
warm_td_constr = [['salting warm', 'plowing warm'], [1.0, 1.0]]
warm_work_constr = [['salting warm', 'plowing warm'], [salting_efficiency['warm'], 1.0]]
salt_warm_constr = [['exc salt warm', 'short salt warm', 'salting warm'], 
                    [1.0, -1.0, 1.0]]
fuel_warm_constr = [['exc fuel warm', 'short fuel warm', 'salting warm', 
                     'plowing warm'], [1.0, -1.0, 1.0, 1.0]]
stg2_warm_constraints = [warm_td_constr, warm_work_constr, salt_warm_constr, 
                         fuel_warm_constr]
stg2_warm_rhs = [truck_days, plowing_req['warm'], 0.0, 0.0]
stg2_warm_constraint_senses = ['L', 'G', 'E', 'E']

stg2_warm_snow_clearing.linear_constraints.add(lin_expr = stg2_warm_constraints,
                               senses = stg2_warm_constraint_senses,
                               rhs = stg2_warm_rhs,
                               names = warm_constr_names)



# step 1
def solve_relaxed(iteration):
    '''
    Takes as input the iteration number.
    Solves the current (relaxed) master problem , updates dictionaries
    to keep track of variables at each iteration and updates lower bound.
    Returns first stage decision variables.
    '''
    stg1_snow_clearing.solve()
    dec_vars = stg1_snow_clearing.solution.get_values()
    salt_x_hat[iteration] = dec_vars[0]
    curr_sum_salt = dec_vars[0]
    fuel_x_hat[iteration] = dec_vars[1]
    curr_sum_fuel = dec_vars[1]
    theta_hat[iteration] = dec_vars[2]
    lower_bound = stg1_snow_clearing.solution.get_objective_value()
    lower_bounds[iteration] = lower_bound
    return curr_sum_salt, curr_sum_fuel

# step 2
def solve_sub(iteration, curr_sum_salt, curr_sum_fuel):
    '''
    Takes as input the iteration number and first stage decision variables.
    Updates the RHS of second stage constraints and solves the subproblems.
    Obtains the dual variable (pi_hat) for each constraint and 
    scenario.
    Updates z_hat (potential upper bound) and checks for least upper bound.
    Updates upper bound if necessary.
    Returns the dual variables.
    '''
    # update RHS
    stg2_cold_snow_clearing.linear_constraints.set_rhs(2, curr_sum_salt)
    stg2_cold_snow_clearing.linear_constraints.set_rhs(3, curr_sum_fuel)
    
    stg2_warm_snow_clearing.linear_constraints.set_rhs(2, curr_sum_salt)
    stg2_warm_snow_clearing.linear_constraints.set_rhs(3, curr_sum_fuel)
    
    # solve subproblems
    stg2_cold_snow_clearing.solve()
    print(stg2_cold_snow_clearing.solution.get_values())
    stg2_warm_snow_clearing.solve()
    print(stg2_cold_snow_clearing.solution.get_values())
    
    # get dual variables
    pi_total_td_cold = stg2_cold_snow_clearing.solution.get_dual_values()[0]
    pi_all_snow_cleared_cold = (
            stg2_cold_snow_clearing.solution.get_dual_values()[1])
    pi_salt_cold = stg2_cold_snow_clearing.solution.get_dual_values()[2]
    pi_fuel_cold = stg2_cold_snow_clearing.solution.get_dual_values()[3]
    
    pi_total_td_warm = stg2_warm_snow_clearing.solution.get_dual_values()[0]
    pi_all_snow_cleared_warm = (
            stg2_warm_snow_clearing.solution.get_dual_values()[1])
    pi_salt_warm = stg2_warm_snow_clearing.solution.get_dual_values()[2]
    pi_fuel_warm = stg2_warm_snow_clearing.solution.get_dual_values()[3]
    
    dual_vars = [pi_total_td_cold, pi_all_snow_cleared_cold, pi_salt_cold, 
                 pi_fuel_cold, pi_total_td_warm, pi_all_snow_cleared_warm,
                 pi_salt_warm, pi_fuel_warm]
    
    # get z_hat
    z_hat = -theta_hat[iteration] + (
            stg1_snow_clearing.solution.get_objective_value() + (
            winter_prob['cold'] * 
            stg2_cold_snow_clearing.solution.get_objective_value() +
            winter_prob['warm'] * 
            stg2_warm_snow_clearing.solution.get_objective_value())) 
            
    potential_upper_bounds[iteration] = z_hat
    if z_hat < upper_bound:
        upper_bounds[iteration] = z_hat
    else:
        upper_bounds[iteration] = upper_bounds[iteration - 1]    
    return dual_vars

    

# step 3
def check_tolerance(iteration):
    '''
    Takes as input the iteration number.
    Updates dictionary for current relative error.
    Checks to see if difference in upper and lower bounds is within specified
    tolerance. 
    Returns true if current relative error is within specified tolerance.
    Returns false otherwise.
    '''
    relative_error[iteration] = (upper_bounds[iteration] - 
                                  lower_bounds[iteration])/(
                                min(abs(upper_bounds[iteration]), 
                                abs(lower_bounds[iteration])))
                                
    if (upper_bounds[iteration] - lower_bounds[iteration]) <= (
            min(abs(upper_bounds[iteration]), abs(lower_bounds[iteration]))
            *tolerance):
        return True
    else:
        return False
    
   
# step 4
def add_cut(iteration, dual_vars):
    '''
    Takes as input the iteration number and dual variables. 
    Creates the cut gradient and intercept.
    Returns the cut gradient and intercept.
    '''
    cut_gradient_salt = (winter_prob['cold']*dual_vars[2] + 
                         winter_prob['warm']*dual_vars[6])
                        
    cut_gradient_fuel = (winter_prob['cold']*dual_vars[3] +
                         winter_prob['warm']*dual_vars[7])
        
    cut_intercept = (winter_prob['cold']*(dual_vars[0]*truck_days +
                                         dual_vars[1]*plowing_req['cold']) +
            winter_prob['warm']*(dual_vars[4]*truck_days +
                               dual_vars[5]*plowing_req['warm']))
    return cut_gradient_salt, cut_gradient_fuel, cut_intercept

def single_cut():
    '''
    Ties together all functions as steps in the single cut algorithm.
    '''
    k = 0
    while not check_tolerance(k):
        print('Iteration ' + str(k))
        k += 1
        sum_salt, sum_fuel = solve_relaxed(k)
        dual_vars = solve_sub(k, sum_salt, sum_fuel)
        # check if solution within specified tolerance
        if check_tolerance(k) == True:
            print('Optimal solution found!')
            break
        else:
            cut_gradient_salt, cut_gradient_fuel, cut_intercept = (
                    add_cut(k, dual_vars))
            # add the cut to the master problem
            stg1_snow_clearing.linear_constraints.add(
                    lin_expr = [[['sum salt', 'sum fuel', 'theta'], 
                                [-cut_gradient_salt, -cut_gradient_fuel, 1]]],
                    senses = 'G',
                    rhs = [cut_intercept],
                    names = ['cut ' + str(k)])
            # check to ensure algorithm doesn't run forever if
            # something is wrong
            if k > 500:
                break
            
single_cut()
