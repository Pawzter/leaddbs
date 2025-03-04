#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 17:28:33 2020

@author: butenko
"""

#This script reads input files from Lead-DBS and updates the default dictionary of GUI.

# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 11:33:13 2020

@author: konstantin
"""

#import tables
import h5py #works better
import numpy as np
import subprocess
#import pickle
#import json
import os

import sys

#from scipy.io import loadmat
#import file

#updates default dictionary
def get_input_from_LeadDBS(settings_location,index_side):     # 0 - rhs, 1 - lhs
    #index_side=1
    #settings_location,index_side=side_and_settings[:]
    index_side=int(index_side)

    #these are input from Lead-DBS
    input_dict = {
        'MRI_data_name': "name_MRI.nii.gz",     #segmented MRI data
        'DTI_data_name': "name_DTI.nii.gz",  #scaled tensor data
        'CSF_index': 0.0,           #index of the tissue in the segmented MRI data
        'WM_index': 0.0,
        'GM_index': 0.0,
        'default_material': 'GM',     # GM, WM or CSF
        'Electrode_type': 'St_Jude6148',
        'Implantation_coordinate_X': -10000000000.0,    # in mm in the MRI data space
        'Implantation_coordinate_Y': -10000000000.0,
        'Implantation_coordinate_Z': -10000000000.0,
        'Second_coordinate_X': -10000000000.0,
        'Second_coordinate_Y': -10000000000.0,
        'Second_coordinate_Z': -10000000000.0,
        'Rotation_Z': 0.0,              # rotation around the lead axis in degrees
        'current_control': 0,           # 0 - VC, 1 - CC
        'Phi_vector': [None, None, None, None],     #Signal vector: give an amplitude. If CC, 0.0 refers to 0 V (ground), other numbers are in A. None is for floating potentials
        'Activation_threshold_VTA': 0.0 ,    # threshold for Astrom VTA (V/mm), compute using the Lead-DBS function.
        'Full_Field_IFFT': 0,
        'external_grounding': False,
        'VTA_from_E': 1,
        'VTA_from_divE': 0,
        'Stim_side': 0, # 0 - rh, 1 - lh
        'Neuron_model_array_prepared': 0,
    }

    #should add for 'Name_prepared_neuron_array' (you need only the name of the file, not the whole path)
    #if 'Name_prepared_neuron_array'!='':
        # 'Neuron_model_array_prepared'=1
    #the same for the 'Brain_shape_name'
    #also we need to choose whether the IFFT will be on neurons or VTA array (currently controlled by 'Full_Field_IFFT')
    # and if VTA, then E-field threshold???

    #file = tables.open_file('oss-dbs_parameters.mat')     #hardwired
    #file = tables.open_file('oss-dbs_parameters.mat')     #hardwired
    print("Input from ",settings_location)
    file = h5py.File(str(settings_location), 'r')
    #file = h5py.File('oss-dbs_parameters.mat')

    #if file.root.settings.current_control[0][0]!=file.root.settings.current_control[0][1]:
    if all(~np.isnan(file['settings']['current_control'][0])):
        if file['settings']['current_control'][0][0] != file['settings']['current_control'][0][1]:
            print("Simultaneous use of VC and CC is not allowed for safety reasons!")
            raise SystemExit

    input_dict['Stim_side']=index_side
    #Phi_vector=file.root.settings.Phi_vector[:,index_side]
    Phi_vector=file['settings']['Phi_vector'][:,index_side]
    Phi_vector=list(Phi_vector)

    import math
    for i in range(len(Phi_vector)):
        if math.isnan(Phi_vector[i]):
            Phi_vector[i]=None

    if file['settings']['current_control'][0][0]==1:
        input_dict['current_control']=1
        Phi_vector=Phi_vector*0.001     # because Lead-DBS uses mA as the input

    # print(type(Phi_vector))
    if all(v is None for v in Phi_vector):
        print("No stimulation defined for this hemisphere")
        return -1

    input_dict['Phi_vector']=Phi_vector


    # convert ascii from Matlab struct to a string
    #array_ascii=file.root.settings.MRI_data_name[:]
    array_ascii=file['settings']['MRI_data_name'][:]
    list_ascii=[]
    for i in range(array_ascii.shape[0]):
        list_ascii.append(array_ascii[i][0])
   # list_ascii = map(lambda s: s.strip(), list_ascii)
    name_split=''.join(chr(i) for i in list_ascii)
    input_dict['MRI_data_name']=name_split.rsplit('/',1)[-1]


    path_to_patient=name_split.rsplit('/',1)[:-1]
    path_to_patient=path_to_patient[0]


   # array_ascii=file.root.settings.DTI_data_name[:]
    array_ascii=file['settings']['DTI_data_name'][:]
    list_ascii=[]
    if array_ascii[0]==0:
        input_dict['DTI_data_name']=''
    else:
        for i in range(array_ascii.shape[0]):
            list_ascii.append(array_ascii[i][0])
        #list_ascii = map(lambda s: s.strip(), list_ascii)
        input_dict['DTI_data_name']=''.join(chr(i) for i in list_ascii)


    input_dict['CSF_index']=file['settings']['CSF_index'][0][0]
    input_dict['WM_index']=file['settings']['WM_index'][0][0]
    input_dict['GM_index']=file['settings']['GM_index'][0][0]

    #input_dict['CSF_index']=file.root.settings.CSF_index[0][0]
    #input_dict['WM_index']=file.root.settings.WM_index[0][0]
    # input_dict['GM_index']=file.root.settings.GM_index[0][0]

    #array_ascii=file.root.settings.default_material[:]
    array_ascii=file['settings']['default_material'][:]
    list_ascii=[]
    for i in range(array_ascii.shape[0]):
        list_ascii.append(array_ascii[i][0])
    #list_ascii = map(lambda s: s.strip(), list_ascii)
    default_material=''.join(chr(i) for i in list_ascii)

    if default_material=='GM':
        input_dict['default_material']=3
    elif default_material=='WM':
        input_dict['default_material']=2
    elif default_material=='CSF':
        input_dict['default_material']=1
    else:
        print("Unrecognized default material")


    #array_ascii=file.root.settings.Electrode_type[:]
    array_ascii=file['settings']['Electrode_type'][:]
    list_ascii=[]
    for i in range(array_ascii.shape[0]):
        list_ascii.append(array_ascii[i][0])
    #list_ascii = map(lambda s: s.strip(), list_ascii)
    Electrode_type=''.join(chr(i) for i in list_ascii)

    if Electrode_type == 'Medtronic 3389':
        input_dict['Electrode_type']="Medtronic3389"#1
    elif Electrode_type == 'Medtronic 3387':
        input_dict['Electrode_type']="Medtronic3387"#1
    elif Electrode_type == 'Medtronic 3391':
        input_dict['Electrode_type']="Medtronic3391"#1
    elif Electrode_type == 'St. Jude Directed 6172 (short)' or Electrode_type == 'St. Jude Directed 6180':  #just different marker colors
        input_dict['Electrode_type']="St_Jude6180"#1
    elif Electrode_type == 'St. Jude Directed 6173 (long)':
        input_dict['Electrode_type']="St_Jude6173"#1
    elif Electrode_type == 'St. Jude ActiveTip (6142-6145)':    # just different tail lenghts, but it does not matter here
        input_dict['Electrode_type']="St_Jude6142"
    elif Electrode_type == 'St. Jude ActiveTip (6146-6149)':    # just different tail lenghts, but it does not matter here
        input_dict['Electrode_type']="St_Jude6148"     #1
    elif Electrode_type == 'Boston Scientific Vercise':
        input_dict['Electrode_type']="Boston_Scientific_Vercise" #1
    elif Electrode_type == 'Boston Scientific Vercise Directed':
        input_dict['Electrode_type']="Boston_Scientific_Vercise_Cartesia" #1
    elif Electrode_type == 'PINS Medical L301':
        input_dict['Electrode_type']="PINS_L301"
    elif Electrode_type == 'PINS Medical L302':
        input_dict['Electrode_type']="PINS_L302"
    elif Electrode_type == 'PINS Medical L303':
        input_dict['Electrode_type']="PINS_L303"
    else:
        print("The electrode is not yet implemented, but we will be happy to add it. Contact us via konstantin.butenko@uni-rostock.de")

    #input_dict['Implantation_coordinate_X'],input_dict['Implantation_coordinate_Y'],input_dict['Implantation_coordinate_Z'] = file.root.settings.Implantation_coordinate[:,index_side]
    #input_dict['Second_coordinate_X'],input_dict['Second_coordinate_Y'],input_dict['Second_coordinate_Z'] = file.root.settings.Second_coordinate[:,index_side]

    input_dict['Implantation_coordinate_X'],input_dict['Implantation_coordinate_Y'],input_dict['Implantation_coordinate_Z'] = file['settings']['Implantation_coordinate'][:,index_side]
    input_dict['Second_coordinate_X'],input_dict['Second_coordinate_Y'],input_dict['Second_coordinate_Z'] = file['settings']['Second_coordinate'][:,index_side]

    #input_dict['Rotation_Z']=file.root.settings.Rotation_Z[0][0]
    #input_dict['Activation_threshold_VTA']=file.root.settings.Activation_threshold_VTA[0][0]

    input_dict['Rotation_Z']=file['settings']['Rotation_Z'][0][0] # this is not implemented, we need to extract rotation angles from markers
    input_dict['Activation_threshold_VTA']=file['settings']['Activation_threshold_VTA'][0][0] #threshold is the same for both hemispheres
    input_dict['external_grounding']=bool(file['settings']['Case_grounding'][:,index_side][0])
    input_dict['Neuron_model_array_prepared']=int(file['settings']['calcAxonActivation'][0][0])    # external model (e.g. from fiber tractograpy)

    if input_dict['Neuron_model_array_prepared']!=1:
        input_dict['Full_Field_IFFT']=1 # for now we have only these two options

    ##just testing
    #input_dict['Electrode_type']="Boston_Scientific_Vercise"
    #input_dict['Phi_vector']=[0.0,-3.0,2.0,None,0.0,-3.0,2.0,None]
    # input_dict['current_control']=1
    # input_dict['Phi_vector']=[None,0.0005,None,None]
    # input_dict['external_grounding']=True
    # input_dict['Full_Field_IFFT']=1
    # input_dict['Activation_threshold_VTA']: 0.12

    from GUI_tree_files.GUI_tree_files.default_dict import d
    d.update(input_dict)

    with open('GUI_tree_files/GUI_tree_files/default_dict.py', 'w') as save_as_dict:
        save_as_dict.write('"""@author: trieu,butenko"""\n')
        #save_as_dict.write('\n')
        save_as_dict.write("d = {\n")
        for key in d:
            if type(d[key])!=str:
                save_as_dict.write("    '{}': {},\n".format(key, d[key]))
            else:
                save_as_dict.write("    '{}': '{}',\n".format(key, d[key]))
        save_as_dict.write("}\n")

    interactive_mode = int(file['settings']['interactiveMode'][0][0])

    return path_to_patient,index_side,interactive_mode


