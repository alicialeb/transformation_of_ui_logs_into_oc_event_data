import json
import pandas as pd

# <editor-fold desc="ID Dictionaries">
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
# </editor-fold>

def calculate_precision_recall_f1(tp, fp, fn):
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    f1_score = 2 * ((precision * recall) / (precision + recall))
    return precision, recall, f1_score


def compare_events(events_truth, events_auto, id_dict):
    # counting true positives (tp), false positives (fp), and false negative (fn) of different labels
    activity_tp = 0 # true positives in activities -> TP: match
    activity_fp = 0 # false positives in activities -> FP: included in auto but missing in truth
    activity_fn = 0 # false negatives in activities -> FN: included in truth but missing in auto

    main_obj_tp = 0
    main_obj_fp = 0
    main_obj_fn = 0

    vmap_tp = 0
    vmap_fp = 0
    vmap_fn = 0

    umap_tp = 0
    umap_fp = 0
    umap_fn = 0

    pmap_tp = 0
    pmap_fp = 0
    pmap_fn = 0

    maps_tp = 0
    maps_fp = 0
    maps_fn = 0

    for event_key_truth, event_labels_truth in events_truth.items():
        if event_key_truth in id_dict:
            event_key_auto = id_dict[event_key_truth]
            event_labels_auto = events_auto[event_key_auto]

            # activities
            if str(event_labels_truth["activity"]).lower() == str(event_labels_auto["activity"]).lower():
                activity_tp += 1
            else:
                if not pd.isna(event_labels_truth["activity"]):
                    activity_fn += 1
                if not pd.isna(event_labels_auto["activity"]):
                    activity_fp += 1

            # main objects
            if str(event_labels_truth["main object"]).lower() == str(event_labels_auto["main object"]).lower():
                main_obj_tp += 1
            else:
                if not pd.isna(event_labels_truth["main object"]):
                    main_obj_fn += 1
                if not pd.isna(event_labels_auto["main object"]):
                    main_obj_fp += 1

            # vmap
            vmap_truth = event_labels_truth["vmap"]
            vmap_auto = event_labels_auto["vmap"]
            for label_truth, value_truth in vmap_truth.items():
                if label_truth in vmap_auto and vmap_auto[label_truth] == value_truth:
                    vmap_tp += 1
                    maps_tp += 1
                else:
                    vmap_fn += 1
                    maps_fn += 1
            # Check for any additional key-value pairs in automatically generated vmap
            for label_auto, value_auto in vmap_auto.items():
                if label_auto not in vmap_truth:
                    vmap_fp += 1
                    maps_fp += 1

            # umap
            umap_truth = event_labels_truth["umap"]
            umap_auto = event_labels_auto["umap"]
            set_truth = set(map(str.lower, umap_truth))
            set_auto = set(map(str.lower, umap_auto))
            # find values that match between umap_truth and umap_auto
            matches = set_truth & set_auto
            umap_tp += len(matches)
            maps_tp += len(matches)
            # find values in umap_truth but not in umap_auto
            only_in_truth = set_truth - set_auto
            umap_fn += len(only_in_truth)
            maps_fn += len(only_in_truth)
            # find values in umap_auto but not in umap_truth
            only_in_auto = set_auto - set_truth
            umap_fp += len(only_in_auto)
            maps_fp += len(only_in_auto)

            # pmap
            pmap_truth = event_labels_truth["pmap"]
            pmap_auto = event_labels_auto["pmap"]
            set_truth = set(map(str.lower, pmap_truth))
            set_auto = set(map(str.lower, pmap_auto))
            # find values that match between pmap_truth and pmap_auto
            matches = set_truth & set_auto
            pmap_tp += len(matches)
            maps_tp += len(matches)
            # find values in pmap_truth but not in pmap_auto
            only_in_truth = set_truth - set_auto
            pmap_fn += len(only_in_truth)
            maps_fn += len(only_in_truth)
            # find values in pmap_auto but not in pmap_truth
            only_in_auto = set_auto - set_truth
            pmap_fp += len(only_in_auto)
            maps_fp += len(only_in_auto)

        else:
            # count values and add to fn
            if not pd.isna(event_labels_truth["activity"]):
                activity_fn += 1

            if not pd.isna(event_labels_truth["main object"]):
                main_obj_fn += 1

            inner_dict = event_labels_truth["vmap"]
            vmap_fn += len(inner_dict.keys()) # count values included in value map
            maps_fn += len(inner_dict.keys())

            umap_fn += len(event_labels_truth["umap"])  # count values included in the list umap
            maps_fn += len(event_labels_truth["umap"])

            pmap_fn += len(event_labels_truth["pmap"])  # count values included in the list pmap
            maps_fn += len(event_labels_truth["pmap"])

    for event_key_auto, event_labels_auto in events_auto.items():
        if event_key_auto not in id_dict.values():
            # count values and add to fp
            if not pd.isna(event_labels_auto["activity"]):
                activity_fp += 1

            if not pd.isna(event_labels_auto["main object"]):
                main_obj_fp += 1

            inner_dict = event_labels_auto["vmap"]
            vmap_fp += len(inner_dict.keys())  # count values included in value map
            maps_fp += len(inner_dict.keys())

            umap_fp += len(event_labels_auto["umap"])  # count values included in the list umap
            maps_fp += len(event_labels_auto["umap"])

            pmap_fp += len(event_labels_auto["pmap"])  # count values included in the list pmap
            maps_fp += len(event_labels_auto["pmap"])

    # calculate scores
    event_activity_precision, event_activity_recall, event_activity_f1 = calculate_precision_recall_f1(activity_tp,
                                                                                                       activity_fp,
                                                                                                       activity_fn)
    event_main_obj_precision, event_main_obj_recall, event_main_obj_f1 = calculate_precision_recall_f1(main_obj_tp,
                                                                                                       main_obj_fp,
                                                                                                       main_obj_fn)
    event_vmap_precision, event_vmap_recall, event_vmap_f1 = calculate_precision_recall_f1(vmap_tp, vmap_fp, vmap_fn)
    event_umap_precision, event_umap_recall, event_umap_f1 = calculate_precision_recall_f1(umap_tp, umap_fp, umap_fn)
    event_pmap_precision, event_pmap_recall, event_pmap_f1 = calculate_precision_recall_f1(pmap_tp, pmap_fp, pmap_fn)
    event_maps_precision, event_maps_recall, event_maps_f1 = calculate_precision_recall_f1(maps_tp, maps_fp, maps_fn)

    return event_activity_precision, event_activity_recall, event_activity_f1, event_main_obj_precision, event_main_obj_recall, event_main_obj_f1, event_vmap_precision, event_vmap_recall, event_vmap_f1,  event_umap_precision, event_umap_recall, event_umap_f1, event_pmap_precision, event_pmap_recall, event_pmap_f1, event_maps_precision, event_maps_recall, event_maps_f1


