/* eslint-disable @typescript-eslint/no-var-requires */
"use strict";
const { history } = require("./lib/config");
// npm run appcenter-promote
const
  config = require("./lib/config"),
  appctr = require('./lib/appcenter'),
  { from } = require('env-var'),
  slack = require("./lib/slack");

// https://github.com/evanshortiss/env-var/blob/master/API.md#asboolstrict
// Add an accessor named 'asLabel' that verifies that the value is a
// valid-looking release label
const env = from(process.env, {
  asLabel: (value) => {
    // Validating label addresses.
    if (value.length === 0 || value === 'undefined') {
      return ""
    }
    if (!value.startsWith('v')) {
      throw new Error('must start with "v"')
    }
    var count = (value.match(/v/g) || []).length;
    if (count !== 1) {
      throw new Error('must contain exactly one "v"')
    }
    return value
  }
})
const targetLabel = env.get('TARGET_LABEL').default("").asLabel();

config.print.targetLabel = targetLabel;

console.log(config.print);

let promote_msg = ''
appctr.login(config.appCenterToken)
  .then(appctr.bundle_history)
  .then(value => {
    if (history) {
      console.log(value);
    }
    return null;
  })
  .then(() => {
    return appctr.bundle_rollback(targetLabel);
  })
  .then(value => {
    value = {
      "owner": {
        "name": config.owner
      },
      "name": config.app
    }
    return slack.okRollbackMessage({
      body: value, environment: config.environment,
      command: value.command, version: targetLabel, msg: value.data
    });
  })
  .catch(e => {
    slack.failRollbackMessage({
      error: ('data' in e ? e.data : e),
      environment: config.environment,
      version: targetLabel, command: e.command
    });
    process.exit(1)
  });
