#!/usr/bin/env python
# coding: utf-8

# # Automated Transformation of UI Logs Into Object-Centric Event Data

# Assumptions: 
# - log is sorted by the timestamp starting with the earliest point in time
# - if the log is already split into cases, the case id is in the first column of the log.

# ## Imports

import json
import copy
import numpy as np

from functions import *

# call the import_log function to read a ui log chosen by the user
# log, file_path = import_log()

file_path = r'C:\Users\Besitzer\Documents\GitHub\master_thesis\Datasets\StudentRecord_preprocessed.csv'
log = pd.read_csv(file_path)

# file_path = r'C:\Users\Besitzer\Documents\GitHub\master_thesis\Datasets\example_ui_log - Copy.xlsx'
# log = pd.read_excel(file_path)

# import action label list taken from https://carbondesignsystem.com/guidelines/content/action-labels/ and
# supplemented with own ideas (confirm, login)
action_labels = pd.read_csv(r'C:\Users\Besitzer\Documents\GitHub\master_thesis\Datasets\action_labels.csv')

# import noun list extracted from wordNet
nouns = pd.read_csv(r'C:\Users\Besitzer\Documents\GitHub\master_thesis\Datasets\nouns_final.csv')

# ration thresholds to be optimized
threshold_ui_obj = 0.15
threshold_act = 0.2
threshold_cont_att = 0.5
threshold_val_att = 1 - threshold_cont_att
threshold_timestamp = 1
threshold_compl = 0.95

# ## Preprocessing

# ### Remove Useless Data

# call function to delete case separation since it is not needed
log = delete_cases(log)

# call function to remove empty columns
log = delete_empty_columns_and_rows(log)

# call function to remove duplicate columns from the log
log = remove_duplicate_columns(log)

# ### Split Camel Case
# call function to unify the string formats by eliminating e.g., camel case
log = unify_string_format(log)

# calling function to split column names written in camel case into separate words
log = split_title_camel_case(log)

# ## 1. Column Type Classification
# call function to calculate the ratio of unique values/total values per column
ratio_dictionary = get_unique_value_ratio(log)

# call function to identify the event column of the ui log and move it to the first position 
log = find_event_column(log, ratio_dictionary, action_labels, threshold_act)

# calling the extract_activity function to separate the activities from the object types in the events
log = extract_activity(log, 0)

# ### Pre-define Dictionaries
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

# call function to calculate the ratio again of unique values/total values per column
ratio_dictionary = get_unique_value_ratio(log)

# call function to calculate the completeness ratio again per column
col_compl_dict = get_column_completeness(log, threshold_compl)

# ### Find Element Types
# initialize list with all column indices
num_columns = len(log.columns)
column_indices = list(range(num_columns))

# call function to find columns that are constant, so have the same value for all rows
const_cols = find_constant_columns(log)

# call function to find columns that belong to the user rather than to any ui object
user_cols = find_user_related_cols(log)

# call function to identify element types in the log's column headers
header_obj_types = find_element_types_in_headers(log, ui_object_synonym)
header_att_types = find_element_types_in_headers(log, attribute_synonym)

# dictionary that holds info on type included for each column of the log
column_type_dictionary = {}

# categorize columns from dictionary as attribute columns
column_type_dictionary = categorize_col_as_att(header_att_types, column_type_dictionary)

# mark user columns as attribute columns
column_type_dictionary = categorize_col_as_att(user_cols, column_type_dictionary)

# call function to save the column indices and the object type according to the matched attribute type in a dictionary
header_obj_type_from_att_type = get_obj_type_based_on_att(header_att_types, att_to_obj_dict)

# call function to re-arrange the dictionaries including info on the column type
ui_obj_att_cols, column_indices, header_obj_type_from_att_type = rearrange_col_type_dicts(header_obj_types,
                                                                                          header_obj_type_from_att_type,
                                                                                          column_indices)

# find ui object types and columns including them
ui_object_match_count_dictionary, ui_object_type_dictionary = find_element_types(log, threshold_ui_obj,
                                                                                 ratio_dictionary, ui_object_synonym)

# find attribute types and columns including them
attribute_match_count_dictionary, attribute_type_dictionary = find_element_types(log, threshold_cont_att,
                                                                                 ratio_dictionary, attribute_synonym)

# find activity types and columns including them
activity_match_count_dictionary, activity_type_dictionary = find_element_types(log, threshold_act, ratio_dictionary,
                                                                               action_labels)

