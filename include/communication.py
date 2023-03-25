from include import Satellite_class
from include import satcompute
from include import GroundStation_class
from include import visibility
from include import Observation_class
from include.Setting_class import Setting
import sys


# asuum satellite using radio frequencies, because only very less satellite use laser
# high carrier frequencies and narrow beamwidths
# The signal delay approximately 20 ms.

# input:    1. t (time passed from start_time_julian)
#           2. package_size(size of data)
#           3. signal_speed(speed of signal)
#           4. from_sat (the satellite hold the data)
#           5. to_sat (the satellite transfer the data)
#           6. buffer_delay (the sum of the delays that occur at each hop in the network due to cell queuing)
#           7. process_delay (the on-board switching and processing delay from satellite)

# output:   t (the time passed from start_time_julian after commnicate), 
#           when > 0 commnicate success, < 0 fail

# reference https://www.researchgate.net/publication/1961144_Analysis_and_Simulation_of_Delay_and_Buffer_Requirements_of_satellite-ATM_Networks_for_TCPIP_Traffic

def inter_sat_commnicate(t, from_sat: Satellite_class.Satellite, to_sat: Satellite_class.Satellite) -> float:
    transmit_delay = Setting.package_size / Setting.data_rate

    inter_sat_distance = satcompute.inter_sat_distance(t, from_sat, to_sat)

    propagation_delay = inter_sat_distance / Setting.signal_speed   # radio speed near speed of light, 299,792,458 m per second, value in signal_speed is m/s

    total_delay = transmit_delay + propagation_delay + Setting.buffer_delay + Setting.process_delay
    final_t = t + total_delay

    if visibility.is_sat_communicable(final_t, from_sat, to_sat):
        return final_t
    else:
        return -1


# input:    1. t (time passed from start_greenwich, in sec)
#           2. package_size(size of data)
#           3. data_rate (data rate of transmission)
#           4. 
#           5. from_sat (the satellite hold the data)
#           6. to_sat (the satellite transfer the data)
#           7. buffer_delay (the delays that occur at each hop in the network due to cell queuing)
#           8. process_delay (the on-board switching and processing delay from satellite)

# output:   t (the time passed from start_time_julian after commnicate), 
#           when > 0 commnicate success, < 0 fail

def sat_ground_commnicate(t, sat: Satellite_class.Satellite, ground_station: GroundStation_class.GroundStation) -> float:

    transmit_delay = Setting.package_size / Setting.data_rate

    distance = satcompute.sat_ground_distance(t, sat, ground_station)

    propagation_delay = distance / Setting.signal_speed        # radio speed near speed of light, 299,792,458 m per second, value in signal_speed is m/s

    total_delay  = transmit_delay + propagation_delay + Setting.buffer_delay + Setting.process_delay
    final_t = t + total_delay

    if visibility.is_gs_communicable(final_t, sat, ground_station):
        return final_t
    else:
        return -1

# A*(distance as cost)
# input:    1. sat_list
#           2. gd
#           3. gs
#           4. offnadir

# output:   1. sat_commnicate_path
#           2. sat_commnicate_delay
def astar_path_decision(sat_list: list, gd: Observation_class.Observation, gs: GroundStation_class.GroundStation):

    t = 0

    imaging_sat = -1
    # search for all sat
    for s in range(len(sat_list)):
        if visibility.is_observation_visible(0, sat_list[s], gd):
            imaging_sat = s
            break

    # if no any satellite obervate the obervation point, exit
    if imaging_sat == -1:
        print("No Satellite able to visit the observation point!!")
        sys.exit(-1)


    # no able to directly transfer data from obervation satellite to ground station
    sat_commnicate_path = []
    sat_commnicate_path.append(imaging_sat)
    sat_commnicate_delay = []
    sat_commnicate_delay.append(0)
    sat_num = 0         #index of the last element in sat_commnicate_path and sat_commnicate_delay
    cost = 0

    end_path = False
    while end_path == False:
        ignore_sat = []
        ignore = True
        while ignore == True:
            min_distance = 999999999999     # store the min distance from next satellite to gs
            min_distance_sat = -1            # store the min distance satellite object index
            distance = -1

            for s in range(len(sat_list)):      # avoid the sat not able to communicate
                if s not in ignore_sat and s not in sat_commnicate_path:
                    if visibility.is_sat_communicable(t, sat_list[sat_commnicate_path[sat_num]], sat_list[s]):
                        # estimated
                        distance = satcompute.sat_ground_distance(t, sat_list[s], gs)

                        # add the cost
                        distance += cost
                        
                        if distance < min_distance:
                            min_distance = distance
                            min_distance_sat = s

            # has sat in vibility
            if min_distance_sat != -1:
                temp = inter_sat_commnicate(t, sat_list[sat_commnicate_path[sat_num]], sat_list[min_distance_sat])
                if temp > 0:
                    # commnicate success
                    t = temp
                    sat_commnicate_path.append(min_distance_sat)
                    sat_num += 1
                    ignore = False
                    cost += min_distance

                    # insert delay
                    sat_commnicate_delay.append(t)

                    if visibility.is_gs_communicable(t, sat_list[sat_commnicate_path[sat_num]], gs) == True:
                        temp = sat_ground_commnicate(t, sat_list[sat_commnicate_path[sat_num]], gs)
                        if temp > 0:
                            t = temp
                            end_path = True

                            sat_commnicate_path.append("gs")
                            sat_commnicate_delay.append(t)
                        else:
                            end_path = False

                else:
                    # commnication fail, loop again and ignore that sat
                    ignore = True
                    ignore_sat.append(min_distance_sat)
                    
            # wait 1 sec and check visibility again
            else:
                    end_path = False
                    t += 1
                    sat_commnicate_path.append(-1)  # mean waiting
                    sat_commnicate_delay.append(t)
                    print("No other Satellites in the visibility, wait 1 sec.")

    return (sat_commnicate_path, sat_commnicate_delay)


