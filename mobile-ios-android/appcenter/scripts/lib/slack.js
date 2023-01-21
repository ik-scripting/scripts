/* eslint-disable @typescript-eslint/no-var-requires */
"use strict";

const https = require('https');
const config = require("./config");

let sendSlackMessage = (messageBody) => {
  // console.log(JSON.stringify(messageBody, null, 2));
  try {
    // make sure the incoming message body can be parsed into valid JSON
    messageBody = JSON.stringify(messageBody);
  } catch (e) {
    throw new Error('Failed to stringify messageBody', e);
  }

  // Promisify the https.request
  return new Promise((resolve, reject) => {
    // general request options, we defined that it's a POST request and content is JSON
    const requestOptions = {
      method: 'POST',
      header: {
        'Content-Type': 'application/json'
      }
    };

    // actual request
    const req = https.request(config.slackUrl, requestOptions, (res) => {
      let response = '';


      res.on('data', (d) => {
        response += d;
      });

      // response finished, resolve the promise with data
      res.on('end', () => {
        resolve(response);
      })
    });

    // there was an error, reject the promise
    req.on('error', (e) => {
      reject(e);
    });

    // send our message body (was parsed to JSON beforehand)
    req.write(messageBody);
    req.end();
  });
}

module.exports.okMessage = (input) => {
  let msg = enrichMessage(input);
  return sendSlackMessage(msg)
};

module.exports.okRollbackMessage = (input) => {
  let msg = enrichRollbackMessage(input);
  return sendSlackMessage(msg)
};

module.exports.failRollbackMessage = (input) => {
  let msg = failureRollbackMessage(input);
  return sendSlackMessage(msg)
};

module.exports.failMessage = (input) => {
  let msg = failureMessage(input);
  return sendSlackMessage(msg)
};

module.exports.promoteMessageOkMessage = (input) => {
  let msg = promoteMessage(input);
  return sendSlackMessage(msg)
};

function promoteMessage(input) {
  let { body, environment, command, msg, version} = input;
  let appCenterUrl = `<https://appcenter.ms/users/${body.owner.name}/apps/${body.name}|AppCenter Url :arrow_right: >`
  let appCenterCodePushUrl = `<https://appcenter.ms/users/${body.owner.name}/apps/${body.name}/distribute/code-push/${environment}|AppCenter Code Push :arrow_right:>`
  let githubActionUrl = `<${config.githubActionUrl}|GithubAction Url :arrow_right:>`
  return {
    "username": "Github Action Bot", // This will appear as user name who posts the message
    "text": `App Center "${body.os}" bundle updated ${config.platformEmoji} ✅.`, // text
    "icon_emoji": " :white_check_mark:", // User icon, you can also use custom icons here
    "mrkdwn_in": ["text", "value"],
    "attachments": [{
      "mrkdwn_in": ["text", "fields", "value", 'title'],
      "color": "#32a832", // color of the attachments sidebar.
      "title": `Env: ${environment}. Version: ${version}.`,
      "fields": [
        {
          "title": "Git Branch",
          "value": config.githubBranch,
          "short": true
        },
        {
          "title": "Release Type",
          "value": body.releaseType,
          "short": true
        },
      ]
    },
    {
      "color": "#32a832",
      "title": `Application. Name: ${body.name}. Owner: ${body.owner.name}`,
    },
    {
      "color": "#32a832",
      "title": `Command: "${command}"`,
    },
    {
      "color": "#32a832",
      "title": `Message: "${msg}"`,
    },
    {
      "blocks": [
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": "*Links*"
          }
        },
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": `${appCenterUrl}`
          }
        },
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": `${appCenterCodePushUrl}`
          }
        },
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": `${githubActionUrl}`
          }
        }
      ]
    }
    ]
  };
}

function enrichMessage(input) {
  let { body, environment, version } = input;
  let appCenterUrl = `<https://appcenter.ms/users/${body.owner.name}/apps/${body.name}|AppCenter Url :arrow_right: >`
  let appCenterCodePushUrl = `<https://appcenter.ms/users/${body.owner.name}/apps/${body.name}/distribute/code-push/${environment}|AppCenter Code Push :arrow_right:>`
  let githubActionUrl = `<${config.githubActionUrl}|GithubAction Url :arrow_right:>`
  return {
    "username": "Github Action Bot", // This will appear as user name who posts the message
    "text": `App Center "${body.os}" bundle updated ${config.platformEmoji} ✅.`, // text
    "icon_emoji": " :white_check_mark:", // User icon, you can also use custom icons here
    "mrkdwn_in": ["text", "value"],
    "attachments": [{
      "mrkdwn_in": ["text", "fields", "value", 'title'],
      "color": "#32a832", // color of the attachments sidebar.
      "title": `Env: ${environment}. Version: ${version}.`,
      "fields": [
        {
          "title": "Git Branch",
          "value": config.githubBranch,
          "short": true
        },
        {
          "title": "Release Type",
          "value": body.releaseType,
          "short": true
        },
      ]
    },
    {
      "color": "#32a832",
      "title": `Application. Name: ${body.name}. Owner: ${body.owner.name}`,
    },
    {
      "blocks": [
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": "*Links*"
          }
        },
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": `${appCenterUrl}`
          }
        },
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": `${appCenterCodePushUrl}`
          }
        },
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": `${githubActionUrl}`
          }
        }
      ]
    }
    ]
  };
}