# regular expressions to find strings that match the given pattern
email_regex = '[^@]+@[^@]+\.[^@]+'
url_regex = '(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})'
timestamp_regex = '\d{4}[-.\/ ]\d{1,2}[-.\/ ]\d{1,2} \d{2}:\d{2}(:\d{2})?([-,* ]\d{3,4})?|(\d{1,2}[-.\/ ])?\d{1,2}[-.\/ ]\d{2,4} \d{2}:\d{2}(:\d{2})?([-,* ]\d{3,4})?|\d{4}[-.\/ ]\w{3}[-.\/ ]\d{1,2} \d{2}:\d{2}(:\d{2})?([-,* ]\d{3,4})?|\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z'

# call function to check for email addresses and urls
mail_match_count_dictionary = check_for_regex(log, email_regex)
url_match_count_dictionary = check_for_regex(log, url_regex)
timestamp_match_count_dictionary = check_for_regex(log, timestamp_regex)

# ### Assign Column Type
# call function to categorize the log columns
column_type_dictionary = get_column_types(log, column_type_dictionary, column_indices, col_compl_dict, ratio_dictionary,
                                          threshold_timestamp, threshold_cont_att, threshold_val_att,
                                          ui_object_match_count_dictionary, timestamp_match_count_dictionary,
                                          url_match_count_dictionary, mail_match_count_dictionary)

# call function to rename the timestamp column
log = rename_timestamp_col(log, column_type_dictionary)

# ### Complete Element Type Dictionaries
# call function to get unique values per column
unique_dictionary = get_unique_values_per_col(log)

# make sure all ui object types are recorded in the object type dictionary
keys = [key for key, value in column_type_dictionary.items() if 'ui object type' in value]
for key in keys:
    value_list = list(unique_dictionary.values())[key]
    for value in value_list:
        ui_object_type_dictionary.setdefault(value, value)

# make sure all attribute types are recorded in the attribute type dictionary
keys = [key for key, value in column_type_dictionary.items() if 'attribute' in value]
for key in keys:
    value = log.columns[key]
    attribute_type_dictionary.setdefault(value, value)

# ## 2. Object Recognition
# ### Object Hierarchy Definition
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

# call save_col_index_of_col_types function 
selected_cols, cont_att_cols, val_att_cols, obj_type_cols, main_obj_type_cols = save_col_index_of_col_types(
    column_type_dictionary)

# the user columns are not relevant to identify the ui object instances
for col in user_cols:
    selected_cols.remove(col)

# add column for object instances 
log['object instance'] = None

# add column to indicate next higher object hierarchy level
log['part of'] = None

# add object instance column to the slected_cols list to loop over this column too in the following
selected_cols.append(log.columns.get_loc('object instance'))

# call function to get a list with columns that potentially include process objects types in some rows
pot_process_obj_cols = get_potential_process_obj_cols(cont_att_cols, url_match_count_dictionary)

# call function to find process objects in the log
process_obj_dict = find_process_objects(log, pot_process_obj_cols, nouns)

# Todo: find out if I still need the old function
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
other_ui_obj_cols = combine_ui_obj_type_dicts(ui_obj_att_cols, header_obj_type_from_att_type)

# call function to get columns including attribute types that are not associated with an object type yet
unmatched_att_list = get_unmatched_att_cols(cont_att_cols, val_att_cols, ui_obj_att_cols, header_obj_type_from_att_type,
                                            user_cols)

# call function to get dictionaries to save other ui object types and their column indices according to their
# hierarchy level
other_ui_obj_cols_highest, other_ui_obj_cols_second, other_ui_obj_cols_third, other_ui_obj_cols_fourth, undecided_obj_cols = categorize_other_ui_obj(
    other_ui_obj_cols, object_hierarchy)

# Todo: move functions to other file
# function to get all keys that match a target_value
def find_matching_pairs(dictionary):
    value_to_keys = {}
    matching_pairs = {}

    for key, value in dictionary.items():
        if value not in value_to_keys:
            value_to_keys[value] = [key]
        else:
            value_to_keys[value].append(key)

    for value, keys in value_to_keys.items():
        matching_pairs[value] = keys

    return matching_pairs

# function to find the lowest value in a dictionary 
def find_lowest_value(dictionary):
    # initialize with float('inf'), so first value encountered will be smaller and will be updated
    min_value = float('inf')
    min_obj = None

    # loop over the values and save the smallest one
    for key, values in dictionary.items():
        for value in values:
            if value < min_value:
                min_obj = key

    return min_obj

