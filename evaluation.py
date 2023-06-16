import json
import pandas as pd

# <editor-fold desc="ID Dictionaries">
id_dict_login_ui_log = {
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

id_dict_student_record = {
    'event_1': 'event_1',
    'event_2': 'event_2',
    'event_3': 'event_3',
    'event_4': 'event_4',
    'event_5': 'event_5',
    'event_6': 'event_6',
    'event_7': 'event_7',
    'event_8': 'event_8',
    'event_9': 'event_9',
    'event_10': 'event_10',
    'event_11': 'event_11',
    'event_12': 'event_12',
    'event_13': 'event_13',
    'event_14': 'event_14',
    'event_15': 'event_15',
    'event_16': 'event_16',
    'event_17': 'event_17',
    'event_18': 'event_18',
    'event_19': 'event_19',
    'event_20': 'event_20',
    'event_21': 'event_21',
    'event_22': 'event_22',
    'event_23': 'event_23',
    'event_24': 'event_24',
    'event_25': 'event_25',
    'event_26': 'event_26',
    'event_27': 'event_27',
    'event_28': 'event_28',
    'event_29': 'event_29',
    'event_30': 'event_30',
    'event_31': 'event_31',
    'event_32': 'event_32',
    'event_33': 'event_33',
    'event_34': 'event_34',
    'event_35': 'event_35',
    'event_36': 'event_36',
    'event_37': 'event_37',
    'event_38': 'event_38',
    'event_39': 'event_39',
    'event_40': 'event_40',
    'event_41': 'event_41',
    'event_42': 'event_42',
    'event_43': 'event_43',
    'event_44': 'event_44',
    'event_45': 'event_45',
    'event_46': 'event_46',
    'event_47': 'event_47',
    'event_48': 'event_48',
    'event_49': 'event_49',
    'event_50': 'event_50',
    'event_51': 'event_51',
    'event_52': 'event_52',
    'event_53': 'event_53',
    'event_54': 'event_54',
    'event_55': 'event_55',
    'event_56': 'event_56',
    'event_57': 'event_57',
    'event_58': 'event_58',
    'event_59': 'event_59',
    'event_60': 'event_60',
    'event_61': 'event_61',
    'event_62': 'event_62',
    'event_63': 'event_63',
    'event_64': 'event_64',
    'event_65': 'event_65',
    'event_66': 'event_66',
    'event_67': 'event_67',
    'event_68': 'event_68',
    'event_69': 'event_69',
    'event_70': 'event_70',
    'event_71': 'event_71',
    'event_72': 'event_72',
    'event_73': 'event_73',
    'event_74': 'event_74',
    'event_75': 'event_75',
    'event_76': 'event_76',
    'event_77': 'event_77',
    'event_78': 'event_78',
    'event_79': 'event_79',
    'event_80': 'event_80',
    'event_81': 'event_81',
    'event_82': 'event_82',
    'event_83': 'event_83',
    'event_84': 'event_84',
    'event_85': 'event_85',
    'event_86': 'event_86',
    'event_87': 'event_87',
    'event_88': 'event_88',
    'event_89': 'event_89',
    'event_90': 'event_90',
    'event_91': 'event_91',
    'event_92': 'event_92',
    'event_93': 'event_93',
    'event_94': 'event_94',
    'event_95': 'event_95',
    'event_96': 'event_96',
    'event_97': 'event_97',
    'event_98': 'event_98',
    'event_99': 'event_99',
    'event_100': 'event_100',
    'event_101': 'event_101',
    'event_102': 'event_102',
    'event_103': 'event_103',
    'event_104': 'event_104',
    'event_105': 'event_105',
    'event_106': 'event_106',
    'event_107': 'event_107',
    'event_108': 'event_108',
    'event_109': 'event_109',
    'event_110': 'event_110',
    'event_111': 'event_111',
    'event_112': 'event_112',
    'event_113': 'event_113',
    'event_114': 'event_114',
    'event_115': 'event_115',
    'event_116': 'event_116',
    'event_117': 'event_117',
    'event_118': 'event_118',
    'event_119': 'event_119',
    'event_120': 'event_120',
    'event_121': 'event_121',
    'event_122': 'event_122',
    'link_1': 'link_1',
    'website_1': 'website_1',
    'file_1': 'file_1',
    'sheet_1': 'sheet_1',
    'checkbox_1': 'checkbox_1',
    'button_1': 'button_1',
    'application_1': 'application_1',
    'application_2': 'application_2',
    'user_1': 'user_1',
    'unknown_1': 'unknown_1',
    'unknown_2': 'unknown_2',
    'unknown_3': 'unknown_3',
    'unknown_4': 'unknown_4',
    'unknown_5': 'unknown_5',
    'unknown_6': 'unknown_6',
    'unknown_7': 'unknown_7',
    'unknown_8': 'unknown_8',
    'unknown_9': 'unknown_9',
    'unknown_10': 'unknown_10',
    'cell_1': 'cell_1',
    'cell_2': 'cell_2',
    'cell_3': 'cell_3',
    'cell_4': 'cell_4',
    'cell_5': 'cell_5',
    'cell_6': 'cell_6',
    'cell_7': 'cell_7',
    'cell_8': 'cell_8',
    'cell_9': 'cell_9',
    'cell_10': 'cell_10',
    'cell_11': 'cell_11',
    'cell_12': 'cell_12',
    'cell_13': 'cell_13',
    'cell_14': 'cell_14',
    'cell_15': 'cell_15',
    'cell_16': 'cell_16',
    'cell_17': 'cell_17',
    'cell_18': 'cell_18',
    'cell_19': 'cell_19',
    'cell_20': 'cell_20',
    'cell_21': 'cell_21',
    'cell_22': 'cell_22',
    'cell_23': 'cell_23',
    'cell_24': 'cell_24',
    'cell_25': 'cell_25',
    'cell_26': 'cell_26',
    'cell_27': 'cell_27',
    'cell_28': 'cell_28',
    'field_1': 'field_1',
    'field_2': 'field_2',
    'field_3': 'field_3',
    'field_4': 'field_4',
    'field_5': 'field_5',
    'field_6': 'field_6',
    'field_7': 'field_7',
    'field_8': 'field_8',
    'field_9': 'field_9'
}
# </editor-fold>

def calculate_precision_recall_f1(tp, fp, fn):
    try:
        precision = tp / (tp + fp)
    except ZeroDivisionError:
        precision = 0

    try:
        recall = tp / (tp + fn)
    except ZeroDivisionError:
        recall = 0

    try:
        f1_score = 2 * ((precision * recall) / (precision + recall))
    except ZeroDivisionError:
        f1_score = 0

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

    event_tp = 0
    event_fp = 0
    event_fn = 0

    for event_key_truth, event_labels_truth in events_truth.items():

        # set local variables to zero, so it can be decided if the entire event is a tp, fn, or fp
        activity_fp_local = 0
        activity_fn_local = 0
        main_obj_fp_local = 0
        main_obj_fn_local = 0
        maps_fp_local = 0
        maps_fn_local = 0

        if event_key_truth in id_dict:
            event_key_auto = id_dict[event_key_truth]
            event_labels_auto = events_auto[event_key_auto]

            # activities
            if str(event_labels_truth["activity"]).lower() == str(event_labels_auto["activity"]).lower():
                activity_tp += 1
            else:
                if not pd.isna(event_labels_truth["activity"]):
                    activity_fn += 1
                    activity_fn_local += 1
                if not pd.isna(event_labels_auto["activity"]):
                    activity_fp += 1
                    activity_fp_local += 1

            # main objects
            if str(event_labels_truth["main object"]).lower() == str(event_labels_auto["main object"]).lower():
                main_obj_tp += 1
            else:
                if not pd.isna(event_labels_truth["main object"]):
                    main_obj_fn += 1
                    main_obj_fn_local += 1
                if not pd.isna(event_labels_auto["main object"]):
                    main_obj_fp += 1
                    main_obj_fp_local += 1

            # vmap
            vmap_truth = event_labels_truth["vmap"]
            vmap_auto = event_labels_auto["vmap"]

            # check if both vmaps are empty
            if not vmap_truth and not vmap_auto:
                vmap_tp += 1
                maps_tp += 1

            for label_truth, value_truth in vmap_truth.items():
                # check if key-value pairs match
                if label_truth in vmap_auto and str(vmap_auto[label_truth]).lower() == str(value_truth).lower():
                    vmap_tp += 1
                    maps_tp += 1
                else:
                    vmap_fn += 1
                    maps_fn += 1
                    maps_fn_local += 1
            # check for any additional key-value pairs in automatically generated vmap
            for label_auto, value_auto in vmap_auto.items():
                if label_auto not in vmap_truth:
                    vmap_fp += 1
                    maps_fp += 1
                    maps_fp_local += 1

            # umap
            umap_truth = event_labels_truth["umap"]
            umap_auto = event_labels_auto["umap"]

            # check if both umaps are empty
            if not umap_truth and not umap_auto:
                umap_tp += 1
                maps_tp += 1

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
            maps_fn_local += len(only_in_truth)
            # find values in umap_auto but not in umap_truth
            only_in_auto = set_auto - set_truth
            umap_fp += len(only_in_auto)
            maps_fp += len(only_in_auto)
            maps_fp_local += len(only_in_auto)

            # pmap
            pmap_truth = event_labels_truth["pmap"]
            pmap_auto = event_labels_auto["pmap"]

            # check if both pmaps are empty
            if not pmap_truth and not pmap_auto:
                pmap_tp += 1
                maps_tp += 1

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
            maps_fn_local += len(only_in_truth)
            # find values in pmap_auto but not in pmap_truth
            only_in_auto = set_auto - set_truth
            pmap_fp += len(only_in_auto)
            maps_fp += len(only_in_auto)
            maps_fp_local += len(only_in_auto)

        else:
            # count values and add to fn
            if not pd.isna(event_labels_truth["activity"]):
                activity_fn += 1
                activity_fn_local += 1

            if not pd.isna(event_labels_truth["main object"]):
                main_obj_fn += 1
                main_obj_fn_local += 1

            inner_dict = event_labels_truth["vmap"]
            vmap_fn += len(inner_dict.keys()) # count values included in value map
            maps_fn += len(inner_dict.keys())
            maps_fn_local += len(inner_dict.keys())

            umap_fn += len(event_labels_truth["umap"])  # count values included in the list umap
            maps_fn += len(event_labels_truth["umap"])
            maps_fn_local += len(event_labels_truth["umap"])

            pmap_fn += len(event_labels_truth["pmap"])  # count values included in the list pmap
            maps_fn += len(event_labels_truth["pmap"])
            maps_fn_local += len(event_labels_truth["pmap"])

        # count macro TP
        if activity_fn_local == 0 and activity_fp_local == 0 and main_obj_fn_local == 0 and main_obj_fp_local == 0 and maps_fn_local == 0 and maps_fp_local == 0:
            event_tp += 1

        else:
            if activity_fn_local != 0 or main_obj_fn_local != 0 or maps_fn_local != 0:
                event_fn += 1
            if activity_fp_local != 0 or main_obj_fp_local != 0 or maps_fp_local != 0:
                event_fp += 1

    for event_key_auto, event_labels_auto in events_auto.items():

        # set local variables to zero, so it can be decided if the entire event is a tp, fn, or fp
        activity_fp_local = 0
        activity_fn_local = 0
        main_obj_fp_local = 0
        main_obj_fn_local = 0
        maps_fp_local = 0
        maps_fn_local = 0

        # cases where an event is in the automated json but not in ground truth json
        if event_key_auto not in id_dict.values():
            # count values and add to fp
            if not pd.isna(event_labels_auto["activity"]):
                activity_fp += 1
                activity_fp_local += 1

            if not pd.isna(event_labels_auto["main object"]):
                main_obj_fp += 1
                main_obj_fp_local += 1

            inner_dict = event_labels_auto["vmap"]
            vmap_fp += len(inner_dict.keys())  # count values included in value map
            maps_fp += len(inner_dict.keys())
            maps_fp_local += len(inner_dict.keys())

            umap_fp += len(event_labels_auto["umap"])  # count values included in the list umap
            maps_fp += len(event_labels_auto["umap"])
            maps_fp_local += len(event_labels_auto["umap"])

            pmap_fp += len(event_labels_auto["pmap"])  # count values included in the list pmap
            maps_fp += len(event_labels_auto["pmap"])
            maps_fp_local += len(event_labels_auto["pmap"])

            # count macro TP
            if activity_fn_local != 0 or main_obj_fn_local != 0 or maps_fn_local != 0:
                event_fn += 1
            if activity_fp_local != 0 or main_obj_fp_local != 0 or maps_fp_local != 0:
                event_fp += 1


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
    event_macro_precision, event_macro_recall, event_macro_f1 = calculate_precision_recall_f1(event_tp, event_fp, event_fn)

    return (
        event_activity_precision, event_activity_recall, event_activity_f1,
        event_main_obj_precision, event_main_obj_recall, event_main_obj_f1,
        event_vmap_precision, event_vmap_recall, event_vmap_f1,
        event_umap_precision, event_umap_recall, event_umap_f1,
        event_pmap_precision, event_pmap_recall, event_pmap_f1,
        event_maps_precision, event_maps_recall, event_maps_f1,
        event_macro_precision, event_macro_recall, event_macro_f1
    )

def compare_ui_objects(ui_obj_truth, ui_obj_auto, id_dict):
    # counting true positives (tp), false positives (fp), and false negative (fn) of different labels
    type_tp = 0
    type_fp = 0
    type_fn = 0

    cmap_tp = 0
    cmap_fp = 0
    cmap_fn = 0

    vmap_tp = 0
    vmap_fp = 0
    vmap_fn = 0

    part_of_tp = 0
    part_of_fp = 0
    part_of_fn = 0

    maps_tp = 0
    maps_fp = 0
    maps_fn = 0

    ui_obj_tp = 0
    ui_obj_fp = 0
    ui_obj_fn = 0

    for ui_obj_key_truth, ui_obj_labels_truth in ui_obj_truth.items():

        # set local variables to zero, so it can be decided if the entire object is a tp, fn, or fp
        type_fp_local = 0
        type_fn_local = 0
        maps_fp_local = 0
        maps_fn_local = 0

        if ui_obj_key_truth in id_dict:
            ui_obj_key_auto = id_dict[ui_obj_key_truth]
            ui_obj_labels_auto = ui_obj_auto[ui_obj_key_auto]

            # object type
            if str(ui_obj_labels_truth["type"]).lower() == str(ui_obj_labels_auto["type"]).lower():
                type_tp += 1
            else:
                if not pd.isna(ui_obj_labels_truth["type"]):
                    type_fn += 1
                    type_fn_local += 1
                if not pd.isna(ui_obj_labels_auto["type"]):
                    type_fp += 1
                    type_fp_local += 1

            # cmap
            cmap_truth = ui_obj_labels_truth["cmap"]
            cmap_auto = ui_obj_labels_auto["cmap"]

            # check if both cmaps are empty
            if not cmap_truth and not cmap_auto:
                cmap_tp += 1
                maps_tp += 1

            for label_truth, value_truth in cmap_truth.items():
                if label_truth in cmap_auto and str(cmap_auto[label_truth]).lower() == str(value_truth).lower():
                    cmap_tp += 1
                    maps_tp += 1
                else:
                    cmap_fn += 1
                    maps_fn += 1
                    maps_fn_local += 1
            # check for any additional key-value pairs in automatically generated cmap
            for label_auto, value_auto in cmap_auto.items():
                if label_auto not in cmap_truth:
                    cmap_fp += 1
                    maps_fp += 1
                    maps_fp_local += 1

            # vmap
            vmap_truth = ui_obj_labels_truth["vmap"]
            vmap_auto = ui_obj_labels_auto["vmap"]

            # check if both vmaps are empty
            if not vmap_truth and not vmap_auto:
                vmap_tp += 1
                maps_tp += 1

            for label_truth, value_truth in vmap_truth.items():
                if label_truth in vmap_auto and str(vmap_auto[label_truth]).lower() == str(value_truth).lower():
                    vmap_tp += 1
                    maps_tp += 1
                else:
                    vmap_fn += 1
                    maps_fn += 1
                    maps_fn_local += 1
            # Check for any additional key-value pairs in automatically generated vmap
            for label_auto, value_auto in vmap_auto.items():
                if label_auto not in vmap_truth:
                    vmap_fp += 1
                    maps_fp += 1
                    maps_fp_local += 1

            # part_of
            part_of_truth = ui_obj_labels_truth["part of"]
            part_of_auto = ui_obj_labels_auto["part of"]

            # check if both part_of are empty
            if not part_of_truth and not part_of_auto:
                part_of_tp += 1
                maps_tp += 1

            set_truth = set(map(str.lower, part_of_truth))
            set_auto = set(map(str.lower, part_of_auto))

            # find values that match between part_of_truth and part_of_auto
            matches = set_truth & set_auto
            part_of_tp += len(matches)
            maps_tp += len(matches)
            # find values in part_of_truth but not in part_of_auto
            only_in_truth = set_truth - set_auto
            part_of_fn += len(only_in_truth)
            maps_fn += len(only_in_truth)
            maps_fn_local += len(only_in_truth)
            # find values in part_of_auto but not in part_of_truth
            only_in_auto = set_auto - set_truth
            part_of_fp += len(only_in_auto)
            maps_fp += len(only_in_auto)
            maps_fp_local += len(only_in_auto)

        else:
            # count values and add to fn
            if not pd.isna(ui_obj_labels_truth["type"]):
               type_fn += 1
               type_fn_local += 1

            inner_dict = ui_obj_labels_truth["cmap"]
            cmap_fn += len(inner_dict.keys())  # count values included in context attribute map
            maps_fn += len(inner_dict.keys())
            maps_fn_local += len(inner_dict.keys())

            inner_dict = ui_obj_labels_truth["vmap"]
            vmap_fn += len(inner_dict.keys()) # count values included in value attribute map
            maps_fn += len(inner_dict.keys())
            maps_fn_local += len(inner_dict.keys())

            part_of_fn += len(ui_obj_labels_truth["part of"])  # count values included in the list object map
            maps_fn += len(ui_obj_labels_truth["part of"])
            maps_fn_local += len(ui_obj_labels_truth["part of"])

        # count macro TP
        if type_fn == 0 and type_fp == 0 and maps_fn == 0 and maps_fp == 0:
            ui_obj_tp += 1

        else:
            if type_fn_local != 0 or maps_fn_local != 0:
                ui_obj_fn += 1
            if type_fp_local != 0 or maps_fp_local != 0:
                ui_obj_fp += 1

    for ui_obj_key_auto, ui_obj_labels_auto in ui_obj_auto.items():

        # set local variables to zero, so it can be decided if the entire object is a tp, fn, or fp
        type_fp_local = 0
        type_fn_local = 0
        maps_fp_local = 0
        maps_fn_local = 0

        if ui_obj_key_auto not in id_dict.values():
            # count values and add to fp
            if not pd.isna(ui_obj_labels_auto["type"]):
                type_fp += 1
                type_fp_local += 1

            inner_dict = ui_obj_labels_auto["cmap"]
            cmap_fp += len(inner_dict.keys())  # count values included in value map
            maps_fp += len(inner_dict.keys())
            maps_fp_local += len(inner_dict.keys())

            inner_dict = ui_obj_labels_auto["vmap"]
            vmap_fp += len(inner_dict.keys())  # count values included in value map
            maps_fp += len(inner_dict.keys())
            maps_fp_local += len(inner_dict.keys())

            part_of_fp += len(ui_obj_labels_auto["part of"])  # count values included in the list pmap
            maps_fp += len(ui_obj_labels_auto["part of"])
            maps_fp_local += len(ui_obj_labels_auto["part of"])

        if type_fn_local != 0 or maps_fn_local != 0:
            ui_obj_fn += 1
        if type_fp_local != 0 or maps_fp_local != 0:
            ui_obj_fp += 1

    # calculate scores
    ui_obj_type_precision, ui_obj_type_recall, ui_obj_type_f1 = calculate_precision_recall_f1(type_tp, type_fp, type_fn)
    ui_obj_cmap_precision, ui_obj_cmap_recall, ui_obj_cmap_f1 = calculate_precision_recall_f1(cmap_tp, cmap_fp, cmap_fn)
    ui_obj_vmap_precision, ui_obj_vmap_recall, ui_obj_vmap_f1 = calculate_precision_recall_f1(vmap_tp, vmap_fp, vmap_fn)
    ui_obj_part_of_precision, ui_obj_part_of_recall, ui_obj_part_of_f1 = calculate_precision_recall_f1(part_of_tp,
                                                                                                       part_of_fp,
                                                                                                       part_of_fn)
    ui_obj_maps_precision, ui_obj_maps_recall, ui_obj_maps_f1 = calculate_precision_recall_f1(maps_tp, maps_fp, maps_fn)
    ui_obj_macro_precision, ui_obj_macro_recall, ui_obj_macro_f1 = calculate_precision_recall_f1(ui_obj_tp, ui_obj_fp, ui_obj_fn)

    return (ui_obj_type_precision, ui_obj_type_recall, ui_obj_type_f1,
            ui_obj_cmap_precision, ui_obj_cmap_recall, ui_obj_cmap_f1,
            ui_obj_vmap_precision, ui_obj_vmap_recall, ui_obj_vmap_f1,
            ui_obj_part_of_precision, ui_obj_part_of_recall, ui_obj_part_of_f1,
            ui_obj_maps_precision, ui_obj_maps_recall, ui_obj_maps_f1,
            ui_obj_macro_precision, ui_obj_macro_recall, ui_obj_macro_f1)


def compare_process_objects(process_obj_truth, process_obj_auto, id_dict):
    # counting true positives (tp), false positives (fp), and false negative (fn) of different labels
    type_tp = 0
    type_fp = 0
    type_fn = 0

    amap_tp = 0
    amap_fp = 0
    amap_fn = 0

    process_obj_tp = 0
    process_obj_fp = 0
    process_obj_fn = 0

    for process_obj_key_truth, process_obj_labels_truth in process_obj_truth.items():

        # set local variables to zero, so it can be decided if the entire object is a tp, fn, or fp
        type_fp_local = 0
        type_fn_local = 0
        amap_fp_local = 0
        amap_fn_local = 0

        if process_obj_key_truth in id_dict:
            process_obj_key_auto = id_dict[process_obj_key_truth]
            process_obj_labels_auto = process_obj_auto[process_obj_key_auto]

            # object type
            if str(process_obj_labels_truth["type"]).lower() == str(process_obj_labels_auto["type"]).lower():
                type_tp += 1
            else:
                if not pd.isna(process_obj_labels_truth["type"]):
                    type_fn += 1
                    type_fn_local += 1
                if not pd.isna(process_obj_labels_auto["type"]):
                    type_fp += 1
                    type_fp_local += 1

            # amap
            amap_truth = process_obj_labels_truth["amap"]
            amap_auto = process_obj_labels_auto["amap"]

            # check if both part_of are empty
            if not amap_truth and not amap_auto:
                amap_tp += 1

            for label_truth, value_truth in amap_truth.items():
                if label_truth in amap_auto and str(amap_auto[label_truth]).lower() == str(value_truth).lower():
                    amap_tp += 1
                else:
                    amap_fn += 1
                    amap_fn_local += 1
            # check for any additional key-value pairs in automatically generated amap
            for label_auto, value_auto in amap_auto.items():
                if label_auto not in amap_truth:
                    amap_fp += 1
                    amap_fp_local += 1

        else:
            # count values and add to fn
            if not pd.isna(process_obj_labels_truth["type"]):
               type_fn += 1
               type_fn_local += 1

            inner_dict = process_obj_labels_truth["amap"]
            amap_fn += len(inner_dict.keys())  # count values included in attribute map
            amap_fn_local += len(inner_dict.keys())

        # count macro TP
        if type_fn_local == 0 and type_fp_local == 0 and amap_fn_local == 0 and amap_fp_local == 0:
            process_obj_tp += 1

        else:
            if type_fn_local != 0 or amap_fn_local != 0:
                process_obj_fn += 1
            if type_fp_local != 0 or amap_fp_local != 0:
                process_obj_fp += 1

    for process_obj_key_auto, process_obj_labels_auto in process_obj_auto.items():

        # set local variables to zero, so it can be decided if the entire object is a tp, fn, or fp
        type_fp_local = 0
        type_fn_local = 0
        amap_fp_local = 0
        amap_fn_local = 0

        if process_obj_key_auto not in id_dict.values():
            # count values and add to fp
            if not pd.isna(process_obj_labels_auto["type"]):
                type_fp += 1
                type_fp_local += 1

            inner_dict = process_obj_labels_auto["amap"]
            amap_fp += len(inner_dict.keys())  # count values included in value map
            amap_fp_local += len(inner_dict.keys())

        if type_fn_local != 0 or amap_fn_local != 0:
            process_obj_fn += 1
        if type_fp_local != 0 or amap_fp_local != 0:
            process_obj_fp += 1

    # calculate scores
    process_obj_type_precision, process_obj_type_recall, process_obj_type_f1 = calculate_precision_recall_f1(type_tp, type_fp, type_fn)
    process_obj_amap_precision, process_obj_amap_recall, process_obj_amap_f1 = calculate_precision_recall_f1(amap_tp, amap_fp, amap_fn)
    process_obj_macro_precision, process_obj_macro_recall, process_obj_macro_f1 = calculate_precision_recall_f1(process_obj_tp, process_obj_fp, process_obj_fn)


    return (
        process_obj_type_precision, process_obj_type_recall, process_obj_type_f1,
        process_obj_amap_precision, process_obj_amap_recall, process_obj_amap_f1,
        process_obj_macro_precision, process_obj_macro_recall, process_obj_macro_f1
    )


def calculate_scores(json_truth, json_auto, id_dict):
    data_truth = json.loads(json_truth)
    data_auto = json.loads(json_auto)

    events_truth = data_truth["events"]
    ui_objects_truth = data_truth["ui_objects"]
    process_objects_truth = data_truth["process_objects"]

    events_auto = data_auto["events"]
    ui_objects_auto = data_auto["ui_objects"]
    process_objects_auto = data_auto["process_objects"]

    # Events
    (event_activity_precision, event_activity_recall, event_activity_f1,
     event_main_obj_precision, event_main_obj_recall, event_main_obj_f1,
     event_vmap_precision, event_vmap_recall, event_vmap_f1,
     event_umap_precision, event_umap_recall, event_umap_f1,
     event_pmap_precision, event_pmap_recall, event_pmap_f1,
     event_maps_precision, event_maps_recall, event_maps_f1,
     event_macro_precision, event_macro_recall, event_macro_f1) = compare_events(events_truth, events_auto, id_dict)

    event_micro_precision = (event_activity_precision + event_main_obj_precision + event_maps_precision) / 3
    event_micro_recall = (event_activity_recall + event_main_obj_recall + event_maps_recall) / 3
    event_micro_f1 = (event_activity_f1 + event_main_obj_f1 + event_maps_f1) / 3

    # UI Objects
    (ui_obj_type_precision, ui_obj_type_recall, ui_obj_type_f1,
     ui_obj_cmap_precision, ui_obj_cmap_recall, ui_obj_cmap_f1,
     ui_obj_vmap_precision, ui_obj_vmap_recall, ui_obj_vmap_f1,
     ui_obj_part_of_precision, ui_obj_part_of_recall, ui_obj_part_of_f1,
     ui_obj_maps_precision, ui_obj_maps_recall, ui_obj_maps_f1,
     ui_obj_macro_precision, ui_obj_macro_recall, ui_obj_macro_f1) = compare_ui_objects(ui_objects_truth, ui_objects_auto, id_dict)

    ui_obj_micro_precision = (ui_obj_type_precision + ui_obj_maps_precision) / 2
    ui_obj_micro_recall = (ui_obj_type_recall + ui_obj_maps_recall) / 2
    ui_obj_micro_f1 = (ui_obj_type_f1 + ui_obj_maps_f1) / 2

    # Process Objects
    (process_obj_type_precision, process_obj_type_recall, process_obj_type_f1,
     process_obj_amap_precision, process_obj_amap_recall, process_obj_amap_f1,
     process_obj_macro_precision, process_obj_macro_recall, process_obj_macro_f1) = compare_process_objects(process_objects_truth, process_objects_auto, id_dict)

    process_obj_micro_precision = (process_obj_type_precision + process_obj_amap_precision) / 2
    process_obj_micro_recall = (process_obj_type_recall + process_obj_amap_recall) / 2
    process_obj_micro_f1 = (process_obj_type_f1 + process_obj_amap_f1) / 2

    # log scores micro
    log_micro_precision = (event_micro_precision + ui_obj_micro_precision + process_obj_micro_precision) / 3
    log_micro_recall = (event_micro_recall + ui_obj_micro_recall + process_obj_micro_recall) / 3
    log_micro_f1 = (event_micro_f1 + ui_obj_micro_f1 + process_obj_micro_f1) / 3

    # log scores micro without process object scores
    log_micro_precision_light = (event_micro_precision + ui_obj_micro_precision) / 2
    log_micro_recall_light = (event_micro_recall + ui_obj_micro_recall) / 2
    log_micro_f1_light = (event_micro_f1 + ui_obj_micro_f1) / 2

    # log scores macro
    log_macro_precision = (event_macro_precision + ui_obj_macro_precision + process_obj_macro_precision) / 3
    log_macro_recall = (event_macro_recall + ui_obj_macro_recall + process_obj_macro_recall) / 3
    log_macro_f1 = (event_macro_f1 + ui_obj_macro_f1 + process_obj_macro_f1) / 3

    # log scores macro without process object scores
    log_macro_precision_light = (event_macro_precision + ui_obj_macro_precision) / 2
    log_macro_recall_light = (event_macro_recall + ui_obj_macro_recall) / 2
    log_macro_f1_light = (event_macro_f1 + ui_obj_macro_f1) / 2

    # log_scores_df = pd.DataFrame([
    #     ["Log Scores Including Event, UI Object, and Process Object Scores:", "", "", ""],
    #     ["", "F1", "Precision", "Recall"],
    #     ["Macro", log_macro_f1, log_macro_precision, log_macro_recall],
    #     ["Micro", log_micro_f1, log_micro_precision, log_micro_recall],
    #     ["", "", "", ""],
    #     ["Log Scores without Process Object Scores:", "", "", ""],
    #     ["", "F1", "Precision", "Recall"],
    #     ["Macro", log_macro_f1_light, log_macro_precision_light, log_macro_recall_light],
    #     ["Micro", log_micro_f1_light, log_micro_precision_light, log_micro_recall_light]
    # ], columns=["", "", "", ""])
    #
    # event_scores_df = pd.DataFrame([
    #     ["Event Scores:", "", "", ""],
    #     ["", "F1", "Precision", "Recall"],
    #     ["Macro", event_macro_f1, event_macro_precision, event_macro_recall],
    #     ["Micro", event_micro_f1, event_micro_precision, event_micro_recall],
    #     ["", "", "", ""],
    #     ["Event Sub-Part Scores:", "", "", ""],
    #     ["", "F1", "Precision", "Recall"],
    #     ["Activities:", event_activity_f1, event_activity_precision, event_activity_recall],
    #     ["Main UI Objects:", event_main_obj_f1, event_main_obj_precision, event_main_obj_recall],
    #     ["Maps:", event_maps_f1, event_maps_precision, event_maps_recall],
    #     ["vmap:", event_vmap_f1, event_vmap_precision, event_vmap_recall],
    #     ["umap:", event_umap_f1, event_umap_precision, event_umap_recall],
    #     ["pmap:", event_pmap_f1, event_pmap_precision, event_pmap_recall]
    # ], columns=["", "", "", ""])
    #
    # ui_obj_scores_df = pd.DataFrame([
    #     ["UI Object Scores:", "", "", ""],
    #     ["", "F1", "Precision", "Recall"],
    #     ["Macro", ui_obj_macro_f1, ui_obj_macro_precision, ui_obj_macro_recall],
    #     ["Micro", ui_obj_micro_f1, ui_obj_micro_precision, ui_obj_micro_recall],
    #     ["", "", "", ""],
    #     ["UI Object Sub-Part Scores:", "", "", ""],
    #     ["", "F1", "Precision", "Recall"],
    #     ["Types:", ui_obj_type_f1, ui_obj_type_precision, ui_obj_type_recall],
    #     ["Maps:", ui_obj_maps_f1, ui_obj_maps_precision, ui_obj_maps_recall],
    #     ["cmap:", ui_obj_cmap_f1, ui_obj_cmap_precision, ui_obj_cmap_recall],
    #     ["vmap:", ui_obj_vmap_f1, ui_obj_vmap_precision, ui_obj_vmap_recall],
    #     ["part of:", ui_obj_part_of_f1, ui_obj_part_of_precision, ui_obj_part_of_recall]
    # ], columns=["", "", "", ""])
    #
    # process_obj_scores_df = pd.DataFrame([
    #     ["Process Object Scores:", "", "", ""],
    #     ["", "F1", "Precision", "Recall"],
    #     ["Macro", process_obj_macro_f1, process_obj_macro_precision, process_obj_macro_recall],
    #     ["Micro", process_obj_micro_f1, process_obj_micro_precision, process_obj_micro_recall],
    #     ["", "", "", ""],
    #     ["Process Object Sub-Part Scores:", "", "", ""],
    #     ["", "F1", "Precision", "Recall"],
    #     ["Types:", process_obj_type_f1, process_obj_type_precision, process_obj_type_recall],
    #     ["amap:", process_obj_amap_f1, process_obj_amap_precision, process_obj_amap_recall]
    # ], columns=["", "", "", ""])
    #
    # # Create an Excel writer object
    #
    # writer = pd.ExcelWriter('evaluation results/scores.xlsx', engine='xlsxwriter')
    #
    # # Write each data frame to a separate sheet in the Excel file
    # log_scores_df.to_excel(writer, sheet_name='Log Scores', index=False, header=False)
    # event_scores_df.to_excel(writer, sheet_name='Event Scores', index=False, header=False)
    # ui_obj_scores_df.to_excel(writer, sheet_name='UI Object Scores', index=False, header=False)
    # process_obj_scores_df.to_excel(writer, sheet_name='Process Object Scores', index=False, header=False)
    #
    # # Save and close the Excel file
    # writer.close()

    return log_micro_f1

def get_log_micro_f1():
    # read the contents of the JSON files
    with open(r'C:\Users\Besitzer\Documents\Master\Thesis\Code\ground truth files\json_login.json', 'r') as file1:
        json_truth = file1.read()

    with open(r'C:\Users\Besitzer\Documents\Master\Thesis\Code\output automated transformation\oc_login_ui_log.json', 'r') as file2:
        json_auto = file2.read()

    try:
        log_micro_f1 = calculate_scores(json_truth, json_auto, id_dict_login_ui_log)
    except KeyError:
        log_micro_f1 = 0

    return log_micro_f1

f1 = get_log_micro_f1()
print(f1)