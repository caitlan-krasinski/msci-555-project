import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# DATA SETUP
M = 6
R = 3

# key: surgery type, value: list at index 0 is list of surgeons that can do the surgery, index 2 is the length of the surgery 
surgery = {1: [[1,2,3], 3],
        2: [[2,5,6], 0.5],
        3: [[1,2,4], 2], 
        4: [[5,6], 1],
        5: [[5,6], 1],
        6: [[1], 8] }

surgery_names = {'Rhinoplasty': 1,
                'Botox injection': 2,
                'Blepharoplasty': 3,
                'Chin Augmentation': 4,
                'Liposuction': 5,
                'Craniofacial/Reconstructive': 6}

def add_job(surgery_type, pj, wj, mi, J):
    if not J:
        J[1] = {'surgery_type': surgery_type,
                'pj': pj,
                'wj': wj,
                'mi': mi}
    else:
        J[len(J)+1] = {'surgery_type': surgery_type,
                    'pj': pj,
                    'wj': wj,
                    'mi': mi}
    return J

def add_clean_job(surgery_type, pj, wj, mi, J):
    if not J:
        J[1] = {'Surgery Type': surgery_type,
                'Processing Time': pj,
                'Weight': wj,
                'Required Surgeon(s)': mi}
    else:
        J[len(J)+1] = {'Surgery Type': surgery_type,
                    'Processing Time': pj,
                    'Weight': wj,
                    'Required Surgeon(s)': mi}
    return J

# ORDER JOBS BY PRIORITY - WSPT        
def order_jobs(J):
    priorities = {}

    for job in J.keys():
        if float(J[job]['wj']) == 1: # weight of 1 means emergency surgery, therefore is put at front of queue 
            priority = float(10) # set to high number bc of botox short pj
            priorities[job] = priority
        else:
            priority = float(J[job]['wj']) / float(J[job]['pj'])
            priorities[job] = priority

    ordered_priority = dict(sorted(priorities.items(), key=lambda x:x[1], reverse = True))
    return ordered_priority

# ASSIGN JOBS TO MACHINES
def assign_machines(ordered_priority, J):
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
    return J

# SCHEDULING TO ROOMS
def schedule_job(r, job, room_available_at, machines_in_service, machine_available_at, next_time_check, time_in_day, Rk, J, t):
    Rk[r].append({'job': job, 
                    'machine': J[job]['assigned_machine'],
                    'start': t, 
                    'end': t + J[job]['pj'],
                    'type': J[job]['surgery_type']
                    })

    room_available_at[r-1] = t + J[job]['pj'] + 0.5
    machines_in_service[r-1] = J[job]['assigned_machine']
    machine_available_at[r-1] = room_available_at[r-1] - 0.5

    next_time_check = min(room_available_at)

    if t + J[job]['pj'] + 0.5 <= 12:
        time_in_day[r-1] = t + J[job]['pj'] + 0.5
    else:
        time_in_day[r-1] = 0

    if t + J[job]['pj'] + 0.5 < next_time_check:
        next_time_check = t + J[job]['pj'] + 0.5

    return room_available_at, machines_in_service, machine_available_at, next_time_check, time_in_day, Rk


