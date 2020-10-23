const AWS = require('aws-sdk');
const stepfunctions = new AWS.StepFunctions();


exports.lambda_handler = async(event, context) => {
  const payload = JSON.parse(event.body);

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
;
