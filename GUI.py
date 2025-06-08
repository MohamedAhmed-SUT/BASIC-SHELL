import tkinter as tk
from tkinter import scrolledtext
import subprocess
import threading


CLI_PROGRAM = "CLI.py"

class GUIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Basic Shell GUI")
        self.root.geometry("800x600")
        

        self.output_widget = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, font=("Courier", 12))
        self.output_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.output_widget.insert(tk.END, "Welcome to the Basic Shell........\n")
        self.output_widget.configure(state="disabled")  
        self.output_widget.config(bg="#121212", fg='#FFFFFF')

        self.command_input = tk.Entry(self.root, font=("Courier", 12))
        self.command_input.pack(fill=tk.X, padx=5, pady=5)
        self.command_input.bind("<Return>", self.send_command)

        self.process = None
        self.start_cli()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def start_cli(self):

        try:
            self.process = subprocess.Popen(
                ["python3", CLI_PROGRAM],  
                stdin=subprocess.PIPE,   
                stdout=subprocess.PIPE,  
                stderr=subprocess.PIPE,  
                text=True,                
                bufsize=1,                
            )
            
            threading.Thread(target=self.read_output, daemon=True).start()
        except FileNotFoundError:
            self.output_widget.configure(state="normal")
            self.output_widget.insert(tk.END, f"Error: {CLI_PROGRAM} not found.\n")
            self.output_widget.configure(state="disabled")

    def read_output(self):

        for line in self.process.stdout:
            self.output_widget.configure(state="normal")
            self.output_widget.insert(tk.END, line)
            self.output_widget.see(tk.END)
            self.output_widget.configure(state="disabled")
        self.process.stdout.close()

    def send_command(self, event=None):

        command = self.command_input.get().strip()
        if not command:
            return 

        self.output_widget.configure(state="normal")
        if command.lower() == "clear":
            self.output_widget.delete(1.0, tk.END)  
            self.output_widget.insert(tk.END, "Terminal cleared.\n")
        else:
            self.output_widget.insert(tk.END, f"Command> {command}\n")
        self.output_widget.configure(state="disabled")
        self.output_widget.see(tk.END)

        if self.process and self.process.stdin:
            self.process.stdin.write(command + "\n")
            self.process.stdin.flush()

        self.command_input.delete(0, tk.END)

    def on_close(self):

        if self.process:
            self.process.terminate()
            self.process.wait()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = GUIApp(root)
    root.mainloop()