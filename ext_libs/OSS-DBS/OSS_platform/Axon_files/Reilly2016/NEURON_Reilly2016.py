# -*- coding: utf-8 -*-
"""
Created on Mon Jan  7 13:49:24 2019

@author: butenko
"""
import h5py
import os
import neuron as n
import numpy as np
from pandas import read_csv
import matplotlib.pyplot as plt

import time as tm
import multiprocessing as mp

#from Axon_files.axon import Axon

from Axon_files.Reilly2016.Parameter_insertion_python3 import paste_to_hoc_python3, paste_paraview_vis_python3

# this script is solely for Reilly2016 model

#This function only saves the dictionary of the activation rate, the visualizator is called externally outside of docker container!
#IMPORTANT: if same connections of different branches will be united (otherwise, the circuit image is unreadable).
#In this case, the activation rate will be assessed as
def connection_visualizator(Activated_models,Initial_number,population_name,iteration):

    import pickle

    if iteration == 0:
        #create and save a dictionary
        dict_connect = {   #connection might be formed from different branches. Therefore, we weight the activation with number of the branches (second entry)
        'HDP_MC_STN'                    :  [0.0,0] ,
        'HDP_STN_GPi'                    :  [0.0,0] ,
        'HDP_STN_SN'                    :  [0.0,0] ,

        'Direct_MC_Str'                    :  [0.0,0] ,
        'Direct_Str_GPi'                    :  [0.0,0] ,
        'Direct_Str_SN'                    :  [0.0,0] ,

        'Indirect_MC_Str'                    :  [0.0,0] ,
        'Indirect_Str_GPe'                    :  [0.0,0] ,
        'Indirect_GPe_GPi'                    :  [0.0,0] ,
        'Indirect_GPe_STN'                    :  [0.0,0] ,
        'Indirect_GPe_SN'                    :  [0.0,0] ,
        'Indirect_STN_GPi'                    :  [0.0,0] ,
        'Indirect_STN_SN'                    :  [0.0,0] ,

        'Excitatory_STN_GPe'                  :  [0.0,0] ,
        'Inhibitory_GPi_Th'                  :  [0.0,0] ,
        'Inhibitory_SN_Th'                  :  [0.0,0] ,
        }
        #for each of these I need an if statement
    else:
        #reload it and update according to the name of the connection
        with open('connections_status.pkl', "rb") as f:
            dict_connect = pickle.load(f)

    mask_designator='_mask'   #required to distinguish structures for a specific connection in case all masks of the pathway are used for naming

    if "Indirect" in population_name:
        if "STN"+mask_designator in population_name and "GPe"+mask_designator in population_name:
            dict_connect['Indirect_GPe_STN'][0]=float(Activated_models)/Initial_number+dict_connect['Indirect_GPe_STN'][0]
            dict_connect['Indirect_GPe_STN'][1]+=1
        if "STN"+mask_designator in population_name and "GPi"+mask_designator in population_name:
            dict_connect['Indirect_STN_GPi'][0]=float(Activated_models)/Initial_number+dict_connect['Indirect_STN_GPi'][0]
            dict_connect['Indirect_STN_GPi'][1]+=1
        if "STN"+mask_designator in population_name and "SN"+mask_designator in population_name:
            dict_connect['Indirect_STN_SN'][0]=float(Activated_models)/Initial_number+dict_connect['Indirect_STN_SN'][0]
            dict_connect['Indirect_STN_SN'][1]+=1
        if "GPi"+mask_designator in population_name and "GPe"+mask_designator in population_name:
            dict_connect['Indirect_GPe_GPi'][0]=float(Activated_models)/Initial_number+dict_connect['Indirect_GPe_GPi'][0]
            dict_connect['Indirect_GPe_GPi'][1]+=1
        if "SN"+mask_designator in population_name and "GPe"+mask_designator in population_name:
            dict_connect['Indirect_GPe_SN'][0]=float(Activated_models)/Initial_number+dict_connect['Indirect_GPe_SN'][0]
            dict_connect['Indirect_GPe_SN'][1]+=1
        if "MC"+mask_designator in population_name and "Str"+mask_designator in population_name:
            dict_connect['Indirect_MC_Str'][0]=float(Activated_models)/Initial_number+dict_connect['Indirect_MC_Str'][0]
            dict_connect['Indirect_MC_Str'][1]+=1
        if "Str"+mask_designator in population_name and "GPe"+mask_designator in population_name:
            dict_connect['Indirect_Str_GPe'][0]=float(Activated_models)/Initial_number+dict_connect['Indirect_Str_GPe'][0]
            dict_connect['Indirect_Str_GPe'][1]+=1
    elif "Direct" in population_name:
        if "MC"+mask_designator in population_name and "Str"+mask_designator in population_name:
            dict_connect['Direct_MC_Str'][0]=float(Activated_models)/Initial_number+dict_connect['Direct_MC_Str'][0]
            dict_connect['Direct_MC_Str'][1]+=1
        if "Str"+mask_designator in population_name and "GPi"+mask_designator in population_name:
            dict_connect['Direct_Str_GPi'][0]=float(Activated_models)/Initial_number+dict_connect['Direct_Str_GPi'][0]
            dict_connect['Direct_Str_GPi'][1]+=1
        if "Str"+mask_designator in population_name and "SN"+mask_designator in population_name:
            dict_connect['Direct_Str_SN'][0]=float(Activated_models)/Initial_number+dict_connect['Direct_Str_SN'][0]
            dict_connect['Direct_Str_SN'][1]+=1
    elif "HDP" in population_name:
        if "MC"+mask_designator in population_name and "STN"+mask_designator in population_name:
            dict_connect['HDP_MC_STN'][0]=float(Activated_models)/Initial_number+dict_connect['HDP_MC_STN'][0]
            dict_connect['HDP_MC_STN'][1]+=1
    else:
        if "STN"+mask_designator in population_name and "GPe"+mask_designator in population_name:
            dict_connect['Excitatory_STN_GPe'][0]=float(Activated_models)/Initial_number+dict_connect['Excitatory_STN_GPe'][0]
            dict_connect['Excitatory_STN_GPe'][1]+=1
        if "GPi"+mask_designator in population_name and "Th"+mask_designator in population_name:
            dict_connect['Inhibitory_GPi_Th'][0]=float(Activated_models)/Initial_number+dict_connect['Inhibitory_GPi_Th'][0]
            dict_connect['Inhibitory_GPi_Th'][1]+=1
        if "SN"+mask_designator in population_name and "Th"+mask_designator in population_name:
            dict_connect['Inhibitory_SN_Th'][0]=float(Activated_models)/Initial_number+dict_connect['Inhibitory_SN_Th'][0]
            dict_connect['Inhibitory_SN_Th'][1]+=1

    f = open("connections_status.pkl","wb")
    pickle.dump(dict_connect,f)
    f.close()

    return True

