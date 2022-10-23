# Kubernetes Tools

## EKS Node Drainer

- [EKS drainer (aws-labs) 7/10](https://github.com/ik-kubernetes/amazon-k8s-node-drainer)
- [EKS serverless drainer (aws-labs) 7/10](https://github.com/ik-kubernetes/amazon-eks-serverless-drainer)
- [Auto Drain](https://github.com/ik-kubernetes/eks-auto-drain)
- [Kube Drainer](https://github.com/ik-kubernetes/kubedrainer)
- [Node Drainer](https://github.com/ik-kubernetes/node-drainer)
- [EKS node drainer 3/10](https://github.com/ik-kubernetes/eks-node-drainer)

- [Node Termination Handler](https://github.com/aws/aws-node-termination-handler)

### Useful Commands

#### Testing by terminating an instance

Obtain a list of instances in a Cluster:

`kubectl get nodes -o=custom-columns=NAME:.metadata.name,INSTANCE:.spec.providerID `

Test by terminating an instance in an ASG

```bash
aws autoscaling terminate-instance-in-auto-scaling-group --no-should-decrement-desired-capacity --instance-id <instance id>
```

The Node should be cordoned, and drained of all Pods before termination. The Lambda function logs can provide output.
