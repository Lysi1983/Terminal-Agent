import os
import subprocess
import platform
import glob
import socket
import time
import datetime
import requests
import json
from pathlib import Path

def is_windows():
    """Check if the current operating system is Windows"""
    return platform.system().lower() == 'windows'

def list_directory(directory='.', include_hidden=False):
    """
    List all files and directories in the specified directory.
    Args:
        directory: Directory path to list (default: current directory)
        include_hidden: Whether to include hidden files (default: False)
    Returns:
        List of files and directories
    """
    if not os.path.exists(directory):
        return f"Error: Directory '{directory}' does not exist"
    
    try:
        items = os.listdir(directory)
        if not include_hidden and is_windows():
            # Filter out hidden files in Windows
            items = [item for item in items if not os.path.isfile(os.path.join(directory, item)) 
                    or not bool(os.stat(os.path.join(directory, item)).st_file_attributes & 2)]
        
        result = []
        for item in items:
            full_path = os.path.join(directory, item)
            item_type = "Directory" if os.path.isdir(full_path) else "File"
            size = os.path.getsize(full_path) if os.path.isfile(full_path) else "<DIR>"
            modified = datetime.datetime.fromtimestamp(os.path.getmtime(full_path)).strftime('%Y-%m-%d %H:%M:%S')
            result.append(f"{item:<30} {item_type:<10} {size:<10} {modified}")
            
        return "\n".join(result)
    except Exception as e:
        return f"Error listing directory: {str(e)}"

def list_subdirectories(directory='.', recursive=False):
    """
    List all subdirectories in the specified directory.
    Args:
        directory: Directory path to list subdirectories from (default: current directory)
        recursive: Whether to recursively list subdirectories (default: False)
    Returns:
        List of subdirectories
    """
    if not os.path.exists(directory):
        return f"Error: Directory '{directory}' does not exist"
    
    try:
        if recursive:
            subdirs = []
            for root, dirs, _ in os.walk(directory):
                for d in dirs:
                    subdirs.append(os.path.join(root, d))
            return "\n".join(subdirs) if subdirs else "No subdirectories found"
        else:
            subdirs = [os.path.join(directory, d) for d in os.listdir(directory) 
                      if os.path.isdir(os.path.join(directory, d))]
            return "\n".join(subdirs) if subdirs else "No subdirectories found"
    except Exception as e:
        return f"Error listing subdirectories: {str(e)}"

def find_files(directory='.', pattern='*', recursive=False):
    """
    Find files matching a pattern in the specified directory.
    Args:
        directory: Directory path to search in (default: current directory)
        pattern: File pattern to match (default: all files)
        recursive: Whether to search recursively (default: False)
    Returns:
        List of matching files
    """
    if not os.path.exists(directory):
        return f"Error: Directory '{directory}' does not exist"
    
    try:
        if recursive:
            search_path = os.path.join(directory, '**', pattern)
            files = glob.glob(search_path, recursive=True)
        else:
            search_path = os.path.join(directory, pattern)
            files = glob.glob(search_path)
        
        return "\n".join(files) if files else f"No files matching '{pattern}' found"
    except Exception as e:
        return f"Error finding files: {str(e)}"

def create_file(filepath, content=""):
    """
    Create a new file with optional content.
    Args:
        filepath: Path to the new file
        content: Content to write to the file (default: empty)
    Returns:
        Success or error message
    """
    try:
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"File created successfully: {filepath}"
    except Exception as e:
        return f"Error creating file: {str(e)}"

def read_file(filepath, line_numbers=None):
    """
    Read and return the contents of a file.
    Args:
        filepath: Path to the file
        line_numbers: Optional tuple (start, end) to read specific lines
    Returns:
        File contents or error message
    """
    if not os.path.exists(filepath):
        return f"Error: File '{filepath}' does not exist"
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            if line_numbers:
                start, end = line_numbers
                lines = f.readlines()
                return ''.join(lines[start-1:end])
            else:
                return f.read()
    except UnicodeDecodeError:
        try:
            with open(filepath, 'r', encoding='latin-1') as f:
                if line_numbers:
                    start, end = line_numbers
                    lines = f.readlines()
                    return ''.join(lines[start-1:end])
                else:
                    return f.read()
        except Exception as e:
            return f"Error reading file with latin-1 encoding: {str(e)}"
    except Exception as e:
        return f"Error reading file: {str(e)}"

