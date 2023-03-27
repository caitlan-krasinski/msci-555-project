# DATA SETUP
M = 4
R = 3

# key: surgery type, value: list at index 0 is list of surgeons that can do the surgery, index 2 is the length of the surgery 
surgery = {1: [[1,2], 5],
            2: [[2,3], 3],
            3: [[4], 1], 
            4: [[1,2,3], 6],
            5: [[2,3], 3],
            6: [[1], 8] }



# setup: {patient id: {'surgery_type': surgery_id,
                # 'pj': surgery[surgery_id][1],
                # 'wj': 0.5,
                # 'mi': surgery[surgery_id][0]}}

def add_job(surgery_type, pj, wj, mi):
    if J is not None:
        J[len(J)+1] = {'surgery_type': surgery_type,
                    'pj': pj,
                    'wj': wj,
                    'mi': mi}
        J
        return J
    else:
        J[1] = {'surgery_type': surgery_type,
                'pj': pj,
                'wj': wj,
                'mi': mi}
        J
        return J
        

# J = {1: {'surgery_type': 1,
#         'pj': surgery[1][1],
#         'wj': 0.5,
#         'mi': surgery[1][0]},
#     2: {'surgery_type': 2,
#         'pj': surgery[2][1], 
#         'wj': 0.1,
#         'mi': surgery[2][0]},
#     3: {'surgery_type': 3,
#         'pj': surgery[3][1],
#         'wj': 0.8,
#         'mi': surgery[3][0]},
#     4: {'surgery_type': 4,
#         'pj': surgery[4][1],
#         'wj': 0.3,
#         'mi': surgery[4][0]},
#     5: {'surgery_type': 3,
#         'pj': surgery[3][1],
#         'wj': 0.5,
#         'mi': surgery[3][0]},
#     6: {'surgery_type': 3,
#         'pj': surgery[3][1],
#         'wj': 0.3,
#         'mi': surgery[3][0]}, 
#     7: {'surgery_type': 5,
#         'pj': surgery[5][1],
#         'wj': 0.6,
#         'mi': surgery[5][0]},
#     8: {'surgery_type': 5,
#         'pj': surgery[5][1],
#         'wj': 0.8,
#         'mi': surgery[5][0]},
#     9: {'surgery_type': 6,
#         'pj': surgery[6][1],
#         'wj': 1,
#         'mi': surgery[6][0]},
#     10: {'surgery_type': 5,
#         'pj': surgery[5][1],
#         'wj': 0.3,
#         'mi': surgery[5][0]}
#     }

# CREATING SELECT BOX
# import streamlit as st

# J = {}

# def app():
#     global J
    
#     surgery_option = st.selectbox(
#         'Please pick surgery you are scheduling',
#         (surgery.keys()))

#     st.write('You selected:', surgery_option)
#     st.write('This is has a processing time of: ', surgery[surgery_option][1])
#     s = surgery[surgery_option][0]
#     st.write('This requires surgeons: ', ' '.join([str(elem) for elem in s]))

#     weight_option = st.selectbox(
#         'Please select the weight of the surgery',
#         ('0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9'))

#     if st.button('add job'):
#         J = add_job(surgery_option, surgery[surgery_option][1], weight_option, surgery[surgery_option][0])
#         st.write(len(J))

# if __name__ == "__main__":
#     app()

import streamlit as st

# Define global dictionary variable
my_dict = {}

# Function to add to the dictionary
def add_to_dict(key, value):
    global my_dict
    my_dict[key] = value

# Streamlit app
def app():
    global my_dict
    st.write("My Dictionary:", my_dict)
    key = st.text_input("Enter Key:")
    value = st.text_input("Enter Value:")
    if st.button("Add to Dictionary"):
        add_to_dict(key, value)
        st.write("Added to Dictionary!")

if __name__ == "__main__":
    app()

# ORDER JOBS BY PRIORITY - WSPT
def order_jobs():
    priorities = {}

    for job in J.keys():
        if J[job]['wj'] == 1: # weight of 1 means emergency surgery, therefore is put at front of queue 
            priority = 1
            priorities[job] = priority
        else:
            priority = J[job]['wj'] / J[job]['pj']
            priorities[job] = priority

    ordered_priority = dict(sorted(priorities.items(), key=lambda x:x[1], reverse = True))
    ordered_priority

# ASSIGN JOBS TO MACHINES
def assign_machines():
    Mi = {}
    for m in range(1, M+1):
        Mi[m] = []

    for job in ordered_priority.keys():
        len_of_assigned_machine = 1000
        machine_assignment = 0
        for m in J[job]['mi']:
            if len(Mi[m]) < len_of_assigned_machine:
                machine_assignment = m
                len_of_assigned_machine = len(Mi[m])

        Mi[machine_assignment].append(job)
        J[job]['assigned_machine'] = machine_assignment

