import subprocess
import time
import sys
import itertools
from itertools import islice
import re
from datetime import datetime
import socket
import json
import socket

def extract_lines(in_file,num):
	with open(in_file) as in_f:
		gen = (line for line in in_f if not line.startswith(''))
		return '\n'.join(islice(gen,num))

def search_in_file(filename, search_string):
	with open(filename, 'r') as file:
		for line in file:
			if search_string in line:
#				print(line.strip() + '\n', flush=True)
				return line.strip()

def parse_line_to_floats(line):
	return [float(num) for num in re.findall(r'-?\d+\.\d+', line)]

def clear_file(a):
	with open(a,'w') as file:
		print('File Cleared' + '\n')
		pass

def check_file(filename):
	try:
		with open(filename, 'r') as file:
			content = file.read().strip()
			return 1 if content else 0
	except FileNotFoundError:
		print("File not found." + '\n')
		return 0

def send_data(roll, pitch, yaw):
    host = '192.168.10.121'
    port = 65432
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((host, port))
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#            print(pitch,roll,yaw,current_time)
            message = f"Pitch: {pitch}, Roll: {roll}, Yaw: {yaw}, Time: {current_time}"
            
            client_socket.sendall(message.encode())
            print(f"Sent: {message}")

    except:
        print('connection refused')

Ans = 0
Do_again = 175
filename = 'output.txt'
search_string = 'Roll'

while Do_again >=  1:
	try:
		with open('output.txt','w') as out_file:
			out_file.flush()
		#	print("Reading sensor output, copying to file")
			subprocess.run('sudo ./main',shell=True,text=True,stdout=out_file,timeout=2)
			out_file.flush()
		#	print("past command")
		
	except subprocess.TimeoutExpired:
		#print('Command timed out, checking file' + '')
		Ans = check_file('output.txt')
		if(Ans != 1):			
			try:
				with open('output.txt','w') as out_file:
		#			print('Reading sensor output, copying to file X2')
					out_file.flush()
					subprocess.run('sudo ./main',shell=True,text=True,stdout=out_file,timeout=2)
			except subprocess.TimeoutExpired:
				print('No content in the file' + '\n')
				time.sleep(5)
				clear_file('output.txt')
				Do_again = Do_again - 1
				pass
		else:
		#	print('file has content, carrying on')
			a1 = search_in_file(filename, search_string)
			result = parse_line_to_floats(a1)
		#	print("Extracted floats:", result)
			send_data(result[0],result[1],result[2])
		#	print("taking a 10 second break")
			time.sleep(28)
			clear_file('output.txt')
			Do_again = Do_again -1

clear_file('output.txt')
