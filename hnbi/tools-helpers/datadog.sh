#!/bin/bash

k exec -it datadog-monitoring-bs92s -- /bin/bash
TOKEN=$(</var/run/secrets/kubernetes.io/serviceaccount/token)
curl  https://$DD_KUBERNETES_KUBELET_HOST:10250/metrics/cadvisor -v -k -H "Authorization: Bearer $TOKEN"
