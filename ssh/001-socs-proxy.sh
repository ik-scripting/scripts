#!/bin/sh
#
# Step 1. Install proctools to use "pgrep" command.
#
# Step 2. Configure your .ssh/config to include:
#
# Host proxy-host
#      HostName proxy-host.example.com
#      User a12345
#      DynamicForward localhost:1080
#
# Step 3. Configure SSH_HOST, SOCKS_PROXY_PORT, and NW_SERVICE variables.
#
SSH_HOST=proxy-host
SOCKS_PROXY_HOST=localhost
SOCKS_PROXY_PORT=1080
NW_SERVICE=Wi-Fi # /usr/sbin/networksetup -listallnetworkservices

# DO NOT CHANGE
NWSETUP_CMD="/usr/sbin/networksetup"
SSH_CMD="/usr/bin/ssh -Nf $SSH_HOST"

SOCKS_PROXY_ENABLED=
if $NWSETUP_CMD -getsocksfirewallproxy $NW_SERVICE | grep -q "^Enabled: Yes"; then
    SOCKS_PROXY_ENABLED=1
fi
SSH_PID=`pgrep -f "$SSH_CMD"`

enable_socks_proxy() {
    echo Enable SOCKS Firewall Proxy.
    $NWSETUP_CMD -setsocksfirewallproxy $NW_SERVICE $SOCKS_PROXY_HOST $SOCKS_PROXY_PORT off
}

disable_socks_proxy() {
    if [ $SOCKS_PROXY_ENABLED ]; then
	echo Disable SOCKS Firewall Proxy.
	$NWSETUP_CMD -setsocksfirewallproxystate $NW_SERVICE off
    fi
}

create_ssh_connection() {
    echo Create SSH Connection to $SSH_HOST.
    $SSH_CMD &> /dev/null
}

destroy_ssh_connection() {
    if [ $SSH_PID ]; then
	echo Destroy SSH Connection to $SSH_HOST.
	kill -TERM $SSH_PID
    fi
}

case $1 in
    start)
	destroy_ssh_connection
	create_ssh_connection
	enable_socks_proxy
	;;
    stop)
	disable_socks_proxy
	destroy_ssh_connection
	;;
    pid)
	if [ $SSH_PID ]; then
	    echo $SSH_PID
	else
	    echo SSH Connection to $SSH_HOST is dead.
	fi
	;;
    status)
	if [ $SSH_PID ]; then
	    echo SSH Connection to $SSH_HOST is alive \(PID:$SSH_PID\).
	else
	    echo SSH Connection to $SSH_HOST is dead.
	fi
	if [ $SOCKS_PROXY_ENABLED ]; then
	    echo SOCKS Firewall Proxy is on.
	else
	    echo SOCKS Firewall Proxy is off.
	fi
	;;
    on)
	enable_socks_proxy
	;;
    off)
	disable_socks_proxy
	;;
    toggle)
	if [ $SOCKS_PROXY_ENABLED ]; then
	    disable_socks_proxy
	else
	    enable_socks_proxy
	fi
	;;
    *)
	echo "Usage: $0 {start|stop|status|on|off|toggle|help}"
	exit 1
	;;
esac

exit 0
