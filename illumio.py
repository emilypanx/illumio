import csv
from collections import defaultdict

CONSTANT_UNTAGGED = 'Untagged'
CONSTANT_UNASSIGNED = 'Unassigned'

def load_protocol_mappings(protocol_mapping_file):
    protocol_mappings_str_to_int = {}
    protocol_mappings_int_to_str = {}
    with open(protocol_mapping_file, mode='r') as file:
        for line in file:
            parts = line.split("\t")
            key = parts[1].lower() # str
            try:
                val = int(parts[0]) # int
            except ValueError as e:
                #print(f"An error occurred when parsing protocol code: {e}")
                val = -1
                key = CONSTANT_UNASSIGNED
            protocol_mappings_str_to_int[key] = val
            protocol_mappings_int_to_str[val] = key
        #print("protocol_mappings:",protocol_mappings)
    return protocol_mappings_str_to_int, protocol_mappings_int_to_str

def load_lookup_table(lookup_file, protocol_mappings_str_to_int):
    """Load the lookup table from the CSV file and build in-memory cache.
       Example data:
       dstport,protocol,tag 
       25,tcp,sv_P1 
       68,udp,sv_P2 
    """
    lookup= {}
    with open(lookup_file, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Use lowercased keys for case insensitive matching
            key = (int(row['dstport']), protocol_mappings_str_to_int.get(row['protocol'].lower(), -1))
            lookup[key] = row['tag'] #(int, int) -> tag
    #print(lookup)
    return lookup 

def parse_flow_logs(flow_log_file, lookup):
    """Parse the flow logs and map them to tags using the lookup table.
       version,account-id,interface-id,srcaddr,dstaddr,srcport,dstport,protocol,packets,bytes,start,end,action,log-status
       dstport: 6th
       protocol: 7th
    """
    tag_counts = defaultdict(int)
    port_protocol_counts = defaultdict(int)
    
    with open(flow_log_file, mode='r') as file:
        for line in file:
            parts = line.split()
            if len(parts) < 14:
                print("ignore line due to incomplete: ", line)
                continue  # Skip incomplete line
            
            # Extract key
            dstport = int(parts[6])
            protocol = int(parts[7])
            key = (dstport, protocol) # (int, int)
            #print(key)
            # Determine the tag
            tag = lookup.get(key, CONSTANT_UNTAGGED)
            #print(key, tag)

            tag_counts[tag] += 1
            port_protocol_counts[key] += 1

    return tag_counts, port_protocol_counts

def write_output(tag_counts, port_protocol_counts, protocol_mappings_int_to_str, output_file_tag_counts, output_file_pp_counts):
    """Write the results to an output file."""

    sorted_tag_counts= dict(sorted(tag_counts.items(), key=lambda item: item[1]))
    sorted_port_protocol_counts= dict(sorted(port_protocol_counts.items(), key=lambda item: item[1]))


    with open(output_file_tag_counts, mode='w') as csvfile:
        fieldnames = ['Tag', 'Count']
        writer = csv.writer(csvfile,delimiter=",")
        writer.writerow(fieldnames)
        for k,v in sorted_tag_counts.items():
            writer.writerow([k, v])

    with open(output_file_pp_counts, mode='w') as csvfile:
        fieldnames = ['Port', 'Protocol', 'Count']
        writer = csv.writer(csvfile,delimiter=",")
        writer.writerow(fieldnames)
        for k,v in sorted_port_protocol_counts.items():
            print(k[1], protocol_mappings_int_to_str.get(k[1]))
            writer.writerow([k[0], protocol_mappings_int_to_str.get(k[1], k[1]), v]) # convert (int, int, count) to (int, str, count)

            

def main(flow_log_file, lookup_file, protocol_mapping_file, output_file_tag_counts, output_file_pp_counts):
    """Main function to run the log parsing and output generation."""
    # load_protocol_mappings
    protocol_mappings_str_to_int, protocol_mappings_int_to_str = load_protocol_mappings(protocol_mapping_file)
    #print(protocol_mappings)
    
    # load lookup file (port,protocol) -> tag mapping
    lookup = load_lookup_table(lookup_file, protocol_mappings_str_to_int)
    #print(lookup)
    
    # parse log and count
    tag_counts, port_protocol_counts = parse_flow_logs(flow_log_file, lookup)
    
    # write results to files
    write_output(tag_counts, port_protocol_counts, protocol_mappings_int_to_str, output_file_tag_counts, output_file_pp_counts)

if __name__ == "__main__":
    # input files
    protocol_mapping_file = 'protocol_mapping_file.csv'
    flow_log_file = 'flow_logs.txt'
    lookup_file = 'lookup_table.csv'
    output_file_tag_counts = 'tag_counts.txt'
    output_file_pp_counts = 'port_protocol_counts.txt'

    main(flow_log_file, lookup_file, protocol_mapping_file, output_file_tag_counts, output_file_pp_counts)
