# Terminal Agent

A versatile command-line utility toolkit that provides various system operations, file management, and network diagnostics functionality with a user-friendly GUI interface.

## Features

- **File Management**
  - List directories and files
  - Find files by pattern
  - Create, read, and copy files
  - Open files with default or specified applications
  - View directory structures recursively

- **System Operations**
  - Get system information
  - Display disk usage
  - List running processes
  - Change working directory
  - Get user information

- **Network Utilities**
  - Ping hosts
  - Display network interfaces
  - Perform traceroutes
  - Scan open ports
  - Telnet connectivity testing
  - HTTP GET and POST requests with status monitoring

## Installation and Running the Application

### Prerequisites
- Python 3.6 or higher
- Required packages: requests, langchain, langchain_google_genai

### Running the Application

There are three ways to start the Terminal Agent:

1. **Standard Start (with console):**
   ```
   python gui_launcher.py
   ```

2. **Using Batch File (with console):**
   ```
   start_terminal_agent.bat
   ```
   This script checks for dependencies and installs them if needed.

3. **Silent Start (no console window):**
   ```
   start_terminal_agent_hidden.vbs
   ```
   Double-click this file to start the application without showing a command prompt window.

## Usage

This toolkit can be used as a standalone command-line utility or integrated into larger applications.

### Example Usage in Python

```python
from crud_cmd import list_directory, find_files, get_system_info, http_get_request

# List files in current directory
print(list_directory())

# Find all Python files recursively
print(find_files(pattern="*.py", recursive=True))

# Get system information
print(get_system_info())

# Send an HTTP GET request
print(http_get_request("https://jsonplaceholder.typicode.com/posts/1"))
```

### Terminal GUI Commands

The following commands can be entered in the Terminal GUI:

```
list/ls/dir [directory]           - List files in directory
find/search [directory] pattern   - Find files matching pattern
read filename                     - Read file contents
tree/structure [directory]        - Show directory structure recursively
disk/storage [path]               - Show disk usage information
sysinfo/system                    - Show system information
network                           - Show network interfaces
ping host                         - Ping a host
copy source destination           - Copy a file
open filename [application]       - Open file with application
cd/chdir/changedir [directory]    - Change current directory
pwd/cwd                           - Show current working directory
whoami/user/userinfo              - Show username and computer name
create filename [content]         - Create a new file
telnet host [port] [timeout]      - Connect to host via telnet
traceroute/trace host             - Trace route to host
scan/ports host [start] [end]     - Scan ports on a host
processes/ps/tasklist             - List running processes
help                              - Show all available commands
```

### HTTP Request Commands

```
# Basic GET request
get https://api.example.com/data

# GET with query parameters (JSON format)
get https://api.example.com/search {"q":"search term","limit":10}

# GET with headers
get https://api.example.com/data {} {"Authorization":"Bearer token"}

# POST request with data
post https://api.example.com/submit "name=John&age=30"

# POST with JSON data
post https://api.example.com/json {} {} {"name":"John","age":30}
```

The HTTP requests will return:
- Status Code
- Response Time
- Response Headers

## File Structure

- `crud_cmd.py` - Core file operations and system utilities
- `files_agent.py` - File management agent with safety features
- `terminal_gui.py` - Terminal UI interface
- `gui_launcher.py` - GUI application launcher

- `start_terminal_agent_hidden.vbs` - VBScript to start the application without showing console
- `start_terminal_agent_helper.bat` - Helper batch file for the VBS launcher
- `log/` - Directory containing command execution logs

## Requirements

- Python 3.6+
- Standard library modules
- External dependencies:
  - requests (for HTTP functionality)
  - langchain (for AI-assisted functionality in files_agent.py)
  - langchain_google_genai (for AI-assisted functionality in files_agent.py)

## Platform Support

- Windows (primary)
- Limited support for macOS and Linux

## Logging

All command executions are logged in the `log/` directory with timestamps for troubleshooting and audit purposes.
