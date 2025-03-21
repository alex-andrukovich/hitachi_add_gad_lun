#!/usr/bin/env python3

# pre req:
# raidcom get resource -fx -I210
# raidcom get resource -fx -I211
# raidcom add rcu -cu_free 800002 M800 0 -mcu_port  cl1-c  -rcu_port cl1-c -I210
# raidcom add rcu -cu_free 800001 M800 0 -mcu_port  cl1-c  -rcu_port cl1-c -I211
# raidcom add rcu_path -cu_free 800002 M800 0 -mcu_port  cl2-c  -rcu_port cl2-c -I210
# raidcom add rcu_path -cu_free 800001 M800 0 -mcu_port  cl2-c  -rcu_port cl2-c -I211
# raidcom get rcu -fx -I210 -cu_free 800002 M8    0
# raidcom get rcu -fx -I211 -cu_free 800001 M8    0
#
# raidcom add quorum -quorum_id 0  -request_id auto -remote_storage 800002 M800 -ldev_id 0x64 -I210
# raidcom add quorum -quorum_id 0  -request_id auto -remote_storage 800001 M800 -ldev_id 0x64 -I211
# raidcom get quorum -fx -I210
# raidcom get quorum -fx -I211
#
# raidcom add resource -resource_name GAD -virtual_type 888888 RH20MH2 -I210
# raidcom add resource -resource_name GAD -virtual_type 888888 RH20MH2 -I211
# raidcom get resource -fx -key opt -I210
# raidcom get resource -fx -key opt -I211

import subprocess
import logging
import time
import re
import sys
import os

vsm_name =                                      "GAD"
name_of_my_cluster_of_servers =                 "win2025_clu"
host_mode_of_my_cluster_of_servers =            "WIN_EX"
host_mode_options_of_my_cluster_of_servers =    ["2", "22", "25"]

storage_a = {
    "ip":                   "10.0.0.11",
    "horcm_id":             "210",
    "horcm_udp":            "45211",
    "serial":               "placeholder",
    "site":                 "site_one",
    "role":                 "P-VOL",
    "username":             "maintenance",
    "password":             "raid-maintenance"
}
storage_b = {
    "ip":                   "10.0.0.12",
    "horcm_id":             "211",
    "horcm_udp":            "45212",
    "serial":               "placeholder",
    "site":                 "site_two",
    "role":                 "S-VOL",
    "username":             "maintenance",
    "password":             "raid-maintenance"
}


servers = [{"server_name" : "windows_srv_2025_node00", "site" : "site_one", "fabric_a": "74498599092A4B00", "fabric_b": "1959058B0DF6F900"},
           {"server_name" : "windows_srv_2025_node01", "site" : "site_one", "fabric_a": "74498599092A4B01", "fabric_b": "1959058B0DF6F901"},
           {"server_name" : "windows_srv_2025_node02", "site" : "site_one", "fabric_a": "74498599092A4B02", "fabric_b": "1959058B0DF6F902"},
           {"server_name" : "windows_srv_2025_node03", "site" : "site_one", "fabric_a": "74498599092A4B03", "fabric_b": "1959058B0DF6F903"},
           {"server_name" : "windows_srv_2025_node04", "site" : "site_one", "fabric_a": "74498599092A4B04", "fabric_b": "1959058B0DF6F904"},
           {"server_name" : "windows_srv_2025_node05", "site" : "site_one", "fabric_a": "74498599092A4B05", "fabric_b": "1959058B0DF6F905"},
		   {"server_name" : "windows_srv_2025_node10", "site" : "site_two", "fabric_a": "74498599092A4B10", "fabric_b": "1959058B0DF6F910"},
           {"server_name" : "windows_srv_2025_node11", "site" : "site_two", "fabric_a": "74498599092A4B11", "fabric_b": "1959058B0DF6F911"},
           {"server_name" : "windows_srv_2025_node12", "site" : "site_two", "fabric_a": "74498599092A4B12", "fabric_b": "1959058B0DF6F912"},
           {"server_name" : "windows_srv_2025_node13", "site" : "site_two", "fabric_a": "74498599092A4B13", "fabric_b": "1959058B0DF6F913"},
           {"server_name" : "windows_srv_2025_node14", "site" : "site_two", "fabric_a": "74498599092A4B14", "fabric_b": "1959058B0DF6F914"},
           {"server_name" : "windows_srv_2025_node15", "site" : "site_two", "fabric_a": "74498599092A4B15", "fabric_b": "1959058B0DF6F915"},
]

