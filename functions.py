#!/usr/bin/env python
# coding: utf-8

# # Functions needed for the UI log transformation
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog as fd
import re
import nltk

# function which lets a user select a ui log from their computer's file structure
def import_log():
    # create the root window
    root = tk.Tk()

    # hide the root window
    root.withdraw()

    # places the window on top of all other windows
    root.call('wm', 'attributes', '.', '-topmost', True)

    # open the file structure 
    file_path = fd.askopenfilename(title='Select the UI log you want to import.')

    # use the user selected path to import the ui log
    while True:
        file_path = input("Enter the file path: ")

        if file_path.endswith('.xls') or file_path.endswith('.xlsx'):
            log = pd.read_excel(file_path)
            break

        elif file_path.endswith('.csv'):
            log = pd.read_csv(file_path)
            break

        else:
            print("Unsupported file format. Please choose a file of type csv, xls, or xlsx instead.")

    return log, file_path

def delete_cases(log):
    if 'case' in log.columns[0]:
        log = log.drop(log.columns[0], axis=1)

    return log

# function to remove camel case and underscore writing
def unify_string_format(log):
    # regex that matches strings including nothing but letters and underscores. So, no numbers or other special
    # characters.
    string_regex = '^[A-Za-z]*([_])?[A-Za-z]*$'

    # regex that recognized camel case
    camel_underscore_regex = '(?<=[a-z])(?=[A-Z])|(?<![A-Z])(?=[A-Z][a-z])|(?<=[A-Za-z])(?=[0-9]|[_])'

    for column, row in log.iteritems():

        for index, value in row.items():

            if re.fullmatch(string_regex, str(value).strip()):
                value = str(value).strip()

                if str(value).lower() == 'nan':
                    break

                else:
                    term = [word for word in re.split(camel_underscore_regex, value)]
                    new_value = " ".join(term).lower()
                    log.at[index, column] = new_value

    return log

# split column names written in camel case into separate words
def split_title_camel_case(log):
    # create dictionary to store the column names in
    new_col_titles = {}

    for col in log.columns:
        # split the column title into separate words
        term = [word for word in
                re.split(r'[.]|(?<=[a-z])(?=[A-Z])|(?<![A-Z])(?=[A-Z][a-z])|(?<=[A-Za-z])(?=[0-9])', col)]
        new_col_title = " ".join(term).lower()

        # store the new column name in the dictionary
        new_col_title = new_col_title.strip()
        new_col_titles[col] = new_col_title

    # rename the columns using the new names in the dictionary
    log = log.rename(columns=new_col_titles)

    return log

# function to delete all empty columns
def delete_empty_columns_and_rows(log):
    current_number_cols = len(log.columns)

    log.dropna(how='all', axis=1, inplace=True)
    log.dropna(how='all', axis=0, inplace=True)

    number_removed_cols = current_number_cols - len(log.columns)
    if number_removed_cols != 0:
        print(f"{number_removed_cols} columns have been removed because they were empty.")

    return log

# function removing all columns that include the same value in every row and therefore do not add value to the log
def find_constant_columns(log):
    # constant_columns = [col for col in log.columns if log[col].nunique(dropna=True) == 1]
    constant_columns = []

    for column in log.columns:
        if len(log[column].unique()) == 1:
            col_index = log.columns.get_loc(column)
            constant_columns.append(col_index)

    return constant_columns

# function removing duplicate columns
def remove_duplicate_columns(log):
    current_number_cols = len(log.columns)

    log = log.T.drop_duplicates().T

    number_removed_cols = current_number_cols - len(log.columns)
    if number_removed_cols != 0:
        print(f"{number_removed_cols} columns have been removed because they were duplicates.")

    return log

def isNaN(value):
    try:
        import math
        return math.isnan(float(value))
    except:
        return False

