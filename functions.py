#!/usr/bin/env python
# coding: utf-8

# <editor-fold desc="Imports">
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog as fd
import re
import nltk

def import_log():
    """
    Import a UI log file and return the log DataFrame along with the file path.

    The function opens a file dialog window to allow the user to select a UI log file (in csv, xls, or xlsx format).
    It then reads the selected file using pandas and returns the log DataFrame along with the file path.

    :return: A tuple containing the log DataFrame and the file path of the imported log.
    """
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
# </editor-fold>


# <editor-fold desc="Preprocessing">
def delete_cases(log):
    """
    Delete the 'case' column from the log DataFrame if it exists.
    The 'case' column is the column that splits the log in multiple cases, usually higher level tasks.
    Assumption: If the log is already split into cases, the case id is in the first column of the log.

    :param log: A pandas DataFrame representing the UI log.
    :return: The modified log with the 'case' column removed if it existed.
    """
    if 'case' in log.columns[0]:
        log = log.drop(log.columns[0], axis=1)

    return log


def delete_empty_columns_and_rows(log):
    """
    Delete empty columns and rows from the log.

    This function removes any columns and rows in the log that contain only NaN values.
    It modifies the log in place and returns the modified one.

    :param log: A pandas DataFrame representing the UI log.
    :return: The modified log without empty columns and rows.
    """
    log.dropna(how='all', axis=1, inplace=True) # drop empty columns
    log.dropna(how='all', axis=0, inplace=True) # drop empty rows
    return log


def remove_duplicate_columns(log):
    """
    Remove duplicate columns from the log.

    This function identifies and removes any columns in the log that have the same values as other columns.
    It returns the modified log with duplicate columns removed.

    :param log: A pandas DataFrame representing the UI log.
    :return: The modified log without duplicate columns.
    """
    log = log.T.drop_duplicates().T
    return log


def unify_string_format(log):
    """
    Modifies the string values in a given log to have a consistent format.

    The function iterates over each column and row in the log. For each string value found,
    it checks if the value matches a specific pattern and performs modifications to unify the format.

    :param log: A pandas DataFrame representing the UI log.
    :return: The modified log with unified string format.
    """
    # regex that matches strings consisting of only letters (uppercase or lowercase),
    #  with an optional underscore (_) character in between, and nothing else before or after
    string_regex = '^[A-Za-z]*([_])?[A-Za-z]*$'

    # regex that matches boundaries between lowercase and uppercase letters,
    #  boundaries between non-uppercase and uppercase followed by lowercase letters,
    #   and boundaries between letters and digits or underscores
    camel_underscore_regex = '(?<=[a-z])(?=[A-Z])|(?<![A-Z])(?=[A-Z][a-z])|(?<=[A-Za-z])(?=[0-9]|[_])'

    for column, row in log.iteritems():
        for index, value in row.items():
            # check if the value (without any leading or trailing whitespace) matches the regex pattern
            if re.fullmatch(string_regex, str(value).strip()):
                # remove leading or trailing whitespace from the value
                value = str(value).strip()

                if value is np.NaN:
                    break

                else:
                    # split the value according to the regex pattern
                    term = [word for word in re.split(camel_underscore_regex, value)]
                    # put single words back together with a whitespace
                    new_value = " ".join(term).lower()
                    # remove leading or trailing whitespace from the value
                    new_value = str(new_value).strip()
                    # write the changed value back to the log
                    log.at[index, column] = new_value

    return log


def split_title_camel_case(log):
    """
    Splits the column titles of the log using camel case notation into separate words.
    Each word is converted to lowercase and whitespace is added between the words.

    :param log: A pandas DataFrame representing the UI log.
    :return: Modified log with updated column titles
    """
    # create dictionary to store the column names in
    new_col_titles = {}

    # regex that matches periods,
    #  points where a lowercase letter is followed by an uppercase letter,
    #   points where a non-uppercase letter is followed by an uppercase letter and a lowercase letter,
    #    and points where a letter is followed by a digit
    regex = '[.]|(?<=[a-z])(?=[A-Z])|(?<![A-Z])(?=[A-Z][a-z])|(?<=[A-Za-z])(?=[0-9])'

    for col in log.columns:
        # split the column title into separate words
        term = [word for word in re.split(regex, col)]
        # put single words back together with a whitespace
        new_col_title = " ".join(term).lower()

        # remove leading or trailing whitespace from the value
        new_col_title = new_col_title.strip()
        # store the new column name in the dictionary
        new_col_titles[col] = new_col_title

    # rename the columns using the new names in the dictionary
    log = log.rename(columns=new_col_titles)

    return log


