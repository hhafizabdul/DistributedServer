import socket                   # Import socket module
import os
import sys
class Client:
	def __init__(self):

		self.conn = socket.socket()
		self.port = 0
		self.host = socket.gethostname()
		# self.host = '192.168.20.114'
		# self.dirBase = 'c:\\users\\hhafi\\downloads\\ClientFiles'
		# self.dirBase = 'c:\\users\\hhafi\\downloads'
		self.dirBase = sys.argv[1]
		self.directory = ''
		
		if self.dirBase[-11:] == 'ClientFiles':
			self.directory = self.dirBase

		elif not 'ClientFiles' in os.listdir(f'{self.dirBase}\\'):
			print('created clientFiles folder')
			os.system(f'mkdir {self.dirBase}\\ClientFiles')
			self.directory = f'{self.dirBase}\\ClientFiles'
		
		
		else:
			self.directory = f'{self.dirBase}\\ClientFiles'
	def get_servers(self):
		try:
			filename = 'servers.txt'
			file = open(filename, 'r')
			lines = file.readlines()
			for i,j in enumerate(lines):
				lines[i] = lines[i].replace('\n','',1)
			return lines
		except FileNotFoundError:
			print(self.directory)
			print('servers.txt not found')
			return ['3000', '3001', '3002']
			# return ['100']

	def get_directory_files(self):
		files = os.listdir(self.dirBase + '\\')
		direct = f'{self.dirBase}\\'
		for i,f in enumerate(files):
			files[i] = f'{f}\t|  {os.stat(direct+f).st_size} B'

		# print(files) 
		return files

	def connectToServer(self, port):
		self.port = port                     # Reserve a port for your service.
		self.conn.connect((self.host, self.port))

	def upload(self, port ,filename):
		# filename='file.txt'
		try:
			self.connectToServer(port)
			self.conn.send(b'/post')
			print('Sent to /post')

			if self.conn.recv(10) == b'Done_1':
				self.conn.send(f'{filename}\n'.encode())
				
				f = open(f'{self.dirBase}\\{filename}','rb')
				l = f.read(1024)
				
				while (l):
				    self.conn.send(l)
				    # print('Sent ',repr(l))
				    l = f.read(1024)
				
				print('file sent to server Successfully')
				f.close()
				
				self.conn.close()
				print('connection closed')

				self.__init__()
				print('Ready for new Connection')
			else:
				self.conn.close()
				self.__init__()
		except Exception:
			print('Server not Found')
			self.conn.close()
			self.__init__()
	
	def download(self, port, filename):
		try:
			self.connectToServer(port)
			
			self.conn.send(b'/getFile')
			if self.conn.recv(10) == b'Done_2':

				self.conn.send(filename.encode())
				filename = filename.replace('\n','',1)
				filename = filename[:-4]
				with open(f'{self.directory}\\{filename}', 'wb') as f:
					while True:
						print('receiving data...')
						data = self.conn.recv(1024)
						# print('data=%s', (data))
						if not data:
							break
				        # write data to a file
						f.write(data)

				f.close()
				print('Successfully get the file')
				self.conn.close()
				print('connection closed')
				self.__init__()
			
			else:
				self.conn.close()
				self.__init__()
		except Exception:
			print('Server not found')
			self.conn.close()
			self.__init__()		

	def getServerFilesList(self, port):
		try:
			self.connectToServer(port)
			fileList = ''
			
			self.conn.send('/getList'.encode())

			if self.conn.recv(10) == b'Done_3' :
				while True:
					data = self.conn.recv(1024)
					if not data:
						break
					fileList = f'{fileList}{data.decode()}'	
				self.conn.close()
				fileList = fileList.split('\n')
				# for i,f in enumerate(fileList):
				# 	temp = f.split('\t')
				# 	temp[0] = temp[0][:-4]
				# 	f = '\t'.join(temp)
				# 	fileList[i] = f[:-4]
				self.__init__()
				return fileList
			
			else:
				self.conn.close()
				self.__init__()
		except Exception:
			print('Server not found')
			self.conn.close()
			self.__init__()

if len(sys.argv) != 2:
	print("Usage: ****python __filename__ __Directory for files__****")
	sys.exit()
