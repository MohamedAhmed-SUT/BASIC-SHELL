import os
import sys
import subprocess
import shutil
import getpass
import signal
import readline
from collections import deque



command_history = deque(maxlen=100) 
background_jobs = []  
environment_variables = os.environ.copy()   


history_file = os.path.expanduser("~/.python_shell_history")


if os.path.exists(history_file):
    readline.read_history_file(history_file)
readline.set_history_length(100) 

def save_history():

    readline.write_history_file(history_file)

def execute_command(command):

    try:
        if shutil.which(command[0]) is None:
            print(f"Error: Command '{command[0]}' not found.")
        else:
            subprocess.run(command, check=True, env=environment_variables)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def builtin_commands(command):

    if command[0] == "exit":
        print("Exiting the shell.")
        save_history()  
        sys.exit()
    elif command[0] == "clear":
        os.system("clear")
    elif command[0] == "whoami":
        print(getpass.getuser())
    elif command[0] == "cd":
        if len(command) < 2:
            print(os.getcwd()) 
        else:
            try:
                os.chdir(command[1])
            except Exception as e:
                print(f"cd: {e}")
    elif command[0] == "mkdir":
        if len(command) < 2:
            print("Error: Please specify the folder name.")
        else:
            try:
                os.makedirs(command[1])
                print(f"Directory '{command[1]}' created successfully.")
            except Exception as e:
                print(f"Error creating directory: {e}")
    elif command[0] == "set":
        if len(command) < 2:
            print("Error: Please specify a variable in the format VAR=VALUE.")
        else:
            key, value = command[1].split("=", 1)
            environment_variables[key] = value
            print(f"Set {key} to {value}")
    elif command[0] == "echo":
        if command[1].startswith("$"):
            var_name = command[1][1:]
            print(environment_variables.get(var_name, ""))
        else:
            print(" ".join(command[1:]))
    elif command[0] == "history":
        for i, cmd in enumerate(command_history):
            print(f"{i + 1}: {cmd}")
    elif command[0] == "help":
        print("Available commands:")
        print("  exit            - Exit the shell")
        print("  clear           - Clear the screen")
        print("  whoami          - Display the current user")
        print("  cd <path>       - Change the current directory")
        print("  mkdir <name>    - Create a new directory")
        print("  set VAR=VALUE   - Set an environment variable")
        print("  echo $VAR       - Display an environment variable's value")
        print("  history         - Show command history")
        print("  help            - Display this help message")
    else:
        return False
    return True

def parse_input(input_command):
    
    global command_history, background_jobs
    background = False
    input_command = input_command.strip()
    command_history.append(input_command) 
    readline.add_history(input_command)  

   
    if input_command.endswith("&"):
        input_command = input_command[:-1].strip()
        background = True

    command_parts = input_command.split()

    if command_parts[0] == "fg":
        fg(command_parts) 
        return

    if "|" in input_command:
        commands = [cmd.strip() for cmd in input_command.split("|")]
        processes = []
        prev_pipe = None
        for i, cmd in enumerate(commands):
            cmd_parts = cmd.split()
            if i == 0:
                prev_pipe = subprocess.Popen(cmd_parts, stdout=subprocess.PIPE)
            elif i == len(commands) - 1:
                subprocess.run(cmd_parts, stdin=prev_pipe.stdout)
                prev_pipe.stdout.close()
            else:
                prev_pipe = subprocess.Popen(cmd_parts, stdin=prev_pipe.stdout, stdout=subprocess.PIPE)
        return

    
    if ">" in input_command or "<" in input_command:
        if ">>" in input_command:
            parts = input_command.split(">>", 1)
            command = parts[0].strip().split()
            output_file = parts[1].strip()
            with open(output_file, "a") as f:
                subprocess.run(command, stdout=f, env=environment_variables)
        elif ">" in input_command:
            parts = input_command.split(">", 1)
            command = parts[0].strip().split()
            output_file = parts[1].strip()
            with open(output_file, "w") as f:
                subprocess.run(command, stdout=f, env=environment_variables)
        elif "<" in input_command:
            parts = input_command.split("<", 1)
            command = parts[0].strip().split()
            input_file = parts[1].strip()
            with open(input_file, "r") as f:
                subprocess.run(command, stdin=f, env=environment_variables)
        return


    command_parts = input_command.split()
    if builtin_commands(command_parts):
        return

    
    if background:
        try:
            pid = os.fork()
            if pid == 0:  
                os.execvp(command_parts[0], command_parts)  
            else: 
                background_jobs.append(pid)  
                print(f"Command '{input_command}' is running in the background with PID {pid}.")
        except Exception as e:
            print(f"Error running background command: {e}")
    else:
        execute_command(command_parts)

def fg(command=None):
    global background_jobs

    if command is None:
        if not background_jobs:
            print("No background jobs to bring to the foreground.")
            return

        pid = background_jobs.pop()  
    else:
        try:
            pid = int(command[1])  
        except (IndexError, ValueError):
            print("Error: Please provide a valid PID for the background job.")
            return

    try:
        print(f"Bringing background job with PID {pid} to the foreground.")
        os.waitpid(pid, 0)  

        background_jobs = [job for job in background_jobs if job != pid]
    except ChildProcessError as e:
        print(f"Error: {e}")


def signal_handler(sig, frame):

    print("\nUse 'exit' to quit the shell.")

def main():

    signal.signal(signal.SIGINT, signal_handler)  

    while True:
        try:
            input_command = input("Basic Python Shell> ").strip().lower()
            if not input_command:
                continue  
            if input_command == "fg":
                fg() 
            else:
                parse_input(input_command)
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit the shell.")
        except EOFError:
            print("\nExiting shell.")
            save_history() 
            break

if __name__ == "__main__":
    main()