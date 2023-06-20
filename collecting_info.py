# importing the required modules
import platform
import psutil
import os
import pwd
import argparse
import subprocess
import yaml

parser = argparse.ArgumentParser(description='This script collecting data about server')
parser.add_argument('--users', action='store_true', help="Collecting informathion about users")
parser.add_argument('--units', action='store_true', help="Collecting information about units")
parser.add_argument('--proc', action='store_true', help="Collecting information about process")
parser.add_argument('--limits', action='store_true', help="Collecting information about limits")
parser.add_argument('--kernel', action='store_true', help="Collecting information about kernel settings")
parser.add_argument('--mount', action='store_true', help="Collecting information about mount point")
parser.add_argument('--packages', action='store_true', help="Collecting information about installed packages")
parser.add_argument('--cpuinfo', action='store_true', help="Collecting information about cpu")
parser.add_argument('--mem', action='store_true', help="Collecting information about memory")
parser.add_argument('--disks', action='store_true', help="Collecting information about disks")
parser.add_argument('--hosts', action='store_true', help="Collecting information from hosts file")
parser.add_argument('--sudoers', action='store_true', help="Collecting information about sudo rights")
parser.add_argument('--domain_info', action='store_true', help="Collecting information about domain settings")

args = parser.parse_args()

# getting users information
def info_users():
    print("\n\t\t\t Users Information\n")
    users = pwd.getpwall()
    for user in users:
        print("[+] User: ", user.pw_name, user.pw_passwd, user.pw_shell, user.pw_uid, user.pw_gid, user.pw_dir )
    print("\n")
    print("\n\t\t\t Genering Users yaml \n")
    with open("/home/user/info/users.yml", "w") as fw:
        user_yml = {
                    "Users": []
        }
        for user in users:
            #if user.pw_uid > 500:
            username = user.pw_name
            user_yml["Users"].append( {
                    username: {
                        'user_name' : user.pw_name,
                        'user_shell' : user.pw_shell,
                        'user_uid' : user.pw_uid,
                        'user_gid' : user.pw_gid,
                        'user_dir' : user.pw_dir,
                        }
                })
        yaml.dump(user_yml, fw, sort_keys=False, default_flow_style=False)

# getting name units
def info_units():
    print("\n\t\t\t Units Information\n")
    path = "/home/user/info/units/"
    os.system("mkdir -p " + path)
    units = subprocess.check_output("systemctl list-units --type=service | awk '{print $1}'", shell=True)
    s = ''.join(map(chr, units))
    str = s.split("\n")
    str = str[1:-7] # Убираем ненужные строки
    print(str)
    for i in str:
        #if "device" or "mount" in i:
        #    continue
        print(i)
        with open (path + i, "w") as fw:
            print(path + i)
            units_settings =  subprocess.check_output("systemctl cat " + i, shell=True)
            d = ''.join(map(chr, units_settings))
            fw.write(d)
        fw.close()
    #for filename in os.listdir("/etc/systemd/system"):
    #    print("[+] Unit: ", filename)

# getting the name of processes currently running
def info_proc():
    print("\n\t\t\t Process Information\n")
    for proc in psutil.process_iter(['name']):
        print("[+] Process: ", proc.info['name'])

# getting limits value
def info_limits():
    print("\n\t\t\t Limits Information\n")
    with open('/etc/security/limits.conf', 'r') as l:
        file_info = l.readlines()
    with open("/home/user/info/limit.yml", "w") as fw:
        limit_yml = {
            "limit": {},
            "limitd" : []
            }
        limit_yml["limit"] = {"param" : [] }
        for line in file_info:
            if not line.startswith("#") and not line.startswith(chr(10)):
                line = line.replace((chr(10)), '')
                limit_yml["limit"]["param"].append(line)              
        s1='/etc/security/limits.d/'
        shet = 0
        if (len(os.listdir(s1)) > 0):
            for x in os.listdir(s1):
                limit_yml["limitd"].append({"path" : s1 + x, "param" : [] })
                with open(s1 + x, 'r') as k:
                    limit_info = k.readlines()
                    for line in limit_info:
                        if not line.startswith("#") and not line.startswith(chr(10)):
                            line = line.replace((chr(10)), '')
                            limit_yml["limitd"][shet]["param"].append( line )
                shet = shet + 1
        yaml.dump(limit_yml, fw, sort_keys=False, default_flow_style=False)

