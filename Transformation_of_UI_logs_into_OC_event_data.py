#!/usr/bin/env python
# coding: utf-8

# Assumptions: 
# - log is sorted by the timestamp starting with the earliest point in time.
# - if the log is already split into cases, the case id is in the first column of the log.
# - every UI log has some sort of event or activity column.
# - object types that cannot be recognized belong to the fourth level.

# <editor-fold desc="Imports">
import json
import copy

import numpy as np

from functions import *

# TODO: restructure code, so it can be run with one click and multiple different parameter settings
# call the import_log function to read a ui log chosen by the user
# log, file_path = import_log()

file_path = r'C:\Users\Besitzer\Documents\GitHub\master_thesis\Datasets\StudentRecord_preprocessed.csv'
log = pd.read_csv(file_path)

# file_path = r'C:\Users\Besitzer\Documents\GitHub\master_thesis\Datasets\example_ui_log - Copy.xlsx'
# log = pd.read_excel(file_path)

# import action label list as DataFrame taken from https://carbondesignsystem.com/guidelines/content/action-labels/ and
# supplemented with own ideas (confirm, login)
action_labels = pd.read_csv(r'C:\Users\Besitzer\Documents\GitHub\master_thesis\Datasets\action_labels.csv')

# TODO: search for other noun list, so process objects can be recognized
# import noun list extracted from wordNet as DataFrame
nouns = pd.read_csv(r'C:\Users\Besitzer\Documents\GitHub\master_thesis\Datasets\nouns_final.csv')
# </editor-fold>


# <editor-fold desc="Pre-defined Dictionaries and Lists">
# dictionary with pre-defined object types and their synonyms
ui_object_synonym = {
    'website': ['website', 'site', 'page', 'web page', 'webpage', 'url', 'link', 'href', 'browser', 'chrome', 'firefox',
                'opera', 'safari', 'microsoft edge'],
    'application': ['application', 'app', 'program', 'tool', 'system', 'excel', 'erp'],
    'file': ['file', 'document', 'workbook'],
    'sheet': ['sheet', 'page'],
    'field': ['field', 'cell', 'value'],
    'button': ['button'],
    'image': ['image', 'picture'],
    'checkbox': ['checkbox', 'check box']
}

# dictionary with pre-defined attribute types and their synonyms
attribute_synonym = {
    'url': ['url', 'web page', 'site', 'link', 'page', 'href'],
    'host name': ['host name', 'host'],
    'page name': ['page name', 'page title'],
    'application name': ['application name', 'application', 'app', 'program'],
    'file name': ['file name', 'file', 'document name', 'document title', 'document', 'workbook name', 'workbook title',
                  'workbook'],
    'sheet name': ['sheet name', 'sheet', 'page name', 'page'],
    'label': ['label', 'field name', 'tag'],
    'column': ['column', 'col'],
    'row': ['row', 'line'],
    'input value': ['input value', 'value', 'content'],
    'cell': ['cell']
}

# ui attribute type to object type mapping
att_to_obj_dict = {
    'website': ['url', 'host name', 'page name'],
    'application': ['application name'],
    'file': ['file name'],
    'sheet': ['sheet name'],
    'field': ['label', 'column', 'row', 'cell', 'input value'],
    'button': ['label'],
    'image': ['label']
}

# dictionary specifying the typical ui object hierarchy
object_hierarchy = {
    'obj_highest_level': ['website', 'application'],
    'obj_second_level': ['file'],
    'obj_third_level': ['sheet'],
    'obj_fourth_level': ['field', 'button', 'image', 'checkbox']
}

# object hierarchy levels; the next level below website is level 4
obj_highest_level = ['website', 'application']
obj_second_level = ['file']
obj_third_level = ['sheet']
obj_fourth_level = ['field', 'button', 'image']
# </editor-fold>


# <editor-fold desc="Ration Thresholds">
# TODO: optimize thresholds
# ration thresholds determining the ratio of unique values a column should hold
threshold_ui_obj = 0.15 # for ui object columns
threshold_act = 0.2 # for activity columns
threshold_cont_att = 0.5 # for context attribute columns
threshold_val_att = 1 - threshold_cont_att # for value attribute columns
threshold_timestamp = 1 # for timestamp column
threshold_compl = 0.95 # determines how complete a column should be
# </editor-fold>