def replace_nan_strings_with_nan(log):
    """
    Replaces 'nan' strings and empty strings with np.NaN,
    so these values can be recognized as proper NaN values later on.

    :param log: A pandas DataFrame representing the UI log.
    :return: Modified log with proper np.NaN values.
    """

    log.replace('nan', np.NaN, inplace=True) # replace string 'nan'
    log.replace('', np.NaN, inplace=True) # replace empty strings
    log = log.fillna(value=np.NaN) # replace None

    return log
# </editor-fold>


def get_unique_value_ratio(log):
    """
    Counts how many unique values there are per column and calculates a ratio (unique_values/total_number_of_values).

    :param log: A pandas DataFrame representing the UI log.
    :return: A dictionary holding the calculated uniqueness-ratio for each column.
    """
    # dictionary to save ratio of how many unique values there are per column
    ratio_dictionary = {}

    # count unique values and total number of values for each column
    for index, column in enumerate(log.columns):
        number_unique_values = log[column].nunique() # unique values per column
        number_values = log[column].count() # total values per column
        ratio_unique = number_unique_values / number_values
        ratio_dictionary.setdefault(index, ratio_unique)

    return ratio_dictionary


def move_column(log, current_column_name, column_index_goal, new_column_name):
    """
    Moves a column of a log to a different position in the log.

    :param log: A pandas DataFrame representing the UI log.
    :param current_column_name: Name of the column that is supposed to be moved.
    :param column_index_goal: Column index of the log the column shall be moved to.
    :param new_column_name: Column name the moved column shall receive.
    :return: Modified log with the selected column renamed and moved to its new position.
    """
    # remove selected column from the log
    column = log.pop(current_column_name)
    # insert selected column at new position with new name
    log.insert(column_index_goal, new_column_name, column)

    return log


def find_element_types(log, ratio_threshold, ratio_dictionary, comparison_dictionary, element_type_dictionary=None):
    """
    Identifies the element types present in columns of a log dataset based on provided dictionaries.

    :param log: A pandas DataFrame representing the UI log.
    :param ratio_threshold: A float indicating the threshold value for the uniqueness-ratio.
    :param ratio_dictionary: A dictionary mapping column indices to uniqueness-ratio values.
    :param comparison_dictionary: A dictionary mapping element types to their corresponding synonyms.
    :param element_type_dictionary: An optional dictionary mapping values to their element types.
    :return: A tuple containing the match count dictionary and the element type dictionary.
    """
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


def find_event_column(log, ratio_dictionary, action_labels, ratio_threshold):
    """
    Recognizes the event or activity column of the log.
    Assumption: every UI log has some sort of event or activity column.

    :param log: A pandas DataFrame representing the UI log.
    :param ratio_dictionary: A dictionary mapping column indices to uniqueness-ratio values.
    :param action_labels: A pandas DataFrame holding action labels.
    :param ratio_threshold: A float indicating the threshold value for the uniqueness-ratio.
    :return: Modified log with the event column renamed to 'event' and moved to the first position in the log.
    """
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

    # get the indices of the columns that have been recognized as potential activity columns
    keys = activity_match_count_dictionary.keys()


    if len(keys) == 1:
        col = list(keys)

        # move the column to the first position in the log
        log = move_column(log, col[0], 0, 'event')

        return log

    # ask user to identify the event column if there are several columns to choose from
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
def extract_activity(log, event_column_index):
    """
    Splits events into their activities and object types.

    :param log: A pandas DataFrame representing the UI log.
    :param event_column_index: Column index of the event column.
    :return: Modified log with the event column split into an activity and a main ui object type column.
    """
    # rename column
    log.rename({event_column_index: "event"})

    # split strings on whitespace and expand them into separate columns in a new df
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
    # column will be empty, so it should be removed
    log = delete_empty_columns_and_rows(log)

    return log