def ping_host(host, count=4):
    """
    Ping a host to check connectivity.
    Args:
        host: Hostname or IP address to ping
        count: Number of ping packets to send (default: 4)
    Returns:
        Ping results
    """
    try:
        if is_windows():
            cmd = ['ping', '-n', str(count), host]
        else:
            cmd = ['ping', '-c', str(count), host]
            
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"Error pinging host: {str(e)}"

def get_network_interfaces():
    """
    Get information about network interfaces.
    Returns:
        Network interface information
    """
    try:
        if is_windows():
            result = subprocess.run(['ipconfig', '/all'], capture_output=True, text=True)
            return result.stdout
        else:
            result = subprocess.run(['ifconfig'], capture_output=True, text=True)
            return result.stdout
    except Exception as e:
        return f"Error getting network interfaces: {str(e)}"

def traceroute(host):
    """
    Perform a traceroute to a host.
    Args:
        host: Hostname or IP address to trace
    Returns:
        Traceroute results
    """
    try:
        if is_windows():
            cmd = ['tracert', host]
        else:
            cmd = ['traceroute', host]
            
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"Error performing traceroute: {str(e)}"

def scan_ports(host, start_port=1, end_port=1024, timeout=1):
    """
    Scan open ports on a host.
    Args:
        host: Hostname or IP address to scan
        start_port: Starting port number (default: 1)
        end_port: Ending port number (default: 1024)
        timeout: Connection timeout in seconds (default: 1)
    Returns:
        List of open ports
    """
    open_ports = []
    try:
        for port in range(start_port, end_port + 1):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            if result == 0:
                try:
                    service = socket.getservbyport(port)
                    open_ports.append(f"Port {port}: {service}")
                except:
                    open_ports.append(f"Port {port}: unknown service")
            sock.close()
        
        return "\n".join(open_ports) if open_ports else f"No open ports found on {host}"
    except socket.gaierror:
        return f"Hostname could not be resolved: {host}"
    except socket.error as e:
        return f"Could not connect to server: {str(e)}"
    except Exception as e:
        return f"Error scanning ports: {str(e)}"

def copy_file(source, destination):
    """
    Copy a file from source to destination.
    Args:
        source: Source file path
        destination: Destination file path
    Returns:
        Success or error message
    """
    if not os.path.exists(source):
        return f"Error: Source file '{source}' does not exist"
    
    try:
        import shutil
        shutil.copy2(source, destination)
        return f"File copied successfully from {source} to {destination}"
    except Exception as e:
        return f"Error copying file: {str(e)}"

def get_system_info():
    """
    Get system information.
    Returns:
        System information
    """
    try:
        info = []
        info.append(f"System: {platform.system()}")
        info.append(f"Node: {platform.node()}")
        info.append(f"Release: {platform.release()}")
        info.append(f"Version: {platform.version()}")
        info.append(f"Machine: {platform.machine()}")
        info.append(f"Processor: {platform.processor()}")
        
        if is_windows():
            result = subprocess.run(['systeminfo'], capture_output=True, text=True)
            info.append("\nDetailed System Information:")
            info.append(result.stdout)
            
        return "\n".join(info)
    except Exception as e:
        return f"Error getting system information: {str(e)}"