# <editor-fold desc="Regular Expressions">
# regular expressions to find strings that match the given pattern
email_regex = '[^@]+@[^@]+\.[^@]+'
url_regex = '(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})'
timestamp_regex = '\d{4}[-.\/ ]\d{1,2}[-.\/ ]\d{1,2} \d{2}:\d{2}(:\d{2})?([-,* ]\d{3,4})?|(\d{1,2}[-.\/ ])?\d{1,2}[-.\/ ]\d{2,4} \d{2}:\d{2}(:\d{2})?([-,* ]\d{3,4})?|\d{4}[-.\/ ]\w{3}[-.\/ ]\d{1,2} \d{2}:\d{2}(:\d{2})?([-,* ]\d{3,4})?|\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z'
# </editor-fold>


# <editor-fold desc="Preprocessing">
# call function to delete case separation since it is not needed for this transformation
log = delete_cases(log)

# call function to remove empty columns
log = delete_empty_columns_and_rows(log)

# call function to remove duplicate columns from the log
log = remove_duplicate_columns(log)

# call function to unify the string formats e.g., by eliminating camel case
log = unify_string_format(log)

# call function to split column names written in camel case into separate words
log = split_title_camel_case(log)

# call function to replace 'nan' strings and empty strings with np.NaN
log = unify_nan_values(log)
# </editor-fold>

# call function to calculate the ratio of unique values/total values per column
ratio_dictionary = get_unique_value_ratio(log)

# call function to identify the event column of the ui log and move it to the first position 
log = find_event_column(log, ratio_dictionary, action_labels, threshold_act)

# call function to separate the activities from the object types in the events
log = extract_activity(log, 0)

# updated the uniqueness-ration dictionary since the columns changed
ratio_dictionary = get_unique_value_ratio(log)

# call function to calculate the completeness-ratio per column
col_compl_dict = get_column_completeness(log, threshold_compl)

# initialize list with all column indices
column_indices = list(range(len(log.columns)))

# call function to find columns that are constant (have the same value for all rows)
const_cols = find_constant_columns(log)

# call function to find columns that belong to the user rather than to any ui object
user_cols = find_user_related_cols(log)

# call function to identify element types in the log's column headers
header_obj_types = find_element_types_in_headers(log, ui_object_synonym) # find object types
header_att_types = find_element_types_in_headers(log, attribute_synonym) # find attribute types

# categorize columns from dictionary as attribute columns
column_type_dictionary = categorize_col_as_att(header_att_types)
column_type_dictionary = categorize_col_as_att(user_cols, column_type_dictionary) # mark user columns as attribute columns

# call function to save the column indices and the object type according to the matched attribute type in a dictionary
header_obj_type_from_att_type = get_obj_type_based_on_att(header_att_types, att_to_obj_dict)

# call function to re-arrange the dictionaries including info on the column type
ui_obj_att_cols, column_indices, att_cols_obj_unclear = rearrange_col_type_dicts(header_obj_types,
                                                                                          header_obj_type_from_att_type,
                                                                                          column_indices)

# find ui object types and columns including them
ui_object_match_count_dictionary, ui_object_type_dictionary = find_element_types(log, threshold_ui_obj,
                                                                                 ratio_dictionary, ui_object_synonym)
# find attribute types and columns including them
attribute_match_count_dictionary, attribute_type_dictionary = find_element_types(log, threshold_cont_att,
                                                                                 ratio_dictionary, attribute_synonym)

# call function to check for regex
mail_match_count_dictionary = check_for_regex(log, email_regex) # check for mail addresses
url_match_count_dictionary = check_for_regex(log, url_regex) # check for urls
timestamp_match_count_dictionary = check_for_regex(log, timestamp_regex) # check for timestamps

# call function to categorize the log columns
log, column_type_dictionary = get_column_types(log, column_type_dictionary, column_indices, col_compl_dict, ratio_dictionary,
                                          threshold_timestamp, threshold_cont_att, threshold_val_att,
                                          ui_object_match_count_dictionary, timestamp_match_count_dictionary,
                                          url_match_count_dictionary, mail_match_count_dictionary)

