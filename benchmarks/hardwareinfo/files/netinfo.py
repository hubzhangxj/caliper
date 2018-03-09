import sys
import os
import socket
import struct

interface=sys.argv[1]
command="ip addr show primary dev " + interface
#print command
output=os.popen(command).read()

address=""
broadcast=""
address6=""
netmask=""
network=""

for line in output.splitlines():
	if not line:
		continue
	words = line.split()
	#print words
        broadcast = ''
        if words[0] == 'inet':
            if '/' in words[1]:
                address, netmask_length = words[1].split('/')
                if len(words) > 3:
                    broadcast = words[3]
            else:
                # pointopoint interfaces do not have a prefix
                address = words[1]
                netmask_length = "32"
            address_bin = struct.unpack('!L', socket.inet_aton(address))[0]
            netmask_bin = (1 << 32) - (1 << 32 >> int(netmask_length))
            netmask = socket.inet_ntoa(struct.pack('!L', netmask_bin))
            network = socket.inet_ntoa(struct.pack('!L', address_bin & netmask_bin))
            iface = words[-1]
        elif words[0] == 'inet6':
            if 'peer' == words[2]:
                address6 = words[1]
                _, prefix = words[3].split('/')
                scope = words[5]
            else:
                address6, prefix = words[1].split('/')
                scope = words[3]

print "  \"address\":\"" + address + "\","
print "  \"broadcast\":\"" + broadcast + "\","
print "  \"netmask\":\"" + netmask + "\","
print "  \"network\":\"" + network + "\","
print "  \"ip6address\":\"" + address6 + "\""
