# COMMON BUILD SCRIPTS

The project is to support Automation within Cloud environments. It leverage the process of automation with
CI&CD, pipelines and any other environments.

## Project Status

This project is under active development.

## Build Status

[Concourse CI](https://concourse.<project-name>cloud.co.uk/teams/common_infrastructure/pipelines/common-resource-pipeline)

## Table of contents

* [Project Status](#project-status)
* [Build Status](#build-status)
* [Introduction](#introduction)
  * [Purpose](#purpose)
  * [Location within <project-name> estate](#location-within-<project-name>-estate)
  * [Wiki](#wiki)
  * [Modules](#modules)
    * [Layout](#layout)
  * [Setup](#setup)
  * [Develop](#develop)
  * [Usage](#usage)
* [Coding Style](#coding-style)
* [Authors](#authors)
* [Release History](#release-history)

## Introduction

### Purpose

The project leverage automation of deployment infrastructure in repeatable manner.

### Location within <project-name> estate

Build Scripts used all over the project that require automation.

### Wiki

[Wiki Resources](https://wiki.<project-name>cloud.co.uk/display/HAPI/2.1+Understanding+the+code)
[Getting Started](https://wiki.<project-name>cloud.co.uk/display/HAPI/2.5+Getting+started)
[Build Pipelines](https://wiki.<project-name>cloud.co.uk/display/HAPI/2.2+Understand+build+pipelines)

### Modules

This is a multi module project. The purpose of each module is described below:

#### Layout

    ├── .vscode                # vscode settings
    ├── functions              # bash&shell functions
    ├── ci                     # Pipeline with CI&&CD definitions
    ├── py                     # root
    ├──── deploy_scripts       # wrappers for different domains
    ├──── py                   # domain modules
    ├──── tests                # tests
    └── README.md

### Setup

The project require to have installed few packages. Currently using virtual environments.

```bash
sudo apt-get install python2.7 python-pip
sudo pip install virtualenv
```

Setup virtual environments with all the dependencies.

```bash
./setup.sh
source ./veenv/bin/activate
```

### Develop

While developing the python code, try to use the ```./watch_tests.sh``` script as it will run the unit tests
periodically and let you know if anything was broken.

### Usage

Run tests:

```bash
./run_tests.sh
```

Bug and quality check:

```bash
./run_linters.sh
```

## Coding Style

This project uses embedded coding styles, the first and most wide reaching is the use of an editorconfig file [link](http://editorconfig.org/) this enables a simple configuration of basic cross-language text styling including indentation styles, sizes, end of line characters etc.

## Authors

[Contributors](https://git.<project-name>cloud.co.uk/everyone/common-build-scripts/graphs/master)

## Release History

### 2.0

Elastic Container Service support

Elastic Container Service waiter. Would not let to deploy service when there are failures.

Added tests framework.

Provide `pylint` and `flake8` libraries to support lintint.

##### 1.1

Slack support

Publish test reports support

Gattling test in docker support

### 1.0

Elastic Beanstalk support

Cloudformation support

Route53(Dns) support

Elastic Container Registry (Docker registry) support
