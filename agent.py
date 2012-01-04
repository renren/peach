import asynchat, asyncore
import logging
import socket, sys


class EchoClient(asynchat.async_chat):
    """Sends messages to the server and receives responses.
    """
    
    def __init__(self, host_port, message):
        self.message = message
        self.received_data = []
        self.logger = logging.getLogger('EchoClient')
        asynchat.async_chat.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logger.debug('connecting to %s', host_port)
        self.connect(host_port)
    def handle_expt_event(self):
		err = self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
		if err:
			raise WindowsError(err)
		
    def handle_connect(self):
        self.logger.debug('handle_connect()')
        # Send the command
        self.push(self.message)
        # Send the data
        #self.push_with_producer(EchoProducer(self.message))
        # We expect the data to come back as-is, 
        # so set a length-based terminator
        self.set_terminator('\r\n')
    
    def collect_incoming_data(self, data):
        """Read an incoming message from the client and put it into our outgoing queue."""
        self.logger.debug('collect_incoming_data() -> (%d)\n"""%s"""', len(data), data)
        self.received_data.append(data)

    def found_terminator(self):
        self.logger.debug('found_terminator()')
        received_message = ''.join(self.received_data)
        if received_message == self.message:
            self.logger.debug('RECEIVED COPY OF MESSAGE')
        else:
            self.logger.debug('ERROR IN TRANSMISSION')
            self.logger.debug('EXPECTED "%s"', self.message)
            self.logger.debug('RECEIVED "%s"', received_message)
        return

class EchoProducer(asynchat.simple_producer):
    logger = logging.getLogger('EchoProducer')
    def more(self):
        response = asynchat.simple_producer.more(self)
        self.logger.debug('more() -> (%s)\n"""%s"""', len(response), response)
        return response
		

def main():
	logging.basicConfig(level=logging.DEBUG,
					format='%(name)s: %(message)s',
					)
	client = EchoClient(('127.0.0.1', 6000), message='[1]\r\n[3]\r\n')
	print 'map:', asyncore.socket_map
	asyncore.loop(timeout=1)
	print 'map', asyncore.socket_map

if __name__ == '__main__':
	main()