def get_one_internodal(N_index,n_segments,last_point,n_Ranvier,Ampl_scale,fiberD):
    os.chdir("..")
    os.chdir("..")
    nodes=[]
    #here we need to load potential only on Ranviers and middle STIN
    if fiberD>3.0:         #load 5th and 6th compartment (middle STINs) and take average
        for point_inx in range(n_segments):
            if point_inx%11==0:
                loc_index=0
                nodes_point_in_time=np.load('/opt/Patient/Points_in_time/Signal_t_conv'+str(point_inx+N_index*n_segments+last_point)+'.npy')
                nodes.append(nodes_point_in_time*(1000)*Ampl_scale)    #convert to mV
            elif loc_index%6==0 and loc_index!=0:
                nodes_point_in_time_left=np.load('/opt/Patient/Points_in_time/Signal_t_conv'+str(point_inx+N_index*n_segments+last_point-1)+'.npy')
                nodes_point_in_time_right=np.load('/opt/Patient/Points_in_time/Signal_t_conv'+str(point_inx+N_index*n_segments+last_point)+'.npy')

                #nodes_point_in_time_left=np.asarray(nodes_point_in_time_left)
                #nodes_point_in_time_left = nodes_point_in_time_left.ravel()

                #nodes_point_in_time_right=np.asarray(nodes_point_in_time_right)
                #nodes_point_in_time_right = nodes_point_in_time_right.ravel()

                nodes_point_in_time=(nodes_point_in_time_left[:]+nodes_point_in_time_right[:])/2

                nodes.append((nodes_point_in_time)*(1000)*Ampl_scale)    #convert to mV
            loc_index+=1
    else:
        for point_inx in range(n_segments):     #take every forth compartment (either Ranvier or middle STIN)
            if point_inx%4==0:
                nodes_point_in_time=np.load('/opt/Patient/Points_in_time/Signal_t_conv'+str(point_inx+N_index*n_segments+last_point)+'.npy')
                nodes.append(nodes_point_in_time*(1000)*Ampl_scale)    #convert to mV

    nodes=np.asarray(nodes)
    nodes = nodes.ravel()

    return nodes

