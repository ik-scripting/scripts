#https://gitlab.cylab.be/cylab/vagrant-boxes/-/blob/master/Makefile

SUB_DIRS=$(shell find . -mindepth 1 -maxdepth 1 -type d -not -path '*/\.*')

.PHONY: default

default:
	for dir in $(SUB_DIRS) ; do \
          $(MAKE) release --directory=$$dir; \
	done