# orbit base algo
# idea, find by lon or orbit.
def orbit_path_decision(sat_list: list, gd: Observation_class.Observation, gs: GroundStation_class.GroundStation, sat_per_orbit: int):
    t = 0

    imaging_sat = -1
    # search for all sat
    for s in range(len(sat_list)):
        if visibility.is_observation_visible(0, sat_list[s], gd):
            imaging_sat = s
            break

    # if no any satellite obervate the obervation point, exit
    if imaging_sat == -1:
        print("No Satellite able to visit the observation point!!")
        sys.exit(-1)


    # no able to directly transfer data from obervation satellite to ground station
    sat_commnicate_path = []
    sat_commnicate_path.append(imaging_sat)
    sat_commnicate_delay = []
    sat_commnicate_delay.append(0)
    sat_num = 0         #index of the last element in sat_commnicate_path and sat_commnicate_delay
    max_orbit = len(sat_list)//sat_per_orbit 
    max_sat = max_orbit * sat_per_orbit

    orbit_num = sat_commnicate_path[sat_num] // sat_per_orbit

    end_path = False
    while end_path == False:
        ignore_sat = []
        ignore = True
        while ignore == True:
            min_distance = 999999999999      # store the min distance from next satellite to gs
            min_distance_sat = -1            # store the min distance satellite object index
            distance = -1

            # the algo ignore the current orbit
            for s in range((orbit_num - 1)*sat_per_orbit, orbit_num*sat_per_orbit):      # avoid the sat not able to communicate
                if s >= max_sat:
                    s -= max_sat
                elif s < 0:
                    s += max_sat

                if s not in ignore_sat and s not in sat_commnicate_path:
                    if visibility.is_sat_communicable(t, sat_list[sat_commnicate_path[sat_num]], sat_list[s]):
                        distance = satcompute.sat_ground_distance(t, sat_list[s], gs)
                        if distance < min_distance:
                            min_distance = distance
                            min_distance_sat = s

            for s in range((orbit_num + 1)*sat_per_orbit, (orbit_num + 2)*sat_per_orbit):      # avoid the sat not able to communicate
                if s >= max_sat:
                    s -= max_sat
                elif s < 0:
                    s += max_sat

                if s not in ignore_sat and s not in sat_commnicate_path:
                    if visibility.is_sat_communicable(t, sat_list[sat_commnicate_path[sat_num]], sat_list[s]):
                        distance = satcompute.sat_ground_distance(t, sat_list[s], gs)
                        if min_distance == -1:
                            min_distance = distance
                            min_distance_sat = s
                        elif distance < min_distance:
                            min_distance = distance
                            min_distance_sat = s

            # has sat in vibility
            if min_distance_sat != -1:
                temp = inter_sat_commnicate(t, sat_list[sat_commnicate_path[sat_num]], sat_list[min_distance_sat])
                if temp > 0:
                    # commnicate success
                    t = temp
                    sat_commnicate_path.append(min_distance_sat)
                    sat_num += 1
                    orbit_num = min_distance_sat // sat_per_orbit


                    ignore = False

                    # insert delay
                    sat_commnicate_delay.append(t)

                    if visibility.is_gs_communicable(t, sat_list[sat_commnicate_path[sat_num]], gs) == True:
                        temp = sat_ground_commnicate(t, sat_list[sat_commnicate_path[sat_num]], gs)
                        if temp > 0:
                            t = temp
                            end_path = True

                            sat_commnicate_path.append("gs")
                            sat_commnicate_delay.append(t)
                        else:
                            end_path = False

                else:
                    # commnication fail, loop again and ignore that sat
                    ignore = True
                    ignore_sat.append(min_distance_sat)
                    
            # wait 1 sec and check visibility again
            else:
                    end_path = False
                    t += 1
                    sat_commnicate_path.append(-1)  # mean waiting
                    sat_commnicate_delay.append(t)
                    print("No other Satellites in the visibility, wait 1 sec.")

    return (sat_commnicate_path, sat_commnicate_delay)


