#!/bin/bash

aws fis create-experiment-template --cli-input-json fileb://aws-spot-experiment.json --query experimentTemplate.id

aws fis start-experiment --experiment-template-id <TEMPLATE_ID> --query experiment.id