# ### Complete Element Type Dictionaries
# call function to get unique values per column
unique_dictionary = get_unique_values_per_col(log)

# make sure all ui object types are recorded in the ui object type dictionary
column_type_dictionary = complete_element_type_dictionary(column_type_dictionary, unique_dictionary,
                                                          column_type_dictionary, 'ui object type')
# make sure all attribute types are recorded in the attribute type dictionary
attribute_type_dictionary = complete_element_type_dictionary(column_type_dictionary, unique_dictionary,
                                                          attribute_type_dictionary, 'attribute')

# call save_col_index_of_col_types function 
selected_cols, cont_att_cols, val_att_cols, obj_type_cols, main_obj_type_cols = save_col_index_of_col_types(
    column_type_dictionary, user_cols)

log['object instance'] = None # add column for object instances
log['part of'] = None # add column to indicate next higher object hierarchy level

# add object instance column to the slected_cols list to loop over this column too in the following
selected_cols.append(log.columns.get_loc('object instance'))

# call function to get a list with columns that potentially include process objects types in some rows
pot_process_obj_cols = get_potential_process_obj_cols(cont_att_cols, url_match_count_dictionary)

# call function to find process objects in the log
process_obj_dict = find_process_objects(log, pot_process_obj_cols, nouns)


# TODO: find out if I still need the old function
# # function to differentiate different log formats
# for key, value_list in ui_object_synonym.items():
#     obj = log.loc[0,'main ui object type']
#     if obj in value_list or obj == key:
#         # if a task starts with an action at the highest object type in the hierarchy the following function has to be used
#         if key in obj_highest_level:
#             # call function to identify the object instances and their hierarchy
#             log = identify_obj_inst_and_hrchy(log, selected_cols, val_att_cols, cont_att_cols, obj_type_cols, ui_object_type_dictionary, obj_highest_level, obj_second_level, obj_third_level, obj_fourth_level)

#         else:
#             # the log structure is different, so a different function is needed
#             print('new function')

# call function to combine the ui object type dictionaries in one dictionary
other_ui_obj_cols = combine_ui_obj_type_dicts(ui_obj_att_cols, att_cols_obj_unclear)

# call function to get columns including attribute types that are not associated with an object type yet
unmatched_att_list = get_unmatched_att_cols(cont_att_cols, val_att_cols, ui_obj_att_cols, att_cols_obj_unclear,
                                            user_cols)

# call function to get dictionaries to save other ui object types and their column indices according to their
# hierarchy level
other_ui_obj_cols_highest, other_ui_obj_cols_second, other_ui_obj_cols_third, other_ui_obj_cols_fourth, undecided_obj_cols = categorize_other_ui_obj(
    other_ui_obj_cols, object_hierarchy)


# dictionary to save ui object instances and their unique identifiers
object_instances_dict = {}
# dictionary to save process object instances and their unique identifiers
process_obj_inst_dict = {}

# dataframe to save other ui object instances and type, their row index and the object instance they are part of
other_ui_obj_df = pd.DataFrame(columns=['row index', 'object instance', 'object type', 'part_of'])
# df to save process objects
process_obj_df = pd.DataFrame(columns=['row index', 'object instance', 'object type'])

# variable to save to which higher instance an object instance belongs and fill last column of the other_ui_obj_df
part_of = None

# lists to keep info on attribute column type for other_ui_obj_df
other_ui_obj_df_val_att_cols = []
other_ui_obj_df_cont_att_cols = []

# create lists to hold the last seen object instance of each object hierarchy and their row
last_app_inst = [] # for applications
last_web_inst = [] # for websites
last_second_obj_inst = [] # for object types on second level
last_third_obj_inst = [] # for object types on third level
last_fourth_obj_inst = [] # for object types on fourth level

obj_counter = 0 # counter to assign ids to the ui object instances
process_obj_counter = 0 # counter to assign ids to the process object instances