# SCHEDULING TO ROOMS
def schedule_rooms():
    Rk = {} #room scheduling object 
    room_available_at = [] # when is room (index) available 
    machines_in_service = [] # what machines (value) are in what room (index)
    machine_available_at = [] # when (value) is the machine (index corresponding to above list) avaialble at 
    time_in_day = [] # time of day (value) when checking in on a room (index)

    for r in range(1, R+1):
        Rk[r] = []
        room_available_at.append(0)
        machines_in_service.append(0)
        machine_available_at.append(0)
        time_in_day.append(0)


    # copy of dict to remove from 
    remaining_jobs = ordered_priority.copy()

    # start time 
    t = 0
    while t <= 60 and len(remaining_jobs) != 0:
        
        next_time_check = min(room_available_at)

        # check in each room 
        for r in Rk.keys():

            # check to see if room is available or still in use - else try again later 
            if room_available_at[r-1] <= t:

                # remove sergeons from room if they are done prev surgery 
                machine_available_at = [t if x <= t else x for x in machine_available_at]
                machines_in_service = [0 if machine_available_at[machines_in_service.index(x)] <= t else x for x in machines_in_service]
                
                # next patient 
                candidate_job = list(remaining_jobs.keys())[0]

                if time_in_day[r-1] + J[candidate_job]['pj'] +  0.5 <= 12 and J[candidate_job]['assigned_machine'] not in machines_in_service:
                    
                    # accept job
                    job = candidate_job 
                
                    # add surgeon start and end times to room list 
                    Rk[r].append({'job': job, 
                        'machine': J[job]['assigned_machine'],
                        'start': t, 
                        'end': t + J[job]['pj']
                        })

                    room_available_at[r-1] = t + J[job]['pj'] + 0.5
                    machines_in_service[r-1] = J[job]['assigned_machine']
                    machine_available_at[r-1] = t + J[job]['pj']
                    next_time_check = min(room_available_at)

                    if t + J[job]['pj'] + 0.5 <= 12:
                        time_in_day[r-1] = t + J[job]['pj'] + 0.5
                    else:
                        time_in_day[r-1] = 0

                    if t + J[job]['pj'] + 0.5 < next_time_check:
                        next_time_check = t + J[job]['pj'] + 0.5
                        
                    remaining_jobs.pop(job)
                    if len(remaining_jobs) == 0:
                        break
            
                else:

                    candidate_job = None 
                    for job in remaining_jobs.keys():
                        if time_in_day[r-1] + J[job]['pj'] + 0.5 <= 12 and J[job]['assigned_machine'] not in machines_in_service:
                            candidate_job = job
                            
                    if candidate_job:
        
                        job = candidate_job 

                        Rk[r].append({'job': job, 
                        'machine': J[job]['assigned_machine'],
                        'start': t, 
                        'end': t + J[job]['pj']
                        })

                        room_available_at[r-1] = t + J[job]['pj'] + 0.5
                        machines_in_service[r-1] = J[job]['assigned_machine']
                        machine_available_at[r-1] = t + J[job]['pj']
                        next_time_check = min(room_available_at)

                        if t + J[job]['pj'] + 0.5 <= 12:
                            time_in_day[r-1] = t + J[job]['pj'] + 0.5
                        else:
                            time_in_day[r-1] = 0

                        if t + J[job]['pj'] + 0.5 < next_time_check:
                            next_time_check = t + J[job]['pj'] + 0.5
                            
                        remaining_jobs.pop(job)
                        if len(remaining_jobs) == 0:
                            break

                    else:
                        next_time_check = 12 * (1 + int((t - 1) / 12)) # go to next day
                            
                        time_in_day[r-1] = 0 
                        
                        room_available_at[r-1] = next_time_check
                        machine_available_at[r-1] = next_time_check
                        machines_in_service[r-1] = 0


        t = next_time_check

    Rk

# PLOT
def plot():
    import matplotlib.pyplot as plt

    # Define chart parameters
    chart_title = "Schedule"
    bar_height = 0.4
    bar_color1 = 'blue'
    bar_color2 = 'green'

    colours = ['c', 'm', 'g', 'r', 'b', 'y']

    # Set up the chart
    fig, ax = plt.subplots(figsize=(30, 8))

    # Set up the y-axis
    ylabels = [f"Room {i+1}" for i in range(R)]
    ypos = range(R)
    ax.set_yticks(ypos)
    ax.set_yticklabels(ylabels)
    ax.tick_params(axis='y', length=0)

    for r in Rk.keys():
        jobs_in_room = Rk[r]
        for job in jobs_in_room:
            duration = job['end'] - job['start']
            ax.barh(r-1, duration, height=bar_height, left=job['start'], align='center', alpha=0.5, color=colours[job['machine']-1])
            ax.text(job['start'] + duration / 2, r-1, f"Surgeon: {job['machine']}\nPatient: {job['job']}", ha='center', va='center', color='black', size = 15)

    # Add the chart title
    ax.set_title(chart_title)

    day_idxs = [12, 24, 36, 48]
    for x in day_idxs:
        ax.axvline(x=x, color='k', linestyle='--')

    xmin = 0
    xmax = 60
    ax.set_xlim(xmin, xmax)
