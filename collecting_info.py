# importing the required modules
import platform
import os
import socket
import pwd
import argparse
import subprocess
import json
import sys
import re

parser = argparse.ArgumentParser(description='This script collecting data about server')
parser.add_argument('--users', action='store_true', help="Collecting informathion about users")
parser.add_argument('--units', action='store_true', help="Collecting information about units")
parser.add_argument('--proc', action='store_true', help="Collecting information about process")
parser.add_argument('--limits', action='store_true', help="Collecting information about limits")
parser.add_argument('--kernel', action='store_true', help="Collecting information about kernel settings")
parser.add_argument('--mount', action='store_true', help="Collecting information about mount point")
parser.add_argument('--packages', action='store_true', help="Collecting information about installed packages")
parser.add_argument('--hardware', action='store_true', help="Collecting information about cpu,mem,disks")
parser.add_argument('--hosts', action='store_true', help="Collecting information from hosts file")
parser.add_argument('--sudoers', action='store_true', help="Collecting information about sudo rights")
parser.add_argument('--domain_info', action='store_true', help="Collecting information about domain settings")

args = parser.parse_args()
path="/home/user/"
hostname = socket.gethostname()

# getting users information
def info_users():
    print("\n\t\t\t Users Information\n")
    users = pwd.getpwall()
    for user in users:
        print("[+] User: ", user.pw_name, user.pw_passwd, user.pw_shell, user.pw_uid, user.pw_gid, user.pw_dir )
    print("\n")
    print("\n\t\t\t Genering Users json \n")
    with open(path + hostname + "/users.js", "w") as fw:
        user_js = {
                    "Users": []
        }
        for user in users:
            #if user.pw_uid > 500:
            username = user.pw_name
            user_js["Users"].append( {
                    username: {
                        'user_name' : user.pw_name,
                        'user_shell' : user.pw_shell,
                        'user_uid' : user.pw_uid,
                        'user_gid' : user.pw_gid,
                        'user_dir' : user.pw_dir,
                        }
                })
        json.dump(user_js, fw)

    def listdirs(path_dir):
        sys.stdout = open(path + hostname + "/struct_home_dir.txt", "w")
        for dirpath, dirnames, filenames in os.walk(path_dir):
    # перебрать каталоги
            for dirname in dirnames:
                print("Каталог:", os.path.join(dirpath, dirname))
    # перебрать файлы
            for filename in filenames:
                print("Файл:", os.path.join(dirpath, filename))
    listdirs("/home/")
    

# getting name units
def info_units():
    print("\n\t\t\t Units Information\n")
    path_units = path + hostname + "/units/"
    os.system("mkdir -p " + path_units)
    units = subprocess.check_output("systemctl list-units --type=service | awk '{print $1}'", shell=True)
    s = ''.join(map(chr, units))
    str = s.split("\n")
    str = str[1:-7] # Убираем ненужные строки
    print(str)
    for i in str:
        with open (path_units + i, "w") as fw:
            print(path_units + i)
            units_settings =  subprocess.check_output("systemctl cat " + i, shell=True)
            d = ''.join(map(chr, units_settings))
            fw.write(d)
        fw.close()
    #for filename in os.listdir("/etc/systemd/system"):
    #    print("[+] Unit: ", filename)

def info_proc():
    with open(path + hostname + "/process.js", "w") as fw:
        process_js = {
            "Process": []
        }
        for x in os.listdir("/proc"):
            if re.match("^\d+$", x) is not None: # Регулярка проверяет, что имя состоит только из цифр
                with open("/proc/" +x + "/status", "r") as l:
                    file_info = l.readlines()
                    for line in file_info:
                        if line.startswith("Name"):
                            line = line.replace((chr(10)), '')
                            line = line.split("\t")
                            print(line)
                            process_js["Process"].append( {
                                "Name" : line[1] 
                }
                    )
        json.dump(process_js, fw)

# getting limits value
def info_limits():
    print("\n\t\t\t Limits Information\n")
    with open('/etc/security/limits.conf', 'r') as l:
        file_info = l.readlines()
    with open(path + hostname + "/limit.js", "w") as fw:
        limit_js = {
            "limit": {},
            "limitd" : []
            }
        limit_js["limit"] = {"param" : [] }
        for line in file_info:
            if not line.startswith("#") and not line.startswith(chr(10)):
                line = line.replace((chr(10)), '')
                limit_js["limit"]["param"].append(line)              
        s1='/etc/security/limits.d/'
        shet = 0
        if (len(os.listdir(s1)) > 0):
            for x in os.listdir(s1):
                limit_js["limitd"].append({"path" : s1 + x, "param" : [] })
                with open(s1 + x, 'r') as k:
                    limit_info = k.readlines()
                    for line in limit_info:
                        if not line.startswith("#") and not line.startswith(chr(10)):
                            line = line.replace((chr(10)), '')
                            limit_js["limitd"][shet]["param"].append( line )
                shet = shet + 1
        json.dump(limit_js, fw)