# read the contents of the JSON files
with open(r'C:\Users\Besitzer\Documents\Master\Thesis\Code\json_example.json', 'r') as file1:
    json_truth = file1.read()

with open(r'C:\Users\Besitzer\Documents\Master\Thesis\Code\oc_example_ui_log.json', 'r') as file2:
    json_auto = file2.read()

data_truth = json.loads(json_truth)
data_auto = json.loads(json_auto)

events_truth = data_truth["events"]
ui_objects_truth = data_truth["ui_objects"]
process_objects_truth = data_truth["process_objects"]

events_auto = data_auto["events"]
ui_objects_auto = data_auto["ui_objects"]
process_objects_auto = data_auto["process_objects"]

event_activity_precision, event_activity_recall, event_activity_f1, event_main_obj_precision, event_main_obj_recall, event_main_obj_f1, event_vmap_precision, event_vmap_recall, event_vmap_f1,  event_umap_precision, event_umap_recall, event_umap_f1, event_pmap_precision, event_pmap_recall, event_pmap_f1, event_maps_precision, event_maps_recall, event_maps_f1 = compare_events(events_truth, events_auto, id_dict_example_ui_log)

event_precision = (event_activity_precision + event_main_obj_precision + event_maps_precision) / 3
event_recall = (event_activity_recall + event_main_obj_recall + event_maps_recall) / 3
event_f1 = (event_activity_f1 + event_main_obj_f1 + event_maps_f1) / 3

print("Events:")
print(f'-F1-Score: {event_f1}')
print(f'-Precision: {event_precision}')
print(f'-Recall: {event_recall}')
print()
print("-Activities:")
print(f'--F1-Score: {event_activity_f1}')
print(f'--Precision: {event_activity_precision}')
print(f'--Recall: {event_activity_recall}')
print()
print("-Main UI Objects:")
print(f'--F1-Score: {event_main_obj_f1}')
print(f'--Precision: {event_main_obj_precision}')
print(f'--Recall: {event_main_obj_recall}')
print()
print("-Maps:")
print(f'--F1-Score: {event_maps_f1}')
print(f'--Precision: {event_maps_precision}')
print(f'--Recall: {event_maps_recall}')
print()
print("--vmap:")
print(f'---F1-Score: {event_vmap_f1}')
print(f'---Precision: {event_vmap_precision}')
print(f'---Recall: {event_vmap_recall}')
print()
print("--umap:")
print(f'---F1-Score: {event_umap_f1}')
print(f'---Precision: {event_umap_precision}')
print(f'---Recall: {event_umap_recall}')
print()
print("--pmap:")
print(f'---F1-Score: {event_pmap_f1}')
print(f'---Precision: {event_pmap_precision}')
print(f'---Recall: {event_pmap_recall}')