# getting settings kernel value
def info_kernel():
    print("\n\t\t\t Kernel Information\n")
    with open('/etc/sysctl.conf', 'r') as l:
        file_info = l.readlines()
    with open("/home/user/info/kernel.yml", "w") as fw:
        kernel_yml = {
            "kernel": {},
            "kerneld" : []
            }
        paramList = []
        for line in file_info:
            if not line.startswith("#") and not line.startswith(chr(10)):
                line = line.replace((chr(10)), '')
                paramList.append(line)
        if paramList:
            kernel_yml["kernel"] = {"param" : paramList }
        s2='/etc/sysctl.d/'
        if (len(os.listdir(s2)) > 0):
            for x in os.listdir(s2):
                if x != "README.sysctl":
                    with open(s2 + x, 'r') as k:
                        limit_info = k.readlines()
                    paramdList = []
                    for line in limit_info:
                        if not line.startswith("#") and not line.startswith(chr(10)):
                            line = line.replace((chr(10)), '')
                            paramdList.append( line )
                    if paramdList:
                        kernel_yml["kerneld"].append({"path" : s2 + x, "param" : paramdList })
        yaml.dump(kernel_yml, fw, sort_keys=False, default_flow_style=False)

# getting settings fstab
def info_mount():
    print("\n\t\t\t fstab Information\n")
    with open('/etc/fstab', 'r') as l:
        file_info = l.readlines()
    with open("/home/user/info/fstab.yml", "w") as fw:
        mount_yml = {
            "Mount": []
        }
        for line in file_info:
            if not line.startswith("#") and not line.startswith(chr(10)):
                line = line.replace((chr(10)), '')
                mount_yml["Mount"].append( {
                    "param" : line
                }
                    )
        yaml.dump(mount_yml, fw, sort_keys=False, default_flow_style=False)

# getting settings hosts
def info_hosts():
    print("\n\t\t\t Hosts Information\n")
    with open('/etc/hosts', 'r') as l:
        file_info = l.readlines()
    with open("/home/user/info/hosts.yml", "w") as fw:
        hosts_yml = {
            "Hosts": []
        }
        for line in file_info:
            if not line.startswith("#") and not line.startswith(chr(10)):
                line = line.replace((chr(10)), '')
                line = line.replace((chr(9)), ' ')
                hosts_yml["Hosts"].append( {
                    "param" : line
                }
                    )
        yaml.dump(hosts_yml, fw, sort_keys=False, default_flow_style=False)

# getting settings sudo
def info_sudo():
    print("\n\t\t\t Sudo rights Information\n")
    with open('/etc/sudoers', 'r') as l:
        file_info = l.readlines()
    with open("/home/user/info/sudoers.yml", "w") as fw:
        sudo_yml = {
            "Sudo": {},
            "Sudod" : []
            }
        paramList = []
        for line in file_info:
            if not line.startswith("#") and not line.startswith("Defaults") and not line.startswith(chr(10)):
                line = line.replace((chr(10)), '') # Убираем \n
                line = line.replace((chr(9)), ' ') # Заменяем \t  на ' '
                paramList.append(line)
        if paramList:
            sudo_yml["Sudo"] = {"param" : paramList }
        s3='/etc/sudoers.d/'
        if (len(os.listdir(s3)) > 0):
            for x in os.listdir(s3):
                if x != "README":
                    with open(s3 + x, 'r') as k:
                        limit_info = k.readlines()
                    paramdList = []
                    for line in limit_info:
                        if not line.startswith("#") and not line.startswith("Defaults") and not line.startswith(chr(10)):
                            line = line.replace((chr(10)), '') # Убираем \n
                            line = line.replace((chr(9)), ' ') # Заменяем \t  на ' '
                            paramdList.append( line )
                    if paramdList:
                        sudo_yml["Sudod"].append({"path" : s3 + x, "param" : paramdList })
        yaml.dump(sudo_yml, fw, sort_keys=False, default_flow_style=False)

# Displaying installed packages
def info_packages():
    print("\n\t\t\t Packages Information\n")
    with open("/home/user/info/package.yml", "w") as fw:
        package_yml = {
                    "Package": []
        }
        if "Ubuntu" or "Debian" or "Astra" in platform.version():
            package_install = subprocess.check_output("dpkg -l | grep ^ii | awk '{ print $2}'", shell=True)
            s = ''.join(map(chr, package_install))
            str = s.split("\n")
            str = str[:-1]
            for i in str:
                package_yml["Package"].append( {
                    "name" : i
                } )
            yaml.dump(package_yml, fw, sort_keys=False, default_flow_style=False)

        if "el" in platform.version():
            package_install = subprocess.check_output("rpm -qa", shell=True)
            s = ''.join(map(chr, package_install))
            print(type(s))
            str = s.split("\n")
            str = str[:-1]
            for i in str:
                package_yml["Package"].append( {
                    "name" : i
                } )
            yaml.dump(package_yml, fw, sort_keys=False, default_flow_style=False)

# Collecting info about domain settings
def info_domain():
    print("\n\t\t\t Domain settings Information\n")
    for proc in psutil.process_iter(['name']):
        if proc == "sssd":
            domain_package = "sssd"
            break;
        else:
            domain_package = "lwsmd"

    if domain_package == "sssd":
        permited_group = subprocess.check_output("realm list | grep permited_groups", shell=True)
        print(permited_group)
    else:
        permited_group = subprocess.check_output("/opt/pbis/bin/config --detail RequireMembershipOf")
        print(permited_group)

