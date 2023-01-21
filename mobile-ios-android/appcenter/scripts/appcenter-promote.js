/* eslint-disable @typescript-eslint/no-var-requires */
"use strict";
// npm run appcenter-promote
const
  config = require("./lib/config"),
  appctr = require('./lib/appcenter'),
  slack = require("./lib/slack");

console.log(config.print);

let promote_msg = ''
appctr.login(config.appCenterToken)
  .then(appctr.bundle_promote)
  .then(value => {
    promote_msg = value
    return appctr.info();
  })
  .then(value => {
    console.log('READY to slack!!!')
    const command = `appcenter codepush promote -a ${config.appName} -s Staging -d Production -t ${config.version}`
    return slack.okMessage({
      body: value,
      version: config.version,
      environment: config.environment, command, msg: promote_msg
    });
  })
  .catch(e => {
    slack.failMessage({
      error: ('data' in e ? e.data : e),
        version: config.version,
        environment: config.environment, command: ('cmd' in e ? e.cmd : "n/a")
    });
    process.exit(1)
  });
