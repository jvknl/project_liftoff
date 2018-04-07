# -*- coding: utf-8 -*-
"""
Created on Sat Apr  7 11:00:08 2018

Algorithm script for deciding nr of cars (and km/h in future)
@author: Thomas & Olivier
"""
import numpy as np

# input is op geaggregeerd niveau output vorige simulatie
#def get_simulationresult(connection, sim_id):
#    connect
#    get result of sim_id
#    return sim_result



     
# adhv formule bepalen aantal TU's noodzakelijk in nieuwe simulatie
#  cost =  waiting_time + km_driven + nr_cars (prod cost + happiness cost) optional: + game of life inefficiency
# minimize cost by running simulations with changed nr of cars

# sim_result : [sim_id, nr of rides, avg waiting time, nr of cars, km driven]
simulation_list = [[1, 100000],[2, 95000]]
simulation_input = []
simulation_db = []
sim_result = {}
sim_result[1] = {"nr_of_rides": 1000, "avg_wait": 300, "nr_cars": 10, "km_driven":4000}
ai_parameters = {"beta_wait": 5, "beta_nr_cars": 100, "beta_km": 1}
learning_rate = 0.5

def get_simulationresult(i):
    simulation_result = {"nr_of_rides": 1000, "avg_wait": 300, "nr_cars": 10, "km_driven":4000}
    return simulation_result


def calc_cost(sim_result, ai_param):
    cost = (ai_parameters["beta_wait"] * sim_result["avg_wait"]) + (ai_parameters["beta_nr_cars"] * sim_result["nr_cars"]) + (ai_parameters["beta_km"] * sim_result["km_driven"])
    return cost


def decide_optimal_cars(simil_list, nr_cars, curr_simulation_cost, learning_rate):
    simil_list.append([nr_cars, curr_simulation_cost])
    gradient = simil_list[-2][1] / simil_list[-1][1]
    new_cars = simil_list[-1][0] * (gradient * learning_rate)
    return simil_list, int(new_cars)

def run_simulation(i, new_cars):
    simulation_input.append(i, new_cars)
    return simulation_input

for i in range(3,10):
    #run simulation
    sim_result[i] = get_simulationresult(i)
    simulation_cost = calc_cost(sim_result[i], ai_parameters)
    simulation_list, new_cars = decide_optimal_cars(simulation_list, sim_result[i]["nr_cars"], simulation_cost, learning_rate)
    simulation_input = run_simulation(i, new_cars)





sim_result[i] = get_simulationresult(i)
simulation_cost = calc_cost(sim_result[i], ai_parameters)
simulation_list, new_cars = decide_optimal_cars(simulation_list, sim_result[i]["nr_cars"], simulation_cost, learning_rate)

    simulation_list.append([sim_result[i]["nr_cars"], simulation_cost])
    simulation_list.append([20, 5000])

gradient = simulation_list[-2][1] / simulation_list[-1][1]
learning_rate = 0.5
new_cars = simulation_list[-1][0] * (gradient * learning_rate)
#run simulation met nieuwe auto's 
sim_result[i] = get_simulationresult(i)
simulation_cost = calc_cost(sim_result[i], ai_parameters)
simulation_list.append([sim_result[i]["nr_cars"], simulation_cost])



def generate_input()
calc_cost(sim_result[1], ai_parameters)
