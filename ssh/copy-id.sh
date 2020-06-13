#!/bin/sh
# ssh-copy-id for mac os x

KEY="$HOME/.ssh/id_rsa.pub"

if [ ! -f $KEY ];then
echo "private key not found at $KEY"
echo "* please create it with "ssh-keygen -t dsa" *"
echo "* to login to the remote host without a password, don't give the key you create with ssh-keygen a password! *"
exit
fi

if [ -z $1 ];then
echo "Please specify user@host.tld as the first switch to this script"
exit
fi

echo "Putting your key on $1... "

KEYCODE=`cat $KEY`
cat $KEY | ssh $1 "cat - >> ~/.authorized_keys ; mkdir -p ~/.ssh ; mv ~/.authorized_keys ~/.ssh/authorized_keys"

echo "done!"
