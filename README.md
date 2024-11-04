- Assumptions
1. the program only supports default log format, not custom and the only version that is supported is 2.
2. While parsing the log, if number of columns is less than 12, it's an incomplete data, would skip the line.
3. Given the input example, the protocol is in numeric, need to have a map to conver it from numeric to string, and another map to conver it back. 
   I got the mapping from here, https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml.
4. Output for tag count is sorted by counts. Same as Port/Protocol Combination Counts.
5. For protocal not exists in the protocal_mapping file, in protocol_mapping_file.csv, you would assum user want to see the actual protocol number. So I didn't mask it to Unassigned. 

- How to compile/run the program
1. Under the same dir, include
	- flow_log.txt
	- lookup_table.csv
	- protocol_mapping_file.csv

2. Run,
$ python3 illumio.py

3. Then 2 files would generated.
	- tag_counts.txt 
	- port_protocol_counts.txt

- Tests were done
1. logs with same key (dstport, protocal)
2. sorted result on both output files
3. incomplete flow log (line 3 in the test file)
4. invalid protocol (not existing in mapping)

- Other analysis
1. the 10 MB flow log file size is not too big to load into memory. But processing the file line by line makes sure if the file becomes bigger and needs more memory, this code still works, no impact on this part.
2. Tuple as the key. 
It needs 2D map to hold the counts. There could be a few approaches to store it.
- list of list: as protocol has values ranges within 0-255, can create a fixed list for protocol dimension. But the ports is a very big range, there might be a lot empty values if using list for the ports demension. The sparse data is not a good fit here.
- dictionary of dictionaries: dictionary is efficient for sparse data, allows for easy addition/removal of entries, and uses less memory. But the hashing might make is slower. 
- list of dictionary: combines the benefits of lists and dictionaries, saving space for unused sparse values while maintaining structured access. Some overhead for the dictionaries, and access requires two steps.
- Dictionary of Tuples: dynamic sizes, and only stores entries with values, which saves memory. Flexible key and simple access.
I chose Dictionary of Tuples, for simple access and dynamic size for the sparse data.

