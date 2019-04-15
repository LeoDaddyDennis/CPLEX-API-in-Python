# -*- coding: utf-8 -*-
"""
ISE 6290 Homework 3
Snow Clearing Problem
Extensive Formulation and Solution
"""

import cplex as cpx

# deterministic and stocahstic data
summer_cost = {'salt': 20.0, 'fuel': 70.0}
truck_days = 5000.0
salv_price = {'salt': 15.0, 'fuel': 65.0}
winter_cost = {'cold': {'salt': 32.0, 'fuel': 73.0},
                'warm':{'salt': 30.0, 'fuel': 73.0}}
operating_cost = {'cold': 120.0, 'warm': 110.0}
winter_prob = {'cold': 0.6, 'warm': 0.4}
salting_efficiency = {'cold': 1.1, 'warm': 1.2}
plowing_req = {'cold': 5100.0, 'warm': 3500.0}
mat_in_method = {'salting': {'salt':1.0, 'fuel': 1.0}, 
                 'plowing': {'salt':0.0, 'fuel': 1.0}}

# set up problem
snow_clearing = cpx.Cplex()
snow_clearing.objective.set_sense(
        snow_clearing.objective.sense.minimize)
# variable names
var_names = ['sum salt', 'sum fuel', 
             'salting cold', 'plowing cold', 'short salt cold', 'short fuel cold', 
             'exc salt cold', 'exc fuel cold', 
             'salting warm', 'plowing warm', 'short salt warm', 'short fuel warm',
             'exc salt warm', 'exc fuel warm']
# objective function
objective = [summer_cost['salt'], summer_cost['fuel'], # sum salt and fuel
       winter_prob['cold']*operating_cost['cold'], # operating cost salting
       winter_prob['cold']*operating_cost['cold'], # operating cost plowing
       winter_prob['cold']*winter_cost['cold']['salt'], # buy salt in winter
       winter_prob['cold']*winter_cost['cold']['fuel'], # buy fuel in winter
       -winter_prob['cold']*salv_price['salt'], # salv salt cold
       -winter_prob['cold']*salv_price['fuel'],
       winter_prob['warm']*operating_cost['warm'], # operating cost salting
       winter_prob['warm']*operating_cost['warm'], # operating cost plowing
       winter_prob['warm']*winter_cost['warm']['salt'], # buy salt in winter
       winter_prob['warm']*winter_cost['warm']['fuel'], # buy fuel in winter
       -winter_prob['warm']*salv_price['salt'], # salv salt cold
       -winter_prob['warm']*salv_price['fuel']] # salv fuel cold
# set bounds
lower_bounds = len(var_names)*[0.0]
upper_bounds = len(var_names)*[cpx.infinity]
# add variables
snow_clearing.variables.add(obj = objective,
                      lb = lower_bounds,
                      ub = upper_bounds,
                      names = var_names)

constr_names = ['total truck days cold', 'all snow cleared cold', 
                'salt cold', 'fuel cold',
                'total truck days warm', 'all snow cleared warm',
                'salt warm', 'fuel warm']

cold_td_constr = [['salting cold', 'plowing cold'], [1.0, 1.0]]
cold_work_constr = [['salting cold', 'plowing cold'], [salting_efficiency['cold'], 1.0]]
salt_cold_constr = [['exc salt cold', 'short salt cold', 'salting cold', 'sum salt'], 
                    [1.0, -1.0, 1.0, -1.0]]
fuel_cold_constr = [['exc fuel cold', 'short fuel cold', 'salting cold', 'plowing cold',
                     'sum fuel'], [1.0, -1.0, 1.0, 1.0, -1.0]]
warm_td_constr = [['salting warm', 'plowing warm'], [1.0, 1.0]]
warm_work_constr = [['salting warm', 'plowing warm'], [salting_efficiency['warm'], 1.0]]
salt_warm_constr = [['exc salt warm', 'short salt warm', 'salting warm', 'sum salt'], 
                    [1.0, -1.0, 1.0, -1.0]]
fuel_warm_constr = [['exc fuel warm', 'short fuel warm', 'salting warm', 'plowing warm',
                     'sum fuel'], [1.0, -1.0, 1.0, 1.0, -1.0]]

constraints = [cold_td_constr, cold_work_constr, salt_cold_constr, fuel_cold_constr, 
               warm_td_constr, warm_work_constr, salt_warm_constr, fuel_warm_constr]

# Can I have variables in rhs?
rhs = [truck_days, plowing_req['cold'], 0.0, 0.0, 
       truck_days, plowing_req['warm'], 0.0, 0.0]

constraint_senses = ['L', 'G', 'E', 'E', 'L', 'G', 'E', 'E']

# add constraints to problem
snow_clearing.linear_constraints.add(lin_expr = constraints,
                               senses = constraint_senses,
                               rhs = rhs,
                               names = constr_names)

# Solve the problem
snow_clearing.solve()

solution_vals = snow_clearing.solution.get_values()
# And print the solutions
print('Total Cost :', snow_clearing.solution.get_objective_value())
for i in range(len(var_names)):
    print(str(var_names[i]), ':', str(solution_vals[i]))

