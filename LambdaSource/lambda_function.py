import boto3
import json
import Crypto
from Crypto.Cipher import AES
import numpy as np

# Generate PUF responses.
def generateResponses(weights,challenges):
  responseDelay = np.multiply(weights,challenges)
  response = np.sum(responseDelay,1)
  response = np.sign(response)
  response = np.add(response,1)
  response = np.divide(response,2)
  return response
  
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

# Main function.
def lambda_handler(event, context):

    # Get PUF weights from dynamodb.
    dynamodb = boto3.resource("dynamodb")
    weightTable = dynamodb.Table('PUF_model_table')
    weightTableResponse = weightTable.scan()
    weightTableResponseData = weightTableResponse['Items']

    # Receive message from SQS queue.
    for record in event['Records']:
        message = record['body']
        print('message:')
        print(message)

        message = json.loads(message)
        
        # Everything we need from the message body.
        challenges = message['challenges']
        cipher = bytes.fromhex(message['cipher'])
        iv = bytes.fromhex(message['iv'])
        response = message['response']
        response = np.array(response, dtype=np.float32)
        print('response:',response)
        print('type(response):',type(response))

        # Loop through weights and attempt to find a match.
        for weightSet in weightTableResponseData:
            weights = weightSet['weights']
            weights = np.array(weights.split(','), dtype=np.float32)

            # See if responses match.
            responses = generateResponses(weights, challenges)

            potentialKey = responses[0:256]
            potentialResponse = responses[256:512]
            print('potentialResponse:',potentialResponse)
            print('type(potentialResponse):',type(potentialResponse))

            match = (potentialResponse == response).all()

            if match:
                # Attempt cipher decryption with potentialKey.
                keyString = ''
                for value in potentialKey:
                    keyString += str(value.astype(int))
                keyBytes = [int(keyString[x:x+8], 2) for x in range(0, len(keyString), 8)]
                keyBytes = bytes(keyBytes)

                #try:
                potentialMessage = decrypt(keyBytes, iv, cipher)
                print('potentialMessage:')
                print(potentialMessage)

                # Add message to dynamodb.
                messageTable = dynamodb.Table('PUF_message_table')

                response = messageTable.put_item(
                    Item={
                        'message':potentialMessage
                    }
                )

                print('Message added to DynamoDB.')

    return {
        'statusCode': 200,
        'body': ''
    }