def conduct_parallel_NEURON(population_name,last_point,N_index_glob,N_index,Ampl_scale,t_steps,n_segments,dt,tstop,n_pulse,v_init,n_Ranvier,output):

    # #This is the old method when I did not have a specific array for Reilly
    #os.chdir("..")
    # os.chdir("..")
    # nodes=[]
    # #here we need to load the potential only on Ranviers and middle STIN
    # if fiberD>3.0:         #load 5th and 6th compartment (middle STINs) and take average
    #     for point_inx in range(n_segments):
    #         if point_inx%11==0:
    #             loc_index=0
    #             nodes_point_in_time=np.load('Points_in_time/Signal_t_conv'+str(point_inx+N_index*n_segments+last_point)+'.npy')
    #             nodes.append(nodes_point_in_time*(1000)*Ampl_scale)    #convert to mV
    #         elif loc_index%6==0 and loc_index!=0:
    #             nodes_point_in_time_left=np.load('Points_in_time/Signal_t_conv'+str(point_inx+N_index*n_segments+last_point-1)+'.npy')
    #             nodes_point_in_time_right=np.load('Points_in_time/Signal_t_conv'+str(point_inx+N_index*n_segments+last_point)+'.npy')

    #             #nodes_point_in_time_left=np.asarray(nodes_point_in_time_left)
    #             #nodes_point_in_time_left = nodes_point_in_time_left.ravel()

    #             #nodes_point_in_time_right=np.asarray(nodes_point_in_time_right)
    #             #nodes_point_in_time_right = nodes_point_in_time_right.ravel()

    #             nodes_point_in_time=(nodes_point_in_time_left[:]+nodes_point_in_time_right[:])/2

    #             nodes.append((nodes_point_in_time)*(1000)*Ampl_scale)    #convert to mV
    #         loc_index+=1
    # else:
    #     for point_inx in range(n_segments):     #take every forth compartment (either Ranvier or middle STIN)
    #         if point_inx%4==0:
    #             nodes_point_in_time=np.load('Points_in_time/Signal_t_conv'+str(point_inx+N_index*n_segments+last_point)+'.npy')
    #             nodes.append(nodes_point_in_time*(1000)*Ampl_scale)    #convert to mV

    # nodes=np.asarray(nodes)
    # nodes = nodes.ravel()

    # V_art=np.zeros((n_Ranvier*2-1,t_steps),float)
    # for i in range(n_Ranvier*2-1):
    #     V_art[i,:]=nodes[(i*t_steps):((i*t_steps)+t_steps)]

    #if  we have a model for Reilly
    os.chdir("..")
    os.chdir("..")
    nodes=[]
    n_segments=n_Ranvier*2-1
    for point_inx in range(n_segments):

        nodes_point_in_time=np.load('/opt/Patient/Points_in_time/Signal_t_conv'+str(point_inx+N_index*n_segments+last_point)+'.npy')   #get solution for each compartment in time for one neuron
        nodes.append(nodes_point_in_time*(1000)*Ampl_scale)    #convert to mV

    nodes=np.asarray(nodes)
    nodes = nodes.ravel()

    V_art=np.zeros((n_segments,t_steps),float)

    for i in range(n_segments):
        V_art[i,:]=nodes[(i*t_steps):((i*t_steps)+t_steps)]

    #only if we want to save potential in time on axons
    #np.save('Field_on_axons_in_time/'+str(population_name)+'axon_'+str(N_index_glob), V_art)

    os.chdir("Axon_files/Reilly2016/")

    n.h('{load_file("init_B5_extracellular.hoc")}')

    n.h.setupAPWatcher_0() # 'left' end of axon
    n.h.setupAPWatcher_1() # 'right' end of axon

    n.h.dt = dt
    n.h.tstop = tstop
    n.h.n_pulse = n_pulse

    for i in range(0,V_art.shape[0]):
        n.h.wf[i]=n.h.Vector(V_art[i,:])    # feed the potential in time for compartment i to NEURON

    n.h.stimul()
    n.h.run()
    spike=n.h.stoprun-0.5

    if spike==0.5:
        return output.put([N_index_glob,N_index])
    else:
        return output.put([N_index_glob,-1])


