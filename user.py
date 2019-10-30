class User(object):

	def __init__(self):
		self.userid = ''
		self.username = ''
		self.password = ''
		self.group_list = None
		self.conn = None
		self.log_file = []

	def set_user_details(self):
		print('\t\tUser Registration\n\n')
		self.username = input('Enter your name : ')
		self.userid = input('Enter a user id : ')
		self.password = input('Enter a password : ')

	def get_user_details(self):
		print('\t\tUser Registration\n\n')
		self.userid = input('Enter a user id : ')
		self.password = input('Enter a password : ')

if __name__ == '__main__':
	pass