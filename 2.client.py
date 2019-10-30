import socket
import threading
import platform
import os
import sys
from queue import Queue
from user import User
import pickle
from datetime import datetime
import time
import math

class Client(object):

	def __init__(self):
		self.host = ''
		self.command_port = 9999
		self.data_port = 9998
		self.command_sock = None
		self.data_sock = None
		self.clear_cmd = ''
		self.user_details = User()
		self.thread_queue = Queue()
		self.NUMBER_OF_THREAD = 2
		self.NUMBER_OF_JOB = 2
		self.JOB_LIST = [1, 2]

	def set_server_add(self,address):
		self.host = address

	def create_socket(self):
		try:
			self.command_sock = socket.socket()
		except Exception as e:
			print('Problem occur while socket creation : \n{0}\n'.format(e))

	def connect_command_socket(self):
		try:
			self.command_sock.connect((self.host, self.command_port))
			print('You are now connected to server.')
		except Exception as e:
			print('Problem occur while connecting command socket : \n{0}\n'.format(e))

	def connect_data_socket(self):
		try:
			self.data_sock = socket.socket()
			self.data_sock.connect((self.host, self.data_port))
			print('Data connection establish.\n')
		except Exception as e:
			print('Problem occur while connecting data socket : \n{0}\n'.format(e))

	def user_interface(self):
		if platform.system() == 'Windows':
			self.clear_cmd = 'cls'
		else:
			self.clear_cmd = 'clear'
		while True:
			os.system(self.clear_cmd)
			user_choice = input('\t\tWelcome To Pluto\n\n1.Log In\n2.Sign Up\n3.Exit\n\nEnter your choice : ')
			if user_choice == '1':
				self.connect_data_socket()
				self.signin_user()
			elif user_choice == '2':
				self.connect_data_socket()
				self.register_user()
			elif user_choice == '3':
				self.command_sock.close()
				os.system('kill '+str(os.getpid()))
				break
			else:
				_ = input('\nInvalid choice, please select correct option.Press enter to continue.\n')

	def recieve_command(self):

		while True:
			try:
				command = str(self.command_sock.recv(1024), 'utf-8')
				self.command_sock.send(str.encode('.'))
				# print('Command data recieve.\n')
			except Exception as e:
				print('Problem occur while collecting command data : \n{0}\n'.format(e))
	

	def register_user(self):
		while True:
			try:
				os.system(self.clear_cmd)
				userObj = User()
				userObj.set_user_details()
				byte_stream = pickle.dumps(('1',userObj))
				self.data_sock.send(byte_stream)
				print('Data sent to server.')
				byte_stream = self.data_sock.recv(102480)
				data = pickle.loads(byte_stream)
				if data[0] == '1':
					print('Userid already exsists.')
					_=input('Press enter key to continue')
				elif data[0] == '2':
					print('User registration successful.')
					_=input('Press enter key to continue')
					byte_stream = pickle.dumps(('3',userObj))
					self.data_sock.send(byte_stream)
					self.data_sock.close()
					break
			except Exception as e:
				print('Problem occur while sending data : \n{0}\n'.format(e))
				_=input('Press enter key to continue')
				break

	def signin_user(self):
		while True:
			try:
				os.system(self.clear_cmd)
				userObj = User()
				userObj.get_user_details()
				byte_stream = pickle.dumps(('2',userObj))
				self.data_sock.send(byte_stream)
				print('Data sent to server.')
				byte_stream = self.data_sock.recv(202480)
				data = pickle.loads(byte_stream)
				if data[0] == '1':
					print('Welcome User.')
					_=input('Press enter key to continue')
					self.user_details.name = data[1][2]
					self.user_details.password = data[1][1]
					self.user_details.userid = data[1][0]
					self.user_details.group_list = data[1][3]
					self.user_details.log_file = data[1][4]
					self.write_log_file('User signin.')
					self.home_page()
					byte_stream = pickle.dumps(('3',userObj))
					self.data_sock.send(byte_stream)
					self.data_sock.close()
					break
				elif data[0] == '2':
					print('Invalid user name or password.')
					_=input('Press enter key to continue or enter "b" to go back : ')
					if _ == 'b':
						userObj = User()
						byte_stream = pickle.dumps(('3',userObj))
						self.data_sock.send(byte_stream)
						self.data_sock.close()
						break
			except Exception as e:
				print('Problem occure while login data : \n{0}\n'.format(e))
				_=input('Press enter key to continue')
				break

	def home_page(self):
		while True:
			try:
				os.system(self.clear_cmd)
				mopt = input('\t\tPluto Home\n\nName : {0}\t\tUser name : {1}\n\n1.Sign Out\n2.Groups\n3.Messages\n4.Check log\n\nEnter your choice : '.format(self.user_details.name, self.user_details.userid))
				if mopt == '1':
					self.write_log_file('User logout.')
					break
				elif mopt== '2':
					while True:
						os.system(self.clear_cmd)
						gopt = input('\t\tPluto Groups\n\nName : {0}\t\tUser name : {1}\n\n1.Go back\n2.Current groups\n3.Join group\n4.Leave group\n\nEnter your choice : '.format(self.user_details.name, self.user_details.userid))
						if gopt=='1':
							break
						if gopt=='2':
							print('\nCurrent Group List\n{0}'.format(self.user_details.group_list))
							_ = input('\nPress enter key to continue.')
						elif gopt=='3':
							self.show_groups()
							_ = input('\nPress enter key to continue.')
						elif gopt == '4':
							self.leave_group()
				elif mopt == '3':
					self.send_messages()
				elif mopt == '4':
					self.read_log_file()
			except Exception as e:
				print('Problem occur while opening home page\n{0}\n'.format(e))

	def show_groups(self):
		try:
			userObj = User()
			byte_stream = pickle.dumps(('4',userObj))
			self.data_sock.send(byte_stream)
			byte_stream = self.data_sock.recv(102480)
			group_data = pickle.loads(byte_stream)
			while True:
				os.system(self.clear_cmd)
				print('\t\tAll Groups\n\n')
				for i,group in enumerate(group_data[0,:]):
					if i==0 or i==1:
						print('{0} : Private(group_id)'.format(i))
					else:
						print('{0} : {1}({2})'.format(i,group[0],group[1]))
				_ = input('\nEnter group number you want to join or enter "b" to go back : ')
				if _ == 'b':
					break
				else:
					try:
						group_num = int(_)
						if group_num>=0 and group_num < len(group_data[0]):
							if group_num == 0 or group_num == 1:
								_ = input('\nYou are not allow to join this group. press enter to continue')
							else:
								byte_stream = pickle.dumps(('5', group_data[0,group_num,1], self.user_details.userid))
								self.data_sock.send(byte_stream)
								byte_stream = self.data_sock.recv(102480)
								info = pickle.loads(byte_stream)
								if info == '1':
									self.user_details.group_list.append(group_data[0,group_num,1])
									self.write_log_file('User joined a group '+str(group_data[0,group_num,1])+'.')
									print('\nYou have joined a new group.')
								elif info == '2':
									print('\nYou are already present in this group.')
								_ = input('\nPress enter to continue')
					except Exception as e:
						pass
		except Exception as e:
			print('Problem occur while fetching group data \n{0}\n'.format(e))

	def leave_group(self):
		while True:
			os.system(self.clear_cmd)
			print('\t\tAll Groups\n\n')
			for i,group in enumerate(self.user_details.group_list):
				print('{0} : {1}'.format(i,group))
			_ = input('\nEnter group number you want to leave or enter "b" to go back : ')
			if _ == 'b':
				break
			else:
				try:
					group_num = int(_)
					if group_num>=0 and group_num < len(self.user_details.group_list):
						byte_stream = pickle.dumps(('6', self.user_details.group_list[group_num], self.user_details.userid))
						self.data_sock.send(byte_stream)
						byte_stream = self.data_sock.recv(102480)
						info = pickle.loads(byte_stream)
						if info == '1':
							self.write_log_file('User left the group '+str(self.user_details.group_list[group_num])+'.')
							del self.user_details.group_list[group_num]
							print('\nThis group is removed from your list.')
						else:
							print('\nProblem occur')
						_ = input('\nPress enter key to continue')
				except Exception as e:
					pass

	def send_messages(self):
		while True:
			try:
				os.system(self.clear_cmd)
				print('\t\tPluto Message\n\n')
				for i,group in enumerate(self.user_details.group_list):
					print('{0} : {1}'.format(i,group))
				_ = input('\nEnter group number to open message box or enter "b" to go back : ')

				if _ == 'b':
					break
				else:
					messopt = int(_)
					if messopt>=0 and messopt<len(self.user_details.group_list):
						group_name = self.user_details.group_list[messopt]
						self.write_log_file('User enter into chat group '+group_name+'.')
						while True:
							os.system(self.clear_cmd)
							print('\t\tGroup chat : {0}\n\t(To send file write following command)\n\t(in place of message : send -f filename.extn)\n\t(to download file use command : get -f filename.extn)'.format(group_name))
							byte_stream = pickle.dumps(('8', group_name))
							self.data_sock.send(byte_stream)
							byte_stream = self.data_sock.recv(202480)
							data = pickle.loads(byte_stream)
							for item in data:
								print(item)
								print('')
							user_mess = input('Enter your message (or type exit to go back) : ')
							if user_mess == 'exit':
								break
							if len(user_mess)>=1:
								mess_list = user_mess.split(' ')
								if 'send' in mess_list and '-f' in mess_list:
									try:
										while True:
											byte_stream = pickle.dumps(('10', mess_list[2], group_name, self.user_details.userid))
											self.data_sock.send(byte_stream)
											time.sleep(0.001)
											d_sock = socket.socket()
											d_sock.connect((self.host,9997))
											
											d_sock.send(pickle.dumps(os.path.getsize(mess_list[2])))

											file = open(mess_list[2], 'rb')
											chunk = file.read(1024)
											print('\n Sending file, please wait.')
											while chunk:
												print('#',end='')
												d_sock.send(chunk)
												chunk = file.read(1024)
											file.close()
											d_sock.send(b'done')
											d_sock.close()
											self.user_details.log_file.append('('+str(datetime.today())+') # '+'User send a file '+mess_list[2]+' to group '+group_name)
											break
									except Exception as e:
										_ = input('\nInvalid file name, press enter to continue')

								elif 'get' in mess_list and '-f' in mess_list:
									try:
										byte_stream = pickle.dumps(('11', mess_list[2], self.user_details.userid))
										self.data_sock.send(byte_stream)
										d_sock = socket.socket()
										d_sock.bind(('',9997))
										d_sock.listen()
										d_conn,d_add = d_sock.accept()
										sdata = pickle.loads(d_conn.recv(102400))
										filesize = 0
										file = open(mess_list[2], "wb")
										print(sdata)
										while filesize<=sdata:
											chunk = d_conn.recv(1024)
											filesize += 1024
											print('#',end='')
											file.write(chunk)
										file.close()
										d_conn.close()
										d_sock.close()
										_ = input('\nFile transfer complete, press enter key to continue\n')
										self.user_details.log_file.append('('+str(datetime.today())+') # '+'User downloaded a file '+mess_list[2]+' from group '+group_name)
									except (KeyboardInterrupt,SystemExit,Exception):
										_ = input('\nProblem occur, press enter to continue')
								else:	
									user_mess = '('+self.user_details.userid+') # '+user_mess
									byte_stream = pickle.dumps(('9', group_name, user_mess))
									self.data_sock.send(byte_stream)
						# _ = input('Press enter key to continue')
			except:
				print('Problem occur while sending message.')

	def write_log_file(self, log_text):
		try:
			log_text = '('+str(datetime.today())+') # '+log_text
			self.user_details.log_file.append(log_text)
			byte_stream = pickle.dumps(('7', self.user_details.userid, log_text))
			self.data_sock.send(byte_stream)
		except Exception as e:
			print('Problem occur while writing log file. \n{0}\n'.format(e))
			_ = input('Press enter key to continue')

	def read_log_file(self):
		try:
			os.system(self.clear_cmd)
			print('\t\tUser log file\n\n')
			for item in self.user_details.log_file:
				print(item)
		except Exception as e:
			print('Problem occur while reading log file. \n{0}\n'.format(e))
		_ = input('Press enter key to continue')

	def create_thread(self):
		for _ in range(self.NUMBER_OF_THREAD):
			t = threading.Thread(target=self.work_thread)
			t.daemon = True
			t.start()

	def create_jobs(self):
		for jobs in self.JOB_LIST:
			self.thread_queue.put(jobs)
		self.thread_queue.join()

	def work_thread(self):
		while True:
			job_number = self.thread_queue.get()
			if job_number == 1:
				self.user_interface()
			if job_number == 2:
				self.recieve_command()
			self.thread_queue.task_done()

if __name__ == '__main__':
	clientObj = Client()
	clientObj.set_server_add('10.1.139.241')
	clientObj.create_socket()
	clientObj.connect_command_socket()
	clientObj.create_thread()
	clientObj.create_jobs()