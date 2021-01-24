import json
import os 

os.system("curl  http://localhost:4040/api/tunnels > tunnels.json")

objectToSend = {}
listOfTunnels = []

with open('tunnels.json') as data_file:    
    datajson = json.load(data_file)


msg = "ngrok URL\'s: \n"
for tunnel in datajson['tunnels']:
  tunnelJson = {}
  tunnelJson['name'] = tunnel['name']
  tunnelJson['publicUrl'] = tunnel['public_url']
  tunnelJson['addr'] = tunnel['config']['addr']
  listOfTunnels.append(tunnelJson)

objectToSend['senderId'] = "PC"
objectToSend['tunnelsList'] = listOfTunnels
jsonToSend = json.dumps(objectToSend)

print(jsonToSend)
