from p2p_python.client import PeerClient
 
def hello(data):
    print('receive msg', data)
    return 'nice to meet you!'
 
pc = PeerClient()
pc.start()  # work as port 2001
pc.event.addevent(cmd='message', f=hello)
 
# connect user2
 
receive = pc.send_direct_cmd(cmd='message', data='I\'m User1.')
print(receive)