def run_simulation_with_NEURON(last_point,population_index,fib_diam,dt,tstop,n_Ranvier,N_models,v_init,t_steps,Ampl_scale,n_processors,stim_side,neuron_array_name=None):
    # this script is solely for Reilly2016 model
    '''Here we assume that all axons have the same number of nodes of Ranvier (and hence the length) and the morphology'''

    if stim_side==0:
        stim_folder='Results_rh/'
    else:
        stim_folder='Results_lh/'

    n_pulse=1   # we always simulate only one pulse from DBS. If need more, we should just copy the array and make sure the time vectors are in order

    axoninter=n_Ranvier-1
    n_segments=int((n_Ranvier-1)*2)+1       # lumped internodal segment

    #passing through n.h. does not work sometimes, so we do insert the parameters straight to the file
    paste_to_hoc_python3(n_Ranvier,axoninter,n_segments,v_init,int(1.0/dt))

    os.chdir("..")
    os.chdir("..")

    if population_index==-1:    # only one population is simulated
        population_name=''
        Vert_full_get=read_csv('/opt/Patient/Neuron_model_arrays/All_neuron_models.csv', delimiter=' ', header=None) # get all neuron models
        Vert_full=Vert_full_get.values
        Vert_full=np.round(Vert_full,8)

        Vert_get=read_csv('/opt/Patient/Neuron_model_arrays/Vert_of_Neural_model_NEURON.csv', delimiter=' ', header=None)    # get only physiologically correct neuron models
        Vert=Vert_get.values
        Vert=np.round(Vert,8)
    else:
        hf = h5py.File('/opt/Patient/Neuron_model_arrays/All_neuron_models_by_populations.h5', 'r')
        lst=list(hf.keys())

        if N_models==0:
            print(str(lst[population_index])+" population was not placed")
            return 0

        Vert_full=hf.get(lst[population_index])
        Vert_full=np.array(Vert_full)
        hf.close()
        Vert_full=np.round(Vert_full,8)

        hf2 = h5py.File('/opt/Patient/Neuron_model_arrays/Vert_of_Neural_model_NEURON_by_populations.h5', 'r')
        lst=list(hf2.keys())
        population_name=str(lst[population_index])+'/'
        Vert=hf2.get(lst[population_index])
        Vert=np.array(Vert)
        hf2.close()
        Vert=np.round(Vert,8)

