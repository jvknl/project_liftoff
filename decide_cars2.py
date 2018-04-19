# -*- coding: utf-8 -*-
"""
Created on Sat Apr  7 11:00:08 2018

Algorithm script for deciding nr of cars (and km/h in future)
@author: Thomas & Olivier
"""
import numpy as np
import os
import json
import datetime
import helper_functions
import argparse 
 
# adhv formule bepalen aantal TU's noodzakelijk in nieuwe simulatie
#  cost =  waiting_time + km_driven + nr_cars (prod cost + happiness cost) optional: + game of life inefficiency
# minimize cost by running simulations with changed nr of cars

# sim_result : [sim_id, nr of rides, avg waiting time, nr of cars, km driven]
simulation_list = [[10,37662],[20,9858]]
simulation_input = []
simulation_db = []
sim_result = {}
sim_result[1] = {"nr_of_rides": 1000, "avg_wait": 300, "nr_cars": 10, "km_driven":4000}
ai_parameters = {"beta_wait": 5, "beta_nr_cars": 100, "beta_km": 1}
n_cars = 76

def get_simulationresult(i):
    simulation_result = {"nr_of_rides": 1000, "avg_wait": 300, "nr_cars": 10, "km_driven":4000}
    return simulation_result


def calc_cost(sim_result, ai_param):
    cost = (ai_parameters["beta_wait"] * sim_result["avg_wait"]) + (ai_parameters["beta_nr_cars"] * sim_result["nr_cars"]) + (ai_parameters["beta_km"] * sim_result["km_driven"])
    return cost


def decide_optimal_cars(simil_list, nr_cars, curr_simulation_cost, learning_rate):
    simil_list.append([nr_cars, curr_simulation_cost])
    gradient = simil_list[-2][1] / simil_list[-1][1]
    if simil_list[-1][0] > simil_list[-2][0]:
        new_cars = simil_list[-1][0] * (gradient**learning_rate)
    else:
        gradient = simil_list[-1][1] /  simil_list[-2][1] 
        new_cars = simil_list[-1][0] * (gradient**learning_rate)
    return simil_list, int(new_cars)

def run_simulation(i, new_cars):
    simulation_input.append(i, new_cars)
    return simulation_input



# helper_functions.distance((53.2194, 6.5665), (53.2350682, 6.6068002))

ride_dict = []
available_tu_ts = {}
waiting_list = []
datum = datetime.datetime(2018, 4, 9, 0, 0, 0)
datum = int(datum.timestamp())

with open('project_liftoff/ridelisttest.json') as json_data:
    ride_list = json.load(json_data)
    ride_list.sort()        
    ride_list_test = ride_list
# len(ride_list) 1000
n_rides = len(ride_list_test)

class Tu():
    _registry = []
    
    def __init__(self, name, lat, lon, person_capacity = 4, battery_state=0.2, battery_capacity=300, 
                 avg_km_per_kwh=7, state=3, km_hour = 50
                ):
        "assumes name is string"
        self._registry.append(self)
        self.name = name
        self.lat = lat
        self.lon = lon
        self.person_capacity = person_capacity
        self.battery_state = battery_state
        self.battery_capacity = battery_capacity
        self.avg_km_per_kwh = avg_km_per_kwh
        self.state = state
        self.km_hour = km_hour
    
    def get_name(self):
        return self.name
    
    def get_location(self):
        return(self.lat, self.lon)

    def get_battery_state(self):
        return self.battery_state
    
    def get_state(self):
        return self.state
    
    def get_radius(self):
        return self.battery_capacity * self.battery_state * self.avg_km_per_kwh
    
    def get_km_hour(self):
        return self.km_hour
    
    def __str__(self):
        return self.get_name() \
        + ' at lat:' + str(self.get_location()[0]) + ' and lon:' + str(self.get_location()[1])\
        +' radius left:'  + str(self.get_radius())
        
    def update_location(self, lat, lon):
        self.lon = lon
        self.lat = lat
        
    def update_state(self, state):
        self.state = state

    def update_capacity(self, capacity):
        self.capacity = capacity
        