if __name__ == '__main__':
    #path_to_patient=get_input_from_LeadDBS(0,*sys.argv[1:])
    path_to_patient,side,interactive_mode=get_input_from_LeadDBS(*sys.argv[1:])
    process_1=-1
    if path_to_patient!=-1:
        if sys.platform == 'linux' or sys.platform == 'Linux':
            output = subprocess.run(['xterm', '-e','python3','GUI_tree_files/AppUI.py',path_to_patient,str(side),str(interactive_mode)])
            #subprocess.check_output(['xterm', '-e','python3','GUI_tree_files/AppUI.py',path_to_patient])
        elif sys.platform == 'darwin' or sys.platform == 'Darwin':
            dir_code = os.getcwd()
            #subprocess.check_output(['open', 'script_for_GUI.sh', path_to_patient, dir_code], executable='/bin/bash')
            output = subprocess.run(['open', 'script_for_GUI.sh', path_to_patient, dir_code, str(side), str(interactive_mode)], executable='/bin/bash')  # in this case we use a bash script that calls Applescript
            #process_1 = subprocess.check_call(['open', 'script_for_GUI.sh', path_to_patient, dir_code, str(side)], executable='/bin/bash')
            #process.wait()
        elif sys.platform == 'win32':
            print("Should be implemented the same way as for Linux (i.e. directly calling an external terminal)")
            raise SystemExit
        else:
            print("The system's OS does not support OSS-DBS")
            raise SystemExit

    # path_to_patient=get_input_from_LeadDBS(1,*sys.argv[1:])
    # if path_to_patient!=-1:
    #     if sys.platform == 'linux' or sys.platform == 'Linux':
    #         output2 = subprocess.run(['xterm', '-e','python3','GUI_tree_files/AppUI.py',path_to_patient])
    #         #subprocess.check_output(['xterm', '-e','python3','GUI_tree_files/AppUI.py',path_to_patient])
    #     elif sys.platform == 'darwin' or sys.platform == 'Darwin':
    #         dir_code = os.getcwd()
    #         output2 = subprocess.run(['open', 'script_for_GUI.sh', path_to_patient, dir_code], executable='/bin/bash')  # in this case we use a bash script that calls Applescript
    #     elif sys.platform == 'win32' or sys.platform == 'win32':
    #         print("Should be implemented the same way as for Linux (i.e. directly calling an external terminal)")
    #         raise SystemExit
    #     else:
    #         print("The system's OS does not support OSS-DBS")
    #         raise SystemExit