ports = {
    "CL1-A": "fabric_a",
    "CL2-A": "fabric_b"
}

volume_list  = [{"ldev_name" : "alias_one",   "pool_id" : "0", "capacity": "11g", "ldev_id": "placeholder"},
                {"ldev_name" : "alias_two",   "pool_id" : "0", "capacity": "12g", "ldev_id": "placeholder"},
                {"ldev_name" : "alias_three", "pool_id" : "0", "capacity": "13g", "ldev_id": "placeholder"}
]


# Create a custom logger
logger = logging.getLogger("logger")
# Set the level of this logger. INFO means that it will handle all messages with a level of INFO and above
logger.setLevel(logging.DEBUG)
# Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('lab-training-add-lun.log')
c_handler.setLevel(logging.DEBUG)
f_handler.setLevel(logging.DEBUG)
# Create formatters and add it to handlers
c_format = logging.Formatter('%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)
# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)

def is_valid_ip(ip):
    logger.info("Function execution started")
    start_time = time.time()
    pattern = re.compile(r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f"The function took {execution_time} seconds to execute.")
    return bool(pattern.match(ip))

def get_horcm_path(os_type):
    logger.info("Function execution started")
    start_time = time.time()
    if os_type == "win32":
        windir = os.environ.get('SystemRoot')
        full_horcmpath = windir + "\\"
        logger.info(
            "queried HORCM directory location, returned: " + full_horcmpath + " horcmXXX.conf files will be created here")
    elif os_type == "linux":
        full_horcmpath = "/etc/"
    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f"The function took {execution_time} seconds to execute.")
    return full_horcmpath

def create_horcm_file(horcm_instance, path, storage_ip, udpport):
    logger.info("Function execution started")
    start_time = time.time()
    horcm_file_full_path = path + "horcm" + horcm_instance + ".conf"
    with open(horcm_file_full_path, 'w') as horcm_file:
        horcm_file.write("HORCM_MON" + '\n')
        horcm_file.write("#ip_address" + '\t' + "service" + '\t' + "poll(10ms)" + '\t' + "timeout(10ms)" + '\n')
        horcm_file.write("localhost" + '\t' + udpport + '\t' + "1000" + '\t\t' + "3000" + '\n\n\n')
        horcm_file.write("HORCM_CMD" + '\n')
        if is_valid_ip(storage_ip):
            horcm_file.write("\\\\.\\IPCMD-" + storage_ip + "-31001" + '\n')
        else:
            horcm_file.write(storage_ip + '\n')
    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f"The function took {execution_time} seconds to execute.")


def shutdown_horcm_instance(horcm_instance, path, os_type):
    logger.info("Function execution started")
    start_time = time.time()
    horcm_file_full_path = path + "\\" + "horcm" + horcm_instance + ".conf"
    # os.environ['HORCM_CONF'] = horcm_file_full_path
    # os.environ['HORCMINST'] = horcm_instance
    os.environ['HORCM_EVERYCLI'] = "1"
    if os_type == "win32":
        subprocess.run(["horcmshutdown",  horcm_instance])
    elif os_type == "linux":
        subprocess.run(["horcmshutdown.sh",  horcm_instance])
    logger.info(f"Waiting 10 sec.")
    time.sleep(10)
    logger.info(f"Done waiting 10 sec.")
    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f"The function took {execution_time} seconds to execute.")


def start_horcm_instance(horcm_instance, path, os_type):
    logger.info("Function execution started")
    start_time = time.time()
    try:
        shutdown_horcm_instance(horcm_instance, path, os_type)
    except:
        logger.info("Could not shutdown HORCM instance, might be down already")
    horcm_file_full_path = path + "horcm" + horcm_instance + ".conf"
    # os.environ['HORCM_CONF'] = horcm_file_full_path
    # os.environ['HORCMINST'] = horcm_instance
    os.environ['HORCM_EVERYCLI'] = "1"
    if os_type == "win32":
        subprocess.run(["horcmstart", horcm_instance])
    elif os_type == "linux":
        subprocess.run(["horcmstart.sh", horcm_instance])
    logger.info(f"Waiting 10 sec.")
    time.sleep(10)
    logger.info(f"Done waiting 10 sec.")
    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f"The function took {execution_time} seconds to execute.")