# loop over the 'main ui object type' column
for row_index, value in log['main ui object type'].iteritems():

    # reset local variables
    local_other_ui_obj_cols_highest = copy.deepcopy(other_ui_obj_cols_highest)
    local_other_ui_obj_cols_second = copy.deepcopy(other_ui_obj_cols_second)
    local_other_ui_obj_cols_third = copy.deepcopy(other_ui_obj_cols_third)
    local_other_ui_obj_cols_fourth = copy.deepcopy(other_ui_obj_cols_fourth)
    local_unmatched_att_list = copy.deepcopy(unmatched_att_list)

    # if the value is given for this row, use it as the main object type
    if value is not np.NaN:

        # initialize value_term for the case that the value is not part of the ui_object_synonym
        value_term = value

        # get standardized name from ui object dictionary
        for key, value_list in ui_object_synonym.items():
            if value in value_list or value == key:
                value_term = key
                break

        # check to which hierarchy level the object type belongs
        obj_level = determine_hierarchy_level(value_term, object_hierarchy)

        # check if the ui object is of the highest hierarchy level
        if obj_level == 'obj_highest_level':

            # call function to figure out what to do with the undecided columns
            local_unmatched_att_list, local_other_ui_obj_cols_fourth = decide_undecided_obj_cols(log,
                                                                                                 undecided_obj_cols,
                                                                                                 value_term, obj_level,
                                                                                                 local_other_ui_obj_cols_fourth,
                                                                                                 local_unmatched_att_list,
                                                                                                 row_index)

            # main highest level
            log, obj_counter, object_instances_dict, last_app_inst, last_web_inst, local_other_ui_obj_cols_highest = identify_main_object_instances(
                log, object_instances_dict, row_index, value, value_term, obj_level, local_other_ui_obj_cols_highest,
                local_unmatched_att_list, val_att_cols, cont_att_cols, last_app_inst, last_web_inst, last_app_inst,
                last_second_obj_inst, last_third_obj_inst, obj_counter)

            # other highest level
            # set variable to None since the main ui object is on this level
            main_not_this_level = None
            log, obj_counter, object_instances_dict, last_app_inst, last_web_inst, other_ui_obj_df, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols = identify_other_obj_inst(
                log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, value,
                local_other_ui_obj_cols_highest, val_att_cols, cont_att_cols, last_app_inst, last_web_inst,
                last_app_inst, last_second_obj_inst, last_third_obj_inst, obj_counter, main_not_this_level, part_of,
                other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols)

            # set variable to true since the main ui object is not on this level
            main_not_this_level = True

            # other second level
            log, obj_counter, object_instances_dict, last_second_obj_inst, last_web_inst, other_ui_obj_df, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols = identify_other_obj_inst(
                log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, value,
                local_other_ui_obj_cols_second, val_att_cols, cont_att_cols, last_second_obj_inst, last_web_inst,
                last_app_inst, last_second_obj_inst, last_third_obj_inst, obj_counter, main_not_this_level, part_of,
                other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols)

            # other third level
            log, obj_counter, object_instances_dict, last_third_obj_inst, last_web_inst, other_ui_obj_df, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols = identify_other_obj_inst(
                log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, value,
                local_other_ui_obj_cols_third, val_att_cols, cont_att_cols, last_third_obj_inst, last_web_inst,
                last_app_inst, last_second_obj_inst, last_third_obj_inst, obj_counter, main_not_this_level, part_of,
                other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols)

            # other fourth level
            log, obj_counter, object_instances_dict, last_fourth_obj_inst, last_web_inst, other_ui_obj_df, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols = identify_other_obj_inst(
                log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, value,
                local_other_ui_obj_cols_fourth, val_att_cols, cont_att_cols, last_fourth_obj_inst, last_web_inst,
                last_app_inst, last_second_obj_inst, last_third_obj_inst, obj_counter, main_not_this_level, part_of,
                other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols)


        # if it is not on the highest hierarchy level
        else:

            # call function to figure out what to do with the undecided columns
            local_unmatched_att_list, local_other_ui_obj_cols_fourth = decide_undecided_obj_cols(log,
                                                                                                 undecided_obj_cols,
                                                                                                 value_term, obj_level,
                                                                                                 local_other_ui_obj_cols_fourth,
                                                                                                 local_unmatched_att_list,
                                                                                                 row_index)

            # set variable to true since the main ui object is not on this level
            main_not_this_level = True

            # other highest level
            log, obj_counter, object_instances_dict, last_app_inst, last_web_inst, other_ui_obj_df, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols = identify_other_obj_inst(
                log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, value,
                local_other_ui_obj_cols_highest, val_att_cols, cont_att_cols, last_app_inst, last_web_inst,
                last_app_inst, last_second_obj_inst, last_third_obj_inst, obj_counter, main_not_this_level, part_of,
                other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols)

            # main second level
            if obj_level == 'obj_second_level':
                log, obj_counter, object_instances_dict, last_second_obj_inst, last_web_inst, local_other_ui_obj_cols_second = identify_main_object_instances(
                    log, object_instances_dict, row_index, value, value_term, obj_level, local_other_ui_obj_cols_second,
                    local_unmatched_att_list, val_att_cols, cont_att_cols, last_second_obj_inst, last_web_inst,
                    last_app_inst, last_second_obj_inst, last_third_obj_inst, obj_counter)

                # other second level
                # set variable to None since the main ui object is on this level
                main_not_this_level = None
                log, obj_counter, object_instances_dict, last_second_obj_inst, last_web_inst, other_ui_obj_df, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols = identify_other_obj_inst(
                    log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, value,
                    local_other_ui_obj_cols_second, val_att_cols, cont_att_cols, last_second_obj_inst, last_web_inst,
                    last_app_inst, last_second_obj_inst, last_third_obj_inst, obj_counter, main_not_this_level, part_of,
                    other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols)

                # set variable to true since the main ui object is not on this level
                main_not_this_level = True

                # other third level
                log, obj_counter, object_instances_dict, last_third_obj_inst, last_web_inst, other_ui_obj_df, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols = identify_other_obj_inst(
                    log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, value,
                    local_other_ui_obj_cols_third, val_att_cols, cont_att_cols, last_third_obj_inst, last_web_inst,
                    last_app_inst, last_second_obj_inst, last_third_obj_inst, obj_counter, main_not_this_level, part_of,
                    other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols)

                # other fourth level
                log, obj_counter, object_instances_dict, last_fourth_obj_inst, last_web_inst, other_ui_obj_df, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols = identify_other_obj_inst(
                    log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, value,
                    local_other_ui_obj_cols_fourth, val_att_cols, cont_att_cols, last_fourth_obj_inst, last_web_inst,
                    last_app_inst, last_second_obj_inst, last_third_obj_inst, obj_counter, main_not_this_level, part_of,
                    other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols)

            else:
                # set variable to true since the main ui object is not on this level
                main_not_this_level = True

                # other second level
                log, obj_counter, object_instances_dict, last_second_obj_inst, last_web_inst, other_ui_obj_df, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols = identify_other_obj_inst(
                    log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, value,
                    local_other_ui_obj_cols_second, val_att_cols, cont_att_cols, last_second_obj_inst, last_web_inst,
                    last_app_inst, last_second_obj_inst, last_third_obj_inst, obj_counter, main_not_this_level, part_of,
                    other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols)

                # main third level                                
                if obj_level == 'obj_third_level':
                    log, obj_counter, object_instances_dict, last_third_obj_inst, last_web_inst, local_other_ui_obj_cols_third = identify_main_object_instances(
                        log, object_instances_dict, row_index, value, value_term, obj_level,
                        local_other_ui_obj_cols_third, local_unmatched_att_list, val_att_cols, cont_att_cols,
                        last_third_obj_inst, last_web_inst, last_app_inst, last_second_obj_inst, last_third_obj_inst,
                        obj_counter)

                    # other third level
                    # set variable to None since the main ui object is on this level
                    main_not_this_level = None
                    log, obj_counter, object_instances_dict, last_third_obj_inst, last_web_inst, other_ui_obj_df, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols = identify_other_obj_inst(
                        log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, value,
                        local_other_ui_obj_cols_third, val_att_cols, cont_att_cols, last_third_obj_inst, last_web_inst,
                        last_app_inst, last_second_obj_inst, last_third_obj_inst, obj_counter, main_not_this_level,
                        part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols)

                    # other fourth level
                    # set variable to true since the main ui object is not on this level
                    main_not_this_level = True
                    log, obj_counter, object_instances_dict, last_fourth_obj_inst, last_web_inst, other_ui_obj_df, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols = identify_other_obj_inst(
                        log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, value,
                        local_other_ui_obj_cols_fourth, val_att_cols, cont_att_cols, last_fourth_obj_inst,
                        last_web_inst, last_app_inst, last_second_obj_inst, last_third_obj_inst, obj_counter,
                        main_not_this_level, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols)

                else:
                    # set variable to true since the main ui object is not on this level
                    main_not_this_level = True

                    # other third level
                    log, obj_counter, object_instances_dict, last_third_obj_inst, last_web_inst, other_ui_obj_df, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols = identify_other_obj_inst(
                        log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, value,
                        local_other_ui_obj_cols_third, val_att_cols, cont_att_cols, last_third_obj_inst, last_web_inst,
                        last_app_inst, last_second_obj_inst, last_third_obj_inst, obj_counter, main_not_this_level,
                        part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols)

                    # main fourth level
                    log, obj_counter, object_instances_dict, last_fourth_obj_inst, last_web_inst, local_other_ui_obj_cols_fourth = identify_main_object_instances(
                        log, object_instances_dict, row_index, value, value_term, obj_level,
                        local_other_ui_obj_cols_fourth, local_unmatched_att_list, val_att_cols, cont_att_cols,
                        last_fourth_obj_inst, last_web_inst, last_app_inst, last_second_obj_inst, last_third_obj_inst,
                        obj_counter)

                    # other fourth level
                    # set variable to None since the main ui object is on this level
                    main_not_this_level = None
                    log, obj_counter, object_instances_dict, last_fourth_obj_inst, last_web_inst, other_ui_obj_df, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols = identify_other_obj_inst(
                        log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, value,
                        local_other_ui_obj_cols_fourth, val_att_cols, cont_att_cols, last_fourth_obj_inst,
                        last_web_inst, last_app_inst, last_second_obj_inst, last_third_obj_inst, obj_counter,
                        main_not_this_level, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols)

    # if the value is not given, use a ui object type from a higher hierarchy level
    else:

        value = 'unknown' # since no main UI object is given
        value_term = value

        # check to which hierarchy level the object type belongs
        obj_level = determine_hierarchy_level(value_term, object_hierarchy)

        # call function to figure out what to do with the undecided columns
        local_unmatched_att_list, local_other_ui_obj_cols_fourth = decide_undecided_obj_cols(log, undecided_obj_cols,
                                                                                             value_term, obj_level,
                                                                                             local_other_ui_obj_cols_fourth,
                                                                                             local_unmatched_att_list,
                                                                                             row_index)

        # set variable to true since the main ui object is not on this level
        main_not_this_level = True

        # other highest level
        log, obj_counter, object_instances_dict, last_app_inst, last_web_inst, other_ui_obj_df, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols = identify_other_obj_inst(
            log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, value,
            local_other_ui_obj_cols_highest, val_att_cols, cont_att_cols, last_app_inst, last_web_inst, last_app_inst,
            last_second_obj_inst, last_third_obj_inst, obj_counter, main_not_this_level, part_of,
            other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols)

        # other second level
        log, obj_counter, object_instances_dict, last_second_obj_inst, last_web_inst, other_ui_obj_df, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols = identify_other_obj_inst(
            log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, value,
            local_other_ui_obj_cols_second, val_att_cols, cont_att_cols, last_second_obj_inst, last_web_inst,
            last_app_inst, last_second_obj_inst, last_third_obj_inst, obj_counter, main_not_this_level, part_of,
            other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols)

        # other third level
        log, obj_counter, object_instances_dict, last_third_obj_inst, last_web_inst, other_ui_obj_df, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols = identify_other_obj_inst(
            log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, value,
            local_other_ui_obj_cols_third, val_att_cols, cont_att_cols, last_third_obj_inst, last_web_inst,
            last_app_inst, last_second_obj_inst, last_third_obj_inst, obj_counter, main_not_this_level, part_of,
            other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols)

        # main fourth level
        log, obj_counter, object_instances_dict, last_fourth_obj_inst, last_web_inst, local_other_ui_obj_cols_fourth = identify_main_object_instances(
            log, object_instances_dict, row_index, value, value_term, obj_level, local_other_ui_obj_cols_fourth,
            local_unmatched_att_list, val_att_cols, cont_att_cols, last_fourth_obj_inst, last_web_inst, last_app_inst,
            last_second_obj_inst, last_third_obj_inst, obj_counter)

        # other fourth level
        # set variable to None since the main ui object is on this level
        main_not_this_level = None
        log, obj_counter, object_instances_dict, last_fourth_obj_inst, last_web_inst, other_ui_obj_df, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols = identify_other_obj_inst(
            log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, value,
            local_other_ui_obj_cols_fourth, val_att_cols, cont_att_cols, last_fourth_obj_inst, last_web_inst,
            last_app_inst, last_second_obj_inst, last_third_obj_inst, obj_counter, main_not_this_level, part_of,
            other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols)

    # generate process object instances for the user-related objects
    process_obj_df, log = add_user_objects(log, process_obj_df, user_cols, row_index, process_obj_inst_dict, process_obj_counter)

    # TODO: manage process objects



