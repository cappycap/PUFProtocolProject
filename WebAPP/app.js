// Imports.
const express = require('express');
const app = express();
const spawn = require('child_process').spawn;
const AWS = require('aws-sdk');
const bodyParser = require('body-parser')
const jsonParser = bodyParser.json({
  limit:'50mb'
})

// Variables.
const port = 3000;

// Routes.
// -- Provide a client with challenge array.
app.get('/challenges', async (req, res) => {

  var challenges = [];

  // Generate 512 challenges.
  for (var i = 0; i < 512; i++) {

    // Generate 128 bits in each challenge.
    var line = []

    for (var j = 0; j < 128; j++) {
      var value = Math.random() < 0.5 ? -1 : 1
      line.push(value)
    }

    challenges.push(line)

  }

  res.send(challenges);
  return

});

// -- Send message request to Lambda via SQS.
app.post('/message', jsonParser, async (req, res) => {

  console.log('Message incoming. Forwarding to SQS...')

  try {

    // Set the region and creds we will be using.
    AWS.config = new AWS.Config();
    AWS.config.accessKeyId = process.env.ID;
    AWS.config.secretAccessKey = process.env.KEY;
    AWS.config.region = "us-west-2";

    // Create SQS service client.
    const sqs = new AWS.SQS();

    // Setup the sendMessage parameter object.
    const params = {
      MessageBody: JSON.stringify({
        challenges:req.body.challenges,
        cipher:req.body.cipher,
        iv:req.body.iv,
        response:req.body.response
      }),
      QueueUrl: `https://sqs.us-west-2.amazonaws.com/241992735641/PUF_msg_queue`
    };

    // Send.
    sqs.sendMessage(params, (err, data) => {
      if (err) {
        console.log("Error", err);
        res.send({success:false});
        return
      } else {
        console.log("Successfully added message", data.MessageId);
        res.send({success:true});
        return
      }
    });

  } catch (e) {

    console.log(e.toString())
    res.send({success:false});
    return

  }

});

// -- View all messages from the dynamodb.
app.get('/message', async (req, res) => {

  // Set the region and creds we will be using.
  AWS.config = new AWS.Config();
  AWS.config.accessKeyId = process.env.ID; 
  AWS.config.secretAccessKey = process.env.KEY;
  AWS.config.region = "us-west-2";

  var ddb = new AWS.DynamoDB({apiVersion: '2012-08-10'});

  var params = {
    TableName: 'PUF_message_table'
  };
  
  ddb.scan(params, function(err, data) {
    if (err) {
      console.log("Error", err);
      res.send({success:false});
      return
    } else {
      console.log("Success", data.Items);
      res.send({success:true,items:data.Items})
      return
    }
  });

});

// Deployment.
app.listen(port, () => {
  console.log(`Running on ${port}`)
});
