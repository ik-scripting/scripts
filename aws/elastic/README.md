# Elastic

- [Snaphosts](https://medium.com/@kirti.garg_70814/manual-snapshot-restore-and-deletion-of-aws-elasticsearch-using-python-79c6f706c8e1)
- [Scripts](https://github.com/davidclin/aws-elasticsearch-snapshot/tree/master)

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "es:ESHttpDelete",
                "es:ESHttpGet",
                "es:ESHttpHead",
                "es:ESHttpPost",
                "es:ESHttpPut"
            ],
            "Effect": "Allow",
            "Resource": "*"
        }
    ]
}
// trusted entity
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com",
        "Service": "es.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

https://medium.com/@kirti.garg_70814/manual-snapshot-restore-and-deletion-of-aws-elasticsearch-using-python-79c6f706c8e1

```
curl -XGET 'elasticsearch-domain-endpoint/_snapshot/repository/_all
curl -XGET 'elasticsearch-domain-endpoint/_snapshot?pretty'
curl -XPUT 'elasticsearch-domain-endpoint/_snapshot/repository/snapshot-name'
curl -XPOST 'elasticsearch-domain-endpoint/_snapshot/repository/snapshot/_restore'
```
