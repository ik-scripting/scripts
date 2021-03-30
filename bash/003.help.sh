#!/bin/bash

help() {
  echo "-----------------------------------------------------------------------"
  echo "                      Available commands                              -"
  echo "-----------------------------------------------------------------------"
  echo -e -n "$BLUE"
  echo "   > build - To build the Docker image"
  echo "   > npm - To install NPM modules/deps"
  echo "   > bower - To install Bower/Js deps"
  echo "   > jkbuild - To build Jekyll project"
  echo "   > grunt - To run grunt task"
  echo "   > jkserve - To serve the project/blog on 127.0.0.1:4000"
  echo "   > install - To execute full install at once"
  echo "   > stop - To stop main jekyll container"
  echo "   > start - To start main jekyll container"
  echo "   > bash - Log you into container"
  echo "   > remove - Remove main jekyll container"
  echo "   > help - Display this help"
  echo -e -n "$NORMAL"
  echo "-----------------------------------------------------------------------"

}