def raidcom_login(horcm_instance, username, password):
    logger.info("Function execution started")
    start_time = time.time()
    subprocess.run(["raidcom", "-login", username, password, "-I" + horcm_instance])
    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f"The function took {execution_time} seconds to execute.")

def get_storage_serial_number(horcm_instance):
    logger.info("Function execution started")
    start_time = time.time()
    get_resource = []
    get_resource = subprocess.check_output(
        ["raidcom", "get", "resource", "-fx", "-key", "opt", "-I" + horcm_instance]).decode().splitlines()
    serial = get_resource[1].split()[5].strip()
    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f"The function took {execution_time} seconds to execute.")
    return serial

def create_host_groups(stg_a, stg_b, storage_ports, cluster_name, host_mode, host_option_modes):
    for port in storage_ports:
        logger.info(f"Creating host groups on port {port}, for {cluster_name + "@" + stg_a['site']} and {cluster_name + "@" + stg_b['site']} on {stg_a['serial']} and {stg_b['serial']}")
        subprocess.check_output(
            ["raidcom", "add", "host_grp", "-port", port ,"-host_grp_name", cluster_name + "@" + stg_a['site'], "-I" + stg_a['horcm_id']])
        subprocess.check_output(
            ["raidcom", "add", "host_grp", "-port", port, "-host_grp_name", cluster_name + "@" + stg_b['site'], "-I" + stg_a['horcm_id']])
        subprocess.check_output(
            ["raidcom", "add", "host_grp", "-port", port ,"-host_grp_name", cluster_name + "@" + stg_a['site'], "-I" + stg_b['horcm_id']])
        subprocess.check_output(
            ["raidcom", "add", "host_grp", "-port", port, "-host_grp_name", cluster_name + "@" + stg_b['site'], "-I" + stg_b['horcm_id']])
        subprocess.check_output(
            ["raidcom", "modify", "host_grp", "-port", port , cluster_name + "@" + stg_a['site'], "-host_mode", host_mode, "-set_host_mode_opt"] + host_option_modes + ["-I" + stg_a['horcm_id']])
        subprocess.check_output(
            ["raidcom", "modify", "host_grp", "-port", port , cluster_name + "@" + stg_b['site'], "-host_mode", host_mode, "-set_host_mode_opt"] + host_option_modes + ['78'] + ["-I" + stg_a['horcm_id']])
        subprocess.check_output(
            ["raidcom", "modify", "host_grp", "-port", port , cluster_name + "@" + stg_a['site'], "-host_mode", host_mode, "-set_host_mode_opt"] + host_option_modes + ['78'] + ["-I" + stg_b['horcm_id']])
        subprocess.check_output(
            ["raidcom", "modify", "host_grp", "-port", port , cluster_name + "@" + stg_b['site'], "-host_mode", host_mode, "-set_host_mode_opt"] + host_option_modes + ["-I" + stg_b['horcm_id']])

def add_host_group_to_vsm(stg_a, stg_b, storage_ports, cluster_name, vsm):
    for port in storage_ports:
        subprocess.check_output(
            ["raidcom", "add", "resource", "-port", port, cluster_name + "@" + stg_a['site'], "-resource_name", vsm, "-I" + stg_a['horcm_id']])
        subprocess.check_output(
            ["raidcom", "add", "resource", "-port", port, cluster_name + "@" + stg_b['site'], "-resource_name", vsm, "-I" + stg_a['horcm_id']])
        subprocess.check_output(
            ["raidcom", "add", "resource", "-port", port, cluster_name + "@" + stg_a['site'], "-resource_name", vsm, "-I" + stg_b['horcm_id']])
        subprocess.check_output(
            ["raidcom", "add", "resource", "-port", port, cluster_name + "@" + stg_b['site'], "-resource_name", vsm, "-I" + stg_b['horcm_id']])