# Todo: figure out how to filter nan values
def get_unique_values_per_col(log):
    # dictionary to save the unique values of each column
    unique_dictionary = {}

    # save unique values 
    for col in log:
        unique_list = log[col].unique()
        unique_list = [value for value in unique_list if str(value).lower != 'nan']
        unique_dictionary[col] = unique_list

    return unique_dictionary

# function to move a column to a different position in the log
def move_column(log, current_column_name, column_index_goal, new_column_name):
    column = log.pop(current_column_name)
    log.insert(column_index_goal, new_column_name, column)

    return log

# recognize the event column of the log
def find_event_column(log, ratio_dictionary, action_labels, ratio_threshold):
    # list including strings that might indicate the event or activity column
    event_strings = ['event', 'activit', 'action']

    # loop over the column headers and match them against strings to identify the event column of the log
    for col in log.columns:

        # check if any column headers indicate the event column
        if any(string in col for string in event_strings):
            # move the column to the first position in the log
            log = move_column(log, col, 0, 'event')

            return log

    # compare the log values to the action label dataset to see if a column matches some of the labels
    activity_match_count_dictionary, activity_type_dictionary = find_element_types(log, ratio_threshold,
                                                                                   ratio_dictionary, action_labels)

    keys = activity_match_count_dictionary.keys()

    if len(keys) == 1:
        col = list(keys)

        # move the column to the first position in the log
        log = move_column(log, col[0], 0, 'event')

        return log

    # ask user to identify the event column
    while True:
        try:
            print(log.head())
            event_column = int(input(
                "Please enter the index of the log's column holding the user interaction assuming that the first "
                "column has the index 0:"))

            # move the column to the first position in the log
            log = move_column(log, event_column, 0, 'event')

        except ValueError:
            print("Sorry, this value cannot be accepted. Please enter a number.")
            # return to the start of the loop
            continue
        else:
            if 0 <= event_column <= len(log.columns):
                # exit the loop.
                break
            else:
                # return to the start of the loop
                continue
    return log

# Todo: POS tagging or list comparison to separate activity and object type
# function splitting the events into their activities and object types
def extract_activity(log, event_column_index):
    # rename column
    log.rename({event_column_index: "event"})

    split_results = log.iloc[:, event_column_index].str.split(' ').apply(pd.Series)

    # if there is only one word included, assume it is the activity
    if len(split_results.columns) == 1:
        log.insert(1, 'activity', split_results[0])

    # if the event consists of only two parts assume the first word is the activity and the second one the object type
    elif len(split_results.columns) == 2:
        log.insert(1, 'activity', split_results[0])
        log.insert(2, 'main ui object type', split_results[1])

    # drop the original event_column
    log = log.drop('event', axis=1)

    # if the column includes activities instead of events (combination of activity and object type), the object
    # column will be empty
    log = delete_empty_columns_and_rows(log)

    return log

# function to find object and attribute types included in the log's headers
def find_element_types_in_headers(log, synonym_dictionary):
    # create dictionary to save element types and their name in the log
    header_element_types = {}

    # loop over every word that is part of a header to find matches in the ui object type dictionary
    for index, header_word in enumerate(log.columns):
        words = header_word.split()
        for word in words:
            for key, value_list in synonym_dictionary.items():
                if word in value_list or word == key:
                    header_element_types[index] = key

    return header_element_types

# function finding columns that have 'user' in their title 
def find_user_related_cols(log):
    user_columns = {}

    # loop over every word that is part of a header to find matches in the ui object type dictionary
    for index, header_word in enumerate(log.columns):
        words = header_word.split()
        for word in words:
            if word == 'user':
                user_columns.setdefault(index, header_word)

    return user_columns

# function to count how many unique values there are per column and calculate a ratio (
# unique_values/total_number_of_values)
def get_unique_value_ratio(log):
    ratio_dictionary = {}

    # count unique values and total number of values for each column
    for index, column in enumerate(log.columns):
        number_unique_values = log[column].nunique()
        number_values = log[column].count()
        ratio_unique = number_unique_values / number_values
        ratio_dictionary.setdefault(index, ratio_unique)
        print('%s: %d / %d = %f' % (column, number_unique_values, number_values, ratio_unique))

    return ratio_dictionary