def schedule_rooms(J, ordered_priority):
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
                machines_in_service = [0 if machine_available_at[machines_in_service.index(x)] <= t else x for x in machines_in_service]
                
                # next patient 
                candidate_job = list(remaining_jobs.keys())[0]

                if time_in_day[r-1] + J[candidate_job]['pj'] +  0.5 <= 12 and J[candidate_job]['assigned_machine'] not in machines_in_service: 

                    # accept job
                    job = candidate_job 

                    # schedule job and update lists 
                    room_available_at, machines_in_service, machine_available_at, next_time_check, time_in_day, Rk = schedule_job(r, job, room_available_at, machines_in_service, machine_available_at, next_time_check, time_in_day, Rk, J, t)
                        
                    remaining_jobs.pop(job)
                    if len(remaining_jobs) == 0:
                        break
            
                else:
                    
                    if J[candidate_job]['assigned_machine'] in machines_in_service: # if surgeon busy - check if another applicable one is free
                      
                        if len(set(J[candidate_job]['mi']) - set(machines_in_service)) > 0: # check if another applicable one is free
                            J[candidate_job]['assigned_machine'] = list(set(J[candidate_job]['mi']) - set(machines_in_service))[0]

                        else: 
                            candidate_job = None 
                            for job in remaining_jobs.keys():
                                if time_in_day[r-1] + J[job]['pj'] + 0.5 <= 12 and J[job]['assigned_machine'] not in machines_in_service:
                                    candidate_job = job
                                    break
                        
                    elif time_in_day[r-1] + J[candidate_job]['pj'] +  0.5 <= 12:
        
                        # see if there is another room that can hold it 
                        for r2 in Rk.keys(): 
                            if time_in_day[r2-1] + J[candidate_job]['pj'] +  0.5 <= 12:
                                job = candidate_job 

                                # schedule job and update lists 
                                room_available_at, machines_in_service, machine_available_at, next_time_check, time_in_day, Rk = schedule_job(r2, job, room_available_at, machines_in_service, machine_available_at, next_time_check, time_in_day, Rk, J, t)
                                    
                                remaining_jobs.pop(job)
                                if len(remaining_jobs) == 0:
                                    break
                        
                    else: # see if there is a diff job to use 
                        
                        candidate_job = None 
                        for job in remaining_jobs.keys():
                            if time_in_day[r-1] + J[job]['pj'] + 0.5 <= 12 and J[job]['assigned_machine'] not in machines_in_service:
                                candidate_job = job
                        
                    if candidate_job:

                        # machine_available_at = [t if x <= t else x for x in machine_available_at]
                        machines_in_service = [0 if machine_available_at[machines_in_service.index(x)] <= t else x for x in machines_in_service]

                        job = candidate_job 

                        # schedule job and update lists 
                        room_available_at, machines_in_service, machine_available_at, next_time_check, time_in_day, Rk = schedule_job(r, job, room_available_at, machines_in_service, machine_available_at, next_time_check, time_in_day, Rk, J, t)

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

    return Rk


# PLOT
def plot(Rk):
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
            ax.barh(r-1, duration, height=bar_height, left=job['start'], align='center', alpha=0.5, color=colours[job['type']-1])
            ax.text(job['start'] + duration / 2, r-1, f"Surgeon: {job['machine']}\nPatient: {job['job']}", ha='center', va='center', color='black', size = 15)

    # Add the chart title
    ax.set_title(chart_title)

    day_idxs = [12, 24, 36, 48]
    for x in day_idxs:
        ax.axvline(x=x, color='k', linestyle='--')

    xmin = 0
    xmax = 30
    ax.set_xlim(xmin, xmax)

    st.pyplot(fig)

def app():
    if 'jobs' not in st.session_state:
        st.session_state.jobs = {} # ensures that the jobs are remembered through a user's session https://docs.streamlit.io/library/advanced-features/session-state
    if 'clean_jobs' not in st.session_state:
        st.session_state.clean_jobs = {} # for a readable front end

    st.title('MSCI 555 - Plastic Surgery Scheduling')

    surgery_option = st.selectbox('Please pick surgery you are scheduling', (surgery_names.keys()))

    st.write('You selected:', surgery_option)
    st.write('This is has a processing time of: ', surgery[surgery_names[surgery_option]][1], ' hours')
    mi = surgery[surgery_names[surgery_option]][0]
    if len(mi) == 1:
        st.write('This requires surgeon: ', ', '.join([str(elem) for elem in mi]))
    else:
        st.write('This requires one of the following surgeons: ', ', '.join([str(elem) for elem in mi]))

    weight_option = st.selectbox(
        'Please select the weight of the surgery',
        ('0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1'))

    if st.button('add job'):
        st.session_state.jobs = add_job(surgery_names[surgery_option], surgery[surgery_names[surgery_option]][1], weight_option, mi, st.session_state.jobs)
        st.session_state.clean_jobs = add_clean_job(surgery_option, surgery[surgery_names[surgery_option]][1], weight_option, mi, st.session_state.clean_jobs)
    
    df = pd.DataFrame(st.session_state.clean_jobs) 
    st.table(df)

    if st.button('schedule jobs'):
        ordered_priority = order_jobs(st.session_state.jobs)
        J = assign_machines(ordered_priority, st.session_state.jobs)
        Rk = schedule_rooms(J, ordered_priority)
        plot(Rk)


if __name__ == "__main__":
    app()