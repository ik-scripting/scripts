/* eslint-disable @typescript-eslint/no-var-requires */
"use strict";
// npm run appcenter-history
const
  config = require("./lib/config"),
  appctr = require('./lib/appcenter');

console.log(config.print);

appctr.login(config.appCenterToken)
  .then(appctr.bundle_history)
  .then(value => {
    console.log(value);
    return null;
  })
  .catch(e => {
    console.log(e);
    process.exit(1)
  });