def add_host_to_host_grp(stg_a, stg_b, storage_ports, cluster_name, server_list):
    for port in storage_ports:
        for host in server_list:
            subprocess.check_output(
                ["raidcom", "add", "hba_wwn", "-port", port, cluster_name + "@" + host['site'], "-hba_wwn",
                 host[storage_ports[port]], "-I" + stg_a['horcm_id']])
            subprocess.check_output(
                ["raidcom", "add", "hba_wwn", "-port", port, cluster_name + "@" + host['site'], "-hba_wwn",
                 host[storage_ports[port]], "-I" + stg_b['horcm_id']])

            subprocess.check_output(
                ["raidcom", "set", "hba_wwn", "-port", port, cluster_name + "@" + host['site'], "-hba_wwn",
                 host[storage_ports[port]], "-wwn_nickname", host['server_name'] + "_" + storage_ports[port] , "-I" + stg_a['horcm_id']])
            subprocess.check_output(
                ["raidcom", "set", "hba_wwn", "-port", port, cluster_name + "@" + host['site'], "-hba_wwn",
                 host[storage_ports[port]], "-wwn_nickname", host['server_name'] + "_" + storage_ports[port] , "-I" + stg_b['horcm_id']])

def get_undefined_ldev_list(stg_a, stg_b):
    undefined_ldevs_list_stg_a = []
    undefined_ldevs_list_stg_b = []

    undefined_ldevs_stg_a = subprocess.check_output(
                ["raidcom", "get", "ldev", "-ldev_list", "undefined", "-fx", "-key",
                 "front_end", "-cnt", "10" , "-I" + stg_a['horcm_id']])
    for line in undefined_ldevs_stg_a.splitlines()[1:]:
        undefined_ldevs_list_stg_a.append(line.decode().split()[1])

    undefined_ldev_stg_b = subprocess.check_output(
                ["raidcom", "get", "ldev", "-ldev_list", "undefined", "-fx", "-key",
                 "front_end", "-cnt", "10" , "-I" + stg_b['horcm_id']])
    for line in undefined_ldev_stg_b.splitlines()[1:]:
        undefined_ldevs_list_stg_b.append(line.decode().split()[1])

    undefined_ldev_list_stg_a_and_b = [item for item in undefined_ldevs_list_stg_a if item in undefined_ldevs_list_stg_b]
    return undefined_ldev_list_stg_a_and_b

def create_dict_from_get_ldev_output(stg, ldev_id):
    dict_of_ldev_attrib = {}
    get_ldev_stg_a = subprocess.check_output(
        ["raidcom", "get", "ldev", "-ldev_id", ldev_id , "-fx", "-I" + stg['horcm_id']])
    get_ldev_stg_a_list = get_ldev_stg_a.decode().splitlines()
    for ldev_attribute in get_ldev_stg_a_list:
        if "VIR_LDEV" in ldev_attribute and "LDEV" in ldev_attribute:
            delimiters = ["VIR_LDEV :", ":"]
            multi_delim_split = re.split('|'.join(map(re.escape, delimiters)), ldev_attribute)
            dict_of_ldev_attrib[multi_delim_split[0].strip()] = multi_delim_split[1].strip()
            dict_of_ldev_attrib['VIR_LDEV'] = multi_delim_split[2].strip()
        else:
            split_ldev_attrib_line = ldev_attribute.split(":")
            dict_of_ldev_attrib[split_ldev_attrib_line[0].strip()] = split_ldev_attrib_line[1].strip()
    return dict_of_ldev_attrib

def reset_ldev_config(stg, ldev_id):
    dict_of_ldev_attributes = create_dict_from_get_ldev_output(stg, ldev_id)
    if dict_of_ldev_attributes['RSGID'] != '0':
        resource_name = subprocess.check_output(
            ["raidcom", "get", "resource", "-resource", dict_of_ldev_attributes['RSGID'], "-I" + stg['horcm_id']])
        resource_name = resource_name.decode().splitlines()
        resource_name = resource_name[1].split()[0]
        logger.info(f'Removing free ldev {ldev_id} from resource {resource_name}')
        if dict_of_ldev_attributes['VIR_LDEV'] == 'ffff':
            subprocess.check_output(
                ["raidcom", "unmap", "resource", "-ldev_id", ldev_id, "-virtual_ldev_id", "reserve", "-I" + stg['horcm_id']])
            dict_of_ldev_attributes = create_dict_from_get_ldev_output(stg, ldev_id)
        if dict_of_ldev_attributes['VIR_LDEV'] == 'fffe':
            subprocess.check_output(
                ["raidcom", "delete", "resource", "-ldev_id", ldev_id, "-resource_name", resource_name, "-I" + stg['horcm_id']])
    return dict_of_ldev_attributes