def get_attribute_values(log, row_index, combined_att_list, val_att_cols, cont_att_cols):
    # lists to save attributes
    att_list = []

    # loop over the column indices and check if the columns hold value attributes or context attributes
    # append the values to the lists accordingly
    for col_index in combined_att_list:

        # for the value attribute columns, save the column title in the list
        if col_index in val_att_cols and str(log.iloc[row_index, col_index]).lower() != 'nan':
            att_list.append(log.columns[col_index])

        # for the context attribute columns save the column value in the list
        if col_index in cont_att_cols and str(log.iloc[row_index, col_index]).lower() != 'nan':
            att_list.append(log.iloc[row_index, col_index])

    return att_list


def add_higher_hierarchy_instances(log, att_list, row_index, obj_level, last_web_inst, last_high_obj_inst, last_second_obj_inst,
                                   last_third_obj_inst, obj_is_main, part_of=None):

    # only add higher levels to the list, if there are already attributes in the list
    if att_list:

        if obj_level == 'obj_second_level' or obj_level == 'obj_third_level':
            # if list is not empty, append the object instance included in it
            if last_high_obj_inst:
                att_list.append(last_high_obj_inst[0])
                if part_of is None:
                    log.loc[row_index, 'part of'] = last_high_obj_inst[0]
                else:
                    part_of = last_high_obj_inst[0]

        if obj_level == 'obj_third_level':
            # if list is not empty, append the object instance included in it
            if last_second_obj_inst:
                att_list.append(last_second_obj_inst[0])
                if part_of is None:
                    log.loc[row_index, 'part of'] = last_second_obj_inst[0]
                else:
                    part_of = last_second_obj_inst[0]

        if obj_level == 'obj_fourth_level':
            # if in same row an object instance of third level exists, then have application as first level
            if row_index == last_third_obj_inst[1]:
                if last_high_obj_inst:
                    att_list.append(last_high_obj_inst[0])
                    if part_of is None:
                        log.loc[row_index, 'part of'] = last_high_obj_inst[0]
                    else:
                        part_of = last_high_obj_inst[0]

                if last_second_obj_inst:
                    att_list.append(last_second_obj_inst[0])
                    if part_of is None:
                        log.loc[row_index, 'part of'] = last_second_obj_inst[0]
                    else:
                        part_of = last_second_obj_inst[0]

                if last_third_obj_inst:
                    att_list.append(last_third_obj_inst[0])
                    if part_of is None:
                        log.loc[row_index, 'part of'] = last_third_obj_inst[0]
                    else:
                        part_of = last_third_obj_inst[0]

            # if no third level obj instance in same row, then have website as first level
            else:
                if last_web_inst:
                    att_list.append(last_web_inst[0])
                    if part_of is None:
                        log.loc[row_index, 'part of'] = last_web_inst[0]
                    else:
                        part_of = last_web_inst[0]

    if obj_is_main is not None:
        return att_list, log
    else:
        return part_of, att_list, log


def get_relevant_att_cols(local_other_ui_obj_cols, unmatched_att_list, value_term):
    # list to collect relevant columns
    relevant_cols = []

    # check if the ui object type matches any other ui object type found in the log headers
    for index, obj_val in local_other_ui_obj_cols.items():
        if str(value_term) in obj_val:
            relevant_cols.append(index)

    # remove column indices from the dictionary because they have already been considered
    for index in relevant_cols:
        local_other_ui_obj_cols.pop(index, None)

    # combine the lists relevant to determine the ui object instance
    combined_att_list = unmatched_att_list + relevant_cols

    return combined_att_list, local_other_ui_obj_cols

def generate_key(att_list, object_instances_dict, value, obj_counter):

    # remove nan values from the list
    att_list = [att for att in att_list if att is not None]

    # if there is more than one value in the list, build a tuple so it can be used as a dictionary key
    if len(att_list) > 1:
        att_combi = tuple(att_list)
        if att_combi not in object_instances_dict:
            obj_counter += 1
            object_instances_dict.setdefault(att_combi, f'{value}_{obj_counter}')
        obj_inst = object_instances_dict[att_combi]

    elif len(att_list) == 1:
        att_val = att_list[0]
        if att_val not in object_instances_dict and str(att_val).lower() != 'nan':
            obj_counter += 1
            object_instances_dict.setdefault(att_val, f'{value}_{obj_counter}')
        obj_inst = object_instances_dict[att_val]

    else:
        obj_inst = None

    return obj_inst, object_instances_dict, obj_counter

