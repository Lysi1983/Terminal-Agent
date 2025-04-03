from langchain_core.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain_experimental.utilities import PythonREPL
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import subprocess
import warnings

import re




warnings.filterwarnings("ignore")

# Security function to check for dangerous commands
def check_code_safety(code):
    # List of dangerous patterns to check for
    dangerous_patterns = [
        # File deletion and modification
        r'\.remove\(', r'\.unlink\(', r'\.rmdir\(', r'os\.remove', r'os\.unlink', 
        r'shutil\.rmtree', r'del\s+', r'rm\s+', r'rmdir', 
        
        # System commands that could be harmful
        r'format\s+[a-zA-Z]:', r'fdisk', r'mkfs', 
        
        # Registry modifications
        r'winreg\.SetValue', r'reg\s+delete', r'reg\s+add',
        
        # Network dangerous operations
        r'socket\.bind\(', r'urllib\.request\.urlopen\(.+?exec', 
        
        # Shell execution that might be risky
        r'subprocess\.call\(.+?rm\s', r'subprocess\.run\(.+?del\s',
        r'os\.system\(.+?(rm|del|format)\s', r'eval\(', r'exec\('
    ]
    
    # Check if code contains any dangerous patterns
    for pattern in dangerous_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            return False, f"Potentially dangerous operation detected: {pattern}"
    
    # Additional checks for specific commands
    if 'os.system' in code or 'subprocess.call' in code or 'subprocess.run' in code:
        cmd = re.search(r'(os\.system|subprocess\.call|subprocess\.run)\s*\(\s*[\'"](.+?)[\'"]', code)
        if cmd:
            command = cmd.group(2).lower()
            # Check for dangerous system commands
            dangerous_cmds = ['del ', 'rm ', 'format', 'fdisk', 'mkfs', 'dd ', 'shutdown', 'reboot']
            for dangerous_cmd in dangerous_cmds:
                if dangerous_cmd in command:
                    return False, f"Dangerous system command detected: {dangerous_cmd}"
    
    return True, "Code appears safe"

# Create a custom PythonREPL class that checks code safety before execution
class SafeLoggingPythonREPL(PythonREPL):
    def run(self, code, **kwargs):
     
        
        # Check if code is safe to execute
        is_safe, reason = check_code_safety(code)
        
        if not is_safe:
            error_msg = f"EXECUTION BLOCKED: {reason}"
           
            return error_msg
        
        # Execute code if it's safe
        result = super().run(code, **kwargs)
        
        # Log the result
       
        return result

# Create more complete globals for the Python REPL
python_repl = SafeLoggingPythonREPL()
# Pre-import common modules in the REPL's globals
python_repl.globals['os'] = os
python_repl.globals['subprocess'] = subprocess

llm = ChatGoogleGenerativeAI(model="", google_api_key="", temperature=0.1)

# Create a proper Tool instance for PythonREPL with improved description
python_tool = Tool(
    name="python_repl",
    description="""Use this to execute python commands. 
The os,subprocess modules are already imported for you.
List,ll, and print are also available.
Read from txt,excel, and csv files are also available.
As a Windows expert:
  - Use Windows-specific path conventions (backslashes or raw strings)
  - Prefer Windows native commands (dir, type) over Unix equivalents
  - Use appropriate modules like winreg for registry operations
  - Handle file permissions according to Windows standards
  - Access Windows-specific directories using os.environ variables
Input should be a valid python command without markdown formatting.
Do not use triple backticks in your code.
    """,
    
    func=python_repl.run
)

# Initialize agent with the properly configured tool
agent = initialize_agent(
    [python_tool],
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=False,  # Changed to False to avoid verbose output
    handle_parsing_errors=True
)



def main(command):
    # Use a proper prompt template to guide the agent's responses
    messages = [  
        ("system", """
         You are a Python expert on Windows and Linux systems. 
         1. First check what is the system Windows or Linux.
         2. Then execute the command in the system.
         3. Always include necessary imports at the top of your code.
         4. Do not use remove or delete commands as they will be blocked.
         
         Windows-specific guidelines:
         - Use Windows-specific path conventions (backslashes or raw strings)
         - Prefer Windows native commands (dir, type) over Unix equivalents
         - Use appropriate modules like winreg for registry operations
         - Access Windows folders using proper environment variables (os.environ)
         - Handle file encoding properly with 'utf-8' when reading/writing files
         
         General best practices:
         - Write clear, commented code with descriptive variable names
         - Handle exceptions appropriately with try/except blocks
         - Verify file/directory existence before operations
         - Use context managers (with) for file operations
         - Format output in a clean, readable manner
         """),      
        ("human", command)  #  
        
    ]
    result = agent.invoke(messages)
    if isinstance(result, dict) and "output" in result:
       return result["output"]
    else:
    
        return result

if __name__ == "__main__":
    command = input("Enter your command: ")
    result = main(command)
    print(result)

