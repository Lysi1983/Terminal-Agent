import tkinter as tk
from tkinter import scrolledtext, ttk, font
from threading import Thread
import datetime
import os
import crud_cmd
import json

class TerminalGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Terminal Commands GUI")
        self.root.geometry("900x600")
        self.root.minsize(800, 500)
        
        # Set theme colors
        self.bg_color = "#2b2b2b"
        self.text_color = "#e0e0e0"
        self.input_bg = "#3c3f41"
        self.accent_color = "#4b6eaf"
        self.output_bg = "#262626"
        
        # Configure styles
        self.configure_styles()
        
        # Configure window
        self.root.configure(bg=self.bg_color)
        
        # Create frames
        self.create_ui_components()
        
        # Command history
        self.command_history = []
        self.history_position = -1
        
        # Set up key bindings
        self.setup_bindings()
        
        # Welcome message
        self.update_output("Terminal Commands GUI\n")
        self.update_output("----------------------------------------\n")
        self.update_output("Enter a command and press Execute or Enter\n")
        self.update_output("Enter a Help to show all capabilities \n\n")
        
        # Log directory
        self.log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log")
        os.makedirs(self.log_dir, exist_ok=True)
    
    def configure_styles(self):
        """Configure the ttk styles for the application"""
        self.style = ttk.Style()
        
        # Try to use a more modern theme if available
        try:
            self.style.theme_use('clam')
        except:
            pass
            
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("TButton", 
                           background=self.accent_color,
                           foreground=self.text_color,
                           borderwidth=0,
                           focusthickness=3,
                           font=('Segoe UI', 10))
        self.style.map('TButton',
                     background=[('active', self.accent_color),
                                 ('pressed', '#395591')])
        self.style.configure("TLabel", 
                           background=self.bg_color,
                           foreground=self.text_color,
                           font=('Segoe UI', 10))
        self.style.configure("Status.TLabel", 
                           background="#1a1a1a",
                           foreground="#8a8a8a",
                           font=('Segoe UI', 9))
    
    def create_ui_components(self):
        """Create all UI components for the application"""
        # Main frame
        main_frame = ttk.Frame(self.root, style="TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Input frame
        input_frame = ttk.Frame(main_frame, style="TFrame")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Command input label
        ttk.Label(input_frame, text="Command:", style="TLabel").pack(side=tk.LEFT, padx=(0, 10))
        
        # Command entry
        self.command_entry = tk.Entry(input_frame, 
                                     bg=self.input_bg, 
                                     fg=self.text_color,
                                     insertbackground=self.text_color,
                                     relief=tk.FLAT,
                                     font=('Consolas', 11),
                                     bd=8)
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.command_entry.focus_set()
        
        # Buttons frame
        button_frame = ttk.Frame(input_frame, style="TFrame")
        button_frame.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Execute button
        self.execute_btn = ttk.Button(button_frame, text="Execute", command=self.execute_command)
        self.execute_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Clear button
        self.clear_btn = ttk.Button(button_frame, text="Clear", command=self.clear_output)
        self.clear_btn.pack(side=tk.LEFT)
        
        # Output frame
        output_frame = ttk.Frame(main_frame, style="TFrame")
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        # Output text
        self.output_text = scrolledtext.ScrolledText(output_frame,
                                                   wrap=tk.WORD,
                                                   bg=self.output_bg,
                                                   fg=self.text_color,
                                                   insertbackground=self.text_color,
                                                   font=('Consolas', 10),
                                                   bd=0,
                                                   padx=10,
                                                   pady=10)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self.root, 
                                  textvariable=self.status_var, 
                                  relief=tk.SUNKEN, 
                                  anchor=tk.W,
                                  style="Status.TLabel")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def setup_bindings(self):
        """Set up all key bindings for the application"""
        self.command_entry.bind("<Return>", self.execute_command)
        self.command_entry.bind("<Up>", self.previous_command)
        self.command_entry.bind("<Down>", self.next_command)
        
        # Add Ctrl+l to clear the output
        self.root.bind("<Control-l>", lambda e: self.clear_output())
        
    def execute_command(self, event=None):
        """Execute the command from the entry field"""
        command = self.command_entry.get().strip()
        if not command:
            return
            
        # Add to history
        self.command_history.append(command)
        self.history_position = len(self.command_history)
        
        # Clear input
        self.command_entry.delete(0, tk.END)
        
        # Update status
        self.status_var.set("Processing command...")
        self.root.update_idletasks()
        
        # Show command in output
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.update_output(f"\n[{timestamp}] > {command}\n")
        
        # Execute in separate thread to keep GUI responsive
        Thread(target=self.process_command, args=(command,)).start()
    
    def process_command(self, command):
        """Process the command in a separate thread"""
        try:
            # Log the command and start time
            start_time = datetime.datetime.now()
            log_timestamp = start_time.strftime("%Y%m%d_%H%M")
            log_file = os.path.join(self.log_dir, f"query_output{log_timestamp}.log")
            
            # Use structural pattern matching to handle different commands
            command_parts = command.strip().split(maxsplit=1)
            cmd = command_parts[0].lower() if command_parts else ""
            args = command_parts[1] if len(command_parts) > 1 else ""
            
            match cmd:
                case "list" | "ls" | "dir" | "directory" | "Show":
                    if not args:
                        result = crud_cmd.list_directory()
                    else:
                        result = crud_cmd.list_directory(args)
                
                case "find" | "search":
                    if not args:
                        result = "Error: Please specify a pattern to search for"
                    else:
                        pattern_parts = args.split(maxsplit=1)
                        directory = "."
                        pattern = pattern_parts[0]
                        if len(pattern_parts) > 1:
                            directory = pattern_parts[0]
                            pattern = pattern_parts[1]
                        result = crud_cmd.find_files(directory, pattern)
                
                case "read":
                    if not args:
                        result = "Error: Please specify a file to read"
                    else:
                        result = crud_cmd.read_file(args)
                
                case "tree" | "structure":
                    if not args:
                        result = crud_cmd.list_subdirectories(".", recursive=True)
                    else:
                        result = crud_cmd.list_subdirectories(args, recursive=True)
                
                case "disk" | "storage":
                    if not args:
                        result = crud_cmd.get_disk_usage()
                    else:
                        result = crud_cmd.get_disk_usage(args)
                
                case "sysinfo" | "system":
                    result = crud_cmd.get_system_info()
                
                case "network":
                    result = crud_cmd.get_network_interfaces()
                
                case "ping":
                    if not args:
                        result = "Error: Please specify a host to ping"
                    else:
                        result = crud_cmd.ping_host(args)
                
                case "copy":
                    parts = args.split(maxsplit=1)
                    if len(parts) != 2:
                        result = "Error: Please specify source and destination"
                    else:
                        source, destination = parts
                        result = crud_cmd.copy_file(source, destination)
                
                case "open":
                    parts = args.split(maxsplit=1)
                    if not args:
                        result = "Error: Please specify a file to open"
                    elif len(parts) == 1:
                        # Open with default application
                        result = crud_cmd.open_file(parts[0])
                    else:
                        # Open with specified application
                        filepath, application = parts
                        result = crud_cmd.open_file(filepath, application)
                
                case "cd" | "chdir" | "changedir":
                    if not args:
                        # Default to home directory when no args provided
                        result = crud_cmd.change_directory(os.path.expanduser("~"))
                    else:
                        result = crud_cmd.change_directory(args)
                
                case "pwd" | "cwd":
                    # Show current working directory
                    result = f"Current directory: {os.getcwd()}"
                
                case "whoami" | "user" | "userinfo":
                    # Show username and computer name
                    result = crud_cmd.get_user_info()
                
                case "create":
                    parts = args.split(maxsplit=1)
                    if not args:
                        result = "Error: Please specify a file path to create"
                    elif len(parts) == 1:
                        # Create empty file
                        result = crud_cmd.create_file(parts[0], "")
                    else:
                        # Create file with content
                        filepath, content = parts
                        result = crud_cmd.create_file(filepath, content)
                
                case "telnet":
                    parts = args.split(maxsplit=2)
                    if not args:
                        result = "Error: Please specify a host to connect to"
                    elif len(parts) == 1:
                        # Connect to host with default port (23)
                        result = crud_cmd.telnet(parts[0])
                    elif len(parts) == 2:
                        # Connect to host with specified port
                        host, port = parts
                        result = crud_cmd.telnet(host, port)
                    else:
                        # Connect with custom timeout
                        host, port, timeout = parts
                        result = crud_cmd.telnet(host, port, int(timeout))
                
                case "traceroute" | "trace":
                    if not args:
                        result = "Error: Please specify a host to trace"
                    else:
                        result = crud_cmd.traceroute(args)
                
                case "scan" | "ports" | "scanports":
                    parts = args.split(maxsplit=3)
                    if not args:
                        result = "Error: Please specify a host to scan"
                    elif len(parts) == 1:
                        # Scan host with default ports (1-1024)
                        result = crud_cmd.scan_ports(parts[0])
                    elif len(parts) == 2:
                        # Scan with start port
                        host, start_port = parts
                        try:
                            start_port = int(start_port)
                            result = crud_cmd.scan_ports(host, start_port=start_port)
                        except ValueError:
                            result = "Error: Port must be an integer"
                    elif len(parts) == 3:
                        # Scan with start and end ports
                        host, start_port, end_port = parts
                        try:
                            start_port = int(start_port)
                            end_port = int(end_port)
                            result = crud_cmd.scan_ports(host, start_port=start_port, end_port=end_port)
                        except ValueError:
                            result = "Error: Ports must be integers"
                    else:
                        # Scan with start, end ports and timeout
                        host, start_port, end_port, timeout = parts
                        try:
                            start_port = int(start_port)
                            end_port = int(end_port)
                            timeout = float(timeout)
                            result = crud_cmd.scan_ports(host, start_port=start_port, end_port=end_port, timeout=timeout)
                        except ValueError:
                            result = "Error: Invalid parameters"
                
                case "processes" | "ps" | "tasklist":
                    result = crud_cmd.list_processes()
                
                case "get" | "http_get":
                    parts = args.split(maxsplit=3)
                    if not args:
                        result = "Error: Please specify a URL for the GET request"
                    elif len(parts) == 1:
                        # Simple GET request with just URL
                        result = crud_cmd.http_get_request(parts[0])
                    elif len(parts) == 2:
                        # GET request with URL and params
                        url, params = parts
                        result = crud_cmd.http_get_request(url, params=params)
                    elif len(parts) == 3:
                        # GET request with URL, params, and headers
                        url, params, headers = parts
                        result = crud_cmd.http_get_request(url, params=params, headers=headers)
                    else:
                        # GET request with URL, params, headers, and timeout
                        url, params, headers, timeout = parts
                        try:
                            timeout = int(timeout)
                            result = crud_cmd.http_get_request(url, params=params, headers=headers, timeout=timeout)
                        except ValueError:
                            result = "Error: Timeout must be an integer value in seconds"
                
                case "post" | "http_post":
                    parts = args.split(maxsplit=4)
                    if not args:
                        result = "Error: Please specify a URL for the POST request"
                    elif len(parts) == 1:
                        # Simple POST request with just URL
                        result = crud_cmd.http_post_request(parts[0])
                    elif len(parts) == 2:
                        # POST request with URL and data
                        url, data = parts
                        result = crud_cmd.http_post_request(url, data=data)
                    elif len(parts) == 3:
                        # POST request with URL, data, and headers
                        url, data, headers = parts
                        result = crud_cmd.http_post_request(url, data=data, headers=headers)
                    elif len(parts) == 4:
                        # POST request with URL, data, headers, and timeout
                        url, data, headers, timeout = parts
                        try:
                            timeout = int(timeout)
                            result = crud_cmd.http_post_request(url, data=data, headers=headers, timeout=timeout)
                        except ValueError:
                            result = "Error: Timeout must be an integer value in seconds"
                    else:
                        # POST request with URL, data, headers, json_data and timeout
                        url, data, headers, json_data, timeout = parts
                        try:
                            timeout = int(timeout)
                            result = crud_cmd.http_post_request(url, data=data, headers=headers, json_data=json_data, timeout=timeout)
                        except ValueError:
                            result = "Error: Timeout must be an integer value in seconds"
                
                case "help":
                    result = """Available commands:
list/ls/dir/directory/show [directory] - List files in directory
find/search [directory] pattern - Find files matching pattern
read filename - Read file contents
tree/structure [directory] - Show directory structure recursively
disk/storage [path] - Show disk usage information
sysinfo/system - Show system information
network - Show network interfaces
ping host - Ping a host
copy source destination - Copy a file from source to destination
open filename [application] - Open file with default or specified application
cd/chdir/changedir [directory] - Change current directory
pwd/cwd - Show current working directory
whoami/user/userinfo - Show username and computer name
create filename [content] - Create a new file with optional content
telnet host [port] [timeout] - Connect to host via telnet
traceroute/trace host - Trace route to host
scan/ports/scanports host [start_port] [end_port] [timeout] - Scan ports on a host
processes/ps/tasklist - List running processes
get/http_get url [params] [headers] [timeout] - Send HTTP GET request
post/http_post url [data] [headers] [timeout] - Send HTTP POST request
help - Show this help message"""
                
                case _:
                    result = f"Unknown command: {cmd}. Type 'help' for available commands."
            
            # Log the result
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(f"Command: {command}\n")
                f.write(f"Timestamp: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Result:\n{result}\n")
            
            # Update UI with the result
            self.root.after(0, self.update_output, f"{result}\n")
            self.root.after(0, self.status_var.set, f"Ready - Command completed in {(datetime.datetime.now() - start_time).total_seconds():.2f}s")
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.root.after(0, self.update_output, f"{error_msg}\n")
            self.root.after(0, self.status_var.set, "Error occurred")
            
            # Log the error
            with open(os.path.join(self.log_dir, f"error_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.log"), "w") as f:
                f.write(f"Command: {command}\n")
                f.write(f"Error: {str(e)}\n")
    
    def update_output(self, text):
        """Update the output text widget"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.NORMAL)  # Keep it editable for copy-paste
    
    def clear_output(self):
        """Clear the output text widget"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.update_output("Terminal output cleared.\n\n")
    
    def previous_command(self, event):
        """Navigate to previous command in history"""
        if not self.command_history or self.history_position <= 0:
            return "break"
        
        self.history_position -= 1
        self.command_entry.delete(0, tk.END)
        self.command_entry.insert(0, self.command_history[self.history_position])
        return "break"
    
    def next_command(self, event):
        """Navigate to next command in history"""
        if not self.command_history or self.history_position >= len(self.command_history) - 1:
            if self.history_position == len(self.command_history) - 1:
                self.history_position += 1
                self.command_entry.delete(0, tk.END)
            return "break"
        
        self.history_position += 1
        self.command_entry.delete(0, tk.END)
        self.command_entry.insert(0, self.command_history[self.history_position])
        return "break"