def get_column_completeness(log, threshold_compl):
    """
    Determines the completeness of the log per column and saves columns passing the set threshold in a dictionary.
    :param log: A pandas DataFrame representing the UI log.
    :param threshold_compl: A float indicating the threshold value for the completeness-ratio.
    :return: A dictionary holding the completeness-ratio of the log per column for the columns passing the set threshold.
    """
    # dictionary to save columns with a high completeness rate
    col_compl_dict = {}

    for index, column in enumerate(log.columns):
        non_nan_values = log[column].count() # number of non-NaN values per column
        row_count = len(log) # number of rows in the log
        ratio = non_nan_values / row_count

        # if threshold fulfilled, add column index and the ration to the dictionary
        if ratio >= threshold_compl:
            col_compl_dict.setdefault(index, ratio)

    return col_compl_dict


def find_constant_columns(log):
    """
    Identifies constant columns in the log.
    Constant columns are columns that have the same value in every row.
    :param log: A pandas DataFrame representing the UI log.
    :return: A list of column indices, where the columns are constant.
    """
    constant_columns = []

    for column in log.columns:
        # check if a column has only one unique value
        if len(log[column].unique()) == 1:
            col_index = log.columns.get_loc(column)
            constant_columns.append(col_index)

    return constant_columns


def find_user_related_cols(log):
    """
    Finds columns that have 'user' in their title.

    :param log: A pandas DataFrame representing the UI log.
    :return: A dictionary with column indices as keys and column titles including the word 'user' as values.
    """
    user_columns = {}

    # loop over every word that is part of a header to find matches in the ui object type dictionary
    for index, header_word in enumerate(log.columns):
        words = header_word.split()
        for word in words:
            if word == 'user':
                user_columns.setdefault(index, header_word)

    return user_columns


def find_element_types_in_headers(log, synonym_dictionary):
    """
    Recognizes element types from a log's column titles
    :param log: A pandas DataFrame representing the UI log.
    :param synonym_dictionary: A dictionary including element types and their synonyms.
    :return: A dictionary including element types and their respective name in the log's titles.
    """
    # create dictionary to save element types and their name in the log
    header_element_types = {}

    # loop over every word that is part of a header to find matches in the ui object type dictionary
    for index, header_word in enumerate(log.columns):
        words = header_word.split() # splits string into a list of individual words
        for word in words:
            for key, value_list in synonym_dictionary.items():
                if word in value_list or word == key:
                    header_element_types[index] = key

    return header_element_types


def categorize_col_as_att(dictionary, column_type_dictionary=None):
    """
    Categorized columns included in the dictionary as 'value attribute', 'context attribute', or 'attribute'.
    :param dictionary: A dictionary including the columns that are supposed to be categorized as attribut type columns.
    :param column_type_dictionary: A dictionary saving the column type of each column.
    :return: A dictionary saving the column type of each column.
    """
    # if dictionary to save column types per column does not exist yet create one
    if column_type_dictionary is None:
        column_type_dictionary = {}

    for key, value in dictionary.items():
        # if the word 'value' is included, the column type should be 'value attribute'
        if value == 'input value':
            column_type_dictionary.setdefault(key, 'value attribute')
        # if the word 'id' is included, the column type is likely 'context attribute'
        elif 'id' in value:
            column_type_dictionary.setdefault(key, 'context attribute')
        else:
            column_type_dictionary.setdefault(key, 'attribute')

    return column_type_dictionary


def get_obj_type_based_on_att(header_att_types, att_to_obj_dict):
    """
    Identifies the object types that match the found attribute types according to the provided dictionary.

    :param header_att_types: Dictionary including the attribute type recognized in the column headers and the column indices.
    :param att_to_obj_dict: Dictionary mapping UI attribute types to UI object types.
    :return: A dictionary the column indices and the object types according to the matched attribute types.
    """
    # dictionary to save the column indices and the object types according to the matched attribute types
    header_obj_type_from_att_type = {}

    # get the object types that match the found attribute types according to the mapping dictionary
    for key1, value1 in header_att_types.items():
        for key2, values2 in att_to_obj_dict.items():
            if value1 in values2:
                if key1 not in header_obj_type_from_att_type:
                    header_obj_type_from_att_type[key1] = [key2]
                # some attributes can belong to different object types
                else:
                    header_obj_type_from_att_type[key1].append(key2)

    return header_obj_type_from_att_type


