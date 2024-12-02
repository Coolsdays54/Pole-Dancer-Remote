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
import smbus

LPS22HB_I2C_ADDRESS  = 0x5c

LPS_ID               = 0xB1

LPS_INT_CFG          = 0x0B
LPS_THS_P_L          = 0x0C
LPS_THS_P_H          = 0x0D
LPS_WHO_AM_I         = 0x0F
LPS_CTRL_REG1        = 0x10
LPS_CTRL_REG2        = 0x11
LPS_CTRL_REG3        = 0x12
LPS_FIFO_CTRL        = 0x14
LPS_REF_P_XL         = 0x15
LPS_REF_P_L          = 0x16
LPS_REF_P_H          = 0x17
LPS_RPDS_L           = 0x18
LPS_RPDS_H           = 0x19
LPS_RES_CONF         = 0x1A
LPS_INT_SOURCE       = 0x25
LPS_FIFO_STATUS      = 0x26
LPS_STATUS           = 0x27
LPS_PRESS_OUT_XL     = 0x28
LPS_PRESS_OUT_L      = 0x29
LPS_PRESS_OUT_H      = 0x2A
LPS_TEMP_OUT_L       = 0x2B
LPS_TEMP_OUT_H       = 0x2C
LPS_RES              = 0x33


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

def send_data(roll, pitch, yaw, temp, press):
    host = '192.168.10.62'
    port = 65432
    Num = 0
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((host, port))
            current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
#            print(pitch,roll,yaw,current_time)
            message = f"ID: 004018019000002 Pitch: {pitch}, Roll: {roll}, Yaw: {yaw}, Time: {current_time}, Lat: 39.6886505, Longi: -77.7410529, Temp: {temp}, Pressure: {press}"
            Fin = Num + 1
            print(Fin)
            client_socket.sendall(message.encode())
            print(f"Sent: {message}")

    except:
        print('connection refused')

#Temp and Pressure Shit
class LPS22HB(object):
	def __init__(self,address=LPS22HB_I2C_ADDRESS):
		self._address = address
		self._bus = smbus.SMBus(1)
		self.LPS22HB_RESET()
		self._write_byte(LPS_CTRL_REG1,0x02)

	def LPS22HB_RESET(self):
		Buf=self._read_ul6(LPS_CTRL_REG2)
		Buf|=0x04
		self._write_byte(LPS_CTRL_REG2, Buf)
		while Buf:
			Buf=self._read_ul6(LPS_CTRL_REG2)
			Buf&=0x04

	def LPS22HB_START_ONESHOT(self):
		Buf = self._read_ul6(LPS_CTRL_REG2)
		Buf|=0x01
		self._write_byte(LPS_CTRL_REG2,Buf)

	def _read_byte(self,cmd):
		return self._bus.read_byte_data(self._address,cmd)

	def _read_ul6(self,cmd):
		LSB = self._bus.read_byte_data(self._address,cmd)
		MSB = self._bus.read_byte_data(self._address,cmd+1)
		return (MSB    << 8) + LSB

	def _write_byte(self,cmd,val):
		self._bus.write_byte_data(self._address,cmd,val)


if __name__ == '__main__':
	PRESS = 0.0
	TEMP = 0.0
	u8Buf=[0,0,0]
	L=LPS22HB()
	Ans = 0
	Do_again = 175
	filename = 'output.txt'
	search_string = 'Roll'


	while Do_again >=  1:
		try:
			with open('output.txt','w') as out_file:
				out_file.flush()
		#		print("Reading sensor output, copying to file")
				subprocess.run('sudo ./main',shell=True,text=True,stdout=out_file,timeout=2)
				out_file.flush()
		#		print("past command")

		except subprocess.TimeoutExpired:
			#print('Command timed out, checking file' + '')
			Ans = check_file('output.txt')
			if(Ans != 1):
				try:
					with open('output.txt','w') as out_file:
		#				print('Reading sensor output, copying to file X2')
						out_file.flush()
						subprocess.run('sudo ./main',shell=True,text=True,stdout=out_file,timeout=2)
				except subprocess.TimeoutExpired:
					print('No content in the file' + '\n')
					time.sleep(15)
					clear_file('output.txt')
					Do_again = Do_again - 1
					pass
			else:
		#		print('file has content, carrying on')
				a1 = search_in_file(filename, search_string)
				result = parse_line_to_floats(a1)
		#		print("Extracted floats:", result)
				try:
					time.sleep(0.1)
					L.LPS22HB_START_ONESHOT()
					if(L._read_byte(LPS_STATUS)&0x01)==0x01:
						u8Buf[0]=L._read_byte(LPS_PRESS_OUT_XL)
						u8Buf[1]=L._read_byte(LPS_PRESS_OUT_L)
						u8Buf[2]=L._read_byte(LPS_PRESS_OUT_H)
						PRESS=((u8Buf[2]<<16)+(u8Buf[1]<<8)+u8Buf[0])/4096.0
						P_F = round(PRESS,2)
					if(L._read_byte(LPS_STATUS)&0x02)==0x02:
						u8Buf[0]=L._read_byte(LPS_TEMP_OUT_L)
						u8Buf[1]=L._read_byte(LPS_TEMP_OUT_H)
						TEMP=((u8Buf[1]<<8)+u8Buf[0])/100.0
						TEMP_F = (TEMP*9/5)+32
						T_F = round(TEMP_F,2)
					print(T_F,P_F)
				except(KeyboardInterrupt):
					print("\n")
					break
				send_data(result[0],result[1],result[2],T_F,P_F)
		#		print("taking a 10 second break")
				time.sleep(18)
				clear_file('output.txt')
				Do_again = Do_again -1

	clear_file('output.txt')
