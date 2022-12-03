import numpy as np
import requests as req
import Crypto
from Crypto.Cipher import AES

# PUF model.
weights = [ 
    -2.28232605,
    -0.69593893,
    -10.88359848,
    -3.2058949,
    3.57914767,
    -7.59192424,
    10.71604453,
    2.68427318,
    8.25605864,
    13.3800692,
    3.78877187,
    -8.38995304,
    3.70122252,
    1.76511599,
    -6.03537901,
    7.82432077,
    3.90332646,
    -3.21680889,
    3.87344499,
    7.33854256,
    -8.37431056,
    3.86145878,
    -4.99432344,
    1.01054683,
    7.94359346,
    3.04283482, 
    3.52147518, 
    -1.35035827,  
    0.43837325, 
    -2.13248853,
    -3.20407026, 
    7.32384405,  
    2.92915361,  
    6.34679261, 
    -0.62869852,
    -1.71977127,
    -7.50254007, 
    13.76077365,  
    6.07546285,  
    1.01965099,
    3.05755015,  
    5.74642919, 
    -2.28533149,  
    0.07616194, 
    -6.19973015,
    4.78718751,  
    2.59791651,  
    3.72744012, 
    -3.21727335, 
    -1.44945205,
    -2.42025041,
    -4.13188431,  
    6.20460101, 
    -1.82724872,  
    3.23383049,
    0.69575238, 
    -3.09170958, 
    -2.5458321, 
    -6.40514127, 
    -2.95301469,
    0.491878,   
    3.64497773, 
    -3.60332231, 
    3.82830521, 
    -2.44336745,
    3.70636405, 
    -1.47238127,  
    3.52507202,  
    8.17799027,  
    0.94064484,
    5.46817797,
    -5.59189422,  
    5.278224,   
    4.24178308, 
    -9.1294133,
    3.49799928,  
    9.30291971, 
    -1.76245167, 
    -8.45083893,  
    5.45400596,
    2.68758704, 
    -0.88938003,  
    4.78519138,  
    6.65323421,  
    1.18788469,
    7.55989853, 
    -4.21300838, 
    -3.1505397, 
    2.51179158,  
    2.52549643,
    -3.86112625, 
    -1.81921275, 
    -5.49344684,
    -3.09738924,
    8.65549731,
    7.15925912,  
    4.87593817,  
    1.59474061, 
    19.53759186, 
    -1.97192872,
    -1.34198933, 
    -6.96656617, 
    -1.3633342,  
    8.27981698, 
    -6.24569943,
    -4.10519056,  
    3.83718698, 
    -1.21784778,  
    1.81200635, 
    -2.77080834,
    7.10950367,  
    2.47688498, 
    -3.97558154, 
    -4.91535826, 
    -8.90803362,
    5.69180407,  
    3.82243611,  
    4.83641921, 
    -4.73901845, 
    0.68534076,
    -0.19278134,  
    9.30042486, 
    -5.81940515,  
    8.97647489,
    13.28145445, 
    -6.08150496, 
    -6.61437666,  
    4.1683101
]

# Encryption and decryption.
def encrypt(key, iv, data):
    aes = AES.new(key, AES.MODE_CBC, iv)
    data = data.encode("utf8")
    length = 16 - (len(data) % 16)
    data += bytes([length])*length
    return aes.encrypt(data)

def decrypt(key, iv, data):
    aes = AES.new(key, AES.MODE_CBC, iv)
    data = aes.decrypt(data)
    data = data[:-data[-1]]
    return data.decode("utf8")

# Generate PUF responses.
def generateResponses(weights,challenges):
  responseDelay = np.multiply(weights,challenges)
  response = np.sum(responseDelay,1)
  response = np.sign(response)
  response = np.add(response,1)
  response = np.divide(response,2)
  return response

# For ensuring challenges are received.
challengesReceived = False
challenges = False

while challengesReceived == False:

    # Prompt user for URL and message.
    print('Enter API URL. Our API: http://ec2co-ecsel-1r13h1vw1h9v0-533578369.us-west-2.elb.amazonaws.com:3000')
    url = input()
    print('')
    print('Enter message:')
    message = input()
    print('')

    try:
        # Retrieve challenge.
        challenges = req.get(url+'/challenges')
        challenges = challenges.json()
        challengesReceived = True
    except: 
        print('There was a problem retrieving challenges. Please check your URL and try again: make sure there is no trailing slash and is a valid URL.')

# Vars we need to build in order to post a message.
responses = generateResponses(weights, challenges)

response = responses[256:512]

key = responses[0:256]
keyString = ''
for value in key:
    keyString += str(value.astype(int))
keyBytes = [int(keyString[x:x+8], 2) for x in range(0, len(keyString), 8)]
keyBytes = bytes(keyBytes)

iv = Crypto.Random.get_random_bytes(16)

cipher = encrypt(keyBytes, iv, message)

print('Message encrypted!')
print('')
print('Testing decryption...')
decryptedMessage = decrypt(keyBytes, iv, cipher)
print('Message:',decryptedMessage)
print('')
print('Sending data to API...')

postdata = {
    'challenges':challenges,
    'cipher':cipher.hex(),
    'iv':iv.hex(),
    'response':response.tolist()
}

try:
    sent = req.post(url+'/message', json=postdata)
    print('')
    print('Sent!')
    print('Please visit this page to view your message (may take a few seconds):')
    print('')
    print(url+'/message')
    print('')
except:
    print('Error sending to API.')