import dns.resolver
import dns.query
import dns.message
import requests
import time

# server address
dns_server = '127.0.0.1'
# doh_server = 'https://dns.google/resolve'
doh_server = 'https://127.0.0.1:4443/dns-query'

# test domain name
domain = 'example.com'
# port
port = 8053

def test_dns_query():
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [dns_server]
    resolver.port = port
    start_time = time.time()
    try:
        answer = resolver.query(domain, 'A')  
        end_time = time.time()
        print("DNS Response Time:", end_time - start_time, "seconds")
        for rdata in answer:
            print("DNS Record:", rdata)
    except Exception as e:
        print("DNS Query Error:", e)

def test_doh_query():
    record_type = "A"

    dns_query = dns.message.make_query(domain, record_type)
    dns_query_data = dns_query.to_wire()

    headers = {
        'Content-Type': 'application/dns-message',
        'Accept': 'application/dns-message',
    }

    start_time = time.time()
    try:
        response = requests.post(doh_server, headers=headers, data=dns_query_data, verify=False)
        end_time = time.time()

        if response.status_code == 200:
            print("DoH Response Time:", end_time - start_time, "seconds")
            print("DoH Response Data (hex):", response.content.hex())
        else:
            print("DoH Query Error:", response.status_code, response.text)
    except Exception as e:
        print("DoH Request Error:", e)


def test_dnssec():
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [dns_server]
    resolver.port = port
    resolver.use_edns(edns=True, payload=1232, ednsflags=0x8000) 
    start_time = time.time()
    try:
        answer = resolver.query(domain, 'A')
        end_time = time.time()
        print("DNS Response Time:", end_time - start_time, "seconds")
        for rrset in answer.response.answer:
            print("DNSSEC Record:", rrset)
    except Exception as e:
        print("DNSSEC Validation Error:", e)


print("Testing DNS Query")
test_dns_query()

print("\nTesting DoH Query")
test_doh_query()

print("\nTesting DNSSEC Validation")
test_dnssec()