def get_disk_usage(path='.'):
    """
    Get disk usage information.
    Args:
        path: Path to check disk usage (default: current directory)
    Returns:
        Disk usage information
    """
    try:
        if is_windows():
            import ctypes
            free_bytes = ctypes.c_ulonglong(0)
            total_bytes = ctypes.c_ulonglong(0)
            available_bytes = ctypes.c_ulonglong(0)
            
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                ctypes.c_wchar_p(path),
                ctypes.pointer(free_bytes),
                ctypes.pointer(total_bytes),
                ctypes.pointer(available_bytes)
            )
            
            total_gb = total_bytes.value / (1024**3)
            free_gb = free_bytes.value / (1024**3)
            used_gb = total_gb - free_gb
            
            return f"Total: {total_gb:.2f} GB\nUsed: {used_gb:.2f} GB\nFree: {free_gb:.2f} GB"
        else:
            result = subprocess.run(['df', '-h', path], capture_output=True, text=True)
            return result.stdout
    except Exception as e:
        return f"Error getting disk usage: {str(e)}"

def list_processes():
    """
    List running processes.
    Returns:
        List of running processes
    """
    try:
        if is_windows():
            result = subprocess.run(['tasklist'], capture_output=True, text=True)
        else:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            
        return result.stdout
    except Exception as e:
        return f"Error listing processes: {str(e)}"

def open_file(filepath, application=None):
    """
    Open a file with the default application or a specified application.
    Args:
        filepath: Path to the file to open
        application: Optional application to use for opening the file
    Returns:
        Success or error message
    """
    if not os.path.exists(filepath):
        return f"Error: File '{filepath}' does not exist"
    
    try:
        # Check if the file is an Excel file
        file_ext = os.path.splitext(filepath)[1].lower()
        excel_extensions = ['.xlsx', '.xls', '.xlsm', '.xlsb', '.xltx', '.xltm', '.xlt']
        
        if file_ext in excel_extensions:
            return f"Warning: Excel files cannot be opened directly. Please use a specific Excel application.\nTry: open {filepath} excel.exe"
        
        if application:
            # Open file with specified application
            if is_windows():
                # For Windows
                subprocess.Popen([application, filepath])
                return f"Opened '{filepath}' with {application}"
            else:
                # For Unix/Linux
                subprocess.Popen([application, filepath])
                return f"Opened '{filepath}' with {application}"
        else:
            # Open file with default application
            if is_windows():
                os.startfile(filepath)
            else:
                # For macOS
                if platform.system() == 'Darwin':
                    subprocess.Popen(['open', filepath])
                # For Linux
                else:
                    subprocess.Popen(['xdg-open', filepath])
            return f"Opened '{filepath}' with default application"
    except Exception as e:
        return f"Error opening file: {str(e)}"

def change_directory(directory):
    """
    Change the current working directory.
    Args:
        directory: Path to the directory to change to
    Returns:
        Success or error message
    """
    try:
        if directory == "~":
            directory = os.path.expanduser("~")
        elif directory == "..":
            directory = os.path.dirname(os.getcwd())
        elif not os.path.isabs(directory):
            directory = os.path.abspath(os.path.join(os.getcwd(), directory))
        
        if not os.path.exists(directory):
            return f"Error: Directory '{directory}' does not exist"
            
        if not os.path.isdir(directory):
            return f"Error: '{directory}' is not a directory"
            
        os.chdir(directory)
        return f"Changed directory to: {os.getcwd()}"
    except Exception as e:
        return f"Error changing directory: {str(e)}"

def get_user_info():
    """
    Get username and computer name information.
    Returns:
        Username and computer name information
    """
    try:
        import getpass
        import socket
        
        username = getpass.getuser()
        computer_name = socket.gethostname()
        
        return f"Username: {username}\nComputer name: {computer_name}"
    except Exception as e:
        return f"Error getting user information: {str(e)}"