def create_new_row(row_index, obj_inst, part_of, other_ui_obj_df):
    # create a new dataframe row
    new_row = pd.DataFrame({'row_index': [row_index], 'object_instance': [obj_inst], 'part_of': [part_of]})

    # append the new row to the existing df
    other_ui_obj_df = pd.concat([other_ui_obj_df, new_row], ignore_index=True)

    return other_ui_obj_df

def determine_hierarchy_level(value, object_hierarchy):
    obj_level = None

    # check to which hierarchy level the object type belongs
    for level, obj_values in object_hierarchy.items():
        if value in obj_values:
            obj_level = level

    return obj_level

def identify_main_object_instances(log, object_instances_dict, row_index, value, value_term, obj_level,
                                   local_other_ui_obj_cols, unmatched_att_list, val_att_cols, cont_att_cols,
                                   last_obj_inst, last_web_inst, last_high_obj_inst, last_second_obj_inst, last_third_obj_inst,
                                   obj_counter):
    # call function to get a list of the relevant attribute columns
    combined_att_list, local_other_ui_obj_cols = get_relevant_att_cols(local_other_ui_obj_cols, unmatched_att_list,
                                                                       value_term)

    # function that loops over the list to combine all attribute values to identify the object instance
    att_list = get_attribute_values(log, row_index, combined_att_list, val_att_cols, cont_att_cols)

    # call function to add value to the 'part of' column
    obj_is_main = True
    att_list, log = add_higher_hierarchy_instances(log, att_list, row_index, obj_level, last_web_inst, last_high_obj_inst,
                                                   last_second_obj_inst, last_third_obj_inst, obj_is_main)

    # call function to form a key from the attribute combination to get the object instance
    obj_inst, object_instances_dict, obj_counter = generate_key(att_list, object_instances_dict, value, obj_counter)

    log.loc[row_index, 'object instance'] = obj_inst

    # saves instance of last object for this  hierarchy level
    if value_term == 'website':
        last_web_inst = [obj_inst, row_index]
    else:
        last_obj_inst = [obj_inst, row_index]


    return log, obj_counter, object_instances_dict, last_obj_inst, last_web_inst, local_other_ui_obj_cols


def identify_other_obj_inst(log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index,
                            local_other_ui_obj_cols, val_att_cols, cont_att_cols, last_obj_inst, last_web_inst, last_high_obj_inst,
                            last_second_obj_inst, last_third_obj_inst, obj_counter, main_not_this_level, part_of):

    # call function to find out which columns have the same object type
    local_other_ui_obj_cols = find_matching_pairs(local_other_ui_obj_cols)

    for obj, indices in local_other_ui_obj_cols.items():

        # check to which hierarchy level the object type belongs
        obj_level = determine_hierarchy_level(obj, object_hierarchy)

        # function that loops over the list to combine all attribute values to identify the object instance
        att_list = get_attribute_values(log, row_index, indices, val_att_cols, cont_att_cols)

        # call function to add value to the 'part of' variable
        obj_is_main = None
        part_of, att_list, log = add_higher_hierarchy_instances(log, att_list, row_index, obj_level, last_web_inst, last_high_obj_inst,
                                                                last_second_obj_inst, last_third_obj_inst, obj_is_main, part_of)

        # call function to form a key from the attribute combination to get the object instance
        obj_inst, object_instances_dict, obj_counter = generate_key(att_list, object_instances_dict, obj, obj_counter)

        # don't add object instances to the df that don't actually exist
        if obj_inst is not None:
            # call function to add a row with new info to the other_ui_obj_df
            other_ui_obj_df = create_new_row(row_index, obj_inst, part_of, other_ui_obj_df)

        # if the main ui object is not on the same level, then set this object instance as last instance of this level
        if main_not_this_level:
            if obj == 'website':
                last_web_inst = [obj_inst, row_index]
            else:
                last_obj_inst = [obj_inst, row_index]

    return log, obj_counter, object_instances_dict, last_obj_inst, last_web_inst, other_ui_obj_df, part_of

# dictionary to save ui object instances and their unique identifiers
object_instances_dict = {}

# dataframe to save other ui object instances, their row index and the object instance they are part of
other_ui_obj_df = pd.DataFrame(columns=['row_index', 'object_instance', 'part_of'])