# function to determine the completeness of the log per column and save columns passing the threshold in a dictionary
def get_column_completeness(log, threshold_compl):
    # dictionary to save columns with a high completeness rate
    col_compl_dict = {}

    for index, column in enumerate(log.columns):
        col = log[column].count()
        ratio = col / len(log)

        if ratio >= threshold_compl:
            col_compl_dict.setdefault(index, ratio)

        print('%s: %d / %d = %f' % (column, col, len(log), ratio))

    return col_compl_dict

def get_obj_type_based_on_att(header_att_types, att_to_obj_dict):
    # dictionary to save the column indices and the object type according to the matched attribute type
    header_obj_type_from_att_type = {}

    # get the object types that match the found attribute types according to the mapping dictionary
    for key1, value1 in header_att_types.items():
        for key2, values2 in att_to_obj_dict.items():
            if value1 in values2:
                if key1 not in header_obj_type_from_att_type:
                    header_obj_type_from_att_type[key1] = [key2]
                else:
                    header_obj_type_from_att_type[key1].append(key2)

    return header_obj_type_from_att_type

# function to identify the element types the columns include
def find_element_types(log, ratio_threshold, ratio_dictionary, comparison_dictionary, element_type_dictionary=None):
    # create a dictionary to store the count of matches per column and object type
    match_count_dictionary = {}

    # if there is an existing dictionary given for a certain element type, then use that one, if not, create a new one
    if element_type_dictionary is None:
        element_type_dictionary = {}

    # find element types per column, given a ratio threshold, looping over every value in each column
    for column, ratio in ratio_dictionary.items():
        if ratio < ratio_threshold:
            for index, row in log.iloc[:, column:column + 1].iterrows():

                # create a set to store the unique matches per column
                unique_matches = set()

                for value in row:

                    # loop over dictionary or list to compare the values
                    for element_type, synonyms in comparison_dictionary.items():

                        for synonym in synonyms:
                            if str(value) in synonym:
                                element_type_dictionary.setdefault(value, element_type)
                                unique_matches.add(element_type)

                # update the match count dictionary with the unique matches per column
                for element_type in unique_matches:
                    match_count_dictionary.setdefault(column, {}).setdefault(element_type, 0)
                    match_count_dictionary[column][element_type] += 1

    return match_count_dictionary, element_type_dictionary

# function to recognize elements that follow a certain structure, e.g., email addresses or urls
def check_for_regex(log, regex):
    # create a dictionary to store the count of matches per column and object type
    match_count_dictionary = {}

    for column, row in log.iteritems():

        # count variable to count how many values match the regex
        count = 0

        for value in row:
            if re.fullmatch(regex, str(value)):
                count += 1

        # get the columns index
        column_index = log.columns.get_loc(column)

        # add values to the dictionary
        if count != 0:
            match_count_dictionary.setdefault(column_index, count)

    return match_count_dictionary

def categorize_col_as_att(dictionary, column_type_dictionary):

    for key, value in dictionary.items():
        if value == 'input value':
            column_type_dictionary.setdefault(key, 'value attribute')
        elif 'id' in value:
            column_type_dictionary.setdefault(key, 'context attribute')
        else:
            column_type_dictionary.setdefault(key, 'attribute')

    return column_type_dictionary

def rearrange_col_type_dicts(header_obj_types, header_obj_type_from_att_type, column_indices):
    # dictionary including attribute columns where the object type is already known
    ui_obj_att_cols = {}

    # list with keys that should be removed from the dictionary
    keys_to_remove = []

    # concatenate columns where the object type is certain in the ui_obj_att_cols dictionary
    for key, value in header_obj_types.items():
        if key in header_obj_type_from_att_type and value in header_obj_type_from_att_type[key]:
            ui_obj_att_cols[key] = value
            keys_to_remove.append(key)

    # remove column indices that have been moved to the new dictionary from the original one
    for key in keys_to_remove:
        del header_obj_type_from_att_type[key]
        column_indices.remove(key)

    return ui_obj_att_cols, column_indices, header_obj_type_from_att_type