def create_ldev(stg_a, stg_b, capacity, pool, vsm, ldev_name):
    free_ldev_ids = get_undefined_ldev_list(stg_a, stg_b)
    logger.info(f'Free undefined ldev list: {free_ldev_ids}')

    free_ldev_id = "0x" + free_ldev_ids[0]
    #reset_ldev_config
    reset_ldev_config(stg_a, free_ldev_id)
    reset_ldev_config(stg_b, free_ldev_id)
    #Unmap
    subprocess.check_output(
        ["raidcom", "unmap", "resource", "-ldev_id", free_ldev_id , "-virtual_ldev_id", free_ldev_id, "-I" + stg_a['horcm_id']])
    subprocess.check_output(
        ["raidcom", "unmap", "resource", "-ldev_id", free_ldev_id , "-virtual_ldev_id", free_ldev_id, "-I" + stg_b['horcm_id']])

    #Add resource
    subprocess.check_output(
        ["raidcom", "add", "resource", "-ldev_id", free_ldev_id , "-resource_name", vsm, "-I" + stg_a['horcm_id']])
    subprocess.check_output(
        ["raidcom", "add", "resource", "-ldev_id", free_ldev_id , "-resource_name", vsm, "-I" + stg_b['horcm_id']])

    #Map
    if stg_a['role'] == "P-VOL" and stg_b['role'] == "S-VOL":
        subprocess.check_output(
            ["raidcom", "map", "resource", "-ldev_id", free_ldev_id , "-virtual_ldev_id", free_ldev_id, "-I" + stg_a['horcm_id']])
        subprocess.check_output(
            ["raidcom", "map", "resource", "-ldev_id", free_ldev_id , "-virtual_ldev_id", "reserve", "-I" + stg_b['horcm_id']])
    elif stg_a['role'] == "S-VOL" and stg_b['role'] == "P-VOL":
        subprocess.check_output(
            ["raidcom", "map", "resource", "-ldev_id", free_ldev_id , "-virtual_ldev_id", "reserve", "-I" + stg_a['horcm_id']])
        subprocess.check_output(
            ["raidcom", "map", "resource", "-ldev_id", free_ldev_id , "-virtual_ldev_id", free_ldev_id, "-I" + stg_b['horcm_id']])

    #Add capacity
    subprocess.check_output(
        ["raidcom", "add", "ldev", "-ldev_id", free_ldev_id , "-pool", pool,
         "-capacity", capacity, "-I" + stg_a['horcm_id']])
    subprocess.check_output(
        ["raidcom", "add", "ldev", "-ldev_id", free_ldev_id , "-pool", pool,
         "-capacity", capacity, "-I" + stg_b['horcm_id']])

    #Set ALUA
    if stg_a['role'] == "P-VOL" and stg_b['role'] == "S-VOL":
        subprocess.check_output(
            ["raidcom", "modify", "ldev", "-ldev_id", free_ldev_id , "-alua", "enable", "-I" + stg_a['horcm_id']])
    elif stg_a['role'] == "S-VOL" and stg_b['role'] == "P-VOL":
        subprocess.check_output(
            ["raidcom", "modify", "ldev", "-ldev_id", free_ldev_id , "-alua", "enable", "-I" + stg_b['horcm_id']])

    # Have to check documentation and verify if alua enable required for both P-VOL and S-VOL, for the LAB test, set alua enable on all
    subprocess.check_output(["raidcom", "modify", "ldev", "-ldev_id", free_ldev_id, "-alua", "enable", "-I" + stg_a['horcm_id']])
    subprocess.check_output(["raidcom", "modify", "ldev", "-ldev_id", free_ldev_id, "-alua", "enable", "-I" + stg_b['horcm_id']])


    #add ldev name
    subprocess.check_output(["raidcom", "modify", "ldev", "-ldev_id", free_ldev_id , "-ldev_name", ldev_name, "-I" + stg_a['horcm_id']])
    subprocess.check_output(["raidcom", "modify", "ldev", "-ldev_id", free_ldev_id , "-ldev_name", ldev_name, "-I" + stg_b['horcm_id']])

    return free_ldev_id

