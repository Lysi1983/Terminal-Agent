# Terminal Agent

A versatile command-line utility toolkit that provides various system operations, file management, and network diagnostics functionality.

## Features

- **File Management**
  - List directories and files
  - Find files by pattern
  - Create, read, and copy files
  - Open files with default or specified applications

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
  - HTTP GET and POST requests

## Usage

This toolkit can be used as a standalone command-line utility or integrated into larger applications.

### Example Usage

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

## File Structure

- `crud_cmd.py` - Core file operations and system utilities
- `files_agent.py` - File management agent with safety features
- `terminal_gui.py` - Terminal UI interface
- `gui_launcher.py` - GUI application launcher

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