# getting settings kernel value
def info_kernel():
    print("\n\t\t\t Kernel Information\n")
    with open('/etc/sysctl.conf', 'r') as l:
        file_info = l.readlines()
    with open(path + hostname + "/kernel.js", "w") as fw:
        kernel_js = {
            "kernel": {},
            "kerneld" : []
            }
        paramList = []
        for line in file_info:
            if not line.startswith("#") and not line.startswith(chr(10)):
                line = line.replace((chr(10)), '')
                paramList.append(line)
        if paramList:
            kernel_js["kernel"] = {"param" : paramList }
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
                        kernel_js["kerneld"].append({"path" : s2 + x, "param" : paramdList })
        json.dump(kernel_js, fw)

# getting settings fstab
def info_mount():
    print("\n\t\t\t fstab Information\n")
    with open('/etc/fstab', 'r') as l:
        file_info = l.readlines()
    with open(path + hostname + "/fstab.js", "w") as fw:
        mount_js = {
            "Mount": []
        }
        for line in file_info:
            if not line.startswith("#") and not line.startswith(chr(10)):
                line = line.replace((chr(10)), '')
                mount_js["Mount"].append( {
                    "param" : line
                }
                    )
        json.dump(mount_js, fw)

# getting settings hosts
def info_hosts():
    print("\n\t\t\t Hosts Information\n")
    with open('/etc/hosts', 'r') as l:
        file_info = l.readlines()
    with open(path + hostname + "/hosts.js", "w") as fw:
        hosts_js = {
            "Hosts": []
        }
        for line in file_info:
            if not line.startswith("#") and not line.startswith(chr(10)):
                line = line.replace((chr(10)), '')
                line = line.replace((chr(9)), ' ')
                hosts_js["Hosts"].append( {
                    "param" : line
                }
                    )
        json.dump(hosts_js, fw)