def add_lun_to_host_grp(stg_a, stg_b, storage_ports, cluster_name, volume):
    # List of free LUN IDs as strings from "0" to "1024"
    free_lun_ids = [str(i) for i in range(1025)]
    used_lun_ids = []
    # List of used LUN IDs
    for port in storage_ports:
        used_lun_string_1 = subprocess.check_output(["raidcom", "get", "lun", "-port", port, cluster_name + "@" + stg_a['site'],  "-I" + stg_a['horcm_id']]).decode().splitlines()[1:]
        for line in used_lun_string_1:
            used_lun = line.split()[3]
            used_lun_ids.append(used_lun)
        used_lun_string_2 = subprocess.check_output(["raidcom", "get", "lun", "-port", port, cluster_name + "@" + stg_b['site'],  "-I" + stg_a['horcm_id']]).decode().splitlines()[1:]
        for line in used_lun_string_2:
            used_lun = line.split()[3]
            used_lun_ids.append(used_lun)
        used_lun_string_3 = subprocess.check_output(["raidcom", "get", "lun", "-port", port, cluster_name + "@" + stg_b['site'],  "-I" + stg_b['horcm_id']]).decode().splitlines()[1:]
        for line in used_lun_string_3:
            used_lun = line.split()[3]
            used_lun_ids.append(used_lun)
        used_lun_string_4 = subprocess.check_output(["raidcom", "get", "lun", "-port", port, cluster_name + "@" + stg_a['site'],  "-I" + stg_b['horcm_id']]).decode().splitlines()[1:]
        for line in used_lun_string_4:
            used_lun = line.split()[3]
            used_lun_ids.append(used_lun)
    # Combine all used LUN IDs into one set
    unique_used_lun_ids = set(used_lun_ids)
    logger.info(f'Used LUN IDs on any of the ports: {unique_used_lun_ids}')
    # Remove used LUN IDs from the free LUN IDs list
    unique_free_lun_ids = [lun_id for lun_id in free_lun_ids if lun_id not in unique_used_lun_ids]
    logger.info(f'Free LUN IDs on all the ports: {unique_free_lun_ids}')


    first_lun_id_to_use = unique_free_lun_ids[0]
    for port in storage_ports:
        logger.info(f'Allocating LDEV {volume}: on port {port} as LUN ID {first_lun_id_to_use} on @ {stg_a['site']} and @ {stg_b['site']} host groups in {stg_a['serial']} and {stg_b['serial']} storage systems')
        subprocess.check_output(["raidcom", "add", "lun", "-port", port, cluster_name + "@" + stg_a['site'], "-lun_id", str(first_lun_id_to_use), "-ldev_id", volume, "-I" + stg_a['horcm_id']])
        subprocess.check_output(["raidcom", "add", "lun", "-port", port, cluster_name + "@" + stg_b['site'], "-lun_id", str(first_lun_id_to_use), "-ldev_id", volume, "-I" + stg_a['horcm_id']])
        subprocess.check_output(["raidcom", "add", "lun", "-port", port, cluster_name + "@" + stg_b['site'], "-lun_id", str(first_lun_id_to_use), "-ldev_id", volume, "-I" + stg_b['horcm_id']])
        subprocess.check_output(["raidcom", "add", "lun", "-port", port, cluster_name + "@" + stg_a['site'], "-lun_id", str(first_lun_id_to_use), "-ldev_id", volume, "-I" + stg_b['horcm_id']])

    # Set ALUA on LUNs
    for port in storage_ports:
        # Set ALUA optimized on LUNs
        logger.info(f'Setting ALUA optimized     state on port {port}, host group {cluster_name + "@" + stg_a['site']}, in storage {stg_a['serial']}, which is located in {stg_a['site']}')
        subprocess.check_output(["raidcom", "modify", "lun", "-port", port, cluster_name + "@" + stg_a['site'], "-lun_id", "all", "-asymmetric_access_state", "optimized", "-I" + stg_a['horcm_id']])
        logger.info(f'Setting ALUA optimized     state on port {port}, host group {cluster_name + "@" + stg_b['site']}, in storage {stg_b['serial']}, which is located in {stg_b['site']}')
        subprocess.check_output(["raidcom", "modify", "lun", "-port", port, cluster_name + "@" + stg_b['site'], "-lun_id", "all", "-asymmetric_access_state", "optimized", "-I" + stg_b['horcm_id']])
        # Set ALUA non_optimized on LUNs
        logger.info(f'Setting ALUA non_optimized state on port {port}, host group {cluster_name + "@" + stg_b['site']}, in storage {stg_a['serial']}, which is located in {stg_a['site']}')
        subprocess.check_output(["raidcom", "modify", "lun", "-port", port, cluster_name + "@" + stg_b['site'], "-lun_id", "all", "-asymmetric_access_state", "non_optimized", "-I" + stg_a['horcm_id']])
        logger.info(f'Setting ALUA non_optimized state on port {port}, host group {cluster_name + "@" + stg_a['site']}, in storage {stg_b['serial']}, which is located in {stg_b['site']}')
        subprocess.check_output(["raidcom", "modify", "lun", "-port", port, cluster_name + "@" + stg_a['site'], "-lun_id", "all", "-asymmetric_access_state", "non_optimized", "-I" + stg_b['horcm_id']])

