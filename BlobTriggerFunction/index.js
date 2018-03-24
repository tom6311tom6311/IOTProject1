module.exports = function (context, myBlob) {
  context.log(context.bindingData);
  const API = {
    AZURE: {
      VISION: {
        URL: 'https://westus.api.cognitive.microsoft.com/vision/v1.0/analyze?visualFeatures=Description&language=en',
        KEY: 'dea4ac603dd3443eaf2faac2bb93ecfb',
      },
      MAILJET: {
        MASTER: {
          KEY: {
            PUB: '070bb7d4f31634869a7ee2d0f3019924',
            PRV: '8b483d97e6890f3fb23a31044eee3810',
          },
        },
        SENDER: {
          Name: 'NTU Health Care Team',
          Email: 'r06942065@ntu.edu.tw',
        },
        RECEIVERS: [
          {
            Name: 'Tom Huang',
            Email: 'tom6311tom6311@gmail.com',
          },
        ],
        SUBJECT: 'Event ALERT'
      },
    },
  };
  const fetch = require('node-fetch');
  const mailjet = require ('node-mailjet').connect(API.AZURE.MAILJET.MASTER.KEY.PUB, API.AZURE.MAILJET.MASTER.KEY.PRV);

  function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
  }
  
  function faceAnalyze(img, callback) {
    fetch(API.AZURE.VISION.URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': API.AZURE.VISION.KEY,
      },
      body: JSON.stringify({
        url: context.bindingData.uri,
      }),
    }).then(res => res.json())
      .then((resJson) => {
        callback(resJson);
      })
      .catch((err) => {
        context.error(err);
        context.done();
      });
  }
  context.log("JavaScript blob trigger function processed blob \n Name:", context.bindingData.name, "\n Blob Size:", myBlob.length, "Bytes");
  faceAnalyze(myBlob, (result) => {
    context.log(JSON.stringify(result));
    const request = mailjet
      .post("send", {'version': 'v3.1'})
      .request({
        "Messages":[
          {
            "From": API.AZURE.MAILJET.SENDER,
            "To": API.AZURE.MAILJET.RECEIVERS,
            "Subject": API.AZURE.MAILJET.SUBJECT,
            "HTMLPart": `
              <div style='text-align: center;'>
                <h3>An Abnormal Event Is Happening at Your Place!</h3>
                <img src='${context.bindingData.uri}' style='display: block; width: 90%; margin: auto;'>
                <br/>The event looks like: <span style='color: red;'>${capitalizeFirstLetter(result.description.captions[0].text)}</span>
                <br/>May be related to: <i><strong>${result.description.tags.join(', ')}</strong></i>
              </div>
            `,
          }
        ]
      });
    request
      .then((result) => {
        context.log(result.body);
        context.done();
      })
      .catch((err) => {
        context.error(err.statusCode);
        context.done();
      });
  });
};