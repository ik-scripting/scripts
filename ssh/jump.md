# How to easy jump around

## On MAC OS

```
ssh-add -K <key>
ssh <user>@<jump-box-istance-ip> -A ssh -T <user>@<to-jump-instance-ip> -t -t
```

`ssh config`
```
Host *
  IdentityFile <key>
  User <user>

Host bastion
  Hostname <ip>

Host vm
  Hostname <ip>
  ProxyCommand ssh bastion -W %h:%p
  LocalForward 8080 127.0.0.1:8080
```
