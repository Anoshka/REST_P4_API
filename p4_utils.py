from pprint import pprint

import pymel.core as pm
import maya.cmds as cmds

import os

import glob
import re

def run_win_cmd(cmd):
    """
    runs a command in Windows command line via subprocess
    args: (str) command to run
    returns: (list) results from OS
    """

    import subprocess

    print("> {}".format(cmd))

    result = []
    process = subprocess.Popen(cmd,
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               universal_newlines=True)

    stderr = process.communicate()[1]
    stdout = process.communicate()[0]

    result = (stdout, stderr)

    if (stderr != ''):
        print("OS Command failed:\n\"{}\"\n").format(stderr.strip())
        pm.error("OS Command failed:\n\"{}\".  See script editor.".format(cmd))
    else:  
        print("# {}".format(stdout))


    return result


def remove_escape_literals(string):
    """
    removes escape literals from a string
    returns: cleaned string
    """

    import re

    regex = re.compile(r'[\n\r\t\b\f]')

    cleaned_string = regex.sub("", string)

    return cleaned_string


def add_files_to_p4(files, changelist=None):
    """
    Takes a list of filepaths and marks them for add in Perforce
    """
    add_cmd_str = "p4 add -f "

    if changelist:
        add_cmd_str = "p4 add -d -c {} ".format(str(changelist))
    else:
        add_cmd_str = "p4 add -d -c default"
 
    if type(files) is list:
        for file in files:
            cmd_str = add_cmd_str + file
            #try:
            #subprocess OS with command str
            run_win_cmd(cmd_str)

    else: 
        print("ERROR: Function only takes type(list)")
        return

 
def get_p4_info():
    """
    Gets high level p4 info using -ztag
    """

    try:
        raw_info = run_win_cmd("p4 -ztag info")
    except:
        print('''
            #-----------------------------------------------#
            Failed to query Perforce, please check Environment Settings
            #-----------------------------------------------#
            ''')

    p4_info_dict = {}

    for raw in raw_info:
        raw_str = raw.decode("utf-8")
        raw_split = raw_str.split(" ")
        raw_split.pop(0)
        #send strings for cleaning
        cleaned_strings = []
        for each in raw_split:
            clean_str = remove_escape_literals(each)
            cleaned_strings.append(clean_str)

        if len(cleaned_strings) > 2:
            p4_key = cleaned_strings[0]
            p4_value_list = cleaned_strings.pop(0)
            p4_info_dict[p4_key] = "".join(p4_value_list)
        elif len(cleaned_strings) == 2:
            p4_info_dict[cleaned_strings[0]] = cleaned_strings[1]
        else:
            continue
    if p4_info_dict:
        return p4_info_dict
    else:
        return


def p4_check_in_files(files):
    """
    Takes a list of files and checks them into Perforce
    """

    cmd_str_sub = "p4 submit -d \"default\" "

    for file in files:

        run_win_cmd(cmd_str_sub + file) 

        
def p4_get_sync_files(filter_arg=None):
    """
    Returns a list of files to sync
    Optional arg to filter list based on string
    """

    sync_files_raw = run_win_cmd("p4 sync -n")

    sync_files = []
    for raw_str in sync_files_raw:
        cleaned_str = remove_escape_literals(raw_str)
        depot_path = cleaned_str.split(" - ")[0]
        sync_files.append(depot_path)

    return sync_files


def p4_get_file_loc(file):
    """
    Takes a file and returns a dict with its depot, user depot 
    and client locations
    """

    cmd_str = "p4 where {}".format(file)

    try:
        loc_data_raw = run_win_cmd(cmd_str)
        loc_strs_dirty = loc_data_raw[0].decode("utf-8").split(" ")
    except:
        print("ERROR: File provided was not found in Perforce Depot")
        return

    
    clean_strs = [remove_escape_literals(x) for x in loc_strs_dirty]
    
    if len(clean_strs) == 3:
        file_loc_dict = {}
        #adds final location info to dict for return
        file_loc_dict['depot_path'] = clean_strs[0]
        file_loc_dict['user_depot_path'] = clean_strs[1]
        file_loc_dict['workspace_path'] = clean_strs[2]

        return file_loc_dict

    else:
        pprint(cleaned_strings)
        return


def scene_check_out():
    """checks if file opened in maya is checked out in perforce"""

    #get file path of current opened maya file
    file_path = pm.sceneName()
    print ("file path", file_path)
    #isolate the name
    file_name = os.path.basename(file_path)
    print ("file name", file_name)
    #get raw name without extension
    raw_name, extension = os.path.splitext(file_name)
    print ("raw name", raw_name)


    #check all open files
    cmd_str = "p4 opened"

    #get info by subprocessing
    all_open_files = run_win_cmd(cmd_str)
    print ("all open files"), all_open_files

    checker = 0

    for file in all_open_files:

        if raw_name in file:
            print ("file is checked out")
            checker = 1
            break
    if checker == 0:
        pm.inViewMessage( amg='Please Check Out file in Perforce', pos='midCenter', fade=True )


def auto_check_in_file():
    """saves and checks in current open file"""
    
    #checks file and saves new version (increments), runs mark for add with given changelist (nonetype), and calls check in

    #get file path of current opened maya file
    file_path = pm.sceneName()
    print ("file path", file_path)  

    #saves current file
    pm.saveFile()

    #adds and checks in
    add_files_to_p4([file_path], changelist = "default")
    p4_check_in_files([file_path])
    
    def script_job():
        pm.scriptJob(scene_check_out(), listEvents = "SceneOpened")





    




    



    

    





            



    

    