def get_potential_process_obj_cols(cont_att_cols, url_match_count_dictionary):
    # dictionary with column indices potentially including process object types
    pot_process_obj_cols = []

    for col in cont_att_cols:
        pot_process_obj_cols.append(col)

    # columns including urls are unlikely to include process object types
    for col in url_match_count_dictionary:
        pot_process_obj_cols.remove(col)

    return pot_process_obj_cols

def combine_ui_obj_type_dicts(ui_obj_att_cols, header_obj_type_from_att_type):
    # combine the ui object type dictionaries in one dictionary
    other_ui_obj_cols = {}

    for key, value in ui_obj_att_cols.items():
        other_ui_obj_cols[key] = value if isinstance(value, list) else [value]

    for key, value in header_obj_type_from_att_type.items():
        other_ui_obj_cols[key] = value if isinstance(value, list) else [value]

    return other_ui_obj_cols


def get_unmatched_att_cols(cont_att_cols, val_att_cols, ui_obj_att_cols, header_obj_type_from_att_type, user_cols):
    # columns including attribute types that are not associated with an object type yet
    unmatched_att_list = cont_att_cols + val_att_cols

    for index in ui_obj_att_cols.keys():
        if index in unmatched_att_list:
            unmatched_att_list.remove(index)

    for index in header_obj_type_from_att_type.keys():
        if index in unmatched_att_list:
            unmatched_att_list.remove(index)

    for index in user_cols:
        if index in unmatched_att_list:
            unmatched_att_list.remove(index)

    return unmatched_att_list


def categorize_other_ui_obj(other_ui_obj_cols, object_hierarchy):
    # dictionaries to save other ui object types and their column indices according to their hierarchy level
    other_ui_obj_cols_highest = {}
    other_ui_obj_cols_second = {}
    other_ui_obj_cols_third = {}
    other_ui_obj_cols_fourth = {}

    # dictionary to store columns that haven't been assigned one clear object type, but a list of possible ones
    undecided_obj_cols = {}

    # split other_ui_obj_cols dictionary into separate dictionaries according to their hierarchy level
    for index, obj_types in other_ui_obj_cols.items():
        if len(obj_types) == 1:
            obj_type = obj_types[0]
            for level, value in object_hierarchy.items():
                if obj_type in value:
                    if level == 'obj_highest_level':
                        other_ui_obj_cols_highest.setdefault(index, obj_type)
                    elif level == 'obj_second_level':
                        other_ui_obj_cols_second.setdefault(index, obj_type)
                    elif level == 'obj_third_level':
                        other_ui_obj_cols_third.setdefault(index, obj_type)
                    else:
                        other_ui_obj_cols_fourth.setdefault(index, obj_type)
        else:
            undecided_obj_cols[index] = obj_types

    return other_ui_obj_cols_highest, other_ui_obj_cols_second, other_ui_obj_cols_third, other_ui_obj_cols_fourth, undecided_obj_cols