#        #only if we want to save potential in time on axons
#        if not os.path.isdir('Field_on_axons_in_time/'+str(lst[population_index])+'/'):
#            os.makedirs('Field_on_axons_in_time/'+str(lst[population_index]))

    Nodes_status=np.zeros((N_models*n_segments,4),float)    #Nodes_status will contain info whether the placed(!) axon was activated
    Nodes_status[:,:3]=Vert[:,:]

    List_of_activated=[]
    List_of_not_activated=[]
    Activated_models=0
    int_counter=0
    Neuron_index=0
    neuron_global_index_array=np.zeros((N_models),int)

    os.chdir("Axon_files/Reilly2016/")

    # run NEURON simulation in parallel
    while Neuron_index<N_models:
        proc=[]
        j_proc=0 #counter for processes
        output=mp.Queue()
        while j_proc<n_processors and Neuron_index<N_models:
            first_axon_point=np.array([Vert[Neuron_index*n_segments,0],Vert[Neuron_index*n_segments,1],Vert[Neuron_index*n_segments,2]])
            second_axon_point=np.array([Vert[Neuron_index*n_segments+1,0],Vert[Neuron_index*n_segments+1,1],Vert[Neuron_index*n_segments+1,2]])
            last_axon_point=np.array([Vert[Neuron_index*n_segments+n_segments-1,0],Vert[Neuron_index*n_segments+n_segments-1,1],Vert[Neuron_index*n_segments+n_segments-1,2]])

            inx_first=np.flatnonzero((Vert_full == first_axon_point).all(1)) # Finally get indices
            inx_second=np.flatnonzero((Vert_full == second_axon_point).all(1)) # Finally get indices
            inx_last=np.flatnonzero((Vert_full == last_axon_point).all(1)) # Finally get indices

            #assuming we do not have axons that start (first two points) and end in the same points
            for j in inx_first:
                for j_second in inx_second:
                    if j_second-j==1:
                        for j_last in inx_last:
                            if j_last-j==n_segments-1:
                                inx_first_true=j
                                break

            neuron_global_index_array[Neuron_index]=int(inx_first_true/n_segments) #index in Prepared_models_full

            processes=mp.Process(target=conduct_parallel_NEURON,args=(population_name,last_point,neuron_global_index_array[Neuron_index],Neuron_index,Ampl_scale,t_steps,n_segments,dt,tstop,n_pulse,v_init,n_Ranvier,output))
            proc.append(processes)

            j_proc=j_proc+1
            Neuron_index=Neuron_index+1

        for p in proc:
            p.start()
        for p in proc:
            p.join()

        #returns list, where activated models have corresponding numbers, others have -1
        Activated_numbers = [output.get() for p in proc]

        for n_mdls in Activated_numbers:            #n_mdls is list[N_glob,N_loc]!
            if n_mdls[1]!=-1:
                Nodes_status[n_segments*n_mdls[1]:(n_segments*n_mdls[1]+n_segments),3]=1.0
                Activated_models=Activated_models+1
                List_of_activated.append(n_mdls[0])
            else:
                List_of_not_activated.append(int(n_mdls[0]))

            int_counter=int_counter+1

    os.chdir("..")
    os.chdir("..")

    Number_of_axons_initially=int(Vert_full.shape[0]/n_segments)
    Vert_full_status=np.zeros(Number_of_axons_initially,int)            # has status of all neurons (-1 - was not placed, 0 - was not activated, 1 - was activated)

    # num_removed=0
    # for axon_i in range(Number_of_axons_initially):
    #     if axon_i in List_of_activated:
    #         Vert_full_status[axon_i]=1
    #     elif axon_i in List_of_not_activated:
    #         Vert_full_status[axon_i]=0
    #     else:
    #         Vert_full_status[axon_i]=-1     #was removed
    #         num_removed=num_removed+1

    Axon_status=np.zeros((N_models,7),float)      #x1,y1,z1,x2,y2,z2,status. Holds info only about placed neurons. Important: coordinates are in the initial MRI space!

    [Mx_mri,My_mri,Mz_mri,x_min,y_min,z_min,x_max,y_max,z_max,MRI_voxel_size_x,MRI_voxel_size_y,MRI_voxel_size_z]=np.genfromtxt('/opt/Patient/MRI_DTI_derived_data/MRI_misc.csv', delimiter=' ')
    shift_to_MRI_space=np.array([x_min,y_min,z_min])

    Axon_Lead_DBS=np.zeros((Number_of_axons_initially*n_segments,5),float)
    num_removed=0

    for axon_i in range(Number_of_axons_initially):
        Axon_Lead_DBS[axon_i*n_segments:n_segments*(axon_i+1),:3]=Vert_full[axon_i*n_segments:n_segments*(axon_i+1),:3]+shift_to_MRI_space
        Axon_Lead_DBS[axon_i*n_segments:n_segments*(axon_i+1),3]=axon_i+1   # because Lead-DBS number them from 1
        if axon_i in List_of_activated:
            Vert_full_status[axon_i]=1
            Axon_Lead_DBS[axon_i*n_segments:n_segments*(axon_i+1),4]=1
        elif axon_i in List_of_not_activated:
            Vert_full_status[axon_i]=0
            Axon_Lead_DBS[axon_i*n_segments:n_segments*(axon_i+1),4]=0
        else:
            Vert_full_status[axon_i]=-1     #was removed
            num_removed=num_removed+1
            Axon_Lead_DBS[axon_i*n_segments:n_segments*(axon_i+1),4]=-1


    from scipy.io import savemat
    mdic = {"fibers": Axon_Lead_DBS, "ea_fibformat": "1.0"}
    if population_index==-1:            # only one population is simulated
        if stim_side==0:
            savemat("/opt/Patient/Results_rh/Axon_state.mat", mdic)
        else:
            savemat("/opt/Patient/Results_lh/Axon_state.mat", mdic)
    else:
        if stim_side==0:
            savemat("/opt/Patient/Results_rh/Axon_state_"+str(lst[population_index])+".mat", mdic)
        else:
            savemat("/opt/Patient/Results_lh/Axon_state_"+str(lst[population_index])+".mat", mdic)

    loc_ind_start=0
    for i in range(N_models):
        Axon_status[i,:3]=Nodes_status[loc_ind_start,:3]+shift_to_MRI_space
        Axon_status[i,3:6]=Nodes_status[loc_ind_start+n_segments-1,:3]+shift_to_MRI_space
        Axon_status[i,6]=Nodes_status[loc_ind_start,3]
        loc_ind_start=loc_ind_start+n_segments

    #for Lead-DBS for visualization purposes
    Nodes_status_MRI_space=np.zeros((N_models*n_segments,4),float)
    Nodes_status_MRI_space[:,:3]=Nodes_status[:,:3]+shift_to_MRI_space
    Nodes_status_MRI_space[:,3]=Nodes_status[:,3]

    print(Activated_models, " models were activated")

    List_of_activated=np.asarray(List_of_activated)

    Nodes_status_MRI_space_only_activated=np.delete(Nodes_status_MRI_space, np.where(Nodes_status_MRI_space[:,3] == 0.0)[0], axis=0)