def add_ldevs_to_horcm_files(stg_a, stg_b, cluster_name, volumes):
    shutdown_horcm_instance(stg_a['horcm_id'], get_horcm_path(os_type), os_type)
    shutdown_horcm_instance(stg_b['horcm_id'], get_horcm_path(os_type), os_type)
    horcm_file_full_path_stg_a = get_horcm_path(os_type) + "horcm" + stg_a['horcm_id'] + ".conf"
    with open(horcm_file_full_path_stg_a, 'a') as horcm_file:
        horcm_file.write('\n' + "HORCM_LDEV" + '\n')
    horcm_file_full_path_stg_b = get_horcm_path(os_type) + "horcm" + stg_b['horcm_id'] + ".conf"
    with open(horcm_file_full_path_stg_b, 'a') as horcm_file:
        horcm_file.write('\n' + "HORCM_LDEV" + '\n')

    for vol in volumes:
        ldev_id = vol['ldev_id']
        ldev_id_str = ldev_id[2:].zfill(4)  # Remove leading "0x" and pad with zeros
        text_ldev_horcm_format = f"{ldev_id_str[:2]}:{ldev_id_str[2:]}"  # Insert colon after the second character
        with open(horcm_file_full_path_stg_a, 'a') as horcm_file:
            horcm_file.write(f'{cluster_name[:22]} {vol['ldev_id']} {stg_a['serial']} {text_ldev_horcm_format}\n')
        with open(horcm_file_full_path_stg_b, 'a') as horcm_file:
            horcm_file.write(f'{cluster_name[:22]} {vol['ldev_id']} {stg_b['serial']} {text_ldev_horcm_format}\n')

    with open(horcm_file_full_path_stg_a, 'a') as horcm_file:
        horcm_file.write('\n' + "HORCM_INST" + '\n')
        horcm_file.write(f'{cluster_name[:22]} localhost {stg_b['horcm_udp']}\n')
    with open(horcm_file_full_path_stg_b, 'a') as horcm_file:
        horcm_file.write('\n' + "HORCM_INST" + '\n')
        horcm_file.write(f'{cluster_name[:22]} localhost {stg_a['horcm_udp']}\n')

    start_horcm_instance(stg_a['horcm_id'], get_horcm_path(os_type), os_type)
    start_horcm_instance(stg_b['horcm_id'], get_horcm_path(os_type), os_type)
    return cluster_name[:22]

def create_gad_replication_pairs(stg_a, stg_b, replication_group_name):
    logger.info(f'Checking replication status of {replication_group_name}, using horcm files {stg_a['horcm_id']} and {stg_b['horcm_id']}')
    replication_status = subprocess.check_output(["pairdisplay", "-IH" + stg_a['horcm_id'], "-g", replication_group_name, "-fcxe", "-CLI"])
    logger.info(replication_status.decode())

    logger.info(f'Create pairs')
    subprocess.check_output(["paircreate", "-IH" + stg_a['horcm_id'], "-g", replication_group_name, "-fg", "never", "55", "-vl", "-c", "15"])
    logger.info(f'Checking replication status of {replication_group_name}, using horcm files {stg_a['horcm_id']} and {stg_b['horcm_id']}')
    replication_status = subprocess.check_output(["pairdisplay", "-IH" + stg_a['horcm_id'], "-g", replication_group_name, "-fcxe", "-CLI"])
    logger.info(replication_status.decode())

    # Wait for pair
    logger.info(f'Waiting for PAIR status')
    subprocess.check_output(["pairevtwait", "-IH" + stg_a['horcm_id'], "-g", replication_group_name, "-s", "pair", "-ss", "pair", "-t", "3600"])
    logger.info(f'Checking replication status of {replication_group_name}, using horcm files {stg_a['horcm_id']} and {stg_b['horcm_id']}')
    replication_status = subprocess.check_output(["pairdisplay", "-IH" + stg_a['horcm_id'], "-g", replication_group_name, "-fcxe", "-CLI"])
    logger.info(replication_status.decode())



