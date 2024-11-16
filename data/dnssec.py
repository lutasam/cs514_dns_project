import csv
import requests

# Function to check DoH support for a resolver
def check_doh_support(ip_address):
    #doh_url = f"https://ip_address/dns-query"
    doh_url = f"https://{ip_address}"
    headers = {
        "accept": "application/dns-json"
    }
    params = {
        "name": "example.com",  
        "type": "A"           
    }

    try:
        requests.get(doh_url, headers=headers, params=params, timeout=5)
        return True
    except Exception:
        return False  # DoH check failed (timeout or other error)

# Input and output file paths
input_file = "nameservers.csv"  # Your CSV file with DNS resolvers
output_file = "resolver_doh_dnssec_support.csv"  # Output file to store results

# Open the CSV file for reading and writing
with open(input_file, mode='r', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    # Open the output file to write the results
    with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
        # Prepare the output CSV headers
        fieldnames = reader.fieldnames + ['doh_supported', 'dnssec_supported']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Iterate through each DNS resolver entry
        for row in reader:
            ip_address = row['ip_address']
            dnssec_supported = row['dnssec'].strip().lower() == 'true'
            # Check DoH support for the resolver
            doh_supported = check_doh_support(ip_address)

            # Append results to the row and write to the output file
            row['doh_supported'] = doh_supported
            row['dnssec_supported'] = dnssec_supported
            writer.writerow(row)
            # print(f"Checked {ip_address}: DoH Supported = {doh_supported}, DNSSEC Supported = {dnssec_supported}")

print(f"Results saved to {output_file}")