def rearrange_col_type_dicts(header_obj_types, header_obj_type_from_att_type, column_indices):
    """
    Re-organize the dictionaries holding information on the column types based on the column headers.

    :param header_obj_types: Dictionary holding column indices and object types related to the columns headers.
    :param header_obj_type_from_att_type: Dictionary holding column indices and attribute types related to the columns headers.
    :param column_indices: A list of column indices where the column type has not been identified yet.
    :return: A tuple consisting of:
                - a dictionary including object type related columns,
                - a list with columns that have not been assigned a type yet
                - a dictionary with the column indices and lists of potential object types.
    """
    # dictionary including attribute columns where the object type is already known
    ui_obj_att_cols = {}

    # list with keys that should be removed from the dictionary
    keys_to_remove = []

    # concatenate columns where the object type is certain in the ui_obj_att_cols dictionary
    for key, value in header_obj_types.items():
        if key in header_obj_type_from_att_type and value in header_obj_type_from_att_type[key]:
            ui_obj_att_cols[key] = value
            keys_to_remove.append(key)

    # handle columns in header_obj_from_att_type with only one value for a key
    for key, value in header_obj_type_from_att_type.items():
        if len(value) == 1 and key not in ui_obj_att_cols:
            ui_obj_att_cols[key] = value[0]
            keys_to_remove.append(key)

    # remove column indices that have been moved to the new dictionary from the original one
    for key in keys_to_remove:
        del header_obj_type_from_att_type[key]
        column_indices.remove(key)

    return ui_obj_att_cols, column_indices, header_obj_type_from_att_type


def check_for_regex(log, regex):
    """
    Recognizes values that follow a certain regex structure.

    :param log: A pandas DataFrame representing the UI log.
    :param regex: A regular expression representing a specific pattern
    :return: A dictionary storing the number of values per column that match the regex pattern.
    """
    # create a dictionary to store the number of values per column that match the regex pattern
    match_count_dictionary = {}

    for column, row in log.iteritems():
        count = 0 # count variable to count how many values match the regex

        for value in row:
            if re.fullmatch(regex, str(value)):
                count += 1

        column_index = log.columns.get_loc(column) # get the columns index

        # add values to the dictionary
        if count != 0:
            match_count_dictionary.setdefault(column_index, count)

    return match_count_dictionary


def rename_timestamp_col(log, column_type_dictionary):
    """
    Renames the timestamp column of the log.
    :param log: A pandas DataFrame representing the UI log.
    :param column_type_dictionary: A dictionary saving the column type of each column.
    :return: Modified log with the renamed timestamp column.
    """
    for index in column_type_dictionary:
        if 'timestamp' in column_type_dictionary[index]:
            log = log.rename(columns={log.columns[index]: 'timestamp'})

    return log


