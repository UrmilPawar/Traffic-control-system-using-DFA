#-------------------------------------------------------Importing Libraries--------------------------------------------------------------------
import pickle
import random
import time
from interval_timer import IntervalTimer

#-----------------------------------------------Defining the States and the transition-----------------------------------------------------------

valid_entries={0,1,2}
state='q0'

states = {'q0', 'q1', 'q2','q3'}
pair_states={'q0': 'q1', 'q1': 'q0','q2': 'q3', 'q3': 'q2'}
alphabet = {'V','H','B','N'}
trans_function = {
            'q0': {'V': 'q2', 'H': 'q1','B': 'q2', 'N': 'q4'},
            'q1': {'V': 'q0', 'H': 'q3','B': 'q3', 'N': 'q4'},
            'q2': {'V': 'q0', 'H': 'q1','B': 'q0', 'N': 'q4'},
            'q3': {'V': 'q0', 'H': 'q1','B': 'q1', 'N': 'q4'},
            'q4': {'V': 'q0', 'H': 'q1','B': 'q0', 'N': 'q4'}
           }
start_state = 'q0'
final_state = {'q4'}

repeat = {'state': 'q0', 'time': 0}          #initilizing with random state and number of time it has occured

with open('repeat.pickle', 'wb') as file:    #saving the dictionary locally
    pickle.dump(repeat, file)
#---------------------------------------------------Defining Necessary Functions------------------------------------------------------------------------
#Function for determining direction of traffic
def direction(input):
    V=input[0] or input[2]  #checking Traffic in vertical direction
    H=input[1] or input[3]  #Checking traffic in horizontal direction
    B=V and H               #checking traffic in both directions

    if B==0:                #if trafffic is there only in one diection 
        if V==1:            #check for Vertical direction
            return 'V'
        elif H==1:
            return 'H'      #Check for Horizontal direction
        else:
            return 'N'      #If traffuc in none of the direction 
    else:
        return 'B'

#Function for determining next state of signal and updating the previous state 
def transition(input,previous_state,direction):
    new_state = trans_function[previous_state][direction]
    if new_state!='q4':
        if input[int(new_state[1])]==0:                           #Eliminating wastage of time on empty rooads(checking if the road is empty or not)
            new_state = transition(input,new_state,direction)     #If road is empty then selecting the oppossing road
    return new_state

def updation(new_state): 
    #updating the previous state
    with open('repeat.pickle', 'rb') as file:               
        loaded_repeat = pickle.load(file)
    if loaded_repeat['state'] == new_state:                         #if previous state is same as current state
        loaded_repeat['time']  += 1
    else:
        loaded_repeat['state'] = new_state
        loaded_repeat['time']  = 1 
    print('Updated_data:',loaded_repeat)
    with open('repeat.pickle', 'wb') as file:                       #saving the updated dictionary locally
        pickle.dump(loaded_repeat, file) 

#function for dealing with the emergency cases
def replace(input):
    for i in range(len(input)):
        if input[i]==1 or input[i]==0:
            input[i]=0
        else:
            input[i]=1
    return input

#function to check the valid input
def isvalid(input):
    if len(input)!=4 or any(x not in valid_entries for x in input): #if input length is greater or smaller than 4 or any entry doesnt matxh with expected input values
        return False
    else:
        return True

#Eliminating Bias on only one road when direct='B'
def repetetion(new_state):                               
        with open('repeat.pickle', 'rb') as file:                         #opening the file to heck the previous states and its repetetion
           loaded_repeat = pickle.load(file)
        loaded_state = loaded_repeat['state']       
        loaded_time = loaded_repeat['time']
        if loaded_state == new_state:                                     #if previous state is same as current state
            if loaded_time >= 3:                                          #checking if the repetation is moe than 3 
                 oppose_states=pair_states[new_state]                     #Switching the signal from vertical to horizontal to vertical
                 new_state=transition(input,oppose_states,'B')            #ensuring that transition occur on proper road(not on empty road)       
        return new_state     

#------------------------------------------------------- Defining the main function--------------------------------------------------------------------------
def traffic(input,previous_state):
    if isvalid(input):
        if any(x == 2 for x in input):
            input=replace(input)
        direct=direction(input)
        print('Direction-detected:',direct)
        new_state=transition(input,previous_state,direct)
        if direct=='B':
          new_state=repetetion(new_state)
        updation(new_state)
        print('Current_state',new_state)
    else:
        new_state='q4'
        updation(new_state)
        print('q4')

#------------------------------------------------------Making an input pipeline----------------------------------------------------------------------------
inputs=[]
for interval in IntervalTimer(1):                         #Iterating with respect to time from 0
    input = [random.choice([0, 1]) for i in range(4)]     #Generating random inputs provided by the sensors
    inputs.append(input)                                  #Storing the contionus inputs
    if (interval.time) % 5 == 0:                          #for every 5th second
        with open('repeat.pickle', 'rb') as file:         #opening the file and loading the previous state
                loaded_repeat = pickle.load(file)
        print('Previous_state:',loaded_repeat['state'])  
        print('Input-received:',inputs[-1])               #Selecting the last(latest) input
        traffic(inputs[-1],loaded_repeat['state'])        #Making the transition
        inputs=[]                                         #Flushing remaining inputs
        print('\n')  