#    if neuron_array_name==None:
#        hf = h5py.File('Field_solutions/Activation/VAT_Neuron_array.h5', 'a')
#        hf.create_dataset('VAT_Neuron_array_'+str(Activated_models), data=Nodes_status_MRI_space_only_activated)
#        hf.close()
#    else:
#        hf = h5py.File('Field_solutions/Activation/Activation_in_'+neuron_array_name[:-3]+'.h5', 'a')
#        hf.create_dataset(str(lst[population_index])+'_'+str(Activated_models), data=Nodes_status_MRI_space_only_activated)
#        hf.close()

    if population_index==-1:
        print(np.round(Activated_models/float(Number_of_axons_initially)*100,2),"% activation (including damaged neurons)\n")
        if stim_side==0:
            #np.savetxt('/opt/Patient/Field_solutions/Activation/Last_run.csv', List_of_activated, delimiter=" ")
            np.savetxt('/opt/Patient/Results_rh/'+stim_folder+'Last_run.csv', List_of_activated, delimiter=" ")
            np.save('/opt/Patient/Results_rh/'+stim_folder+'Connection_status',Axon_status)
            #np.save('/opt/Patient/Results_rh/'+stim_folder+'Network_status',Vert_full_status)
            np.savetxt('/opt/Patient/Results_rh/'+stim_folder+'Network_status.csv', Vert_full_status, delimiter=" ")  #Ningfei prefers .csv
            np.savetxt('/opt/Patient/Results_rh/'+stim_folder+'Activation_VAT_Neuron_Array_'+str(Activated_models)+'.csv', Nodes_status_MRI_space_only_activated, delimiter=" ")
        else:
            #np.savetxt('/opt/Patient/Field_solutions/Activation/Last_run.csv', List_of_activated, delimiter=" ")
            np.savetxt('/opt/Patient/Results_lh/'+stim_folder+'Last_run.csv', List_of_activated, delimiter=" ")
            np.save('/opt/Patient/Results_lh/'+stim_folder+'Connection_status',Axon_status)
            #np.save('/opt/Patient/Results_lh/'+stim_folder+'Network_status',Vert_full_status)
            np.savetxt('/opt/Patient/Results_lh/'+stim_folder+'Network_status.csv', Vert_full_status, delimiter=" ")  #Ningfei prefers .csv
            np.savetxt('/opt/Patient/Results_lh/'+stim_folder+'Activation_VAT_Neuron_Array_'+str(Activated_models)+'.csv', Nodes_status_MRI_space_only_activated, delimiter=" ")

    else:
        print(np.round(Activated_models/float(Number_of_axons_initially)*100,2),"% activation in ",lst[population_index], "(including damaged neurons)\n")
        if stim_side==0:
            np.savetxt('/opt/Patient/Results_rh/'+stim_folder+'Last_run_in_'+str(lst[population_index])+'.csv', List_of_activated, delimiter=" ")
            np.save('/opt/Patient/Results_rh/'+stim_folder+'Connection_status_'+str(lst[population_index]),Axon_status)
            np.savetxt('/opt/Patient/Results_rh/'+stim_folder+'Activation_'+neuron_array_name[:-3]+'___'+str(lst[population_index])+'_'+str(Activated_models)+'.csv', Nodes_status_MRI_space_only_activated, delimiter=" ")

            hf = h5py.File('/opt/Patient/Results_rh/'+stim_folder+'Network_status.h5', 'a')
            hf.create_dataset(str(lst[population_index]), data=Vert_full_status)
            hf.close()
        else:
            np.savetxt('/opt/Patient/Results_lh/'+stim_folder+'Last_run_in_'+str(lst[population_index])+'.csv', List_of_activated, delimiter=" ")
            np.save('/opt/Patient/Results_lh/'+stim_folder+'Connection_status_'+str(lst[population_index]),Axon_status)
            np.savetxt('/opt/Patient/Results_lh/'+stim_folder+'Activation_'+neuron_array_name[:-3]+'___'+str(lst[population_index])+'_'+str(Activated_models)+'.csv', Nodes_status_MRI_space_only_activated, delimiter=" ")

            hf = h5py.File('/opt/Patient/Results_lh/'+stim_folder+'Network_status.h5', 'a')
            hf.create_dataset(str(lst[population_index]), data=Vert_full_status)
            hf.close()

    #this function will prepare data for connection states due to DBS
    if population_index!=-1:
        connection_visualizator(Activated_models,Number_of_axons_initially,lst[population_index],last_point)



    return Activated_models

