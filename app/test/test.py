import json

# python object(dictionary) to be dumped
dict1 = {"city": "*city*", "data_time": "*data_time*"}

# the json file where the output must be stored
out_file = open("myfile.json", "a")

json.dump(dict1, out_file, indent=4)

out_file.close()
