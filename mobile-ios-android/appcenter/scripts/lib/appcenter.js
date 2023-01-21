/* eslint-disable @typescript-eslint/no-var-requires */
"use strict";

const
  config = require("./config"),
  cmd = require('node-cmd');


module.exports.info = async () => {
  return new Promise(function (resolve, reject) {
    console.log(`RUN: appcenter apps show -a ${config.appName} --output json`)
    cmd.run(`appcenter apps show -a ${config.appName} --output json`,
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      (err, data, stderr) => {
        if (err) {
          reject(JSON.stringify({
            data: data,
            err: err
          }));
        }
        resolve(JSON.parse(data))
      }
    );
  })
};

module.exports.bundle_push = async () => {
  return new Promise(function (resolve, reject) {
    const command = `appcenter codepush release-react -a ${config.appName} -d ${config.environment} -m -t ${config.version}`
    console.log(`RUN: ${command}`);
    cmd.run(command,
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      (err, data, stderr) => {
        if (err) {
          reject({
            data: data,
            msg: err,
            cmd: command
          });
        }
        resolve(data)
      }
    );
  })
};

// appcenter analytics app-versions
module.exports.login = async (token) => {
  return new Promise(function (resolve, reject) {
    console.log(`RUN: appcenter login --token <TOKEN>`)
    const command = `appcenter login --token ${token}`
    cmd.run(command,
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      (err, data, stderr) => {
        if (err) {
          reject({
            data: data,
            msg: err,
            cmd: command
          });
        }
        resolve(data)
      }
    );
  })
};

// https://docs.microsoft.com/en-us/appcenter/distribution/codepush/cli
module.exports.bundle_promote = async () => {
  return new Promise(function (resolve, reject) {
    const command = `appcenter codepush release-react -a ${config.appName} -d Production -m -t ${config.version}`;
    console.log(`RUN: ${command}`);
    cmd.run(command,
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      (err, data, stderr) => {
        if (err) {
          reject({
            data: data,
            msg: err,
            cmd: command
          });
        }
        resolve(data)
      }
    );
  })
};

module.exports.bundle_history = async () => {
  return new Promise(function (resolve, reject) {
    const list = cmd.runSync(`appcenter codepush deployment list -a ${config.appName}`);
    console.log(list.data)
    const command = `appcenter codepush deployment history -a ${config.appName} ${config.environment}`
    console.log(`RUN: ${command}`);
    cmd.run(command,
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      (err, data, stderr) => {
        if (err) {
          reject({
            data: data,
            msg: err,
            cmd: command
          });
        }
        resolve(data)
      }
    );
  })
};

module.exports.bundle_rollback = async (label) => {
  return new Promise(function (resolve, reject) {
    let command = `appcenter codepush rollback -a ${config.appName} ${config.environment} --quiet`
    if (label.length !== 0) {
      command += `--target-release ${label}`
    }
    console.log(`RUN: ${command}`);
    cmd.run(command,
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      (err, data, stderr) => {
        if (err) {
          reject({
            data: data,
            msg: err,
            command
          });
        }
        resolve({ data , command})
      }
    );
  })
};
