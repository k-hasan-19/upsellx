const AWS = require('aws-sdk');
const stepfunctions = new AWS.StepFunctions();


exports.lambda_handler = async(event, context) => {
  const payload = JSON.parse(event.body);
  if (!_checkIsValidDomain(payload['domain']))
    return _response(400, {
      "message": "Invalid request body"
    })
  const stateMachineArn = process.env.STATE_MACHINE_ARN;
  const params = {
    stateMachineArn: stateMachineArn,
    /* required */
    input: JSON.stringify(payload)
  };

  const execmeta = await stepfunctions.startExecution(params).promise();
  const params2 = {
    executionArn: execmeta.executionArn /* required */
  };
  const res = await stepfunctions.describeExecution(params2).promise();
  return _response(200, {
    execution_id: res.name,
    execution_status: res.status
  });
};


function _response(statusCode, body) {
  return {
    statusCode: statusCode,
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(body)
  }
}
function _checkIsValidDomain(domain) {
  var re = new RegExp(/^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9](?:\.[a-zA-Z]{2,})+$/);
  return domain.match(re);
}