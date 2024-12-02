import subprocess
import time

def clear_cache():
    try:
        # Clear PageCache
        subprocess.run(['sudo', 'sh', '-c', 'sync; echo 1 > /proc/sys/vm/drop_caches'], check=True)
        print("PageCache cleared")

        # Clear Dentries and Inodes
        subprocess.run(['sudo', 'sh', '-c', 'sync; echo 2 > /proc/sys/vm/drop_caches'], check=True)
        print("Dentries and Inodes cleared")

        # Clear PageCache, Dentries, and Inodes
        subprocess.run(['sudo', 'sh', '-c', 'sync; echo 3 > /proc/sys/vm/drop_caches'], check=True)
        print("PageCache, Dentries, and Inodes cleared")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

def run_command_with_timeout(command, timeout):
    try:
        clear_cache()
        # Start the command
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for the command to complete or timeout
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            print(f"Command output: {stdout.decode()}")
            if stderr:
                print(f"Command error: {stderr.decode()}")
        except subprocess.TimeoutExpired:
            # Timeout expired, terminate the process
            process.terminate()
            print("Command timed out and was terminated.")
            process.wait()
            #wait for process to terminate
            subprocess.run('sudo reboot',shell=True,text=True) 
            return False  # Indicate that the command did not complete in time

        return True  # Indicate that the command completed successfully

    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def main():  # Replace with your command
    command = "cd /home/pole/Sense_HAT_C_Pi/RaspberryPi/IMU/lgpio && sudo python A$.py"
    timeout = 3000  # Timeout in seconds (60 minutes)

    while True:
        print(f"Running command: {command}")
        success = run_command_with_timeout(command, timeout)
        
        if not success:
            print("Rerunning the command due to timeout...")
        else:
            print("Command completed successfully.")
            break  # Exit the loop if the command completed successfully

if __name__ == "__main__":
    main()