# getting settings sudo
def info_sudo():
    print("\n\t\t\t Sudo rights Information\n")
    with open('/etc/sudoers', 'r') as l:
        file_info = l.readlines()
    with open(path + hostname + "/sudoers.js", "w") as fw:
        sudo_js = {
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
            sudo_js["Sudo"] = {"param" : paramList }
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
                        sudo_js["Sudod"].append({"path" : s3 + x, "param" : paramdList })
        json.dump(sudo_js, fw)

# Displaying installed packages
def info_packages():
    print("\n\t\t\t Packages Information\n")
    with open(path + hostname + "/package.js", "w") as fw:
        package_js = {
                    "Package": []
        }
        if "Ubuntu" or "Debian" or "Astra" in platform.version():
            package_install = subprocess.check_output("dpkg -l | grep ^ii | awk '{ print $2}'", shell=True)
            s = ''.join(map(chr, package_install))
            str = s.split("\n")
            str = str[:-1]
            for i in str:
                package_js["Package"].append( {
                    "name" : i
                } )
            json.dump(package_js, fw)

        if "el" in platform.version():
            package_install = subprocess.check_output("rpm -qa", shell=True)
            s = ''.join(map(chr, package_install))
            print(type(s))
            str = s.split("\n")
            str = str[:-1]
            for i in str:
                package_js["Package"].append( {
                    "name" : i
                } )
            json.dump(package_js, fw)

# Collecting info about domain settings
def info_domain():
    print("\n\t\t\t Domain settings Information\n")
    domain_package = ""
    for x in os.listdir("/proc"):
            if re.match("^\d+$", x) is not None: # Регулярка проверяет, что имя состоит только из цифр
                with open("/proc/" +x + "/status", "r") as l:
                    file_info = l.readlines()
                    for line in file_info:
                        if line.startswith("Name"):
                            line = line.replace((chr(10)), '')
                            line = line.split("\t")
                            if line.includes("sssd"):
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


def info_hardware():
    sys.stdout = open(path + hostname + "/hardware.txt", "w")
    def info_cpu():
        # Displaying The CPU information
        print("\n\t\t\t CPU Information\n")

    # This code will print the number of CPU cores present
        print("[+] Number of Physical cores :", ''.join(map(chr, subprocess.check_output("cat /proc/cpuinfo | grep processor | wc -l", shell=True))))
        print("\n")
        # This will print current CPU frequency
        print("[+] Current Frequency :", ''.join(map(chr, subprocess.check_output("cat /proc/cpuinfo | grep Hz | tail -1 | awk '{print $4 $2}'", shell=True))))
        print("\n")
        with open("/proc/cpuinfo", "r")  as f:
            file_info = f.readlines()

        cpuinfo = [x.strip().split(":")[1] for x in file_info if "model name"  in x]
        for index, item in enumerate(cpuinfo):
            print("[+] Processor " + str(index) + " : " + item)

    def info_mem():
        print("\n\t\t\t Memory Information\n")
    #This will print the primary memory details
        print("[+] Total Memory present :", ''.join(map(chr, subprocess.check_output("cat /proc/meminfo | grep MemTotal | awk '{print $2}'", shell=True))))
        print("[+] Total Memory Available :", ''.join(map(chr, subprocess.check_output("grep MemAvailable /proc/meminfo | awk '{print $2}'", shell=True))))
        print("[+] Total Memory Used :", ''.join(map(chr, subprocess.check_output("free | awk '{print $3}' | head -2 | tail -1", shell=True))))
        print("\n")
        # This will print the swap memory details if available
        print(f"[+] Total swap memory :",''.join(map(chr, subprocess.check_output("grep SwapTotal /proc/meminfo | awk '{print $2}'", shell=True))))
        print(f"[+] Free swap memory :",''.join(map(chr, subprocess.check_output("grep SwapFree /proc/meminfo | awk '{print $2}'", shell=True))))
        print(f"[+] Used swap memory :",''.join(map(chr, subprocess.check_output("free | awk '{print $3}' | tail -1", shell=True))))

    def info_disk():
    # accessing all the disk partitions
        print("\n\t\t\t Disk Information\n")

    # displaying the partition and usage information

        disk_list = subprocess.check_output("lsblk -l -o NAME | tail -n+2", shell = True)
        s = ''.join(map(chr, disk_list))
        s = s.split("\n")[:-1]
        print(s)

        for device in s:
            print("[+] Partition Device : ", ''.join(map(chr, subprocess.check_output("lsblk -l -o NAME,SIZE,MOUNTPOINT,FSTYPE,FSAVAIL,FSUSED,FSUSE% | grep " + device + " | awk '{print $1}'| head -1", shell=True))))
            print("[+] File System : ", ''.join(map(chr, subprocess.check_output("lsblk -l -o NAME,SIZE,MOUNTPOINT,FSTYPE,FSAVAIL,FSUSED,FSUSE% | grep " + device + " | awk '{print $4}' | head -1", shell=True))))
            print("[+] Mountpoint : ", ''.join(map(chr, subprocess.check_output("lsblk -l -o NAME,SIZE,MOUNTPOINT,FSTYPE,FSAVAIL,FSUSED,FSUSE% | grep " + device + " | awk '{print $3}' | head -1", shell=True))))

            print("[+] Total Disk Space : ", ''.join(map(chr, subprocess.check_output("lsblk -l -o NAME,SIZE,MOUNTPOINT,FSTYPE,FSAVAIL,FSUSED,FSUSE% | grep " + device + " | awk '{print $2}' | head -1", shell=True))))
            print("[+] Free Disk Space : ", ''.join(map(chr,subprocess.check_output("lsblk -l -o NAME,SIZE,MOUNTPOINT,FSTYPE,FSAVAIL,FSUSED,FSUSE% | grep " + device + " | awk '{print $5}' | head -1", shell=True))))
            print("[+] Used Disk Space : ", ''.join(map(chr,subprocess.check_output("lsblk -l -o NAME,SIZE,MOUNTPOINT,FSTYPE,FSAVAIL,FSUSED,FSUSE% | grep " + device + " | awk '{print $6}' | head -1", shell=True))))
            print("[+] Percentage Used : ", ''.join(map(chr,subprocess.check_output("lsblk -l -o NAME,SIZE,MOUNTPOINT,FSTYPE,FSAVAIL,FSUSED,FSUSE% | grep " + device + " | awk '{print $7}' | head -1", shell=True))))
            print("\n")

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
    info_cpu()
    info_mem()
    info_disk()

os.system("mkdir -p /home/user/" + hostname)
if args.users:
    info_users()
if args.units:
    info_units()
if args.packages:
    info_packages()
if args.proc:
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
if args.hardware:
    info_hardware()

if not args.users and not args.units and not args.packages and not args.proc and not args.limits and not args.kernel and not args.mount and not args.hosts and not args.sudoers and not args.domain_info and not args.hardware:
    info_users()
    info_units()
    info_packages()
    info_proc()
    info_limits()
    info_kernel()
    info_mount()
    info_hosts()
    info_sudo()
    info_hardware()