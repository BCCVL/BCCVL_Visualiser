import xmlrpclib
import os
import sys

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s\n'
          '(example: "%s")' % (cmd, cmd))
    sys.exit(1)

def main(argv=sys.argv):
    # Create an object to represent our server.
    server_url = 'http://localhost:6543/api.xml';
    server = xmlrpclib.Server(server_url);

    # Call the server and get our result.
    result = server.xmlsss(5, 3)
    print "content:", result['content']
