import asynchat, asyncore
import logging
import socket

import json

class RangeHandler(asynchat.async_chat):
	"""Handles agent push messages
	"""
	
	def __init__(self, sock):
		self.received_data = ''
		self.logger = logging.getLogger('range')
		asynchat.async_chat.__init__(self, sock)
		# Start looking for the JSON command
		self.process_data = self._process_command
		self.set_terminator('\r\n')
		return

	def collect_incoming_data(self, data):
		"""Read an incoming message from the client and put it into our outgoing queue."""
		self.logger.debug('recv [%d]: %s', len(data), data)
		self.received_data += data

	def found_terminator(self):
		"""The end of a command or message has been seen."""
		self.logger.debug('found_terminator')
		self.process_data(self.received_data)
		self.received_data = ''
	
	def _process_command(self, data):
		""" save/merge """
		j = json.loads(data)
		self.push(json.dumps(j) + '\n')
		
class RangeServer(asyncore.dispatcher):
	"""Receives connections and establishes handlers for each client.
	"""
	
	def __init__(self, address):
		asyncore.dispatcher.__init__(self)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.bind(address)
		self.address = self.socket.getsockname()
		self.listen(1)
		return

	def handle_accept(self):
		# Called when a client connects to our socket
		client_info = self.accept()
		print 'accept:', client_info
		RangeHandler(sock=client_info[0])
		# We only want to deal with one client at a time,
		# so close as soon as we set up the handler.
		# Normally you would not do this and the server
		# would run forever or until it received instructions
		# to stop.
		#self.handle_close()
	
	def handle_close(self):
		self.close()
		
def main():
	logging.basicConfig(level=logging.DEBUG,
					format='%(name)s: %(message)s',
					)
	address = ('0.0.0.0', 6000) # let the kernel give us a port
	server = RangeServer(address)
	ip, port = server.address # find out what port we were given
	print ip,port
	asyncore.loop()


if __name__ == '__main__':
	main()
