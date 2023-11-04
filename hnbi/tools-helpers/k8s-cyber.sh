#!/bin/bash

alias k=kubectl

k exec -it POD_NAME -- capsh --print
k exec -it POD_NAME -- cat /etc/passwd
k exec -it POD_NAME -- whoami
kubectl exec svc/ik-callback-app-helm -- date

