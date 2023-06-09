#!/usr/bin/env python
# coding: utf-8

# <editor-fold desc="Imports">
import pandas as pd

from functions import *
import sys
import os

# TODO: optimize thresholds
# retrieve command-line arguments
args = sys.argv[1:]

# if only the file path is handed over, use default parameters
if len(args) == 1:
    # check if the argument is a file path with valid extensions
    file_path = args[0]
    # check if the file format is correct
    if not file_path.endswith('.xls') and not file_path.endswith('.xlsx') and not file_path.endswith('.csv'):
        raise ValueError("Invalid file path provided. Please choose a file of type csv, xls, or xlsx instead.")

    # use default parameter values
    threshold_ui_obj = 0.15  # for ui object columns
    threshold_act = 0.2  # for activity columns
    threshold_cont_att = 0.5  # for context attribute columns
    threshold_val_att = threshold_cont_att  # for value attribute columns
    threshold_timestamp = 1  # for timestamp column
    threshold_compl = 0.95  # determines how complete a column should be

# if parameters are handed over, assign them to the ration thresholds determining the ratio of unique values a column should hold
elif len(args) == 6:
    file_path = args[0]
    threshold_ui_obj = float(args[1]) # for ui object columns
    threshold_act = float(args[2]) # for activity columns
    threshold_cont_att = float(args[3]) # for context attribute columns
    threshold_val_att = threshold_cont_att # for value attribute columns
    threshold_timestamp = float(args[4]) # for timestamp column
    threshold_compl = float(args[5]) # determines how complete a column should be

else:
    print("Usage: python main.py [<file_path> <threshold_ui_object> <threshold_activity> <threshold_attribute> <threshold_timestamp> <threshold_col_completeness>]")
    sys.exit(1)

# handle specific file paths "example_ui_log.xlsx" or "student_record.csv"
if file_path == "example_ui_log.xlsx" or file_path == "student_record.csv":
    file_path = os.path.join(os.path.dirname(__file__), "datasets", file_path)

# check if the file format is correct
if file_path.endswith('.xls') or file_path.endswith('.xlsx'):
    log = pd.read_excel(file_path, dtype=str)
elif file_path.endswith('.csv'):
    log = pd.read_csv(file_path, dtype=str)
else:
    raise ValueError("Unsupported file format. Please choose a file of type csv, xls, or xlsx instead.")

#log = pd.read_excel(r'C:\Users\Besitzer\Documents\Master\Thesis\Code\datasets\example_ui_log.xlsx',  dtype=str)

# log = pd.read_excel(r'C:\Users\Besitzer\Documents\Master\Thesis\Code\datasets\student_record.xlsx',  dtype=str)
#
# threshold_ui_obj = 0.15  # for ui object columns
# threshold_act = 0.2  # for activity columns
# threshold_cont_att = 0.55  # for context attribute columns
# threshold_val_att = threshold_cont_att # for value attribute columns
# threshold_timestamp = 1  # for timestamp column
# threshold_compl = 0.95  # determines how complete a column should be

# import action label list as DataFrame taken from https://carbondesignsystem.com/guidelines/content/action-labels/ and
# supplemented with own ideas (confirm, login)
action_labels = pd.read_csv(r'C:\Users\Besitzer\Documents\GitHub\master_thesis\Datasets\action_labels.csv')
# </editor-fold>


# <editor-fold desc="Pre-defined Dictionaries and Lists">
# dictionary with pre-defined object types and their synonyms
ui_object_synonym = {
    'website': ['website', 'site', 'page', 'web page', 'webpage', 'url', 'link', 'href'],
    'application': ['application', 'app', 'program', 'tool', 'system', 'excel', 'power point' 'erp', 'browser', 'chrome', 'firefox',
                'opera', 'safari', 'microsoft edge'],
    'file': ['file', 'document', 'workbook'],
    'sheet': ['sheet', 'page'],
    'field': ['field', 'cell', 'value'],
    'button': ['button'],
    'image': ['image', 'picture'],
    'checkbox': ['checkbox', 'check box']
}

# dictionary with pre-defined attribute types and their synonyms
attribute_synonym = {
    'url': ['url', 'site', 'link', 'page', 'href'],
    'host name': ['host name', 'host'],
    'page name': ['page name', 'page title'],
    'application name': ['application name', 'application', 'app', 'program', 'browser'],
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

# words not to be tagged as process objects even though the classifier classifies some of them as nouns
excluded_words = ['chrome', 'firefox', 'safari', 'microsoft edge', 'opera', 'excel', 'power point']
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


# <editor-fold desc="1. Column Type Classification">
# call function to calculate the ratio of unique values/total values per column
uniqueness_ratio_dictionary = get_unique_value_ratio(log)

# call function to identify the event column of the ui log and move it to the first position 
log = find_event_column(log, uniqueness_ratio_dictionary, action_labels, threshold_act)

# call function to separate the activities from the object types in the events
log = extract_activity(log, 0)

# updated the uniqueness-ration dictionary since the columns changed
uniqueness_ratio_dictionary = get_unique_value_ratio(log)

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
                                                                                 uniqueness_ratio_dictionary, ui_object_synonym)