def get_column_types(log, column_type_dictionary, column_indices, col_compl_dict, ratio_dictionary, threshold_timestamp,
                     threshold_cont_att, threshold_val_att, ui_object_match_count_dictionary,
                     timestamp_match_count_dictionary, url_match_count_dictionary, mail_match_count_dictionary):

    # there can only be one 'main ui object type' column holding the ui object interacted with; counter
    main_ui_obj_type_counter = 0

    # we know where the activity column is because the 'find_event_column' function puts it in the first position
    column_type_dictionary.setdefault(0, 'activity')
    # remove this index from the list because a type has been assigned
    column_indices.remove(0)

    # if there had been an event column, which has been split by the 'extract_activity' function, then the ui object
    # types are in the third position
    if log.columns[1] == 'main ui object type':
        column_type_dictionary.setdefault(1, 'main ui object type')
        # remove this index from the list because a type has been assigned
        column_indices.remove(1)
        main_ui_obj_type_counter += 1

    else:
        # check the ui_object_match_count_dictionary to find other ui object type columns
        ui_object_type_keys = ui_object_match_count_dictionary.keys()
        if len(ui_object_type_keys) > 0:
            columns = list(ui_object_type_keys)
            # loop over columns no type has been assigned to yet
            for col in column_indices:
                # check if the column is also in the ui_object_type_key list
                if col in columns:
                    # if the column has a high completeness rate, then it is likely to be the main ui object type column
                    if col in col_compl_dict and main_ui_obj_type_counter == 0:
                        # assign type to the column
                        column_type_dictionary.setdefault(col, 'main ui object type')
                        # remove this index from the list because a type has been assigned
                        column_indices.remove(col)
                        # set the counter, so no more columns can be identified as main ui object type columns
                        main_ui_obj_type_counter += 1
                    else:
                        # assign type to the column
                        column_type_dictionary.setdefault(col, 'ui object type')
                        # remove this index from the list because a type has been assigned
                        column_indices.remove(col)

    # timestamp column has been found with regex
    timestamp_keys = timestamp_match_count_dictionary.keys()
    if len(timestamp_keys) > 0:
        columns = list(timestamp_keys)
        # loop over columns no type has been assigned to yet
        for col in column_indices:
            # check if the column is also in the timestamp_key list
            if col in columns:
                # check if column includes 100% unique values, since every timestamp in a log should be unique
                if ratio_dictionary[col] == threshold_timestamp:
                    column_type_dictionary.setdefault(col, 'timestamp')
                    # remove this index from the list because a type has been assigned
                    column_indices.remove(col)

    # if urls are found in a column: assume this column includes attribute values and the column header is an
    # attribute type
    url_keys = url_match_count_dictionary.keys()
    if len(url_keys) > 0:
        columns = list(url_keys)
        # loop over columns no type has been assigned to yet
        for col in column_indices:
            # check if the column is also in the url_key list
            if col in columns:
                column_type_dictionary.setdefault(col, 'context attribute')
                # remove this index from the list because a type has been assigned
                column_indices.remove(col)

    # if email addresses are found in a column: assume this column includes attribute values and the column header is
    # an attribute type
    mail_keys = mail_match_count_dictionary.keys()
    if len(mail_keys) > 0:
        columns = list(mail_keys)
        # loop over columns no type has been assigned to yet
        for col in column_indices:
            # check if the column is also in the mail_key list
            if col in columns:
                column_type_dictionary.setdefault(col, 'value attribute')
                # remove this index from the list because a type has been assigned
                column_indices.remove(col)

    # check whether the attribute columns are context or value attribute columns depending on the uniqueness of the values
    for col in column_type_dictionary:
        if column_type_dictionary[col] == 'attribute':
            # if there are few unique values it is likely that the column includes context attribute values
            if ratio_dictionary[col] < threshold_cont_att:
                column_type_dictionary[col] = 'context attribute'
            # if there are many unique values it is likely that the column includes value attribute values
            elif ratio_dictionary[col] > threshold_val_att:
                column_type_dictionary[col] = 'value attribute'

    # loop over columns no type has been assigned to yet
    for col in column_indices:
        # ids are usually context attributes even though they have a high uniqueness rate
        if 'id' in log.columns[col]:
            column_type_dictionary.setdefault(col, 'context attribute')
        # if there are few unique values it is likely that the column includes attribute types
        elif ratio_dictionary[col] < threshold_cont_att:
            column_type_dictionary.setdefault(col, 'context attribute')
        # if there are many unique values it is likely that the column includes attribute values
        elif ratio_dictionary[col] > threshold_val_att:
            column_type_dictionary.setdefault(col, 'value attribute')

        # ask user for column type
        else:
            while True:
                possible_values = ['ui object type', 'value attribute', 'context attribute']
                first_7_unique = log[log.columns[col]].unique()[:7].tolist()
                print(f'Column: {log.columns[col]}: {first_7_unique} \nPossible column types: {possible_values}')
                column_type = input("Please enter the type of this column choosing from this list:")
                if column_type not in possible_values:
                    print("Column type invalid. Please try again.")
                    # return to the start of the loop
                    continue
                else:
                    column_type_dictionary.setdefault(col, column_type)
                    # exit the loop
                    break

    # sort the dictionary, so the columns are in the right order
    column_type_dictionary = dict(sorted(column_type_dictionary.items()))

    return column_type_dictionary