# Dijkstra
def dijkstra_path_decision(sat_list: list, gd: Observation_class.Observation, gs: GroundStation_class.GroundStation):
    t = 0

    imaging_sat = -1
    # search for all sat
    for s in range(len(sat_list)):
        if visibility.is_observation_visible(0, sat_list[s], gd):
            imaging_sat = s
            break

    # if no any satellite obervate the obervation point, exit
    if imaging_sat == -1:
        print("No Satellite able to visit the observation point!!")
        sys.exit(-1)

    end_path = False
    sat_commnicate_path = []
    sat_commnicate_path.append(imaging_sat)
    sat_commnicate_delay = []
    sat_commnicate_delay.append(0)
    sat_num = 0

    while end_path == False:

        su = [0] * len(sat_list)
        su[sat_commnicate_path[0]] = 1
        dis = [999999999999] * len(sat_list)
        path = [[]]* len(sat_list)

        for s in range(len(sat_list)):
            if s != sat_commnicate_path[sat_num]:
                if visibility.is_sat_communicable(t, sat_list[sat_commnicate_path[sat_num]], sat_list[s]):
                    dis[s] = satcompute.inter_sat_distance(t, sat_list[s], sat_list[sat_commnicate_path[sat_num]])
                    path[s] = [sat_commnicate_path[sat_num], s]


        for _ in range(len(sat_list)):      # avoid the sat not able to communicate
            min_distance = 999999999999
            min_distance_sat = -1            # store the min distance satellite object index
            
            for j in range(len(sat_list)): 
                if su[j] == 0 and dis[j] < min_distance:
                    min_distance = dis[j]
                    min_distance_sat = j

            if min_distance_sat != -1:
                su[min_distance_sat] = 1

                for k in range(len(sat_list)):
                    if k != min_distance_sat:
                        if visibility.is_sat_communicable(t, sat_list[min_distance_sat], sat_list[k]):
                            if dis[k] > dis[min_distance_sat] + satcompute.inter_sat_distance(t, sat_list[min_distance_sat], sat_list[k]):
                                dis[k] = dis[min_distance_sat] + satcompute.inter_sat_distance(t, sat_list[min_distance_sat], sat_list[k])
                                path[k] = path[min_distance_sat] + [k]

        end = -1
        for i in range(len(sat_list)):
            if visibility.is_gs_communicable(t, sat_list[i], gs):
                end = i
                break

        if len(path[end]) > 0:
            for s in range(len(path[end])-1):
                if visibility.is_sat_communicable(t, sat_list[path[end][s]], sat_list[path[end][s+1]]):
                    temp = inter_sat_commnicate(t, sat_list[path[end][s]], sat_list[path[end][s+1]])
                    if temp > 0:
                        t = temp
                        sat_commnicate_path.append(path[end][s+1])
                        sat_num += 1

                        sat_commnicate_delay.append(t)
                        end_path = True

                    else:
                        # communicate fail, continuous looping, s as the start point
                        end_path = False
                        break
                
            if visibility.is_gs_communicable(t, sat_list[path[end][-1]], gs) == True:
                temp = sat_ground_commnicate(t, sat_list[path[end][-1]], gs)
                if temp > 0:
                    t = temp
                    end_path = True

                    sat_commnicate_path.append("gs")
                    sat_commnicate_delay.append(t)
                else:
                    end_path = False
        else:
            end_path = False
            t += 1
            sat_commnicate_path.append(-1)  # mean waiting
            sat_commnicate_delay.append(t)
            print("No other Satellites in the visibility, wait 1 sec.")

    return (sat_commnicate_path, sat_commnicate_delay)