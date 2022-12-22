import json
# Opening JSON file
jsondatafile = open('my_data.json',encoding="utf8")
# Returns JSON object as a dictionary
jsonobject = json.load(jsondatafile)
# Display value
print(jsonobject['Programs'][0]['Name'])
