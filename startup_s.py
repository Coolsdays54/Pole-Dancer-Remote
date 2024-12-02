#!/usr/bin/env python3
import subprocess

def run_commands():
    commands = [
        "echo 'Running startup command 1'",
        "echo 'Running startup command 2'"
    ]
    
    for command in commands:
        try:
            subprocess.run(command, shell=True, check=True)
            print(f"Successfully ran: {command}")
        except subprocess.CalledProcessError as e:
            print(f"Error running {command}: {e}")

if __name__ == "__main__":
    run_commands()
