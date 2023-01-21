#!/usr/bin/env bash

cd ios || return
sudo gem install bundler -n /usr/local/bin
bundler install
cd ..