# function to rename the timestamp column
def rename_timestamp_col(log, column_type_dictionary):
    for index in column_type_dictionary:
        if 'timestamp' in column_type_dictionary[index]:
            log = log.rename(columns={log.columns[index]: 'timestamp'})

    return log


# function to save the column indices of the different element types
def save_col_index_of_col_types(column_type_dictionary):
    # lists to save column indices of different column types
    selected_cols = []
    cont_att_cols = []
    val_att_cols = []
    obj_type_cols = []
    main_obj_type_cols = []

    for index in column_type_dictionary:
        column_type = column_type_dictionary.get(index)
        if column_type == 'value attribute':
            if index not in selected_cols:
                selected_cols.append(index)
            if index not in val_att_cols:
                val_att_cols.append(index)
        if column_type == 'context attribute':
            if index not in selected_cols:
                selected_cols.append(index)
            if index not in cont_att_cols:
                cont_att_cols.append(index)
        if 'ui object type' in column_type:
            if 'main ui object type' in column_type:
                if index not in selected_cols:
                    selected_cols.append(index)
                if index not in obj_type_cols:
                    main_obj_type_cols.append(index)
            else:
                if index not in selected_cols:
                    selected_cols.append(index)
                if index not in obj_type_cols:
                    obj_type_cols.append(index)

    # sort list, so columns stay in the right order
    selected_cols.sort()

    return selected_cols, cont_att_cols, val_att_cols, obj_type_cols, main_obj_type_cols


