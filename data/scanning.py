import requests
import csv

# Function to check DoH support for a domain using Cloudflare's DoH service
def check_doh_support(domain):
    doh_url = "https://cloudflare-dns.com/dns-query"  # Cloudflare DoH resolver
    headers = {
        "accept": "application/dns-json"
    }
    params = {
        "name": domain,
        "type": "A"
    }
    try:
        response = requests.get(doh_url, headers=headers, params=params, timeout=5)
        if response.status_code == 200:
            return True  # DoH is supported
        else:
            return False  # DoH is not supported
    except requests.exceptions.RequestException:
        return False  # DoH check failed (timeout or other error)

# Input and output files
input_file = "top-100000-domains.txt"
output_file = "doh_support_results.csv"

# Read the list of websites from the text file
with open(input_file, mode='r', newline='', encoding='utf-8') as infile:
    websites = [line.strip() for line in infile.readlines()]


# Prepare to write results to a new CSV file
with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
    fieldnames = ['Domain', 'DoH Supported']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    # Iterate over the websites and check DoH support
    for domain in websites:
        doh_supported = check_doh_support(domain)
        writer.writerow({'Domain': domain, 'DoH Supported': 'Yes' if doh_supported else 'No'})
        # print(f"Checked {domain}: DoH Supported = {'Yes' if doh_supported else 'No'}")

print(f"Results saved to {output_file}")