class Tr():
    
    def __init__(self, start_lat, start_lon, end_lat, end_lon,  request_time, transport_type, request_id, factor_ride=1.5):
        self.start_lat = float(start_lat)
        self.start_lon = float(start_lon)
        self.end_lat = float(end_lat)
        self.end_lon = float(end_lon)
        self.request_id = request_id
        self.transport_type = transport_type
        self.request_time = request_time
        self.factor_ride = factor_ride
    
    def get_distance_ride(self):
        return helper_functions.distance((self.start_lat, self.start_lon),(self.end_lat,self.end_lon)) * self.factor_ride
    
    def get_request_id(self):
        return self.request_id
    
    def get_request_time(self):
        return self.request_time
    
    def get_start_loc(self):
        return(self.start_lat, self.start_lon)
    
    def get_distance_to_tu(self, tu_location):
        #location of transportation unit
        return helper_functions.distance((tu_location[0], tu_location[1]), (self.start_lat, self.start_lon)) * self.factor_ride
    
    def __str__(self):
             return 'id:' + str(self.get_request_id()) + ' requests a transport at ' \
        + str(self.request_time) +' for ' \
        + str(round(self.get_distance_ride(),3)) + " KM" \
        + ' at '+ str(self.get_start_loc())
        #+ datetime.time.strftime("%Y-%m-%d %H:%M:%S", self.request_time)
        
def generate_ride(tu, tr, ride_dict, distance_tu_tr, current_ts):
    tu.update_state(4)
    waiting_time = (current_ts-tr.get_request_time())  + ((distance_tu_tr/tu.get_km_hour())*3600)
    # key transportation_request  value: tr_name, distance van unit tot request, distance ride, waiting_time
    #ride_dict[tr.get_request_id()] = [tu.get_name(), distance_tu_tr, tr.get_distance_ride(), waiting_time, tu.get_location(), \
    #          tu.get_state(), tr.get_request_id, tr.get_request_time, current_ts, tu, tr]
    ride_dict.append([distance_tu_tr + tr.get_distance_ride(), waiting_time])
    
    available_ts = int(current_ts + ((distance_tu_tr/tu.get_km_hour())*3600) + ((tr.get_distance_ride()/tu.get_km_hour())*3600))
    available_tu_ts[tu.get_name()] = [available_ts, tr.end_lat, tr.end_lon]
    del tr
    return ride_dict, available_tu_ts

def finish_ride(tu, end_lat, end_lon):
    tu.update_state(3)
    tu.update_location(end_lat, end_lon)
    
#input is 1 tr
def find_tu(tr):
    distance_dict = {}
    for tu in Tu._registry:
        if tu.get_state() == 3:
            distance_dict[tu.get_name()] = round(tr.get_distance_to_tu(tu.get_location()),2)
    if len(distance_dict.keys()) > 0 :
        match_tu_str = min(distance_dict, key=distance_dict.get)
        return match_tu_str, distance_dict[match_tu_str]
    else: 
        return -1, -1

def generate_cars(n_cars):
    objs = list()
    for i in range(n_cars):
        name = i
        objs.append(Tu(name=name, lat=53.21720922, lon=6.575406761, person_capacity = 4, battery_state=0.2, battery_capacity=85, 
                     avg_km_per_kwh=7, state=3))
    return objs

def read_rides():
    with open('project_liftoff/ridelisttest.json') as json_data:
        ride_list = json.load(json_data)
        ride_list.sort()        
        ride_list_test = ride_list
    return ride_list_test

def run_simulationset(ride_dict,available_tu_ts):
    for i in range(24*60*60):
        current_ts = datum + i
        if len(ride_list_test) > 0 and current_ts >= ride_list_test[0][0]:
            # now the logic for the ride starts for selecting a transportation unit
            tr = Tr(ride_list_test[0][3], ride_list_test[0][4], ride_list_test[0][5], ride_list_test[0][6], ride_list_test[0][0], 
                   1, ride_list_test[0][2])
            #print(tr)
            del ride_list_test[0]
            waiting_list.append(tr)
        
        waiting_list2 = waiting_list.copy()
        if len(waiting_list2) > 0:
            for tr in waiting_list2:
                match_tu, distance_tu_tr = find_tu(tr)
                if match_tu != -1:
                    ride_dict, available_tu_ts = generate_ride(objs[match_tu], tr, ride_dict, distance_tu_tr, current_ts)
                    waiting_list.remove(tr)
                else:
                    pass
                del match_tu, distance_tu_tr
            #kijk of timestamp overeenkomt met einde rit tijd die terugkomt uit generate_ride
        available_tu_ts2 = available_tu_ts.copy()
        for tu, ts in available_tu_ts2.items():
            if int(current_ts) >= int(ts[0]):
                finish_ride(objs[tu], ts[1], ts[2])
                available_tu_ts.pop(tu, None)
    print(n_cars, sum([x[0] for x in ride_dict]), sum([x[1] for x in ride_dict])/n_rides)
    return n_cars, sum([x[0] for x in ride_dict]), sum([x[1] for x in ride_dict])/n_rides