# unify nan values
log = unify_nan_values(log)
other_ui_obj_df = unify_nan_values(other_ui_obj_df)
process_obj_df = unify_nan_values(process_obj_df)



# TODO: adjust json to new layout
cont_att_list = []
for i in cont_att_cols:
    cont_att_list.append(log.columns[i])

val_att_list = []
for i in val_att_cols:
    val_att_list.append(log.columns[i])

# ## 5. Restructuring the Log
# ### Create Event DataFrame
event_df = pd.DataFrame()

event_instances = []

for x in range(1, len(log) + 1):
    event_instances.append(f'event_{x}')

event_df['event id'] = event_instances

for col_index in val_att_cols:
    col = log.columns[col_index]
    event_df[col] = log.iloc[:, col_index]

for col in log.columns:
    if 'activity' in col:
        event_df[col] = log.pop(col)
    if 'timestamp' in col:
        event_df[col] = log[col]
    if 'object instance' in col:
        event_df[col] = log[col]

events_dict = {}

# convert timestamp to string, so json can parse it
event_df['timestamp'] = event_df['timestamp'].astype(str)

for index, row in event_df.iterrows():
    val_att_dict = {}
    for att in val_att_list:
        if att is not np.NaN:
            val_att_dict[f"{row['object instance']}.{att}"] = row[att]

    events_dict[row["event id"]] = {
        "activity": row["activity"],
        "timestamp": row["timestamp"],
        "omap": row["object instance"],
        "vmap": val_att_dict
    }

