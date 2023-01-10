import json
# Load JSON settings
with open('my_data.json', 'r',encoding='utf8') as json_data_file:
    json_object = json.load(json_data_file)
# Display value
print(json_object['Programs'][0]['Name'])