# variable to save to which higher instance an object instance belongs and fill last column of the other_ui_obj_df
part_of = None

# create lists to hold the last seen object instance of each object hierarchy and their row
last_high_obj_inst = []
last_web_inst = [] # for websites
last_second_obj_inst = []
last_third_obj_inst = []
last_fourth_obj_inst = []

# counter to assign ids to the object instances
obj_counter = 0

# loop over the 'main ui object type' column
for row_index, value in log['main ui object type'].iteritems():

    # reset local variables
    local_other_ui_obj_cols_highest = copy.deepcopy(other_ui_obj_cols_highest)
    local_other_ui_obj_cols_second = copy.deepcopy(other_ui_obj_cols_second)
    local_other_ui_obj_cols_third = copy.deepcopy(other_ui_obj_cols_third)
    local_other_ui_obj_cols_fourth = copy.deepcopy(other_ui_obj_cols_fourth)

    # if the value is given for this row, use it as the main object type
    if str(value).lower() != 'nan':

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
            # main highest level
            log, obj_counter, object_instances_dict, last_high_obj_inst, last_web_inst, local_other_ui_obj_cols_highest = identify_main_object_instances(
                log, object_instances_dict, row_index, value, value_term, obj_level, local_other_ui_obj_cols_highest,
                unmatched_att_list, val_att_cols, cont_att_cols, last_high_obj_inst, last_web_inst, last_high_obj_inst,
                last_second_obj_inst, last_third_obj_inst, obj_counter)

            # other highest level
            # set variable to false since the main ui object is on this level
            main_not_this_level = None
            log, obj_counter, object_instances_dict, last_high_obj_inst, last_web_inst, other_ui_obj_df, part_of = identify_other_obj_inst(
                log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index,
                local_other_ui_obj_cols_highest, val_att_cols, cont_att_cols, last_high_obj_inst, last_web_inst, last_high_obj_inst,
                last_second_obj_inst, last_third_obj_inst, obj_counter, main_not_this_level, part_of)

            # set variable to true since the main ui object is not on this level
            main_not_this_level = True

            # other second level
            log, obj_counter, object_instances_dict, last_second_obj_inst, last_web_inst, other_ui_obj_df, part_of = identify_other_obj_inst(
                log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index,
                local_other_ui_obj_cols_second, val_att_cols, cont_att_cols, last_second_obj_inst, last_web_inst, last_high_obj_inst,
                last_second_obj_inst, last_third_obj_inst, obj_counter, main_not_this_level, part_of)

            # other third level
            log, obj_counter, object_instances_dict, last_third_obj_inst, last_web_inst, other_ui_obj_df, part_of = identify_other_obj_inst(
                log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, local_other_ui_obj_cols_third,
                val_att_cols, cont_att_cols, last_third_obj_inst, last_web_inst, last_high_obj_inst, last_second_obj_inst,
                last_third_obj_inst, obj_counter, main_not_this_level, part_of)

            # other fourth level
            log, obj_counter, object_instances_dict, last_fourth_obj_inst, last_web_inst, other_ui_obj_df, part_of = identify_other_obj_inst(
                log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index,
                local_other_ui_obj_cols_fourth, val_att_cols, cont_att_cols, last_fourth_obj_inst, last_web_inst, last_high_obj_inst,
                last_second_obj_inst, last_third_obj_inst, obj_counter, main_not_this_level, part_of)


        # if it is not on the highest hierarchy level
        else:

            # set variable to true since the main ui object is not on this level
            main_not_this_level = True

            # other highest level
            log, obj_counter, object_instances_dict, last_high_obj_inst, last_web_inst, other_ui_obj_df, part_of = identify_other_obj_inst(
                log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index,
                local_other_ui_obj_cols_highest, val_att_cols, cont_att_cols, last_high_obj_inst, last_web_inst, last_high_obj_inst,
                last_second_obj_inst, last_third_obj_inst, obj_counter, main_not_this_level, part_of)

            # main second level
            if obj_level == 'obj_second_level':
                log, obj_counter, object_instances_dict, last_second_obj_inst, last_web_inst, local_other_ui_obj_cols_second = identify_main_object_instances(
                    log, object_instances_dict, row_index, value, value_term, obj_level, local_other_ui_obj_cols_second,
                    unmatched_att_list, val_att_cols, cont_att_cols, last_second_obj_inst, last_web_inst, last_high_obj_inst,
                    last_second_obj_inst, last_third_obj_inst, obj_counter)

                # other second level
                # set variable to false since the main ui object is on this level
                main_not_this_level = None
                log, obj_counter, object_instances_dict, last_second_obj_inst, last_web_inst, other_ui_obj_df, part_of = identify_other_obj_inst(
                    log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index,
                    local_other_ui_obj_cols_second, val_att_cols, cont_att_cols, last_second_obj_inst, last_web_inst,
                    last_high_obj_inst, last_second_obj_inst, last_third_obj_inst, obj_counter, main_not_this_level,
                    part_of)

                # set variable to true since the main ui object is not on this level
                main_not_this_level = True

                # other third level
                log, obj_counter, object_instances_dict, last_third_obj_inst, last_web_inst, other_ui_obj_df, part_of = identify_other_obj_inst(
                    log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index,
                    local_other_ui_obj_cols_third, val_att_cols, cont_att_cols, last_third_obj_inst, last_web_inst, last_high_obj_inst,
                    last_second_obj_inst, last_third_obj_inst, obj_counter, main_not_this_level, part_of)

                # other fourth level
                log, obj_counter, object_instances_dict, last_fourth_obj_inst, last_web_inst, other_ui_obj_df, part_of = identify_other_obj_inst(
                    log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index,
                    local_other_ui_obj_cols_fourth, val_att_cols, cont_att_cols, last_fourth_obj_inst, last_web_inst,
                    last_high_obj_inst, last_second_obj_inst, last_third_obj_inst, obj_counter, main_not_this_level,
                    part_of)

            else:
                # set variable to true since the main ui object is not on this level
                main_not_this_level = True

                # other second level
                log, obj_counter, object_instances_dict, last_second_obj_inst, last_web_inst, other_ui_obj_df, part_of = identify_other_obj_inst(
                    log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index,
                    local_other_ui_obj_cols_second, val_att_cols, cont_att_cols, last_second_obj_inst, last_web_inst,
                    last_high_obj_inst, last_second_obj_inst, last_third_obj_inst, obj_counter, main_not_this_level,
                    part_of)

                # main third level                                
                if obj_level == 'obj_third_level':
                    log, obj_counter, object_instances_dict, last_third_obj_inst, last_web_inst, local_other_ui_obj_cols_third = identify_main_object_instances(
                        log, object_instances_dict, row_index, value, value_term, obj_level,
                        local_other_ui_obj_cols_third, unmatched_att_list, val_att_cols, cont_att_cols,
                        last_third_obj_inst, last_web_inst, last_high_obj_inst, last_second_obj_inst, last_third_obj_inst, obj_counter)

                    # other third level
                    # set variable to true since the main ui object is not on this level
                    main_not_this_level = None
                    log, obj_counter, object_instances_dict, last_third_obj_inst, last_web_inst, other_ui_obj_df, part_of = identify_other_obj_inst(
                        log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index,
                        local_other_ui_obj_cols_third, val_att_cols, cont_att_cols, last_third_obj_inst, last_web_inst,
                        last_high_obj_inst, last_second_obj_inst, last_third_obj_inst, obj_counter, main_not_this_level,
                        part_of)

                    # other fourth level
                    # set variable to true since the main ui object is not on this level
                    main_not_this_level = True
                    log, obj_counter, object_instances_dict, last_fourth_obj_inst, last_web_inst, other_ui_obj_df, part_of = identify_other_obj_inst(
                        log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index,
                        local_other_ui_obj_cols_fourth, val_att_cols, cont_att_cols, last_fourth_obj_inst, last_web_inst,
                        last_high_obj_inst, last_second_obj_inst, last_third_obj_inst, obj_counter, main_not_this_level,
                        part_of)

                else:
                    # set variable to true since the main ui object is not on this level
                    main_not_this_level = True

                    # other third level
                    log, obj_counter, object_instances_dict, last_third_obj_inst, last_web_inst, other_ui_obj_df, part_of = identify_other_obj_inst(
                        log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index,
                        local_other_ui_obj_cols_third, val_att_cols, cont_att_cols, last_third_obj_inst, last_web_inst,
                        last_high_obj_inst, last_second_obj_inst, last_third_obj_inst, obj_counter, main_not_this_level,
                        part_of)

                    # main fourth level
                    log, obj_counter, object_instances_dict, last_fourth_obj_inst, last_web_inst, local_other_ui_obj_cols_fourth = identify_main_object_instances(
                        log, object_instances_dict, row_index, value, value_term, obj_level,
                        local_other_ui_obj_cols_fourth, unmatched_att_list, val_att_cols, cont_att_cols,
                        last_fourth_obj_inst, last_web_inst, last_high_obj_inst, last_second_obj_inst, last_third_obj_inst,
                        obj_counter)

                    # other fourth level
                    # set variable to true since the main ui object is not on this level
                    main_not_this_level = None
                    log, obj_counter, object_instances_dict, last_fourth_obj_inst, last_web_inst, other_ui_obj_df, part_of = identify_other_obj_inst(
                        log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index,
                        local_other_ui_obj_cols_fourth, val_att_cols, cont_att_cols, last_fourth_obj_inst, last_web_inst,
                        last_high_obj_inst, last_second_obj_inst, last_third_obj_inst, obj_counter, main_not_this_level,
                        part_of)

    # if the value is not given, use a ui object type from a higher hierarchy level
    else:
        # call function to find out which columns have the same object type
        local_other_ui_obj_cols_highest_matched = find_matching_pairs(local_other_ui_obj_cols_highest)

        # use ui object from highest level with lowest index as replacement
        value = find_lowest_value(local_other_ui_obj_cols_highest_matched)

        # initialize value_term for the case that the value is not part of the ui_object_synonym
        value_term = value

        # get standardized name from ui object dictionary
        for key, value_list in ui_object_synonym.items():
            if value in value_list or value == key:
                value_term = key
                break

        # check to which hierarchy level the object type belongs
        obj_level = determine_hierarchy_level(value_term, object_hierarchy)

        # main highest level
        log, obj_counter, object_instances_dict, last_high_obj_inst, last_web_inst, local_other_ui_obj_cols_highest = identify_main_object_instances(
            log, object_instances_dict, row_index, value, value_term, obj_level, local_other_ui_obj_cols_highest,
            unmatched_att_list, val_att_cols, cont_att_cols, last_high_obj_inst, last_web_inst, last_high_obj_inst,
            last_second_obj_inst, last_third_obj_inst, obj_counter)

        # other highest level
        # set variable to false since the main ui object is on this level
        main_not_this_level = None
        log, obj_counter, object_instances_dict, last_high_obj_inst, last_web_inst, other_ui_obj_df, part_of = identify_other_obj_inst(
            log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, local_other_ui_obj_cols_highest,
            val_att_cols, cont_att_cols, last_high_obj_inst, last_web_inst, last_high_obj_inst, last_second_obj_inst,
            last_third_obj_inst, obj_counter, main_not_this_level, part_of)

        # set variable to true since the main ui object is not on this level
        main_not_this_level = True

        # other second level
        log, obj_counter, object_instances_dict, last_second_obj_inst, last_web_inst, other_ui_obj_df, part_of = identify_other_obj_inst(
            log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, local_other_ui_obj_cols_second,
            val_att_cols, cont_att_cols, last_second_obj_inst, last_web_inst, last_high_obj_inst, last_second_obj_inst,
            last_third_obj_inst, obj_counter, main_not_this_level, part_of)

        # other third level
        log, obj_counter, object_instances_dict, last_third_obj_inst, last_web_inst, other_ui_obj_df, part_of = identify_other_obj_inst(
            log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, local_other_ui_obj_cols_third,
            val_att_cols, cont_att_cols, last_third_obj_inst, last_web_inst, last_high_obj_inst, last_second_obj_inst,
            last_third_obj_inst, obj_counter, main_not_this_level, part_of)

        # other fourth level
        log, obj_counter, object_instances_dict, last_fourth_obj_inst, last_web_inst, other_ui_obj_df, part_of = identify_other_obj_inst(
            log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, local_other_ui_obj_cols_fourth,
            val_att_cols, cont_att_cols, last_fourth_obj_inst, last_web_inst, last_high_obj_inst, last_second_obj_inst,
            last_third_obj_inst, obj_counter, main_not_this_level, part_of)

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
        if str(row[att]).lower() != 'nan':
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
        if str(row[att]).lower() != 'nan':
            cont_att_dict[att] = row[att]
    for att in val_att_list:
        if str(row[att]).lower() != 'nan':
            val_att_dict[att] = row[att]

    if str(row["part of"]).lower() != 'nan':
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

print('success')