# find attribute types and columns including them
attribute_match_count_dictionary, attribute_type_dictionary = find_element_types(log, threshold_cont_att,
                                                                                 uniqueness_ratio_dictionary, attribute_synonym)

# call function to check for regex
mail_match_count_dictionary = check_for_regex(log, email_regex) # check for mail addresses
url_match_count_dictionary = check_for_regex(log, url_regex) # check for urls
timestamp_match_count_dictionary = check_for_regex(log, timestamp_regex) # check for timestamps

# call function to categorize the log columns
log, column_type_dictionary = get_column_types(log, column_type_dictionary, column_indices, col_compl_dict, uniqueness_ratio_dictionary,
                                          threshold_timestamp, threshold_cont_att, threshold_val_att,
                                          ui_object_match_count_dictionary, timestamp_match_count_dictionary,
                                          url_match_count_dictionary, mail_match_count_dictionary)
# </editor-fold>


# <editor-fold desc="2. Object Recognition">
# call function to get unique values per column
unique_dictionary = get_unique_values_per_col(log)

# make sure all ui object types are recorded in the ui object type dictionary
ui_object_type_dictionary = complete_element_type_dictionary(column_type_dictionary, unique_dictionary,
                                                          ui_object_type_dictionary, 'ui object type')
# make sure all attribute types are recorded in the attribute type dictionary
attribute_type_dictionary = complete_element_type_dictionary(column_type_dictionary, unique_dictionary,
                                                          attribute_type_dictionary, 'attribute')

# call save_col_index_of_col_types function 
selected_cols, cont_att_cols, val_att_cols, obj_type_cols, main_obj_type_cols = save_col_index_of_col_types(
    column_type_dictionary, user_cols)

log['object instance'] = None # add column for object instances
log['part of'] = None # add column to indicate next higher object hierarchy level
log['related ui object'] = None # add column for the ui objects that are also related to the event but not to the main ui object

# add object instance column to the selected_cols list to loop over this column too in the following
selected_cols.append(log.columns.get_loc('object instance'))

# call function to get a list with columns that potentially include process objects types in some rows
pot_process_obj_cols = get_potential_process_obj_cols(cont_att_cols, url_match_count_dictionary)

# df to save process objects
process_obj_df = pd.DataFrame(columns=['row index', 'object instance', 'object type'])

# call function to find process objects in the log
process_obj_df = find_process_objects(log, pot_process_obj_cols, process_obj_df, excluded_words)
#process_obj_df = find_process_objects_new(log, cont_att_cols, process_obj_df)

# call function to combine the ui object type dictionaries in one dictionary
other_ui_obj_cols = combine_ui_obj_type_dicts(ui_obj_att_cols, att_cols_obj_unclear)

# call function to get columns including attribute types that are not associated with an object type yet
unmatched_att_list = get_unmatched_att_cols(cont_att_cols, val_att_cols, ui_obj_att_cols, att_cols_obj_unclear,
                                            user_cols)

# call function to get dictionaries to save other ui object types and their column indices according to their
# hierarchy level
other_ui_obj_cols_highest, other_ui_obj_cols_second, other_ui_obj_cols_third, other_ui_obj_cols_fourth, undecided_obj_cols = categorize_other_ui_obj(
    other_ui_obj_cols, object_hierarchy)

log, other_ui_obj_df, process_obj_df, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols = recognize_obj_instances(
    log, object_hierarchy, ui_object_synonym, undecided_obj_cols, other_ui_obj_cols_highest, other_ui_obj_cols_second,
    other_ui_obj_cols_third, other_ui_obj_cols_fourth, val_att_cols, cont_att_cols, user_cols, unmatched_att_list,
    process_obj_df)
# </editor-fold>


# <editor-fold desc="3. Element Linkage">
# unify nan values
log = unify_nan_values(log)
other_ui_obj_df = unify_nan_values(other_ui_obj_df)
process_obj_df = unify_nan_values(process_obj_df)

# call function to create the event json file
event_dict = create_event_dict(log, val_att_cols, process_obj_df)

# call function to create a df suitable to convert to json for the main ui objects
ui_obj_dict = create_main_ui_obj_dict(log, cont_att_cols, val_att_cols)

# call function to create the ui object json file
ui_obj_dict = create_ui_obj_dict(ui_obj_dict, other_ui_obj_df, other_ui_obj_df_cont_att_cols,
                                 other_ui_obj_df_val_att_cols)

# call function to create the process object json file
process_obj_dict = create_process_obj_dict(process_obj_df)

# call function to merge all dictionaries and create the final object-centric event data json file
merge_dicts_and_create_json(event_dict, ui_obj_dict, process_obj_dict)
# </editor-fold>