# write the event dictionary to a JSON file
with open('event_output.json', 'w') as f:
    json.dump(events_dict, f)

# ### Create Object DataFrame
# copy log
object_df = copy.deepcopy(log)

# drop duplicate object instances and keep only the once that occure latest in time
object_df = object_df.sort_values('timestamp').drop_duplicates(['object instance'], keep='last').sort_index()

# drop the timestamp column
object_df = object_df.drop(['timestamp'], axis=1)

# reset indices, so they start with zero again and don't have gaps
object_df.reset_index(drop=True, inplace=True)

objects_dict = {}
att_list = []

# convert the df into json format
for index, row in object_df.iterrows():
    cont_att_dict = {}
    val_att_dict = {}
    part_of = []

    for att in cont_att_list:
        if att is not np.NaN:
            cont_att_dict[att] = row[att]
    for att in val_att_list:
        if att is not np.NaN:
            val_att_dict[att] = row[att]

    if row["part of"] is not np.NaN:
        part_of.append(row["part of"])

    objects_dict[row["object instance"]] = {
        "type": row["main ui object type"],
        "cmap": cont_att_dict,
        "vmap": val_att_dict,
        "omap": part_of
    }

# write the object dictionary to a JSON file
with open('object_output.json', 'w') as f:
    json.dump(objects_dict, f)

# TODO: merge json files to one json file
print('success')