def get_column_types(log, column_type_dictionary, column_indices, col_compl_dict, ratio_dictionary, threshold_timestamp,
                     threshold_cont_att, threshold_val_att, ui_object_match_count_dictionary,
                     timestamp_match_count_dictionary, url_match_count_dictionary, mail_match_count_dictionary):
    """
    Assigns a column type to each column.

    :param log: A pandas DataFrame representing the UI log.
    :param column_type_dictionary: A dictionary saving the column type of each column.
    :param column_indices: A list of column indices where the column type has not been identified yet.
    :param col_compl_dict: A dictionary to save columns with a high completeness rate.
    :param ratio_dictionary: A dictionary mapping column indices to uniqueness-ratio values.
    :param threshold_timestamp: A float indicating the threshold value for the uniqueness-ratio for the timestamp column.
    :param threshold_cont_att: A float indicating the threshold value for the uniqueness-ratio for context attribute columns.
    :param threshold_val_att: A float indicating the threshold value for the uniqueness-ratio for value attribute columns.
    :param ui_object_match_count_dictionary: A dictionary including ui object types and their count per column.
    :param timestamp_match_count_dictionary: A dictionary including the number of timestamps recognized and their column.
    :param url_match_count_dictionary: A dictionary including the number of urls recognized and their column.
    :param mail_match_count_dictionary: A dictionary including the number of mails recognized and their column.
    :return: A tuple consisting of the potentially modified log and a dictionary saving the column type of each column.
    """
    # counter, since there can only be one 'main ui object type' column holding the ui object interacted with
    main_ui_obj_type_counter = 0

    # we know where the activity column is because the 'find_event_column' function puts it in the first position
    column_type_dictionary.setdefault(0, 'activity')
    column_indices.remove(0) # remove index from the list because a type has been assigned

    # if there was an event column, which has been split by the 'extract_activity' function, then the ui object
    # types are in the second position
    if log.columns[1] == 'main ui object type':
        column_type_dictionary.setdefault(1, 'main ui object type')
        column_indices.remove(1) # remove this index from the list because a type has been assigned
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
                        # move the column to the second position in the log
                        log = move_column(log, col, 1, 'main ui object type')
                        # assign type to the column
                        column_type_dictionary.setdefault(1, 'main ui object type')
                        # remove this index from the list because a type has been assigned
                        column_indices.remove(col)
                        # set the counter, so no more columns can be identified as main ui object type columns
                        main_ui_obj_type_counter += 1
                    else:
                        # assign type to the column
                        column_type_dictionary.setdefault(col, 'ui object type')
                        # remove this index from the list because a type has been assigned
                        column_indices.remove(col)
        else:
            # ask user to identify the ui object type column
            while True:
                try:
                    print(log.head())
                    main_ui_obj_column = int(input(
                        "Please enter the index of the log's column holding the ui object type to which the activity belongs"
                        " assuming that the first column has the index 0:"))

                    # move the column to the second position in the log
                    log = move_column(log, main_ui_obj_column, 1, 'main ui object type')

                except ValueError:
                    print("Sorry, this value cannot be accepted. Please enter a number.")
                    # return to the start of the loop
                    continue
                else:
                    if 0 <= main_ui_obj_column <= len(log.columns):
                        # exit the loop.
                        break
                    else:
                        # return to the start of the loop
                        continue

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

    # if urls are found assume this column includes attribute values and the column header is a context attribute type
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

    # if urls are found assume this column includes attribute values and the column header is a value attribute type
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
                # if there a timestamp column has already been recognized, 'timestamp' can't be assigned to additional columns
                if 'timestamp' in column_type_dictionary.values():
                    possible_values = ['ui object type', 'value attribute', 'context attribute']
                else:
                    possible_values = ['ui object type', 'value attribute', 'context attribute', 'timestamp']
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

    # call function to rename the timestamp column
    log = rename_timestamp_col(log, column_type_dictionary)

    # sort the dictionary, so the columns are in the right order
    column_type_dictionary = dict(sorted(column_type_dictionary.items()))

    return log, column_type_dictionary


def get_unique_values_per_col(log):
    """
    Lists unique values per column.

    :param log: A pandas DataFrame representing the UI log.
    :return: A dictionary listing unique values per column.
    """
    # dictionary to save the unique values of each column
    unique_dictionary = {}

    # save unique values
    for col in log:
        unique_list = log[col].unique()
        unique_list = [value for value in unique_list if value is not np.NaN]
        unique_dictionary[col] = unique_list

    return unique_dictionary


def complete_element_type_dictionary(column_type_dictionary, unique_dictionary, element_type_dictionary, element_type):
    """
    Adds missing element types to the element type dictionary.

    :param column_type_dictionary: A dictionary saving the column type of each column.
    :param unique_dictionary: A dictionary listing unique values per column.
    :param element_type_dictionary: A dictionary mapping values to their element types.
    :param element_type: A string indicating the element type.
    :return: A dictionary mapping values to their element types.
    """

    keys = [key for key, value in column_type_dictionary.items() if element_type in value]
    for key in keys:
        value_list = list(unique_dictionary.values())[key]
        for value in value_list:
            element_type_dictionary.setdefault(value, value)

    return element_type_dictionary


def save_col_index_of_col_types(column_type_dictionary, user_cols):
    """
    Saves the column indices of the different element types in separate lists.

    :param user_cols: A dictionary holding the column indices that are related to columns that have 'user' in their title.
    :param column_type_dictionary: A dictionary saving the column type of each column.
    :return: A tuple of different lists saving the column indices per element type.
    """
    # lists to save column indices of different column types
    cont_att_cols = []
    val_att_cols = []
    obj_type_cols = []
    main_obj_type_cols = []

    # list collecting all of the indices
    selected_cols = []

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

    # the user columns are not relevant to identify the ui object instances
    for col in user_cols:
        selected_cols.remove(col)

    # sort list, so columns stay in the right order
    selected_cols.sort()

    return selected_cols, cont_att_cols, val_att_cols, obj_type_cols, main_obj_type_cols


