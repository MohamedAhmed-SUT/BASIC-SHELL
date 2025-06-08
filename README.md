# BASIC-SHELL
This project is a custom-built shell implemented in **Python**, featuring a full command-line interface and an optional **Tkinter-based GUI**. The shell supports common built-in commands, external command execution, piping, redirection, background processes, and a GUI frontend for enhanced usability.

### ✅ Shell Core (C.L.I.py)

- **Built-in Commands:**
  - `exit`, `cd`, `mkdir`, `clear`, `echo`, `history`, `set VAR=VALUE`, `whoami`, `help`
- **External Commands:**
  - Executes any command found in system PATH using `subprocess`
- **Redirection:**
  - `>` write, `>>` append, `<` read from file
- **Piping:**
  - Supports `cmd1 | cmd2` style piping
- **Background Execution:**
  - Appends `&` to run command in background
- **Job Control:**
  - `fg` command to bring background jobs to foreground
- **Environment Variable Support**
- **History:**
  - Maintains history using `readline` (stored in `~/.python_shell_history`)
- **Signal Handling:**
  - Gracefully handles `Ctrl+C` (SIGINT)

##🔧 Prerequisites
- Python 3.7 or later
- Platform: Unix-based OS (Linux/macOS). Windows is supported **with limitations** (e.g., `os.fork()` won't work natively).  