def identify_obj_inst_and_hrchy(log, selected_cols, val_att_cols, cont_att_cols, obj_type_cols,
                                ui_object_type_dictionary, obj_highest_level, obj_second_level, obj_third_level,
                                obj_fourth_level):
    # dictionary to save object instances and their unique identifiers
    object_instances_dict = {}

    # counter to assign ids to the object instances
    obj_counter = 0

    # create variables to hold the last seen object instance of each object hierarchy
    #last_high_obj_inst = np.nan
   # last_second_obj_inst = np.nan
    #last_third_obj_inst = np.nan

    # loop over selected columns only
    for index, row in log.iloc[:, selected_cols].iterrows():
        # list for the attribute types
        att_list = []
        # list for the attribute types and values
        att_val_combi_list = []
        # list for the ui objects
        ui_obj_list = []
        # loop over column values
        for col_name, value in row.iteritems():
            col_index = log.columns.get_loc(col_name)
            # save object type
            if 'main ui object type' in col_name and str(value).lower() != 'nan':
                object_type = value
            # for the value attribute columns, save the column title in the list
            if col_index in val_att_cols and str(value).lower() != 'nan':
                att_list.append(col_name)
                att_val_combi_list.append(value)
            # for the context attribute columns save the column value in the list
            if col_index in cont_att_cols and str(value).lower() != 'nan':
                att_list.append(value)
                att_val_combi_list.append(value)
                # list additional ui object types
            if col_index in obj_type_cols and str(value).lower() != 'nan':
                ui_obj_list.append(value)

        # depending on the hierarchy level: add more values to the list to identify object instances
        # add highest level object instance to list (for all but highest level objects)
        if object_type in ui_object_type_dictionary and ui_object_type_dictionary[object_type] not in obj_highest_level:
            if str(last_high_obj_inst).lower() != 'nan':
                att_list.append(last_high_obj_inst)
        # add second level object instance to the list (for all third level objects)
        if object_type in ui_object_type_dictionary and ui_object_type_dictionary[object_type] in obj_third_level:
            if str(last_second_obj_inst).lower() != 'nan':
                att_list.append(last_second_obj_inst)
        # add third level object instance to the list (for all fourth level objects)
        if object_type in ui_object_type_dictionary and ui_object_type_dictionary[object_type] in obj_fourth_level:
            if str(last_third_obj_inst).lower() != 'nan':
                att_list.append(last_third_obj_inst)

        # transform lists in tuples, so they can act as keys in the dictionary
        if object_type in ui_object_type_dictionary and ui_object_type_dictionary[object_type] in obj_highest_level:
            att_combi = tuple(att_val_combi_list)
        else:
            att_combi = tuple(att_list)

        # if key is not in dictionary yet, add it together with the object instance
        if att_combi not in object_instances_dict:
            obj_counter += 1
        object_instances_dict.setdefault(att_combi, f'{object_type}_{obj_counter}')

        # add object instance id to the object instance column of the log
        obj_inst = object_instances_dict[att_combi]
        log.loc[index, 'object instance'] = obj_inst

        # saves instances of last object for each hierarchy level
        if object_type in ui_object_type_dictionary and ui_object_type_dictionary[object_type] in obj_highest_level:
            last_high_obj_inst = obj_inst
        elif object_type in ui_object_type_dictionary and ui_object_type_dictionary[object_type] in obj_second_level:
            last_second_obj_inst = obj_inst
            log.loc[index, 'part of'] = last_high_obj_inst
        elif object_type in ui_object_type_dictionary and ui_object_type_dictionary[object_type] in obj_third_level:
            last_third_obj_inst = obj_inst
            if str(last_second_obj_inst).lower() != 'nan':
                log.loc[index, 'part of'] = last_second_obj_inst
            else:
                log.loc[index, 'part of'] = last_high_obj_inst
        elif object_type in ui_object_type_dictionary and ui_object_type_dictionary[object_type] in obj_fourth_level:
            if str(last_third_obj_inst).lower() != 'nan':
                log.loc[index, 'part of'] = last_third_obj_inst
            elif str(last_second_obj_inst).lower() != 'nan':
                log.loc[index, 'part of'] = last_second_obj_inst
            else:
                log.loc[index, 'part of'] = last_high_obj_inst
        else:
            log.loc[index, 'part of'] = last_high_obj_inst

    return log


# find process object types in the log; only the context attribute columns are interesting here 
def find_process_objects(log, cont_att_cols, nouns):
    # regex that recognized camel case
    camel_underscore_regex = '(?<=[a-z])(?=[A-Z])|(?<![A-Z])(?=[A-Z][a-z])|(?<=[A-Za-z])(?=[0-9]|[_]|[.]|[-])'

    # dictionary to save the process object types and their row index
    process_obj_dict = {}

    for index, row in log.iloc[:, cont_att_cols].iterrows():
        # list for the ui objects
        process_obj_list = []
        # loop over column values
        for col_name, value in row.iteritems():

            # unify the string format first
            value = str(value).strip()
            if str(value).lower() == 'nan':
                break
            else:
                term = [word for word in re.split(camel_underscore_regex, value)]
                new_value = " ".join(term).lower()

            stem_value = nltk.stem.WordNetLemmatizer().lemmatize(str(new_value))

            # check if the value is in the noun list 
            if stem_value in nouns:
                if value not in process_obj_list:
                    process_obj_list.append(value)

        if len(process_obj_list) != 0:
            process_obj_dict.setdefault(index, process_obj_list)

    return process_obj_dict