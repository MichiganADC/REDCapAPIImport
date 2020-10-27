import requests
from configparser import ConfigParser
from typing import Dict, List

# Read config file
config = ConfigParser()
config.read("config.cfg")

# Get config values
redcap_api_url: str = config.get("redcap", "api_url")
redcap_project_token: str = config.get("redcap", "project_token")

# Try different JSON strings:
# Because this REDCap project is longitudinal, the primary key is composite, consisting of
# "ptid" and "redcap_event_name".
# Both are required in the JSON string (sorta... see `json_data_bad3` below).

# -- Good JSON
json_data_good: str = '[{"ptid": "1", "redcap_event_name": "visit_1_arm_1", "maristat": 1},' \
                      '{"ptid": "2", "redcap_event_name": "visit_1_arm_1", "maristat": "2"}]'  # accepts int or str
# >> HTTP Status: 200
# >> JSON Result: ['1', '2']
# >> Note: The result ['1', '2'] is an array of IDs whose records were affected by successful data import.

# -- Bad JSON: Event not defined
json_data_bad1: str = '[{"ptid": "1", "redcap_event_name": "visit_11_arm_1", "maristat": 1},' \
                      '{"ptid": "2", "redcap_event_name": "visit_12_arm_1", "maristat": 2}]'
# >> HTTP Status: 400
# >> JSON Result: {'error': 'The following values of redcap_event_name are invalid: visit_11_arm_1, visit_12_arm_1'}
# >> Note: Plain English. Doesn't get much better than that.

# -- Bad JSON: No field provided
json_data_bad2: str = '[{"ptid": "1", "redcap_event_name": "visit_1_arm_1"},' \
                      '{"ptid": "2", "redcap_event_name": "visit_1_arm_1"}]'
# >> HTTP Status: 200
# >> JSON Result: ['1', '2']
# >> Note: There's no error, but no data is imported.

# -- Bad JSON: No `redcap_event_name` field/values provided
json_data_bad3: str = '[{"ptid": "1", "maristat": "4"},' \
                      '{"ptid": "2", "maristat": "4"}]'
# >> HTTP Status: 200
# >> JSON Result: ['1', '2']
# >> Note: There's no error b/c apparently REDCap defaults to the first longitudinal event,
#          i.e., "redcap_event_name": "visit_1_arm_1".

# -- Bad JSON: Nonexistent field/variable
json_data_bad4: str = '[{"ptid": "1", "redcap_event_name": "visit_1_arm_1", "foo": "bar"},' \
                      '{"ptid": "2", "redcap_event_name": "visit_1_arm_1", "baz": "qux"}]'
# >> HTTP Status: 400
# >> JSON Result: {'error': 'The following fields were not found in the project as real data fields: foo, baz'}
# Note: Plain English.

# -- Bad JSON: Invalid values for a given field
json_data_bad5: str = '[{"ptid": "1", "redcap_event_name": "visit_1_arm_1", "maristat": "01234"},' \
                      '{"ptid": "2", "redcap_event_name": "visit_1_arm_1", "maristat": "56789"}]'
# >> HTTP Status: 400
# >> JSON Result: {'error': '"1","maristat","01234","The value is not a valid category for maristat"\n
#                  "2","maristat","56789","The value is not a valid category for maristat"'}
# Note: Plain English.


request_dict: Dict[str, str] = {
    'token': redcap_project_token,
    'content': "record",
    'format': "json",  # "xml" (default), "csv", "json", "odm"
    'type': "flat",  # "flat" (default), "eav"
    'forceAutoNumber': "false",  # "false" (default), "true"
    'overwriteBehavior': "normal",  # "normal" (default), "overwrite"
    'data': "",
    'returnContent': "ids",  # "count" (default), "ids", "auto_ids"
    'returnFormat': "json"  # "json" (default), "csv", "xml"
}

json_data_list: List[str] = [
    json_data_good,
    json_data_bad1,
    json_data_bad2,
    json_data_bad3,
    json_data_bad4,
    json_data_bad5,
]

for json_data in json_data_list:

    request_dict['data'] = json_data
    r = requests.post(redcap_api_url, data=request_dict, verify=False)

    print(f"JSON String: {json_data}")
    print(f"HTTP Status: {str(r.status_code)}")
    print(f"JSON Result: {r.json()}\n")
