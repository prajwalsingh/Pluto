#Refrence : https://www.youtube.com/playlist?list=PLhTjy8cBISErYuLZUvVOYsR1giva2payF
#Python Network Programming TCP/IP Socket Programming
#File : https://stackoverflow.com/questions/27241804/sending-a-file-over-tcp-sockets-in-python
import socket
import threading
from queue import Queue
import sys
import platform
import os
import numpy as np 
import time
import pickle
from datetime import datetime

class Server(object):

	def __init__(self):
		self.host = ''
		self.command_port = 9999
		self.data_port = 9998
		self.command_sock = None
		self.data_sock = None
		self.NUMBER_OF_THREAD = 5
		self.NUMBER_OF_JOB = 5
		self.JOB_LIST = [1, 2, 3, 4, 5]
		self.thread_queue = Queue()
		self.all_command_details = []
		self.all_data_details = []
		self.clients_list = None
		self.groups_list = None
		if platform.system() == 'Windows':
			self.clear_cmd = 'cls'
		else:
			self.clear_cmd = 'clear'


	def create_scoket(self):
		try:
			self.command_sock = socket.socket()
			self.data_sock = socket.socket()
			print('Socket is created successfully.')
		except Exception as e:
			print('Problem occur while socket creation :\n{0}\nRetrying...\n'.format(e))
			self.create_scoket()

	def bind_listen_socket(self):
		try:
			self.command_sock.bind((self.host, self.command_port))
			self.data_sock.bind((self.host, self.data_port))
			print('Socket binding successfull.')
			self.command_sock.listen(5)
			self.data_sock.listen(5)
			print('Socket is in listening state.')
		except Exception as e:
			print('Problem occur while socket binding :\n{0}\nRetrying....\n'.format(e))
			self.bind_socket()

	def accept_command_conn(self):
		while True:
			try:
				conn, address = self.command_sock.accept()
				self.command_sock.setblocking(1)
				self.all_command_details.append((conn, address))
				print('Command connection establish with client : {0}:{1}\n'.format(address[0], address[1]))
			except Exception as e:
				print('Problem occur while accepting command connection :\n{0}\nRetrying...\n'.format(e))

	def accept_data_conn(self):
		while True:
			try:
				conn, address = self.data_sock.accept()
				print('Data connection establish with client : {0}:{1}\n'.format(address[0], address[1]))
				self.all_data_details.append((conn, address))
				self.data_sock.setblocking(1)
				t = threading.Thread(target=self.fetch_client_data, args=(conn,address))
				t.daemon = True
				t.start()
				#t.join()
			except Exception as e:
				print('Problem occur while accepting data connection :\n{0}\nRetrying...\n'.format(e))

	def server_shell(self):
		while True:
			terminal = input('s_shell>')
			try:
				if terminal == 'list':
					self.get_all_connections()
				elif terminal == 'clist':
					self.show_clients_detail()
				elif terminal == 'clear' or terminal == 'cls':
					os.system(self.clear_cmd)
				elif terminal == 'exit':
					self.close_all_connections()
				elif terminal == 'gpadd':
					self.add_group()
				elif terminal == 'gpview':
					self.show_groups()
			except Exception as e:
				print('Problem occure while processing command :\n{0}\n'.format(e))


	def get_all_connections(self):
		print('\nConnected Clients:\n\n{0}\t{1}\t{2}'.format('Client ID', 'IP address', 'Port'))
		for client_id,client in enumerate(self.all_command_details):
			try:
				client[0].send(str.encode('test_data'))
				client_response = str(client[0].recv(1024), 'utf-8')
				print('{0}\t\t{1}\t{2}'.format(client_id, client[1][0], client[1][1]))
			except Exception as e:
				print('\nClient is disconnected : \n{0}\n'.format(e))
				del self.all_command_details[client_id]
		print('')


	def close_all_connections(self):
		for client in self.all_command_details:
			client[0].close()
		for client in self.all_data_details:
			client[0].close()
		self.command_sock.close()
		self.data_sock.close()
		os.system('kill '+str(os.getpid()))


	def fetch_client_details(self):
		while True:
			try:
				with open('root/all_user/clients_list.pkl', 'rb') as pickel_data:
					self.clients_list = pickle.load(pickel_data)
			except Exception as e:
				print('User list not exsists : \n{0}\n'.format(e))
				l = []
				l.append(['rootA','rootA','rootA',[], []])
				l.append(['rootB','rootB','rootB',[], []])
				user_details = np.array([l])
				with open('root/all_user/clients_list.pkl', 'wb') as pickel_data:
					pickle.dump(user_details, pickel_data)

			try:
				with open('root/groups/group_list.pkl', 'rb') as group:
					self.groups_list = pickle.load(group)
			except Exception as e:
				print('Groups not exsists : \n{0}\n'.format(e))
				l = []
				l.append(['group_name','group_id','group_desc',['user_list'],['message']])
				l.append(['dummy','dummy','dummy',['dummy'],['message']])
				with open('root/groups/group_list.pkl', 'wb') as group:
					pickle.dump(np.array([l]), group)

			time.sleep(0.5)

	def show_clients_detail(self):
		try:
			print(self.clients_list[0])
			print('')
			# for client in self.clients_list[0]:
			# 	print(client)
		except Exception as e:
			print('Unable to fetch clients detail : \n{0}\n'.format(e))

	def fetch_client_data(self,conn,address):
		while True:
			try:
				if conn is not None:
					byte_stream = conn.recv(202480)
					data = pickle.loads(byte_stream)
					# print(data)
					if data[0] == '1':
						if np.any(self.clients_list[:,:,0]==data[1].userid):
							print('User alread exsists.')
							byte_stream = pickle.dumps('1')
							conn.send(byte_stream)
							print('User notified.')
						else:
							self.clients_list = self.clients_list.tolist()[0]
							self.clients_list.append([data[1].userid,data[1].password,data[1].username,[], []])
							self.clients_list = np.array([self.clients_list])
							with open('root/all_user/clients_list.pkl', 'wb') as pickel_data:
								pickle.dump(self.clients_list, pickel_data)
							print('Data is Updated successfully')
							byte_stream = pickle.dumps('2')
							conn.send(byte_stream)
							print('User notified.')

					elif data[0] == '2':
						if np.any(self.clients_list[:,:,0]==data[1].userid):
							index = np.where((self.clients_list[:,:,0]==data[1].userid)[0])[0][0]
							if self.clients_list[0,index,1] == data[1].password:
								print('User Login successfull.')
								byte_stream = pickle.dumps(('1',self.clients_list[0,index]))
								conn.send(byte_stream)
								print('User notified.')
							else:
								print('User login unsuccessfull.')
								byte_stream = pickle.dumps('2')
								conn.send(byte_stream)
								print('User notified.')
						else:
							print('User login unsuccessfull.')
							byte_stream = pickle.dumps('2')
							conn.send(byte_stream)
							print('User notified.')

					elif data[0] == '3':
						conn.close()

					elif data[0] == '4':
						byte_stream = pickle.dumps(self.groups_list)
						conn.send(byte_stream)
						print('User notified.')

					elif data[0] == '5':
						# print('Group id : {0}'.format(data[1]))
						# print('User id : {0}'.format(data[2]))

						if np.any(self.clients_list[:,:,0]==data[2]):
							index = np.where((self.clients_list[:,:,0]==data[2])[0])[0][0]
							if data[1] not in self.clients_list[:,index,3][0]:
								self.clients_list = self.clients_list.tolist()[0]
								userdata = self.clients_list[index]
								del self.clients_list[index]
								userdata[3].append(data[1])
								self.clients_list.append(userdata)
								self.clients_list = np.array([self.clients_list])
								with open('root/all_user/clients_list.pkl', 'wb') as pickel_data:
									pickle.dump(self.clients_list, pickel_data)

								gindex = np.where((self.groups_list[:,:,1]==data[1])[0])[0][0] 
								self.groups_list = self.groups_list.tolist()[0]
								groupdata = self.groups_list[gindex]
								del self.groups_list[gindex]
								groupdata[3].append(data[2])
								self.groups_list.append(groupdata)
								self.groups_list = np.array([self.groups_list])
								with open('root/groups/group_list.pkl', 'wb') as group:
									pickle.dump(self.groups_list, group)
								
								print('Data is Updated successfully')
								byte_stream = pickle.dumps('1')
								conn.send(byte_stream)
								print('User notified')
							else:
								print('Group leaving unsuccessfull.')
								byte_stream = pickle.dumps('2')
								conn.send(byte_stream)
								print('User notified')
						# byte_stream = pickle.dumps(self.groups_list)
						# conn.send(byte_stream)
						# print('User notified.')

					elif data[0] == '6':
						# print('Group id : {0}'.format(data[1]))
						# print('User id : {0}'.format(data[2]))

						if np.any(self.clients_list[:,:,0]==data[2]):
							index = np.where((self.clients_list[:,:,0]==data[2])[0])[0][0]

							if data[1] in self.clients_list[:,index,3][0]:
								self.clients_list = self.clients_list.tolist()[0]
								userdata = self.clients_list[index]
								del self.clients_list[index]
								del userdata[3][userdata[3].index(data[1])]
								self.clients_list.append(userdata)
								self.clients_list = np.array([self.clients_list])
								with open('root/all_user/clients_list.pkl', 'wb') as pickel_data:
									pickle.dump(self.clients_list, pickel_data)

								gindex = np.where((self.groups_list[:,:,1]==data[1])[0])[0][0] 
								self.groups_list = self.groups_list.tolist()[0]
								groupdata = self.groups_list[gindex]
								del self.groups_list[gindex]
								del groupdata[3][groupdata[3].index(data[2])]
								self.groups_list.append(groupdata)
								self.groups_list = np.array([self.groups_list])
								with open('root/groups/group_list.pkl', 'wb') as group:
									pickle.dump(self.groups_list, group)
								
								print('Data is Updated successfully')
								byte_stream = pickle.dumps('1')
								conn.send(byte_stream)
								print('User notified')
							else:
								print('Group leaving unsuccessfull.')
								byte_stream = pickle.dumps('2')
								conn.send(byte_stream)
								print('User notified')
						# byte_stream = pickle.dumps(self.groups_list)
						# conn.send(byte_stream)
						# print('User notified.')

					elif data[0] == '7':
						# print('User id : {0}'.format(data[1]))
						# print('Message : {0}'.format(data[2]))

						if np.any(self.clients_list[:,:,0]==data[1]):
							index = np.where((self.clients_list[:,:,0]==data[1])[0])[0][0]

							self.clients_list = self.clients_list.tolist()[0]
							userdata = self.clients_list[index]
							del self.clients_list[index]
							userdata[4].append(data[2])
							self.clients_list.append(userdata)
							self.clients_list = np.array([self.clients_list])
							with open('root/all_user/clients_list.pkl', 'wb') as pickel_data:
								pickle.dump(self.clients_list, pickel_data)

					elif data[0] == '8':
						# print('Group id : {0}'.format(data[1]))
						
						if np.any(self.groups_list[:,:,1]==data[1]):
							index = np.where((self.groups_list[:,:,1]==data[1])[0])[0][0]
							byte_stream = pickle.dumps(self.groups_list[0,index,4])
							conn.send(byte_stream)
							# print('Group chat sent, user notified.')
						else:
							print('Group not found.')

					elif data[0] == '9':
						# print('Group id : {0}'.format(data[1]))
						# print('Message : {0}'.format(data[2]))

						if np.any(self.groups_list[:,:,1]==data[1]):
							index = np.where((self.groups_list[:,:,1]==data[1])[0])[0][0]

							self.groups_list = self.groups_list.tolist()[0]
							userdata = self.groups_list[index]
							del self.groups_list[index]
							userdata[4].append(data[2])
							self.groups_list.append(userdata)
							self.groups_list = np.array([self.groups_list])
							with open('root/groups/group_list.pkl', 'wb') as group:
									pickle.dump(self.groups_list, group)
						else:
							print('Group not found.')

					elif data[0] == '10':
						try:
							d_sock = socket.socket()
							d_sock.bind(('',9997))
							d_sock.listen()
							d_conn,d_add = d_sock.accept()

							sdata = pickle.loads(d_conn.recv(102400))
							filesize = 0
							file = open('root/files/'+data[1], "wb")
							while filesize<=sdata:
								chunk = d_conn.recv(1024)
								filesize+=1024
								file.write(chunk)
							file.close()
							d_conn.close()
							d_sock.close()

							if np.any(self.groups_list[:,:,1]==data[2]):
								index = np.where((self.groups_list[:,:,1]==data[2])[0])[0][0]

								self.groups_list = self.groups_list.tolist()[0]
								userdata = self.groups_list[index]
								del self.groups_list[index]
								userdata[4].append('('+data[3]+') # '+'User send file : '+data[1])
								self.groups_list.append(userdata)
								self.groups_list = np.array([self.groups_list])
								with open('root/groups/group_list.pkl', 'wb') as group:
										pickle.dump(self.groups_list, group)
							else:
								print('Group not found.')


							if np.any(self.clients_list[:,:,0]==data[3]):
								index = np.where((self.clients_list[:,:,0]==data[3])[0])[0][0]

								self.clients_list = self.clients_list.tolist()[0]
								userdata = self.clients_list[index]
								del self.clients_list[index]
								userdata[4].append('('+str(datetime.today())+') # '+'User send a file '+data[1]+' to group '+data[2])
								self.clients_list.append(userdata)
								self.clients_list = np.array([self.clients_list])
								with open('root/all_user/clients_list.pkl', 'wb') as pickel_data:
									pickle.dump(self.clients_list, pickel_data)

						except Exception as e:
							print('Problem occur while receiving file. \n{0}\n'.format(e))

					elif data[0] == '11':
						try:
							d_sock = socket.socket()
							d_sock.connect((address[0],9997))
							byte_stream = pickle.dumps(os.path.getsize('root/files/'+data[1]))
							d_sock.send(byte_stream)
							file = open('root/files/'+data[1], "rb")
							chunk = file.read(1024)
							# print('\n Sending file, please wait.')
							while chunk:
								d_sock.send(chunk)
								chunk = file.read(1024)
							file.close()
							d_sock.close()

							if np.any(self.clients_list[:,:,0]==data[2]):
								index = np.where((self.clients_list[:,:,0]==data[2])[0])[0][0]

								self.clients_list = self.clients_list.tolist()[0]
								userdata = self.clients_list[index]
								del self.clients_list[index]
								userdata[4].append('('+str(datetime.today())+') # '+'User downloaded a file '+data[1]+' from group '+data[2])
								self.clients_list.append(userdata)
								self.clients_list = np.array([self.clients_list])
								with open('root/all_user/clients_list.pkl', 'wb') as pickel_data:
									pickle.dump(self.clients_list, pickel_data)

						except Exception as e:
							print('Problem occur while receiving file. \n{0}\n'.format(e))
				else:
					print('connection closed.')
					break					
			except Exception as e:
				print('Problem occure while fetching client data : \n{0}\n'.format(e))
				conn.close()
				break

	def add_group(self):
		try:
			group_name = input('Group name : ')
			group_desc = input('About group : ')
			while True:
				group_id   = input('Group id : ')
				if np.any(self.groups_list[0,:,1]== group_id):
					_ = input('Group id already taken re-enter group id, press enter to continue')
				else:
					self.groups_list = self.groups_list.tolist()[0]
					self.groups_list.append([group_name, group_id, group_desc, [], []])
					self.groups_list = np.array([self.groups_list])
					with open('root/groups/group_list.pkl', 'wb') as group:
						pickle.dump(self.groups_list, group)
					_ = input('Group is created successfully.Press enter to continue.')
					break

		except Exception as e:
			print('Problem occur while reading group list : \n{0}\n'.format(e))


	def show_groups(self):
		try:
			print(self.groups_list[0])
			print('')
		except Exception as e:
			print('Problem occur while reading group list \n{0}\n'.format(e))


	def create_thread(self):
		for _ in range(self.NUMBER_OF_THREAD):
			thread = threading.Thread(target=self.work_thread)
			thread.daemon = True
			thread.start()

	def create_jobs(self):
		for jobs in self.JOB_LIST:
			self.thread_queue.put(jobs)
		self.thread_queue.join()

	def work_thread(self):
		while True:
			job_number = self.thread_queue.get()
			if job_number == 1:
				self.create_scoket()
				self.bind_listen_socket()
			if job_number == 2:
				self.accept_command_conn()
			if job_number == 3:
				self.accept_data_conn()
			if job_number == 4:
				self.server_shell()
			if job_number == 5:
				self.fetch_client_details()
			self.thread_queue.task_done()



if __name__=='__main__':
	try:
		os.makedirs('root/all_user/')
	except Exception as e:
		pass
	try:
		os.makedirs('root/files/')
	except Exception as e:
		pass
	try:
		os.makedirs('root/groups/')
	except Exception as e:
		pass
	serverObj = Server()
	serverObj.create_thread()
	serverObj.create_jobs()