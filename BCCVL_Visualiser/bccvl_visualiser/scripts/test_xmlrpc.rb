require "xmlrpc/client"

# Make an object to represent the XML-RPC server.
server = XMLRPC::Client.new( "localhost", "/api.xml", 6543)

# Call the remote server and get our result
result = server.call("xml", "asds", "sadsd")

content = result["content"]

puts "content: #{content}"