for iter in range(25):
    objs = generate_cars(n_cars)
    n_cars, km_driven, waiting_time = run_simulationset(ride_dict,available_tu_ts)
    sim_result[1] = {"nr_of_rides": 1000, "avg_wait": waiting_time, "nr_cars": n_cars, "km_driven":km_driven}
    ai_parameters = {"beta_wait": 5, "beta_nr_cars": 100, "beta_km": 1}
    learning_rate = 1.001
    simulation_cost = calc_cost(sim_result[1], ai_parameters)
    simulatietje, n_new_cars = decide_optimal_cars(simulation_list, n_cars, simulation_cost, learning_rate)
    print("For",n_cars, " Transportation Units", "the total cost is:", simulation_cost)
    print("--> AI recommends using", n_new_cars, "Transportation Units")
    n_cars = n_new_cars
    ride_list_test = read_rides()
    ride_dict = []
    available_tu_ts = {}
    sim_result = {}
    class Tu():
        _registry = [] 
        def __init__(self, name, lat, lon, person_capacity = 4, battery_state=0.2, battery_capacity=300, 
                     avg_km_per_kwh=7, state=3, km_hour = 50
                    ):
            "assumes name is string"
            self._registry.append(self)
            self.name = name
            self.lat = lat
            self.lon = lon
            self.person_capacity = person_capacity
            self.battery_state = battery_state
            self.battery_capacity = battery_capacity
            self.avg_km_per_kwh = avg_km_per_kwh
            self.state = state
            self.km_hour = km_hour
        
        def get_name(self):
            return self.name
        
        def get_location(self):
            return(self.lat, self.lon)
    
        def get_battery_state(self):
            return self.battery_state
        
        def get_state(self):
            return self.state
        
        def get_radius(self):
            return self.battery_capacity * self.battery_state * self.avg_km_per_kwh
        
        def get_km_hour(self):
            return self.km_hour
        
        def __str__(self):
            return self.get_name() \
            + ' at lat:' + str(self.get_location()[0]) + ' and lon:' + str(self.get_location()[1])\
            +' radius left:'  + str(self.get_radius())
            
        def update_location(self, lat, lon):
            self.lon = lon
            self.lat = lat
            
        def update_state(self, state):
            self.state = state
    
        def update_capacity(self, capacity):
            self.capacity = capacity
        
    class Tr():
        def __init__(self, start_lat, start_lon, end_lat, end_lon,  request_time, transport_type, request_id, factor_ride=1.5):
            self.start_lat = float(start_lat)
            self.start_lon = float(start_lon)
            self.end_lat = float(end_lat)
            self.end_lon = float(end_lon)
            self.request_id = request_id
            self.transport_type = transport_type
            self.request_time = request_time
            self.factor_ride = factor_ride
        
        def get_distance_ride(self):
            return helper_functions.distance((self.start_lat, self.start_lon),(self.end_lat,self.end_lon)) * self.factor_ride
        
        def get_request_id(self):
            return self.request_id
        
        def get_request_time(self):
            return self.request_time
        
        def get_start_loc(self):
            return(self.start_lat, self.start_lon)
        
        def get_distance_to_tu(self, tu_location):
            #location of transportation unit
            return helper_functions.distance((tu_location[0], tu_location[1]), (self.start_lat, self.start_lon)) * self.factor_ride
        
        def __str__(self):
                 return 'id:' + str(self.get_request_id()) + ' requests a transport at ' \
            + str(self.request_time) +' for ' \
            + str(round(self.get_distance_ride(),3)) + " KM" \
            + ' at '+ str(self.get_start_loc())
            #+ datetime.time.strftime("%Y-%m-%d %H:%M:%S", self.request_time)
            


print("-----------------------")
print("Optimal solution found by AI:", n_cars, "Transportation units used with a total cost of", simulation_cost )    
print("-----------------------") 
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
