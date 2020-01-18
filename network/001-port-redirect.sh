# Redirect port 3080/3443 to 80/443 for local dev

#Requests from outside
iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-ports 3080
iptables -t nat -A PREROUTING -p tcp --dport 443 -j REDIRECT --to-ports 3443

#Requests from localhost
iptables -t nat -I OUTPUT -p tcp -d 127.0.0.1 --dport 80 -j REDIRECT --to-ports 3080
iptables -t nat -I OUTPUT -p tcp -d 127.0.0.1 --dport 443 -j REDIRECT --to-ports 3443
@ivankatliarchuk
 
