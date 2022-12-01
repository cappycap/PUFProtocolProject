// Imports.
const express = require('express');
const app = express();
const spawn = require('child_process').spawn;

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
app.post('/message', async (req, res) => {

  res.send({success:false});
  return

});

// Deployment.
app.listen(port, () => {
  console.log(`Running on ${port}`)
});
