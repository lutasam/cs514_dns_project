# cs514_dns_project

## directories

data: includes data collection, e.g. datasheet of the domain names, dns resolvers ...

cool_diy_dns_server: the high-performance dns server made by us

test: the test scripts for the dns server

## database source

1. domains: https://github.com/zer0h/top-1000000-domains/tree/master
2. dns resolvers: https://public-dns.info/nameservers.csv

## scripts

1. data/scanning.py: determine the doh support for the domain name
2. data/dnssec.py: determine the doh % dnssec support for the dns resolvers
3. test/test_script.py: test the performance of dns, doh and dnssec

## how to use (start the dns server)

1. git clone https://github.com/lutasam/cs514_dns_project
2. install go 1.22.1 https://go.dev/doc/install
   1. `curl -OL https://golang.org/dl/go1.22.1.linux-amd64.tar.gz`
   2. `sudo tar -C /usr/local -xvf go1.22.1.linux-amd64.tar.gz`
   3. `export PATH=$PATH:/usr/local/go/bin`
3. `cd cool_diy_dns_server`
4. `go build`
5. `./my_dns_server`
6. test dns, dnssec and doh by using `python3 test/test_script.py`

## other

* the password for key.pem: cs514 (there is also a key-decrypted.pem which do not need password)
* change the ports if you want
  * in `cool_diy_dns_server/main.go`, you can change the port of the server
  * default ports are 8053 and 4443(for doh server)
  * you also need to change the port numbers in `test/test_script.py`