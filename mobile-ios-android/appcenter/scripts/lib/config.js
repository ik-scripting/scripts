/* eslint-disable @typescript-eslint/no-var-requires */
"use strict";

const { get } = require('env-var'),
  fs = require('fs'),
  YAML = require('yaml');

const slackUrl = get('SLACK_WEBHOOK').required().asString(),
  platform = get('PLATFORM').required().asString(),
  versionFile = get('VERSION_FILE').default('versions.yml').required().asString(),
  appCenterToken = get('APP_CENTER_TOKEN_BASE64').required().convertFromBase64().asString(),
  environment = get('ENVIRONMENT').required().asEnum(['Staging', 'Production']),
  appName = get('OWNERNAME_APPNAME').required().asString(),
  githubActionUrl = get('GITHUB_ACTION_RUN_URL').default("https://github.com").asUrlString(),
  githubActionWorkflowUrl = get('GITHUB_ACTION_WORKFLOW_URL').default("https://github.com").asUrlString(),
  history =  get('HISTORY').default('false').asBoolStrict(),
  githubBranch = get('GITHUB_BRANCH').default("main").asString();

let platformEmoji = (platform) => {
  return (platform.toLowerCase() === 'android' ? '🤖' : '🍎')
}

let readTargetVersion = (platform, fromFile) => {
  const file = fs.readFileSync(fromFile, 'utf8')
  return YAML.parse(file)[platform.toLowerCase()]['version']
}

let ownerName = (input) => {
  return input.split('/')[0];
}

let application = (input) => {
  return input.split('/')[1];
}

module.exports = {
  slackUrl,
  platform,
  versionFile,
  appCenterToken,
  environment,
  appName,
  githubActionUrl,
  githubActionWorkflowUrl,
  githubBranch,
  platformEmoji: platformEmoji(platform),
  version: readTargetVersion(platform, versionFile),
  history,
  owner: ownerName(appName),
  app: application(appName),
  print: {
    app: appName,
    branch: githubBranch,
    env: environment,
    actionUrl: githubActionUrl,
    platform: platform,
    emoji: platformEmoji(platform),
    version: readTargetVersion(platform, versionFile),
  }
};
