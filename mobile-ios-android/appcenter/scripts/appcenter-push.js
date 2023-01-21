/* eslint-disable @typescript-eslint/no-var-requires */
"use strict";
// npm run appcenter-push
const
  config = require("./lib/config"),
  appctr = require('./lib/appcenter'),
  slack = require("./lib/slack");

console.log(config.print)

appctr.login(config.appCenterToken)
  .then(appctr.bundle_push)
  .then(value => {
    console.log(value)
    return appctr.info();
  })
  .then(value => {
    console.log('READY to slack!!!')
    const command = `appcenter codepush release-react -a ${config.appName} -d ${config.environment} -m -t ${config.version}`
    return slack.okMessage({ body: value, environment: config.environment, command, version: config.version });
  })
  .catch(e => {
    slack.failMessage({
      error: ('msg' in e ? e.data : e),
        version: config.version,
        environment: config.environment, command: ('cmd' in e ? e.cmd : "n/a")
    });

    process.exit(1)
  });