def get_potential_process_obj_cols(cont_att_cols, url_match_count_dictionary):
    """
    Retrieves columns that potentially include process objects.

    :param cont_att_cols: List of columns of type context attribute.
    :param url_match_count_dictionary: Dictionary including columns that include urls.
    :return: A list of column indices, where the columns potentially include process objects.
    """
    # dictionary to save column indices potentially including process object types
    pot_process_obj_cols = []

    for col in cont_att_cols:
        pot_process_obj_cols.append(col)

    # columns including urls are unlikely to include process object types
    for col in url_match_count_dictionary:
        pot_process_obj_cols.remove(col)

    return pot_process_obj_cols


# find process object types in the log; only the context attribute columns are interesting here
def find_process_objects(log, cont_att_cols, nouns):
    """
    Recognizes process objects in the log.

    :param log: A pandas DataFrame representing the UI log.
    :param cont_att_cols: List of columns of type context attribute.
    :param nouns: A pandas DataFrame including nouns.
    :return: A dictionary with row indices as keys and a list of process objects included in that row as values.
    """
    # regex that recognized camel case
    camel_underscore_regex = '(?<=[a-z])(?=[A-Z])|(?<![A-Z])(?=[A-Z][a-z])|(?<=[A-Za-z])(?=[0-9]|[_]|[.]|[-])'

    # dictionary to save the process object types and their row index
    process_obj_dict = {}

    for row_index, row in log.iloc[:, cont_att_cols].iterrows():
        # list for the ui objects
        process_obj_list = []
        # loop over column values
        for col_name, value in row.iteritems():

            # unify the string format first
            value = str(value).strip()
            if value is np.NaN:
                break
            else:
                term = [word for word in re.split(camel_underscore_regex, value)]
                new_value = " ".join(term).lower()
                str(new_value).strip()

            stem_value = nltk.stem.WordNetLemmatizer().lemmatize(str(new_value))

            # check if the value is in the noun list
            if stem_value in nouns:
                if value not in process_obj_list:
                    process_obj_list.append(value)

        if len(process_obj_list) != 0:
            process_obj_dict.setdefault(row_index, process_obj_list)

    return process_obj_dict


def combine_ui_obj_type_dicts(ui_obj_att_cols, att_cols_obj_unclear):
    """
    Combines two
    :param ui_obj_att_cols: A dictionary including object type related columns.
    :param att_cols_obj_unclear: A dictionary with the column indices and lists of potential object types.
    :return: A dictionary including all columns related to ui objects except for the main ui object one and
                the ui object types.
    """
    # combine the ui object type dictionaries in one dictionary
    other_ui_obj_cols = {}

    for key, value in ui_obj_att_cols.items():
        other_ui_obj_cols[key] = value if isinstance(value, list) else [value]

    for key, value in att_cols_obj_unclear.items():
        other_ui_obj_cols[key] = value if isinstance(value, list) else [value]

    return other_ui_obj_cols


def get_unmatched_att_cols(cont_att_cols, val_att_cols, ui_obj_att_cols, att_cols_obj_unclear, user_cols):
    """
    Identifies columns that have not been assigned to an object type yet.

    :param cont_att_cols: List of columns of type context attribute.
    :param val_att_cols: List of columns of type value attribute.
    :param ui_obj_att_cols: A dictionary including object type related columns.
    :param att_cols_obj_unclear: A dictionary with the column indices and lists of potential object types.
    :param user_cols: A dictionary holding the column indices that are related to columns that have 'user' in their title.
    :return: List of column indices of columns that have not not been assigned to an object type yet.
    """
    # columns including attribute types that are not associated with an object type yet
    unmatched_att_list = cont_att_cols + val_att_cols

    for index in ui_obj_att_cols.keys():
        if index in unmatched_att_list:
            unmatched_att_list.remove(index)

    for index in att_cols_obj_unclear.keys():
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