def info_cpu():
# Displaying The CPU information
    print("\n\t\t\t CPU Information\n")

# This code will print the number of CPU cores present
    print("[+] Number of Physical cores :", psutil.cpu_count(logical=False))
    print("[+] Number of Total cores :", psutil.cpu_count(logical=True))
    print("\n")

# This will print the maximum, minimum and current CPU frequency
    cpu_frequency = psutil.cpu_freq()
    print(f"[+] Max Frequency : {cpu_frequency.max:.2f}Mhz")
    print(f"[+] Min Frequency : {cpu_frequency.min:.2f}Mhz")
    print(f"[+] Current Frequency : {cpu_frequency.current:.2f}Mhz")
    print("\n")

# This will print the usage of CPU per core
    for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
        print(f"[+] CPU Usage of Core {i} : {percentage}%")
    print(f"[+] Total CPU Usage : {psutil.cpu_percent()}%")


# reading the cpuinfo file to print the name of
# the CPU present
    with open("/proc/cpuinfo", "r")  as f:
        file_info = f.readlines()

    cpuinfo = [x.strip().split(":")[1] for x in file_info if "model name"  in x]
    for index, item in enumerate(cpuinfo):
        print("[+] Processor " + str(index) + " : " + item)

def info_mem():
# Using the virtual_memory() function it will return a tuple
    virtual_memory = psutil.virtual_memory()
    print("\n\t\t\t Memory Information\n")
#This will print the primary memory details
    print("[+] Total Memory present :", bytes_to_GB(virtual_memory.total), "Gb")
    print("[+] Total Memory Available :", bytes_to_GB(virtual_memory.available), "Gb")
    print("[+] Total Memory Used :", bytes_to_GB(virtual_memory.used), "Gb")
    print("[+] Percentage Used :", virtual_memory.percent, "%")
    print("\n")

# This will print the swap memory details if available
    swap = psutil.swap_memory()
    print(f"[+] Total swap memory :{bytes_to_GB(swap.total)}")
    print(f"[+] Free swap memory : {bytes_to_GB(swap.free)}")
    print(f"[+] Used swap memory : {bytes_to_GB(swap.used)}")
    print(f"[+] Percentage Used: {swap.percent}%")

# Gathering memory information from meminfo file
    print("\nReading the /proc/meminfo file: \n")
    with open("/proc/meminfo", "r") as f:
        lines = f.readlines()

    print("[+] " + lines[0].strip())
    print("[+] " + lines[1].strip())

def bytes_to_GB(bytes):
        gb = bytes/(1024*1024*1024)
        gb = round(gb, 2)
        return gb

def info_disk():
# accessing all the disk partitions
    disk_partitions = psutil.disk_partitions()
    print("\n\t\t\t Disk Information\n")

# displaying the partition and usage information
    for partition in disk_partitions:
        print("[+] Partition Device : ", partition.device)
        print("[+] File System : ", partition.fstype)
        print("[+] Mountpoint : ", partition.mountpoint)

        disk_usage = psutil.disk_usage(partition.mountpoint)
        print("[+] Total Disk Space :", bytes_to_GB(disk_usage.total), "GB")
        print("[+] Free Disk Space :", bytes_to_GB(disk_usage.free), "GB")
        print("[+] Used Disk Space :", bytes_to_GB(disk_usage.used), "GB")
        print("[+] Percentage Used :", disk_usage.percent, "%")
        print("\n")

# First We will print the basic system information
# using the platform module
print("\n\t\t\t Basic System Information\n")

print("[+] Architecture :", platform.architecture()[0])
print("[+] Machine :", platform.machine())
print("[+] Operating System Release :", platform.release())
print("[+] System Name :",platform.system())
print("[+] Operating System Version :", platform.version())
print("[+] Node: " + platform.node())
print("[+] Platform :", platform.platform())
print("[+] Processor :",platform.processor())
print("\n")

os.system("mkdir -p /home/user/info/")
if args.users:
    info_users()
if args.units:
    info_units()
if args.packages:
    info_packages()
if args.proc: # Только принты
    info_proc()
if args.limits:
    info_limits()
if args.kernel:
    info_kernel()
if args.mount:
    info_mount()
if args.hosts:
    info_hosts()
if args.sudoers:
    info_sudo()
if args.domain_info: # Доделать
    info_domain()
if args.cpuinfo: # Только принты
    info_cpu()
if args.mem: # Только принты
    info_mem()
if args.disks: # Только принты
    info_disk()
if not args.users and not args.units and not args.packages and not args.proc and not args.limits and not args.kernel and not args.mount and not args.hosts and not args.sudoers and not args.domain_info and not args.cpuinfo and not args.mem and not args.disks:
    info_users()
    info_units()
    info_packages()
    info_proc()
    info_limits()
    info_kernel()
    info_mount()
    info_hosts()
    info_sudo()