os_type = sys.platform
create_horcm_file(storage_a['horcm_id'], get_horcm_path(os_type), storage_a['ip'], storage_a['horcm_udp'])
create_horcm_file(storage_b['horcm_id'], get_horcm_path(os_type), storage_b['ip'], storage_b['horcm_udp'])
start_horcm_instance(storage_a['horcm_id'], get_horcm_path(os_type), os_type)
start_horcm_instance(storage_b['horcm_id'], get_horcm_path(os_type), os_type)

# Login
raidcom_login(storage_a['horcm_id'], storage_a['username'], storage_a['password'])
raidcom_login(storage_b['horcm_id'], storage_b['username'], storage_b['password'])


# Get serial
storage_a['serial'] = get_storage_serial_number(storage_a['horcm_id'])
storage_b['serial'] = get_storage_serial_number(storage_b['horcm_id'])
logger.info(f'Storage A technical details: {storage_a}')
logger.info(f'Storage A technical details: {storage_b}')
for server in servers:
    logger.info(server)
logger.info(f'Ports: {ports}')

create_host_groups(storage_a, storage_b, ports,name_of_my_cluster_of_servers, host_mode_of_my_cluster_of_servers, host_mode_options_of_my_cluster_of_servers)
add_host_group_to_vsm(storage_a, storage_b, ports, name_of_my_cluster_of_servers, vsm_name)
add_host_to_host_grp(storage_a, storage_b, ports, name_of_my_cluster_of_servers, servers)


logger.info(f'Creating LDEVs: {volume_list}')
for index, vol in enumerate(volume_list):
    logger.info(f'index:{index}')
    logger.info(f'vol:{vol}')
    ldev = create_ldev(storage_a, storage_b, vol['capacity'], vol['pool_id'], vsm_name, vol['ldev_name'])
    volume_list[index]['ldev_id'] = ldev
    logger.info(f'Created LDEV ID: {ldev}')
logger.info(f'Created LDEVs: {volume_list}')

# Add ldevs to host groups
for index, vol in enumerate(volume_list):
    logger.info(f'index:{index}')
    logger.info(f'vol:{vol}')
    add_lun_to_host_grp(storage_a, storage_b, ports, name_of_my_cluster_of_servers, vol['ldev_id'])

#Add LDEVs to HORCM files
horcm_group_name = add_ldevs_to_horcm_files(storage_a, storage_b, name_of_my_cluster_of_servers, volume_list)

#Create GAD PAIRs
create_gad_replication_pairs(storage_a, storage_b, horcm_group_name)

# Shutdown horcm instances
# shutdown_horcm_instance(storage_a['horcm_id'], get_horcm_path(os_type), os_type)
# shutdown_horcm_instance(storage_b['horcm_id'], get_horcm_path(os_type), os_type)


# ## Cleanup example
# pairdisplay -IH210 -g win2025_clu -fcxe -CLI
# pairsplit -IH210 -g win2025_clu
# pairsplit -IH210 -g win2025_clu -S
#
# raidcom get host_grp -port cl1-a -fx -I210
# raidcom get host_grp -port cl2-a -fx -I210
# raidcom get host_grp -port cl1-a -fx -I211
# raidcom get host_grp -port cl2-a -fx -I211
#
# raidcom delete host_grp -port cl1-a win2025_clu@site_one -I210
# raidcom delete host_grp -port cl1-a win2025_clu@site_two -I210
# raidcom delete host_grp -port cl2-a win2025_clu@site_one -I210
# raidcom delete host_grp -port cl2-a win2025_clu@site_two -I210
#
# raidcom delete host_grp -port cl1-a win2025_clu@site_one -I211
# raidcom delete host_grp -port cl1-a win2025_clu@site_two -I211
# raidcom delete host_grp -port cl2-a win2025_clu@site_one -I211
# raidcom delete host_grp -port cl2-a win2025_clu@site_two -I211

