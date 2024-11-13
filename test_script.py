import dns.resolver
import dns.query
import dns.message
import requests
import time

# 服务器地址
dns_server = '8.8.8.8'
doh_server = 'https://dns.google/resolve'

# 测试域名
domain = 'example.com'

# DNS查询函数
def test_dns_query():
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [dns_server]
    start_time = time.time()
    try:
        answer = resolver.query(domain, 'A')  # 使用 query 而非 resolve
        end_time = time.time()
        print("DNS Response Time:", end_time - start_time, "seconds")
        for rdata in answer:
            print("DNS Record:", rdata)
    except Exception as e:
        print("DNS Query Error:", e)

# DoH查询函数
def test_doh_query():
    url = doh_server
    params = {
        'name': domain,   # 查询的域名
        'type': 'A'       # 查询的记录类型
    }
    headers = {
        'accept': 'application/json'  # 指定返回JSON格式
    }
    start_time = time.time()
    try:
        response = requests.get(url, headers=headers, params=params)
        end_time = time.time()
        if response.status_code == 200:
            print("DoH Response Time:", end_time - start_time, "seconds")
            print("DoH Response JSON:", response.json())
        else:
            print("DoH Query Error:", response.status_code, response.text)
    except Exception as e:
        print("DoH Request Error:", e)

# DNSSEC验证函数
def test_dnssec():
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [dns_server]
    resolver.use_edns(edns=True, payload=1232, ednsflags=0x8000)  # 添加payload参数
    start_time = time.time()
    try:
        answer = resolver.query(domain, 'A')
        end_time = time.time()
        print("DNS Response Time:", end_time - start_time, "seconds")
        for rrset in answer.response.answer:
            print("DNSSEC Record:", rrset)
    except Exception as e:
        print("DNSSEC Validation Error:", e)

# 执行测试
print("Testing DNS Query")
test_dns_query()

print("\nTesting DoH Query")
test_doh_query()

print("\nTesting DNSSEC Validation")
test_dnssec()