function failureMessage(input) {
  let { error, environment, version} = input;
  const githubActionUrl = `<${config.githubActionUrl}|GithubAction Url :arrow_right:>`
  const block_command = ('command' in input ? {
    "color": "#fc038c",
    "title": `Command: ${input.command}. `,
  } : {})
  return {
    "username": "Github Action Bot", // This will appear as user name who posts the message
    "text": `App Center "${config.platform}" bundle update failed ${config.platformEmoji} ❌`, // text
    "icon_emoji": " :white_check_mark:", // User icon, you can also use custom icons here
    "mrkdwn_in": ["text", "value"],
    "attachments": [{
      "mrkdwn_in": ["text", "fields", "value", 'title'],
      "color": "#fc038c", // color of the attachments sidebar.
      "title": `Env: ${environment}. Version: ${version}.`,
      "fields": [
        {
          "title": "Git Branch",
          "value": config.githubBranch,
          "short": true
        },
      ]
    },
    {
      "color": "#fc038c",
      "title": `Application. Name: ${config.appName}. `,
    },
    {
      "color": "#fc038c",
      "title": `Failure message. ${error}`,
    },
      block_command,
    {
      "color": "#fc038c",
      "blocks": [
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": "*Links*"
          }
        },
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": `${githubActionUrl}`
          }
        }
      ]
    }
    ]
  };
}

function enrichRollbackMessage(input) {
  let { body, environment, version } = input;
  let appCenterUrl = `<https://appcenter.ms/users/${body.owner.name}/apps/${body.name}|AppCenter Url :arrow_right: >`
  let appCenterCodePushUrl = `<https://appcenter.ms/users/${body.owner.name}/apps/${body.name}/distribute/code-push/${environment}|AppCenter Code Push :arrow_right:>`
  let githubActionUrl = `<${config.githubActionUrl}|GithubAction Url :arrow_right:>`
  return {
    "username": "Github Action Bot", // This will appear as user name who posts the message
    "text": `App Center ${config.platformEmoji} Rollback a deployment to a previous release ${version}  ✅.`, // text
    "icon_emoji": " :white_check_mark:", // User icon, you can also use custom icons here
    "mrkdwn_in": ["text", "value"],
    "attachments": [{
      "mrkdwn_in": ["text", "fields", "value", 'title'],
      "color": "#32a832", // color of the attachments sidebar.
      "title": `Env: ${environment}. Rollback version: ${version}.`,
      "fields": []
    },
    {
      "color": "#32a832",
      "title": `Application. Name: ${body.name}. Owner: ${body.owner.name}`,
    },
    {
      "blocks": [
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": "*Links*"
          }
        },
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": `${appCenterUrl}`
          }
        },
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": `${appCenterCodePushUrl}`
          }
        },
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": `${githubActionUrl}`
          }
        }
      ]
    }
    ]
  };
}

function failureRollbackMessage(input) {
  let { error, environment, version} = input;
  const githubActionUrl = `<${config.githubActionUrl}|GithubAction Url :arrow_right:>`
  const block_command = ('command' in input ? {
    "color": "#fc038c",
    "title": `Command: ${input.command}. `,
  } : {})
  return {
    "username": "Github Action Bot", // This will appear as user name who posts the message
    "text": `App Center ${config.platformEmoji} ROLLBACK failed ❌`, // text
    "icon_emoji": " :white_check_mark:", // User icon, you can also use custom icons here
    "mrkdwn_in": ["text", "value"],
    "attachments": [{
      "mrkdwn_in": ["text", "fields", "value", 'title'],
      "color": "#fc038c", // color of the attachments sidebar.
      "title": `Env: ${environment}. Rollback version: ${version}.`,
      "fields": []
    },
    {
      "color": "#fc038c",
      "title": `Application. Name: ${config.appName}. `,
    },
    {
      "color": "#fc038c",
      "title": `Failure message. ${error}`,
    },
      block_command,
    {
      "color": "#fc038c",
      "blocks": [
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": "*Links*"
          }
        },
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": `${githubActionUrl}`
          }
        }
      ]
    }
    ]
  };
}
