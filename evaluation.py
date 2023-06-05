# TODO: compare automatically generated json file with the manually generated one
import json

import pandas as pd


def count_label_values(element):
    count = 0
    for label, values in element.items():
        if isinstance(values, list):
            for value in values:
                count += 1
        elif isinstance(values, dict):
            for value in values.values():
                count += 1
        elif not pd.isna(values):
            count += 1
    return count

def compare_elements(elements_1, elements_2, id_dict):
    # Compare events
    number_elements_1 = len(elements_1)
    number_elements_2 = len(elements_2)

    element_amount_score = number_elements_2 / number_elements_1
    element_score_dict = {}

    for element_key_1, element_labels_1 in elements_1.items():
        if element_key_1 in id_dict:
            element_key_2 = id_dict[element_key_1]
            element_labels_2 = elements_2[element_key_2]
        else:
            break

        matches = 0
        total_values_1 = count_label_values(element_labels_1)
        total_values_2 = count_label_values(element_labels_2)

        for label, value_1 in element_labels_1.items():
            value_2 = element_labels_2[label]
            if isinstance(value_1, list) and isinstance(value_2, list):
                if any(val.lower() in [item.lower() for item in value_2] for val in value_1):
                    matches += 1
            elif isinstance(value_1, dict) and isinstance(value_2, dict):
                if any(value_1.get(key).lower() == value_2.get(key).lower() if value_1.get(
                        key) is not None and value_2.get(key) is not None else False for key in value_1.keys()):
                    matches += 1
            elif value_2.lower() == value_1.lower():
                matches += 1

        event_score = matches / total_values_1
        element_score_dict.setdefault(element_key_1, event_score)

    sum_element_scores = 0
    for score in element_score_dict.values():
        sum_element_scores = sum_element_scores + score

    element_scores = sum_element_scores / len(id_dict)

    element_precision = (element_amount_score + element_scores) / 2

    return element_precision

def compare_json(json_1, json_2, id_dict):
    data_1 = json.loads(json_1)
    data_2 = json.loads(json_2)

    events_1 = data_1["events"]
    ui_objects_1 = data_1["ui_objects"]
    process_objects_1 = data_1["process_objects"]

    events_2 = data_2["events"]
    ui_objects_2 = data_2["ui_objects"]
    process_objects_2 = data_2["process_objects"]

    event_precision = compare_elements(events_1, events_2, id_dict)
    ui_object_precision = compare_elements(ui_objects_1, ui_objects_2, id_dict)
    process_object_precision = compare_elements(process_objects_1, process_objects_2, id_dict)

    file_precision = (event_precision + ui_object_precision + process_object_precision) / 3

    return file_precision, event_precision, ui_object_precision, process_object_precision


id_dict_example_ui_log = {
    "event_1": "event_1",
    "event_2": "event_2",
    "event_3": "event_3",
    "event_4": "event_4",
    "event_5": "event_5",
    "event_6": "event_6",
    "event_7": "event_7",
    "event_8": "event_8",
    "event_9": "event_9",
    "event_10": "event_10",
    "event_11": "event_11",
    "event_12": "event_12",
    "event_13": "event_13",
    "event_14": "event_14",
    "event_15": "event_15",
    "event_16": "event_16",
    "event_17": "event_17",
    "event_18": "event_18",
    "event_19": "event_19",
    "event_20": "event_20",
    "event_21": "event_21",
    "event_22": "event_22",
    "event_23": "event_23",
    "event_24": "event_24",
    "event_25": "event_25",
    "event_26": "event_26",
    "event_27": "event_27",
    "event_28": "event_28",
    "link_1": "link_1",
    "link_2": "link_2",
    "link_3": "link_3",
    "value_1": "value_1",
    "value_2": "value_2",
    "value_3": "value_3",
    "value_4": "value_4",
    "value_5": "value_5",
    "value_6": "value_6",
    "button_1": "button_1",
    "button_2": "button_2",
    "button_3": "button_3",
    "application_1": "application_1",
    "application_2": "application_2",
    "application_3": "application_3",
    "user_1": "user_1"
}

# read the contents of the JSON files
with open(r'C:\Users\Besitzer\Documents\Master\Thesis\Code\json_example.json', 'r') as file1:
    json_gold_standard = file1.read()

with open(r'C:\Users\Besitzer\Documents\Master\Thesis\Code\oc_example_ui_log.json', 'r') as file2:
    json_auto_created = file2.read()

# call the compare_json method with the file contents
file_precision, event_precision, ui_object_precision, process_object_precision = compare_json(json_gold_standard , json_auto_created, id_dict_example_ui_log)

print(f'File precision: {file_precision}')
print(f'Event precision: {event_precision}')
print(f'UI object precision: {ui_object_precision}')
print(f'Process object precision: {process_object_precision}')