def telnet(host, port=23, timeout=10):
    """
    Connect to a remote host using telnet protocol.
    Args:
        host: Hostname or IP address to connect to
        port: Port number to connect to (default: 23)
        timeout: Connection timeout in seconds (default: 10)
    Returns:
        Connection status message
    """
    try:
        import socket
        
        # Create a socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        # Attempt to connect
        result = sock.connect_ex((host, int(port)))
        
        if result == 0:
            sock.close()
            return f"Successfully connected to {host} on port {port}. Connection established."
        else:
            error_code = socket.errno.errorcode.get(result, "Unknown error")
            return f"Failed to connect to {host} on port {port}. Error code: {result} ({error_code})"
    
    except socket.gaierror:
        return f"Hostname could not be resolved: {host}"
    except socket.error as e:
        return f"Socket error: {str(e)}"
    except ValueError:
        return f"Invalid port number: {port}"
    except Exception as e:
        return f"Error connecting to {host}:{port}: {str(e)}"
    finally:
        try:
            sock.close()
        except:
            pass

def http_get_request(url, params=None, headers=None, timeout=30):
    """
    Send an HTTP GET request to the specified URL.
    Args:
        url: URL to send the request to
        params: Optional query parameters as a dictionary
        headers: Optional HTTP headers as a dictionary
        timeout: Request timeout in seconds (default: 30)
    Returns:
        Response content and status information
    """
    try:
        # Convert headers string to dictionary if provided as a string
        if headers and isinstance(headers, str):
            try:
                headers = json.loads(headers)
            except json.JSONDecodeError:
                return "Error: Invalid headers format. Please provide valid JSON."
        
        # Convert params string to dictionary if provided as a string
        if params and isinstance(params, str):
            try:
                params = json.loads(params)
            except json.JSONDecodeError:
                return "Error: Invalid params format. Please provide valid JSON."
        
        # Send the GET request
        response = requests.get(url, params=params, headers=headers, timeout=timeout)
        
        # Prepare the response details
        result = []
        result.append(f"Status Code: {response.status_code}")
        result.append(f"Response Time: {response.elapsed.total_seconds():.2f} seconds")
        
        # Add headers to the result
        result.append("\nResponse Headers:")
        for key, value in response.headers.items():
            result.append(f"  {key}: {value}")
        
        return "\n".join(result)
    except requests.exceptions.RequestException as e:
        return f"Error sending GET request: {str(e)}"
    except Exception as e:
        return f"Unexpected error during GET request: {str(e)}"

def http_post_request(url, data=None, json_data=None, headers=None, timeout=30):
    """
    Send an HTTP POST request to the specified URL.
    Args:
        url: URL to send the request to
        data: Optional form data as a dictionary or string
        json_data: Optional JSON data as a dictionary or string
        headers: Optional HTTP headers as a dictionary
        timeout: Request timeout in seconds (default: 30)
    Returns:
        Response content and status information
    """
    try:
        # Convert headers string to dictionary if provided as a string
        if headers and isinstance(headers, str):
            try:
                headers = json.loads(headers)
            except json.JSONDecodeError:
                return "Error: Invalid headers format. Please provide valid JSON."
        
        # Convert data string to dictionary if provided as a string
        if data and isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                # If it's not valid JSON, treat it as form data
                pass
        
        # Convert json_data string to dictionary if provided as a string
        if json_data and isinstance(json_data, str):
            try:
                json_data = json.loads(json_data)
            except json.JSONDecodeError:
                return "Error: Invalid JSON data format. Please provide valid JSON."
        
        # Send the POST request
        if json_data:
            response = requests.post(url, json=json_data, headers=headers, timeout=timeout)
        else:
            response = requests.post(url, data=data, headers=headers, timeout=timeout)
        
        # Prepare the response details
        result = []
        result.append(f"Status Code: {response.status_code}")
        result.append(f"Response Time: {response.elapsed.total_seconds():.2f} seconds")
        
        # Add headers to the result
        result.append("\nResponse Headers:")
        for key, value in response.headers.items():
            result.append(f"  {key}: {value}")
        
        return "\n".join(result)
    except requests.exceptions.RequestException as e:
        return f"Error sending POST request: {str(e)}"
    except Exception as e:
        return f"Unexpected error during POST request: {str(e)}"

# Example usage
if __name__ == "__main__":
    res=find_files (directory='.', pattern='*.py', recursive=True)
    print(res)