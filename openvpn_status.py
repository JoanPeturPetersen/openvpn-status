"""Usage: openvpn_status.py [--host=ADDRPORT] MANAGMENT_ADDR ...

 OpenVPN status pull without blocking. This simple script can collect
the status from multiple OpenVPN instances and returns a concatenated
result to the inquirer. It can either run as an TCP server or as single
command line request.

Arguments:
  MANAGMENT_ADDR     Address of a management interface in the style of
                     "ADDRESS:PORT", both most be specified for each
                     interface, e.g. localhost:7575.

Options:
  --host=ADDRPORT    If specified, then the script will run as a TCP
                     server on this address and port. It should also be
                     given in the form of "ADDR:PORT". For example
                     `--host=localhost:9999`. Telnet to this port
                     to get the status of all the OpenVPN management
                     interfaces.

Example:
  openvpn_status --host localhost:9999 192.168.1.1:7575 192.168.1.1:7574
  Here we open a TCP service on 9999 which probes two OpenVPN interfaces
  for their status. Just "telnet localhost 9999" to get the summary.

"""


import SocketServer
import telnetlib
from docopt import docopt
import sys

# Server address and port:
HOST, PORT = "localhost", 9999
# Servers to poll for status
poll_servers = []

def get_online_ships(addr, port):
    """
    """
    res = "\n" + "-"*79 + "\n"
    res += addr + ":" + str(port) + "\n" 
    res += "-"*79 + "\n"
    try:
        tn = telnetlib.Telnet(addr, port)
        tn.write('status\n')
        out = tn.read_until("END", timeout=2.0)
        tn.close()
    except Exception, e:
        out = str(e)
    res += out
    return res

class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.
    """

    def handle(self):
        for addr, port in poll_servers:
            self.request.sendall(get_online_ships(addr, port))
        self.request.close()

def parse_addr(addr_str):
    """Parse an ADDR:PORT type of address. Terminates program with error
    code if fails."""
    try:
        host, port = addr_str.split(":")
        return host, port
    except ValueError:
        sys.stderr.write('Could not understand: "%s"\n'
                % addr_str)
        sys.exit(1)     
                

if __name__ == "__main__":
    args = docopt(__doc__)
    for addr in args['MANAGMENT_ADDR']:
        poll_servers.append(parse_addr(addr)) 
    
    if args['--host']:
        host, port = parse_addr(args['--host'])
        port = int(port)
        server = SocketServer.TCPServer((host, port), MyTCPHandler)
        server.serve_forever()
    else:
        # Just make the request now:
        for addr, port in poll_servers:
            print get_online_ships(addr, port)



