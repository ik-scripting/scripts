const yargs = require('yargs')
const plist = require('plist')
const fs = require('fs')
const path = require('path')
const semver = require('semver')

const { argv } = yargs
  .option('bump-type', {
    alias: 'b',
    describe: 'The type of version bump to do e.g. patch, minor, major',
    requiresArg: true,
    demandOption: true,
  })
  .help('help')

const SUPPORTED_BUMP_TYPES = ['patch', 'minor', 'major']

function getPathRelativeToProject(relativePath) {
  return path.resolve(__dirname, '..', '..', ...relativePath.split('/'))
}

function updatePackageVersion(bumpType) {
  console.log('Updating version in package json...')

  const packagePath = getPathRelativeToProject('package.json')
  const packageJson = fs.readFileSync(packagePath, 'utf-8')
  const data = JSON.parse(packageJson)
  data.lastVersion = data.version

  const newVersion = semver.inc(data.version, bumpType)
  data.version = newVersion

  const stringData = JSON.stringify(data, null, 2)
  fs.writeFileSync(packagePath, `${stringData}\n`)

  return newVersion
}

function versionAndroid(version) {
  console.log('Writing version to Android project')

  const gradlePath = getPathRelativeToProject('android/app/build.gradle')
  const gradleText = fs.readFileSync(gradlePath, 'utf-8')
  const updatedText = gradleText.replace(
    /versionName\s".*"/,
    `versionName "${version}"`,
  )

  fs.writeFileSync(gradlePath, updatedText)
}

function versionIos(version) {
  console.log('Writing version to iOS project')

  const plistPaths = [
    getPathRelativeToProject('ios/hbapp/Info.plist'),
    getPathRelativeToProject('ios/NotificationServiceExtension/Info.plist'),
    getPathRelativeToProject('ios/NotificationContentExtension/Info.plist'),
  ]

  plistPaths.forEach((plistPath) => {
    const plistContents = fs.readFileSync(plistPath, 'utf-8')
    const parsedPlist = plist.parse(plistContents)

    parsedPlist.CFBundleVersion = version
    parsedPlist.CFBundleShortVersionString = version

    fs.writeFileSync(plistPath, plist.build(parsedPlist))
  })
}

function getBumpType() {
  const bumpType = argv['bump-type']

  if (!SUPPORTED_BUMP_TYPES.includes(bumpType)) {
    console.error(
      `bump-type ${bumpType} is not supported. Use one of patch, minor, major`,
    )
    process.exit(1)
  }

  return bumpType
}

function versionFiles() {
  const bumpType = getBumpType()

  console.log(`Bumping app version with ${bumpType} bump`)
  const appVersion = updatePackageVersion(bumpType)

  console.log(`Got updated version ${appVersion} from package json update`)
  versionAndroid(appVersion)
  versionIos(appVersion)
}

versionFiles()
