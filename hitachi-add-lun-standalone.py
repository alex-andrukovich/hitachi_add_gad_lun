#!/usr/bin/env python3

import subprocess
import logging
import time
import re
import sys
import os

vsm_name =                                      "meta_resource"
name_of_my_cluster_of_servers =                 "vmware2025_clu"
host_mode_of_my_cluster_of_servers =            "VMWARE_EX"
host_mode_options_of_my_cluster_of_servers =    ["54", "63", "114"]

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



servers = [{"server_name" : "windows_srv_2025_node00", "site" : "site_one", "fabric_a": "84498599092A4B00", "fabric_b": "9959058B0DF6F900"},
           {"server_name" : "windows_srv_2025_node01", "site" : "site_one", "fabric_a": "84498599092A4B01", "fabric_b": "9959058B0DF6F901"},
           {"server_name" : "windows_srv_2025_node02", "site" : "site_one", "fabric_a": "84498599092A4B02", "fabric_b": "9959058B0DF6F902"},
           {"server_name" : "windows_srv_2025_node03", "site" : "site_one", "fabric_a": "84498599092A4B03", "fabric_b": "9959058B0DF6F903"},
           {"server_name" : "windows_srv_2025_node04", "site" : "site_one", "fabric_a": "84498599092A4B04", "fabric_b": "9959058B0DF6F904"},
           {"server_name" : "windows_srv_2025_node05", "site" : "site_one", "fabric_a": "84498599092A4B05", "fabric_b": "9959058B0DF6F905"},
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

def create_host_groups(stg_a, storage_ports, cluster_name, host_mode, host_option_modes):
    for port in storage_ports:
        logger.info(f"Creating host groups on port {port}, for {cluster_name + "@" + stg_a['site']}")
        subprocess.check_output(
            ["raidcom", "add", "host_grp", "-port", port ,"-host_grp_name", cluster_name + "@" + stg_a['site'], "-I" + stg_a['horcm_id']])
        subprocess.check_output(
            ["raidcom", "modify", "host_grp", "-port", port , cluster_name + "@" + stg_a['site'], "-host_mode", host_mode, "-set_host_mode_opt"] + host_option_modes + ["-I" + stg_a['horcm_id']])


def add_host_group_to_vsm(stg_a, storage_ports, cluster_name, vsm):
    for port in storage_ports:
        subprocess.check_output(
            ["raidcom", "add", "resource", "-port", port, cluster_name + "@" + stg_a['site'], "-resource_name", vsm, "-I" + stg_a['horcm_id']])


def add_host_to_host_grp(stg_a, storage_ports, cluster_name, server_list):
    for port in storage_ports:
        for host in server_list:
            subprocess.check_output(
                ["raidcom", "add", "hba_wwn", "-port", port, cluster_name + "@" + host['site'], "-hba_wwn",
                 host[storage_ports[port]], "-I" + stg_a['horcm_id']])
            subprocess.check_output(
                ["raidcom", "set", "hba_wwn", "-port", port, cluster_name + "@" + host['site'], "-hba_wwn",
                 host[storage_ports[port]], "-wwn_nickname", host['server_name'] + "_" + storage_ports[port] , "-I" + stg_a['horcm_id']])


def get_undefined_ldev_list(stg_a):
    undefined_ldevs_list_stg_a = []

    undefined_ldevs_stg_a = subprocess.check_output(
                ["raidcom", "get", "ldev", "-ldev_list", "undefined", "-fx", "-key",
                 "front_end", "-cnt", "10" , "-I" + stg_a['horcm_id']])
    for line in undefined_ldevs_stg_a.splitlines()[1:]:
        undefined_ldevs_list_stg_a.append(line.decode().split()[1])
    reversed_arr = undefined_ldevs_list_stg_a[::-1]
    return reversed_arr

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

def create_ldev(stg_a, capacity, pool, vsm, ldev_name):
    free_ldev_ids = get_undefined_ldev_list(stg_a)
    logger.info(f'Free undefined ldev list: {free_ldev_ids}')

    free_ldev_id = "0x" + free_ldev_ids[0]
    #reset_ldev_config
    reset_ldev_config(stg_a, free_ldev_id)

    #Add capacity
    subprocess.check_output(
        ["raidcom", "add", "ldev", "-ldev_id", free_ldev_id , "-pool", pool,
         "-capacity", capacity, "-I" + stg_a['horcm_id']])
    #add ldev name
    subprocess.check_output(["raidcom", "modify", "ldev", "-ldev_id", free_ldev_id , "-ldev_name", ldev_name, "-I" + stg_a['horcm_id']])
    return free_ldev_id

def add_lun_to_host_grp(stg_a, storage_ports, cluster_name, volume):
    # List of free LUN IDs as strings from "0" to "1024"
    free_lun_ids = [str(i) for i in range(1025)]
    used_lun_ids = []
    # List of used LUN IDs
    for port in storage_ports:
        used_lun_string_1 = subprocess.check_output(["raidcom", "get", "lun", "-port", port, cluster_name + "@" + stg_a['site'],  "-I" + stg_a['horcm_id']]).decode().splitlines()[1:]
        for line in used_lun_string_1:
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
        logger.info(f'Allocating LDEV {volume}: on port {port} as LUN ID {first_lun_id_to_use} on @ {stg_a['site']}  storage systems')
        subprocess.check_output(["raidcom", "add", "lun", "-port", port, cluster_name + "@" + stg_a['site'], "-lun_id", str(first_lun_id_to_use), "-ldev_id", volume, "-I" + stg_a['horcm_id']])








os_type = sys.platform
create_horcm_file(storage_a['horcm_id'], get_horcm_path(os_type), storage_a['ip'], storage_a['horcm_udp'])

start_horcm_instance(storage_a['horcm_id'], get_horcm_path(os_type), os_type)


# Login
raidcom_login(storage_a['horcm_id'], storage_a['username'], storage_a['password'])



# Get serial
storage_a['serial'] = get_storage_serial_number(storage_a['horcm_id'])

logger.info(f'Storage A technical details: {storage_a}')

for server in servers:
    logger.info(server)
logger.info(f'Ports: {ports}')

create_host_groups(storage_a, ports,name_of_my_cluster_of_servers, host_mode_of_my_cluster_of_servers, host_mode_options_of_my_cluster_of_servers)
add_host_group_to_vsm(storage_a, ports, name_of_my_cluster_of_servers, vsm_name)
add_host_to_host_grp(storage_a, ports, name_of_my_cluster_of_servers, servers)


logger.info(f'Creating LDEVs: {volume_list}')
for index, vol in enumerate(volume_list):
    logger.info(f'index:{index}')
    logger.info(f'vol:{vol}')
    ldev = create_ldev(storage_a, vol['capacity'], vol['pool_id'], vsm_name, vol['ldev_name'])
    volume_list[index]['ldev_id'] = ldev
    logger.info(f'Created LDEV ID: {ldev}')
logger.info(f'Created LDEVs: {volume_list}')

# Add ldevs to host groups
for index, vol in enumerate(volume_list):
    logger.info(f'index:{index}')
    logger.info(f'vol:{vol}')
    add_lun_to_host_grp(storage_a, ports, name_of_my_cluster_of_servers, vol['ldev_id'])



# Shutdown horcm instances
# shutdown_horcm_instance(storage_a['horcm_id'], get_horcm_path(os_type), os_type)



# Cleanup
# raidcom delete host_grp -port CL1-A vmware2025_clu@site_one -I210
# raidcom delete host_grp -port CL2-A vmware2025_clu@site_one -I210