def identify_obj_inst_and_hrchy(log, selected_cols, val_att_cols, cont_att_cols, obj_type_cols,
                                ui_object_type_dictionary, obj_highest_level, obj_second_level, obj_third_level,
                                obj_fourth_level):
    # dictionary to save object instances and their unique identifiers
    object_instances_dict = {}

    # counter to assign ids to the object instances
    obj_counter = 0

    # create variables to hold the last seen object instance of each object hierarchy
    #last_app_inst = np.nan
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
            if 'main ui object type' in col_name and value is not np.NaN:
                object_type = value
            # for the value attribute columns, save the column title in the list
            if col_index in val_att_cols and value is not np.NaN:
                att_list.append(col_name)
                att_val_combi_list.append(value)
            # for the context attribute columns save the column value in the list
            if col_index in cont_att_cols and value is not np.NaN:
                att_list.append(value)
                att_val_combi_list.append(value)
                # list additional ui object types
            if col_index in obj_type_cols and value is not np.NaN:
                ui_obj_list.append(value)

        # depending on the hierarchy level: add more values to the list to identify object instances
        # add highest level object instance to list (for all but highest level objects)
        if object_type in ui_object_type_dictionary and ui_object_type_dictionary[object_type] not in obj_highest_level:
            if last_high_obj_inst is not np.NaN:
                att_list.append(last_high_obj_inst)
        # add second level object instance to the list (for all third level objects)
        if object_type in ui_object_type_dictionary and ui_object_type_dictionary[object_type] in obj_third_level:
            if last_second_obj_inst is not np.NaN:
                att_list.append(last_second_obj_inst)
        # add third level object instance to the list (for all fourth level objects)
        if object_type in ui_object_type_dictionary and ui_object_type_dictionary[object_type] in obj_fourth_level:
            if last_third_obj_inst is not np.NaN:
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
            if last_second_obj_inst is not np.NaN:
                log.loc[index, 'part of'] = last_second_obj_inst
            else:
                log.loc[index, 'part of'] = last_high_obj_inst
        elif object_type in ui_object_type_dictionary and ui_object_type_dictionary[object_type] in obj_fourth_level:
            if last_third_obj_inst is not np.NaN:
                log.loc[index, 'part of'] = last_third_obj_inst
            elif last_second_obj_inst is not np.NaN:
                log.loc[index, 'part of'] = last_second_obj_inst
            else:
                log.loc[index, 'part of'] = last_high_obj_inst
        else:
            log.loc[index, 'part of'] = last_high_obj_inst

    return log


# function to get all keys that match a target_value
def find_matching_pairs(dictionary):
    """
     Finds matching keys based on their corresponding values in the input dictionary and returns a dictionary
     where the keys are unique values and the values are lists of keys associated with those values.

    :param dictionary: A dictionary where some keys have potentially the same values.
    :return: A dictionary where the keys are unique values and the values are lists of keys associated with those values.
    """
    # dictionary that helps swapping keys with values
    value_to_keys = {}

    # dictionary to save the final matching keys and values in
    matching_pairs = {}

    for key, value in dictionary.items():
        if value not in value_to_keys:
            value_to_keys[value] = [key]
        else:
            value_to_keys[value].append(key)

    for value, keys in value_to_keys.items():
        matching_pairs[value] = keys

    return matching_pairs


def find_lowest_value(dictionary):
    """
    Finds the lowest value in a dictionary and returns its key.

    :param dictionary: A dictionary where the lowest value is supposed to be found in.
    :return: A string, which is the key associated with the lowest value in the dictionary.
    """
    # initialize with float('inf'), so first value encountered will be smaller and will be updated
    min_value = float('inf')
    min_obj = None

    # loop over the values and save the smallest one
    for key, values in dictionary.items():
        for value in values:
            if value < min_value:
                min_obj = key

    return min_obj


def determine_hierarchy_level(object_type, object_hierarchy):
    """
    Determines the object type hierarchy level of an input object type.

    :param object_type: A UI object type.
    :param object_hierarchy: A dictionary specifying the typical ui object hierarchy
    :return: A string indicating one of four hierarchy levels ('obj_highest_level', 'obj_second_level',
                'obj_third_level', 'obj_fourth_level')
    """
    obj_level = None

    # check to which hierarchy level the object type belongs
    for level, obj_values in object_hierarchy.items():
        if object_type in obj_values:
            obj_level = level

    # if no level can be assigned, assign the lowest level
    if obj_level is None:
        obj_level = 'obj_fourth_level'

    return obj_level


