#!/usr/bin/env python
# coding: utf-8

# <editor-fold desc="Imports">
import os
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog as fd
import re
import nltk
from nltk.corpus import wordnet
import copy
import json


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
class WordCounter:
    def __init__(self):
        self.counts = {}

    def get_next_count(self, word):
        if word in self.counts:
            self.counts[word] += 1
        else:
            self.counts[word] = 1
        return self.counts[word]

counter = WordCounter()

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
    camel_underscore_regex = r'(?<=[a-z])(?=[A-Z])|_'


    for column, row in log.items():
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


def unify_nan_values(log):
    """
    Replaces 'nan' strings and empty strings with np.NaN,
    so these values can be recognized as proper NaN values later on.

    :param log: A pandas DataFrame representing the UI log.
    :return: Modified log with proper np.NaN values.
    """

    log.replace('nan', np.NaN, inplace=True) # replace string 'nan'
    log.replace('', np.NaN, inplace=True) # replace empty strings
    log.fillna(value=np.NaN, inplace=True) # replace None

    return log
# </editor-fold>


# <editor-fold desc="1. Column Type Classification">
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

    event_column_found = None # flag to track if the event column has been found

    # loop over the column headers and match them against strings to identify the event column of the log
    for col in log.columns:

        # check if any column headers indicate the event column
        if any(string in col for string in event_strings):
            # move the column to the first position in the log
            log = move_column(log, col, 0, 'event')
            event_column_found = True # set flag to True
            break

    # if flag still false (event column not found yet)
    if event_column_found is None:
        # compare the log values to the action label dataset to see if a column matches some of the labels
        activity_match_count_dictionary, activity_type_dictionary = find_element_types(log, ratio_threshold,
                                                                                       ratio_dictionary, action_labels)

        # get the indices of the columns that have been recognized as potential activity columns
        keys = activity_match_count_dictionary.keys()

        # if only one column has the potential to be the event column
        if len(keys) == 1:
            col = list(keys)

            # move the column to the first position in the log
            log = move_column(log, col[0], 0, 'event')

        # ask user to identify the event column if there are several columns to choose from
        else:
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


def extract_activity(log, event_column_index, action_labels):
    """
    Splits events into their activities and object types.

    :param log: A pandas DataFrame representing the UI log.
    :param event_column_index: Column index of the event column.
    :param action_labels: DataFrame with action labels.
    :return: Modified log with the event column split into an activity and a main ui object type column.
    """
    # rename column
    log.rename({event_column_index: "event"})

    # split strings on whitespace and expand them into separate columns in a new df
    split_results = log.iloc[:, event_column_index].str.split(' ').apply(pd.Series)

    # if there is only one word included, assume it is the activity
    if len(split_results.columns) == 1:
        log.insert(1, 'activity', split_results[0]) #figure our how to address tuple in list/col

    elif len(split_results.columns) > 3:
        raise ValueError("An event column should not have more than three words as a value. Please adjust your log.")

    # if the event consists of only two parts assume the first word is the activity and the second one the object type
    else:
        log.insert(1, 'activity', '')
        log.insert(2, 'main ui object type', '')

        for index, row in split_results.iterrows():
            if len(split_results.columns) == 2:
                if split_results.loc[index, 0] in action_labels['Action labels'].values:
                    if is_dictionary_noun(split_results.loc[index, 1]):
                        log.loc[index, 'activity'] = split_results.loc[index, 0]
                        log.loc[index, 'main ui object type'] = split_results.loc[index, 1]
                    # if no object is given
                    elif not split_results.loc[index, 1]:
                        log.loc[index, 'activity'] = split_results.loc[index, 0]
                        log.loc[index, 'main ui object type'] = split_results.loc[index, 1]
                    else:
                        log.loc[index, 'activity'] = split_results.loc[index, 0] + ' ' + split_results.loc[
                            index, 1]

                elif split_results.loc[index, 1] in action_labels['Action labels'].values:
                    if is_dictionary_noun(split_results.loc[index, 0]):
                        log.loc[index, 'activity'] = split_results.loc[index, 1]
                        log.loc[index, 'main ui object type'] = split_results.loc[index, 0]
                    # if no object is given
                    elif not split_results.loc[index, 0]:
                        log.loc[index, 'activity'] = split_results.loc[index, 1]
                        log.loc[index, 'main ui object type'] = split_results.loc[index, 0]
                    else:
                        log.loc[index, 'activity'] = split_results.loc[index, 1] + ' ' + split_results.loc[index, 0]
                # else assume the activity comes first and is followed by the ui obj
                else:
                    log.loc[index, 'activity'] = split_results.loc[index, 0]
                    log.loc[index, 'main ui object type'] = split_results.loc[index, 1]

            elif len(split_results.columns) == 3:
                if split_results.loc[index, 0] in action_labels['Action labels'].values:
                    if is_dictionary_noun(split_results.loc[index, 2]):
                        if is_dictionary_noun(split_results.loc[index, 1]):
                            log.loc[index, 'activity'] = split_results.loc[index, 0]
                            log.loc[index, 'main ui object type'] = split_results.loc[index, 1] + ' ' + split_results.loc[index, 2]
                        else:
                            log.loc[index, 'activity'] = split_results.loc[index, 0] + ' ' + split_results.loc[index, 1]
                            log.loc[index, 'main ui object type'] = split_results.loc[index, 2]

                if split_results.loc[index, 1] in action_labels['Action labels'].values:
                    if is_dictionary_noun(split_results.loc[index, 0]):
                        log.loc[index, 'activity'] = split_results.loc[index, 1] + ' ' + split_results.loc[index, 2]
                        log.loc[index, 'main ui object type'] = split_results.loc[index, 0]
                    elif is_dictionary_noun(split_results.loc[index, 0]):
                        log.loc[index, 'activity'] = split_results.loc[index, 0] + ' ' + split_results.loc[index, 1]
                        log.loc[index, 'main ui object type'] = split_results.loc[index, 2]

                if split_results.loc[index, 2] in action_labels['Action labels'].values:
                    if is_dictionary_noun(split_results.loc[index, 0]):
                        if is_dictionary_noun(split_results.loc[index, 1]):
                            log.loc[index, 'activity'] = split_results.loc[index, 2]
                            log.loc[index, 'main ui object type'] = split_results.loc[index, 0] + ' ' + split_results.loc[index, 1]
                        else:
                            log.loc[index, 'activity'] = split_results.loc[index, 1] + ' ' + split_results.loc[index, 2]
                            log.loc[index, 'main ui object type'] = split_results.loc[index, 0]

                # else assume the activity comes first and is followed by the ui obj
                else:
                    log.loc[index, 'activity'] = split_results.loc[index, 0] + ' ' + split_results.loc[index, 1]
                    log.loc[index, 'main ui object type'] = split_results.loc[index, 2]

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
    :param column_type_dictionary: An optional dictionary saving the column type of each column.
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

    for column, row in log.items():
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
                # check if column includes nearly 100% unique values, since every timestamp in a log should be unique
                if ratio_dictionary[col] >= threshold_timestamp:
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
        elif ratio_dictionary[col] >= threshold_val_att:
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

    if pot_process_obj_cols:
        # columns including urls are unlikely to include process object types
        for col in url_match_count_dictionary:
            pot_process_obj_cols.remove(col)

    return pot_process_obj_cols


def create_new_row_process_obj_df(log, obj_type, log_row_index, obj_inst, process_obj_df, user_cols=None):
    """
    Adds a new row to the input DataFrame and populates it with input values.
    It also adds additional columns to the df if they don't exist, assigns attribute values to the corresponding columns,
    and removes the values from the log.

    :param log: A pandas DataFrame representing the UI log.
    :param obj_type: String with the object type.
    :param log_row_index: Row index of the log.
    :param obj_inst: String with the object instance.
    :param process_obj_df: DataFrame including object instances other than the main object instances.
    :param user_cols: Optional dictionary with indices of the attribute columns that are user-related and the column titles.
    :return: Tuple of the modified df, log, and lists of columns in the df that are of type value and context attribute.
    """
    # get index of the new row
    new_row_index = len(process_obj_df)

    process_obj_df.at[new_row_index, 'row index'] = log_row_index
    process_obj_df.at[new_row_index, 'object instance'] = obj_inst
    process_obj_df.at[new_row_index, 'object type'] = obj_type

    if user_cols is not None:
        for log_col_index in user_cols.keys():
            column_title = log.columns[log_col_index]
            attribute_value = log.iloc[log_row_index, log_col_index]
            # if the column title does not exist in the df, add it
            if column_title not in process_obj_df.columns:
                process_obj_df[column_title] = None

            # add the value to the df
            process_obj_df.at[new_row_index, column_title] = attribute_value

            # remove the value from the log
            log.iloc[log_row_index, log_col_index] = np.NaN

    return process_obj_df, log

def is_dictionary_noun(word):
    """

    :param word:
    :return:
    """
    synsets = wordnet.synsets(word)

    return any(synset.pos() in ['n', 'N'] for synset in synsets)


# find process object types in the log; only the context attribute columns are interesting here
def find_process_objects(log, cont_att_cols, process_obj_df, excluded_words):
    """
    Recognizes process objects in the log.

    :param excluded_words:
    :param log: A pandas DataFrame representing the UI log.
    :param cont_att_cols: List of columns of type context attribute.
    :param process_obj_df: A pandas DataFrame for the process objects found in the log.
    :return: A dictionary with row indices as keys and a list of process objects included in that row as values.
    """
    # regex that recognized camel case
    camel_underscore_regex = '(?<=[a-z])(?=[A-Z])|(?<![A-Z])(?=[A-Z][a-z])|(?<=[A-Za-z])(?=[0-9]|[_]|[.]|[-])'

    process_obj_inst_dict = {}

    for row_index, row in log.iloc[:, cont_att_cols].iterrows():
        # list for the ui objects
        process_obj_list = []

        # loop over column values
        for col_name, value in row.items():

            if pd.isna(value):
                break
            else:
                value = str(value).strip() # unify the string format first
                term = [word for word in re.split(camel_underscore_regex, value)]
                new_value = " ".join(term).lower()
                str(new_value).strip()

            stem_value = nltk.stem.WordNetLemmatizer().lemmatize(str(new_value))

            if is_dictionary_noun(stem_value) and value not in excluded_words:
                if value not in process_obj_list:
                    process_obj_list.append(value)
                    process_obj_inst_dict.setdefault(value, f'{value}_{counter.get_next_count(value)}')

        for process_obj in process_obj_list:
            process_obj_inst = process_obj_inst_dict[process_obj]
            # call function to create a new row in the process_obj_df
            process_obj_df, log = create_new_row_process_obj_df(log, process_obj, row_index, process_obj_inst, process_obj_df)

    return process_obj_df


def combine_ui_obj_type_dicts(ui_obj_att_cols, att_cols_obj_unclear):
    """
    Combines two dictionaries in one.
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
    """
    Categorizes the ui object types found in the log and saves them in separate dictionaries.

    :param other_ui_obj_cols: A dictionary with column indices as keys and object types as values.
    :param object_hierarchy: A dictionary specifying the typical ui object hierarchy.
    :return: A tuple of the dictionaries including the column indices and object types per hierarchy level.
    """
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
# </editor-fold>


# <editor-fold desc="2. Object Recognition">
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
    :param object_hierarchy: A dictionary specifying the typical ui object hierarchy.
    :return: A string indicating one of four hierarchy levels ('obj_highest_level', 'obj_second_level',
                'obj_third_level', 'obj_fourth_level').
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


def check_value_availability(log, dictionary, row_index):
    """
    Checks if values from the input dictionary are given in the respective cell of the input log.

    :param log: A pandas DataFrame representing the UI log.
    :param dictionary: A dictionary with object types as keys and column indices as values.
    :param row_index: Row index of the input log.
    :return: A dictionary with object types available in the log as keys and their column indices in the log as values.
    """
    # dictionary to save object types that have existing attribute values and their column index
    available_obj = {}

    for obj_type, col_indices in dictionary.items():
        col_index_list = []
        for col_index in col_indices:
            if log.iloc[row_index][col_index] is not np.NaN:
                col_index_list.append(col_index)

        if col_index_list:
            available_obj.setdefault(obj_type, col_index_list)

    return available_obj


def get_attribute_values(log, row_index, combined_att_list, val_att_cols, cont_att_cols):
    """
    Saves attribute combination needed to identify object instances in a list.

    :param log: A pandas DataFrame representing the UI log.
    :param row_index: Row index of the input log.
    :param combined_att_list: List with column indices indicating relevant attribute columns.
    :param val_att_cols: List of columns of type value attribute.
    :param cont_att_cols: List of columns of type context attribute.
    :return: A tuple of a list to save the attribute combination needed to identify object instances
                and a list to save the respective column indices.
    """
    # lists to save attributes
    att_list = []

    # list to save the column indices belonging to the attributes
    att_col_indices_list = []

    # loop over the column indices and check if the columns hold value attributes or context attributes
    # append the values to the lists accordingly
    for col_index in combined_att_list:

        cell_value = log.iloc[row_index, col_index]

        # for the context attribute columns save the column value in the list
        if col_index in cont_att_cols and not pd.isna(cell_value):
            att_list.append(log.iloc[row_index, col_index])
            att_col_indices_list.append(col_index)

        # for the value attribute columns save the column title in the list
        elif col_index in val_att_cols and not pd.isna(cell_value):
            att_list.append(log.columns[col_index])
            att_col_indices_list.append(col_index)

    return att_list, att_col_indices_list


def add_higher_hierarchy_instances(log, object_type, att_list, row_index, obj_level, last_web_inst, last_app_inst, last_second_obj_inst,
                                   last_third_obj_inst, obj_is_main, part_of=None):
    """
    Adds object instances of higher hierarchy levels to the attribute combination, so the object instance can be determined.

    :param object_type: String with the object type.
    :param log: A pandas DataFrame representing the UI log.
    :param att_list: A list with the attribute combination needed to identify object instances.
    :param row_index: Row index of the input log.
    :param obj_level:  A string indicating one of four UI object hierarchy levels ('obj_highest_level',
                        'obj_second_level', 'obj_third_level', 'obj_fourth_level')
    :param last_web_inst: A string with the object instance of the last seen website object.
    :param last_app_inst: A string with the object instance of the last seen application object.
    :param last_second_obj_inst: A string with the object instance of the last seen second level object.
    :param last_third_obj_inst: A string with the object instance of the last seen third level object.
    :param obj_is_main: Boolean indicating if the object at question is the main UI object type of the current row.
    :param part_of: An optional string with the last mentioned next higher object instance that the object at question is part of.
                    This parameter is only given for UI object types other than the main UI object type of the row.
    :return: A tuple of a string with the last mentioned next higher object instance (optional),
                a list with the attribute combination needed to identify object instances, and
                the modified log with the part_of-column filled.
    """
    # only add higher levels to the list, if there are already attributes in the list
    if att_list:

        if obj_level == 'obj_highest_level':
            if obj_is_main is None:
                part_of = None

                if object_type == 'website':
                    # check if last_app_inst exists and if it is in the same row
                    if last_app_inst:
                        if row_index == last_app_inst[1]:
                            log.loc[row_index, 'related ui object'] = last_app_inst[0]

                elif object_type == 'application':
                    # check if last_web_inst exists and if it is in the same row
                    if last_web_inst:
                        if row_index == last_web_inst[1]:
                            log.loc[row_index, 'related ui object'] = last_web_inst[0]

        elif obj_level == 'obj_second_level' or obj_level == 'obj_third_level':
            # if list is not empty, append the object instance included in it
            if last_app_inst:
                att_list.append(last_app_inst[0])
                if obj_is_main is True:
                    log.loc[row_index, 'part of'] = last_app_inst[0]

                    # check if last_web_inst exists and if it is in the same row
                    if last_web_inst:
                        if row_index == last_web_inst[1]:
                            log.loc[row_index, 'related ui object'] = last_web_inst[0]
                else:
                    part_of = last_app_inst[0]

            if obj_level == 'obj_third_level':
                # if list is not empty, append the object instance included in it
                if last_second_obj_inst:
                    att_list.append(last_second_obj_inst[0])
                    if obj_is_main is True:
                        log.loc[row_index, 'part of'] = last_second_obj_inst[0]

                        # check if last_web_inst exists and if it is in the same row
                        if last_web_inst:
                            if row_index == last_web_inst[1]:
                                log.loc[row_index, 'related ui object'] = last_web_inst[0]
                    else:
                        part_of = last_second_obj_inst[0]

        elif obj_level == 'obj_fourth_level':
            # if in same row an object instance of third level exists, then have application as first level
            if last_third_obj_inst:
                if row_index == last_third_obj_inst[1]:
                    if last_app_inst:
                        att_list.append(last_app_inst[0])

                    if last_second_obj_inst:
                        att_list.append(last_second_obj_inst[0])

                    att_list.append(last_third_obj_inst[0])
                    if obj_is_main:
                        log.loc[row_index, 'part of'] = last_third_obj_inst[0]

                        # check if last_web_inst exists and if it is in the same row
                        if last_web_inst:
                            if row_index == last_web_inst[1]:
                                log.loc[row_index, 'related ui object'] = last_web_inst[0]
                    else:
                        part_of = last_third_obj_inst[0]

                # if no third level obj instance in same row, then have website as first level
                else:
                    if last_web_inst:
                        att_list.append(last_web_inst[0])
                        if obj_is_main:
                            log.loc[row_index, 'part of'] = last_web_inst[0]

                            # check if last_app_insts exist and if it is in the same row
                            if last_app_inst:
                                if row_index == last_app_inst[1]:
                                    log.loc[row_index, 'related ui object'] = last_app_inst[0]
                        else:
                            part_of = last_web_inst[0]

            # if no third level obj instance have website as first level
            else:
                if last_web_inst:
                    att_list.append(last_web_inst[0])
                    if obj_is_main:
                        log.loc[row_index, 'part of'] = last_web_inst[0]

                        # check if last_app_inst exists and if it is in the same row
                        if last_app_inst:
                            if row_index == last_app_inst[1]:
                                log.loc[row_index, 'related ui object'] = last_app_inst[0]
                    else:
                        part_of = last_web_inst[0]

                # if no website is available, then have application as highest level
                else:
                    if obj_is_main:
                        log.loc[row_index, 'part of'] = last_app_inst[0]

                        # check if last_web_inst exists and if it is in the same row
                        if last_web_inst:
                            if row_index == last_web_inst[1]:
                                log.loc[row_index, 'related ui object'] = last_web_inst[0]
                    else:
                        part_of = last_app_inst[0]

    if obj_is_main is True:
        return att_list, log
    else:
        return part_of, att_list, log


def  get_relevant_att_cols(local_other_ui_obj_cols, unmatched_att_list, value_term):
    """
    Retrieves attribute columns relevant to determine the UI object instance.

    :param local_other_ui_obj_cols: Dictionary with columns related to object types other than the main UI object type;
                                        with indices as keys and object types as values.
    :param unmatched_att_list: List with attribute columns that have not been assigned an object type yet.
    :param value_term: String with the object type of the current object.
    :return: A tuple of a list with all relevant attribute columns and the updated local_other_ui_obj_cols.
    """
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


def generate_key(att_list, object_instances_dict, value):
    """
    Generates a key for a dictionary based on the given attributes and values.

    This key serves as a basis to determine the object instance.

    :param att_list: A list with the attribute combination needed to identify object instances.
    :param object_instances_dict: A dictionary to save the attribute combinations as keys and the object instances as values.
    :param value: A String with the object type currently in question.
    :return: A tuple consisting of the object instance, and the dictionary with all object instances and their keys.
    """
    # remove None values from the list
    att_list = [att for att in att_list if att is not None]

    # if there is more than one value in the list, build a tuple so it can be used as a dictionary key
    if len(att_list) > 1:
        att_combi = tuple(att_list)
        if att_combi not in object_instances_dict:
            object_instances_dict.setdefault(att_combi, f'{value}_{counter.get_next_count(value)}')
        obj_inst = object_instances_dict[att_combi]

    elif len(att_list) == 1:
        att_val = att_list[0]
        if att_val not in object_instances_dict and att_val is not np.NaN:
            object_instances_dict.setdefault(att_val, f'{value}_{counter.get_next_count(value)}')
        obj_inst = object_instances_dict[att_val]

    # if the att_list is empty, no object instance should be created
    else:
        obj_inst = None

    return obj_inst, object_instances_dict


def create_new_row_ui_obj_df(log, obj, log_row_index, obj_inst, part_of, other_ui_obj_df, att_col_indices_list, val_att_cols, cont_att_cols, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols):
    """
    Adds a new row to the input DataFrame and populates it with input values.
    It also adds additional columns to the df if they don't exist, assigns attribute values to the corresponding columns,
    and removes the values from the log.

    :param log: A pandas DataFrame representing the UI log.
    :param obj: String with the object type.
    :param log_row_index: Row index of the log.
    :param obj_inst: String with the object instance.
    :param part_of: String with the object instance the object in question is part of.
    :param other_ui_obj_df: DataFrame including object instances other than the main object instances.
    :param att_col_indices_list: List with indices of the attribute columns that are relevant for the object instance.
    :param val_att_cols: List of columns in the log that are of type value attribute.
    :param cont_att_cols: List of columns in the log that are of type context attribute.
    :param other_ui_obj_df_val_att_cols: List of columns in the df that are of type value attribute.
    :param other_ui_obj_df_cont_att_cols: List of columns in the df that are of type context attribute.
    :return: Tuple of the modified df, log, and lists of columns in the df that are of type value and context attribute.
    """
    # get index of the new row
    new_row_index = len(other_ui_obj_df)

    other_ui_obj_df.at[new_row_index, 'row index'] = log_row_index
    other_ui_obj_df.at[new_row_index, 'object instance'] = obj_inst
    other_ui_obj_df.at[new_row_index, 'object type'] = obj
    other_ui_obj_df.at[new_row_index, 'part of'] = part_of

    for log_col_index in att_col_indices_list:
        column_title = log.columns[log_col_index]
        attribute_value = log.iloc[log_row_index, log_col_index]
        # if the column title does not exist in the df, add it
        if column_title not in other_ui_obj_df.columns:
            other_ui_obj_df[column_title] = None

        column_index = other_ui_obj_df.columns.get_loc(column_title)

        # carry on info about the attribute column type
        if log_col_index in val_att_cols:
            if column_index not in other_ui_obj_df_val_att_cols:
                other_ui_obj_df_val_att_cols.append(column_index)
        elif log_col_index in cont_att_cols:
            if column_index not in other_ui_obj_df_cont_att_cols:
                other_ui_obj_df_cont_att_cols.append(column_index)

        # add the value to the df
        other_ui_obj_df.at[new_row_index, column_title] = attribute_value

        # remove the value from the log
        log.iloc[log_row_index, log_col_index] = np.NaN

    return other_ui_obj_df, log, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols


def decide_undecided_obj_cols(log, undecided_obj_cols, value_term, obj_level, local_other_ui_obj_cols_fourth, unmatched_att_list, row_index, val_att_cols):
    """
    Chooses how to handle the columns where the object type is not clear yet.

    :param val_att_cols: Dictionary with value attribute indices columns.
    :param log: A pandas DataFrame representing the UI log.
    :param undecided_obj_cols: A dictionary with column indices that haven't been assigned one clear object type
                                but a list of possible ones.
    :param value_term: String with the object type of the current object.
    :param obj_level: A string indicating UI object's hierarchy level ('obj_highest_level',
                        'obj_second_level', 'obj_third_level', or 'obj_fourth_level').
    :param local_other_ui_obj_cols_fourth: A dictionary with the column indices and object types that are on the fourth
                                            hierarchy level.
    :param unmatched_att_list: List with attribute columns that have not been assigned an object type yet.
    :param row_index: Row index of the log.
    :return: A tuple of the updated unmatched_att_list and the updated local_other_ui_obj_cols_fourth.
    """
    if obj_level == 'obj_fourth_level':
        # columns of type value attribute have to be assigned to the main obj
        for col_index in list(local_other_ui_obj_cols_fourth.keys()):
            if col_index in val_att_cols:
                unmatched_att_list.append(col_index)
                local_other_ui_obj_cols_fourth.pop(col_index)

        for obj_index, obj_types in undecided_obj_cols.items():
            # if the undecided column object possibility matches the main, then add it to the unmatched list,
            #  so it will be added to the main's attributes
            if value_term in obj_types:
                if obj_index not in unmatched_att_list:
                    unmatched_att_list.append(obj_index)

            else:
                # call function to find out which columns have the same object type
                local_other_ui_obj_cols_fourth_matched = find_matching_pairs(local_other_ui_obj_cols_fourth)

                # check which object type of the highest level is present in this row
                available_obj = check_value_availability(log, local_other_ui_obj_cols_fourth_matched, row_index)

                # if it doesn't match the main, check if it matches any available other fourth level object type
                if available_obj in obj_types:
                    local_other_ui_obj_cols_fourth.setdefault(obj_index, available_obj)

                # if non matches it will be added to the main
                else:
                    if obj_index not in unmatched_att_list:
                        unmatched_att_list.append(obj_index)

    else:
        for obj_index, obj_types in undecided_obj_cols.items():
            # call function to find out which columns have the same object type
            local_other_ui_obj_cols_fourth_matched = find_matching_pairs(local_other_ui_obj_cols_fourth)

            # check which object type of the highest level is present in this row
            available_obj = check_value_availability(log, local_other_ui_obj_cols_fourth_matched, row_index)

            # if it doesn't match the main, check if it matches any available other fourth level object type
            for avail_obj in available_obj:
                if avail_obj in obj_types:
                    local_other_ui_obj_cols_fourth.setdefault(obj_index, avail_obj)

                # if non matches it will be added to the main
                else:
                    if obj_index not in unmatched_att_list:
                        unmatched_att_list.append(obj_index)

    return unmatched_att_list, local_other_ui_obj_cols_fourth


def identify_main_object_instances(log, object_instances_dict, row_index, value, value_term, obj_level,
                                   local_other_ui_obj_cols, unmatched_att_list, val_att_cols, cont_att_cols,
                                   last_obj_inst, last_web_inst, last_app_inst, last_second_obj_inst, last_third_obj_inst):
    """
    Identifies main object instances.

    :param log: A pandas DataFrame representing the UI log.
    :param object_instances_dict: A dictionary to save the attribute combinations as keys and the object instances as values.
    :param row_index: Row index of the log.
    :param value: String with the object type.
    :param value_term: String with the official term for the object type.
    :param obj_level: A string indicating UI object's hierarchy level ('obj_highest_level',
                        'obj_second_level', 'obj_third_level', or 'obj_fourth_level').
    :param local_other_ui_obj_cols: Dictionary with columns related to object types other than the main UI object type;
                                        with indices as keys and object types as values.
    :param unmatched_att_list: List with attribute columns that have not been assigned an object type yet.
    :param val_att_cols: List of columns in the log that are of type value attribute.
    :param cont_att_cols: List of columns in the log that are of type context attribute.
    :param last_obj_inst: String holding the last higher level object instance.
    :param last_web_inst: A string with the object instance of the last seen website object.
    :param last_app_inst: A string with the object instance of the last seen application object.
    :param last_second_obj_inst: A string with the object instance of the last seen second level object.
    :param last_third_obj_inst: A string with the object instance of the last seen third level object.
    :return: A tuple consisting of:
                - the modified log,
                - the modified object_instances_dict,
                - the updated last_obj_inst,
                - the adjusted last_web_inst,
                - the modified local_other_ui_obj_cols.
    """

    # call function to get a list of the relevant attribute columns
    combined_att_list, local_other_ui_obj_cols = get_relevant_att_cols(local_other_ui_obj_cols, unmatched_att_list,
                                                                       value_term)

    # function that loops over the list to combine all attribute values to identify the object instance
    att_list, att_col_indices_list = get_attribute_values(log, row_index, combined_att_list, val_att_cols, cont_att_cols)

    # call function to add value to the 'part of' column
    obj_is_main = True
    att_list, log = add_higher_hierarchy_instances(log, value_term, att_list, row_index, obj_level, last_web_inst,
                                                   last_app_inst, last_second_obj_inst, last_third_obj_inst,
                                                   obj_is_main)

    # call function to form a key from the attribute combination to get the object instance
    obj_inst, object_instances_dict = generate_key(att_list, object_instances_dict, value)

    log.loc[row_index, 'object instance'] = obj_inst

    # saves instance of last object for this  hierarchy level
    if value_term == 'website':
        last_web_inst = [obj_inst, row_index]
    else:
        last_obj_inst = [obj_inst, row_index]

    return log, object_instances_dict, last_obj_inst, last_web_inst, local_other_ui_obj_cols


def identify_other_obj_inst(log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, value_term,
                            local_other_ui_obj_cols, val_att_cols, cont_att_cols, last_obj_inst, last_web_inst, last_app_inst,
                            last_second_obj_inst, last_third_obj_inst, main_not_this_level, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols):
    """
     Identifies object instances for objects other than the main object.

    :param value_term: String with the official object type term.
    :param log: A pandas DataFrame representing the UI log.
    :param object_hierarchy: A dictionary specifying the typical ui object hierarchy.
    :param other_ui_obj_df: DataFrame including object instances other than the main object instances.
    :param object_instances_dict: A dictionary to save the attribute combinations as keys and the object instances as values.
    :param row_index: Row index of the log.
    :param local_other_ui_obj_cols: Dictionary with columns related to object types other than the main UI object type;
                                        with indices as keys and object types as values.
    :param val_att_cols: List of columns in the log that are of type value attribute.
    :param cont_att_cols: List of columns in the log that are of type context attribute.
    :param last_obj_inst: String holding the last higher level object instance.
    :param last_web_inst: A string with the object instance of the last seen website object.
    :param last_app_inst: A string with the object instance of the last seen application object.
    :param last_second_obj_inst: A string with the object instance of the last seen second level object.
    :param last_third_obj_inst: A string with the object instance of the last seen third level object.
    :param main_not_this_level: Boolean indicating whether the main UI object of the current row is on the same hierarchy level.
    :param part_of: String with the object instance the object in question is part of.
    :param other_ui_obj_df_val_att_cols: List of columns in the df that are of type value attribute.
    :param other_ui_obj_df_cont_att_cols: List of columns in the df that are of type context attribute.
    :return: A tuple consisting of:
            - the modified log,
            - the modified object_instances_dict,
            - the new last_obj_inst,
            - the new last_web_inst,
            - the modified other_ui_obj_df,
            - the updated part_of,
            - the changed other_ui_obj_df_val_att_cols,
            - the changed other_ui_obj_df_cont_att_cols.
    """
    # call function to find out which columns have the same object type
    local_other_ui_obj_cols = find_matching_pairs(local_other_ui_obj_cols)

    for obj, indices in local_other_ui_obj_cols.items():

        # check to which hierarchy level the object type belongs
        obj_level = determine_hierarchy_level(obj, object_hierarchy)

        # function that loops over the list to combine all attribute values to identify the object instance
        att_list, att_col_indices_list = get_attribute_values(log, row_index, indices, val_att_cols, cont_att_cols)

        # call function to add value to the 'part of' variable
        obj_is_main = None
        part_of, att_list, log = add_higher_hierarchy_instances(log, obj, att_list, row_index, obj_level,
                                                                last_web_inst, last_app_inst, last_second_obj_inst,
                                                                last_third_obj_inst, obj_is_main, part_of)

        # call function to form a key from the attribute combination to get the object instance
        obj_inst, object_instances_dict = generate_key(att_list, object_instances_dict, obj)

        # don't add object instances to the df that don't actually exist
        if obj_inst is not None:
            # call function to add a row with new info to the other_ui_obj_df
            other_ui_obj_df, log, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols = create_new_row_ui_obj_df(
                log, obj, row_index, obj_inst, part_of, other_ui_obj_df, att_col_indices_list, val_att_cols,
                cont_att_cols, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols)

        # if the main ui object is not on the same level, then set this object instance as last instance of this level
        if main_not_this_level is True and obj_inst is not None:
            if obj == 'website':
                last_web_inst = [obj_inst, row_index]
            else:
                last_obj_inst = [obj_inst, row_index]

        # on the highest level the last values of both types have to be saved
        if obj_level == 'obj_highest_level':
            if value_term == 'website' and obj != value_term:
                last_obj_inst = [obj_inst, row_index]
            if value_term == 'application' and obj != value_term:
                last_web_inst = [obj_inst, row_index]

    return log, object_instances_dict, last_obj_inst, last_web_inst, other_ui_obj_df, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols


def add_user_objects(log, process_obj_df, user_cols, row_index, process_obj_inst_dict):
    """
    Manages the user objects found in the log.

    :param log: A pandas DataFrame representing the UI log.
    :param process_obj_df: A pandas DataFrame for the process object instances and their attributes.
    :param user_cols: Dictionary with indices of the attribute columns that are user-related and the column titles.
    :param row_index: Row index of the log.
    :param process_obj_inst_dict: A Dictionary with process object instances as values and their attribute combinations as keys.
    :return: A tuple of the modified process_obj_df and the modified log
    """
    obj_type = 'user'

    att_list = []  # list to save relevant attribute values

    # save relevant attribute values
    for col_index in user_cols.keys():
        att_value = log.iloc[row_index, col_index]
        att_list.append(att_value)

    # as user always exists; so if there are no attributes
    if not att_list:
        att_list.append('user')

    process_obj_inst, process_obj_inst_dict = generate_key(att_list, process_obj_inst_dict, obj_type)

    process_obj_df, log = create_new_row_process_obj_df(log, obj_type, row_index, process_obj_inst, process_obj_df,
                                                        user_cols)

    return process_obj_df, log


def recognize_obj_instances(log, object_hierarchy, ui_object_synonym, undecided_obj_cols, other_ui_obj_cols_highest,
                 other_ui_obj_cols_second, other_ui_obj_cols_third, other_ui_obj_cols_fourth, val_att_cols,
                 cont_att_cols, user_cols, unmatched_att_list, process_obj_df):
    """
    Recognizes object instances in a log based on their hierarchy levels and attributes.

    :param log: A pandas DataFrame representing the UI log.
    :param object_hierarchy: A dictionary specifying the typical ui object hierarchy.
    :param ui_object_synonym: A dictionary with pre-defined UI object types and their synonyms.
    :param undecided_obj_cols: A dictionary with column indices that haven't been assigned one clear object type
                                but a list of possible ones.
    :param other_ui_obj_cols_highest: A dictionaries to save ui object types of the highest hierarchy level and
                                        their column indices.
    :param other_ui_obj_cols_second: A dictionaries to save ui object types of the second hierarchy level and
                                        their column indices.
    :param other_ui_obj_cols_third: A dictionaries to save ui object types of the third hierarchy level and
                                        their column indices.
    :param other_ui_obj_cols_fourth: A dictionaries to save ui object types of the fourth hierarchy level and
                                        their column indices.
    :param val_att_cols: List of columns in the log that are of type value attribute.
    :param cont_att_cols: List of columns in the log that are of type context attribute.
    :param user_cols: Dictionary with indices of the attribute columns that are user-related and the column titles.
    :param unmatched_att_list: List with attribute columns that have not been assigned an object type yet.
    :param process_obj_df: A pandas DataFrame for the process object instances and their attributes.
    :return: A tuple of the modified versions of the log, the other_ui_obj_df and the process_obj_df.
    """
    object_instances_dict = {}  # dictionary to save ui object instances and their unique identifiers
    process_obj_inst_dict = {}  # dictionary to save process object instances and their unique identifiers

    # dataframe to save other ui object instances and type, their row index and the object instance they are part of
    other_ui_obj_df = pd.DataFrame(columns=['row index', 'object instance', 'object type', 'part of'])

    # variable to save to which higher instance an object instance belongs and fill last column of the other_ui_obj_df
    part_of = None

    # lists to keep info on attribute column type for other_ui_obj_df
    other_ui_obj_df_val_att_cols = []
    other_ui_obj_df_cont_att_cols = []

    # create lists to hold the last seen object instance of each object hierarchy and their row
    last_app_inst = []  # for applications
    last_web_inst = []  # for websites
    last_second_obj_inst = []  # for object types on second level
    last_third_obj_inst = []  # for object types on third level
    last_fourth_obj_inst = []  # for object types on fourth level

    # loop over the 'main ui object type' column
    for row_index, value in log['main ui object type'].items():

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
                                                                                                     value_term,
                                                                                                     obj_level,
                                                                                                     local_other_ui_obj_cols_fourth,
                                                                                                     local_unmatched_att_list,
                                                                                                     row_index,
                                                                                                     val_att_cols)

                # main highest level
                log, object_instances_dict, last_app_inst, last_web_inst, local_other_ui_obj_cols_highest = identify_main_object_instances(
                    log, object_instances_dict, row_index, value, value_term, obj_level,
                    local_other_ui_obj_cols_highest, local_unmatched_att_list, val_att_cols, cont_att_cols,
                    last_app_inst, last_web_inst, last_app_inst, last_second_obj_inst, last_third_obj_inst)

                # other highest level
                # set variable to None since the main ui object is on this level
                main_not_this_level = None
                log, object_instances_dict, last_app_inst, last_web_inst, other_ui_obj_df, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols = identify_other_obj_inst(
                    log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, value_term,
                    local_other_ui_obj_cols_highest, val_att_cols, cont_att_cols, last_app_inst, last_web_inst,
                    last_app_inst, last_second_obj_inst, last_third_obj_inst, main_not_this_level, part_of,
                    other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols)

                # set variable to true since the main ui object is not on this level
                main_not_this_level = True

                # other second level
                log, object_instances_dict, last_second_obj_inst, last_web_inst, other_ui_obj_df, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols = identify_other_obj_inst(
                    log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, value_term,
                    local_other_ui_obj_cols_second, val_att_cols, cont_att_cols, last_second_obj_inst, last_web_inst,
                    last_app_inst, last_second_obj_inst, last_third_obj_inst, main_not_this_level, part_of,
                    other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols)

                # other third level
                log, object_instances_dict, last_third_obj_inst, last_web_inst, other_ui_obj_df, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols = identify_other_obj_inst(
                    log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, value_term,
                    local_other_ui_obj_cols_third, val_att_cols, cont_att_cols, last_third_obj_inst, last_web_inst,
                    last_app_inst, last_second_obj_inst, last_third_obj_inst, main_not_this_level, part_of,
                    other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols)

                # other fourth level
                log, object_instances_dict, last_fourth_obj_inst, last_web_inst, other_ui_obj_df, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols = identify_other_obj_inst(
                    log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, value_term,
                    local_other_ui_obj_cols_fourth, val_att_cols, cont_att_cols, last_fourth_obj_inst, last_web_inst,
                    last_app_inst, last_second_obj_inst, last_third_obj_inst, main_not_this_level, part_of,
                    other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols)

                # if only highest level objects are in a column, last_app_inst or last_obj_inst won't be added to the related_ui_obj column
                # add it to column
                if value_term == 'website' and last_app_inst:
                    if row_index == last_app_inst[1]:
                        log.loc[row_index, 'related ui object'] = last_app_inst[0]

                if value_term == 'application' and last_web_inst:
                    if row_index == last_web_inst[1]:
                        log.loc[row_index, 'related ui object'] = last_web_inst[0]

            # if it is not on the highest hierarchy level
            else:

                # call function to figure out what to do with the undecided columns
                local_unmatched_att_list, local_other_ui_obj_cols_fourth = decide_undecided_obj_cols(log,
                                                                                                     undecided_obj_cols,
                                                                                                     value_term,
                                                                                                     obj_level,
                                                                                                     local_other_ui_obj_cols_fourth,
                                                                                                     local_unmatched_att_list,
                                                                                                     row_index,
                                                                                                     val_att_cols)

                # set variable to true since the main ui object is not on this level
                main_not_this_level = True

                # other highest level
                log, object_instances_dict, last_app_inst, last_web_inst, other_ui_obj_df, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols = identify_other_obj_inst(
                    log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, value_term,
                    local_other_ui_obj_cols_highest, val_att_cols, cont_att_cols, last_app_inst, last_web_inst,
                    last_app_inst, last_second_obj_inst, last_third_obj_inst, main_not_this_level, part_of,
                    other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols)

                # main second level
                if obj_level == 'obj_second_level':
                    log, object_instances_dict, last_second_obj_inst, last_web_inst, local_other_ui_obj_cols_second = identify_main_object_instances(
                        log, object_instances_dict, row_index, value, value_term, obj_level,
                        local_other_ui_obj_cols_second, local_unmatched_att_list, val_att_cols, cont_att_cols,
                        last_second_obj_inst, last_web_inst, last_app_inst, last_second_obj_inst, last_third_obj_inst)

                    # other second level
                    # set variable to None since the main ui object is on this level
                    main_not_this_level = None
                    log, bject_instances_dict, last_second_obj_inst, last_web_inst, other_ui_obj_df, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols = identify_other_obj_inst(
                        log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, value_term,
                        local_other_ui_obj_cols_second, val_att_cols, cont_att_cols, last_second_obj_inst,
                        last_web_inst, last_app_inst, last_second_obj_inst, last_third_obj_inst, main_not_this_level,
                        part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols)

                    # set variable to true since the main ui object is not on this level
                    main_not_this_level = True

                    # other third level
                    log, object_instances_dict, last_third_obj_inst, last_web_inst, other_ui_obj_df, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols = identify_other_obj_inst(
                        log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, value_term,
                        local_other_ui_obj_cols_third, val_att_cols, cont_att_cols, last_third_obj_inst, last_web_inst,
                        last_app_inst, last_second_obj_inst, last_third_obj_inst, main_not_this_level, part_of,
                        other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols)

                    # other fourth level
                    log, object_instances_dict, last_fourth_obj_inst, last_web_inst, other_ui_obj_df, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols = identify_other_obj_inst(
                        log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, value_term,
                        local_other_ui_obj_cols_fourth, val_att_cols, cont_att_cols, last_fourth_obj_inst,
                        last_web_inst, last_app_inst, last_second_obj_inst, last_third_obj_inst, main_not_this_level,
                        part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols)

                else:
                    # set variable to true since the main ui object is not on this level
                    main_not_this_level = True

                    # other second level
                    log, object_instances_dict, last_second_obj_inst, last_web_inst, other_ui_obj_df, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols = identify_other_obj_inst(
                        log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, value_term,
                        local_other_ui_obj_cols_second, val_att_cols, cont_att_cols, last_second_obj_inst,
                        last_web_inst, last_app_inst, last_second_obj_inst, last_third_obj_inst, main_not_this_level,
                        part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols)

                    # main third level
                    if obj_level == 'obj_third_level':
                        log, object_instances_dict, last_third_obj_inst, last_web_inst, local_other_ui_obj_cols_third = identify_main_object_instances(
                            log, object_instances_dict, row_index, value, value_term, obj_level,
                            local_other_ui_obj_cols_third, local_unmatched_att_list, val_att_cols, cont_att_cols,
                            last_third_obj_inst, last_web_inst, last_app_inst, last_second_obj_inst,
                            last_third_obj_inst)

                        # other third level
                        # set variable to None since the main ui object is on this level
                        main_not_this_level = None
                        log, object_instances_dict, last_third_obj_inst, last_web_inst, other_ui_obj_df, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols = identify_other_obj_inst(
                            log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, value_term,
                            local_other_ui_obj_cols_third, val_att_cols, cont_att_cols, last_third_obj_inst,
                            last_web_inst, last_app_inst, last_second_obj_inst, last_third_obj_inst,
                            main_not_this_level, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols)

                        # other fourth level
                        # set variable to true since the main ui object is not on this level
                        main_not_this_level = True
                        log, object_instances_dict, last_fourth_obj_inst, last_web_inst, other_ui_obj_df, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols = identify_other_obj_inst(
                            log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, value_term,
                            local_other_ui_obj_cols_fourth, val_att_cols, cont_att_cols, last_fourth_obj_inst,
                            last_web_inst, last_app_inst, last_second_obj_inst, last_third_obj_inst,
                            main_not_this_level, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols)

                    else:
                        # set variable to true since the main ui object is not on this level
                        main_not_this_level = True

                        # other third level
                        log, object_instances_dict, last_third_obj_inst, last_web_inst, other_ui_obj_df, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols = identify_other_obj_inst(
                            log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, value_term,
                            local_other_ui_obj_cols_third, val_att_cols, cont_att_cols, last_third_obj_inst,
                            last_web_inst, last_app_inst, last_second_obj_inst, last_third_obj_inst,
                            main_not_this_level, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols)

                        # main fourth level
                        log, object_instances_dict, last_fourth_obj_inst, last_web_inst, local_other_ui_obj_cols_fourth = identify_main_object_instances(
                            log, object_instances_dict, row_index, value, value_term, obj_level,
                            local_other_ui_obj_cols_fourth, local_unmatched_att_list, val_att_cols, cont_att_cols,
                            last_fourth_obj_inst, last_web_inst, last_app_inst, last_second_obj_inst,
                            last_third_obj_inst)

                        # other fourth level
                        # set variable to None since the main ui object is on this level
                        main_not_this_level = None
                        log, object_instances_dict, last_fourth_obj_inst, last_web_inst, other_ui_obj_df, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols = identify_other_obj_inst(
                            log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, value_term,
                            local_other_ui_obj_cols_fourth, val_att_cols, cont_att_cols, last_fourth_obj_inst,
                            last_web_inst, last_app_inst, last_second_obj_inst, last_third_obj_inst,
                            main_not_this_level, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols)

        # if the value is not given, use a ui object type from a higher hierarchy level
        else:

            value = 'unknown'  # since no main UI object is given
            value_term = value

            # check to which hierarchy level the object type belongs
            obj_level = determine_hierarchy_level(value_term, object_hierarchy)

            # call function to figure out what to do with the undecided columns
            local_unmatched_att_list, local_other_ui_obj_cols_fourth = decide_undecided_obj_cols(log,
                                                                                                 undecided_obj_cols,
                                                                                                 value_term, obj_level,
                                                                                                 local_other_ui_obj_cols_fourth,
                                                                                                 local_unmatched_att_list,
                                                                                                 row_index,
                                                                                                 val_att_cols)

            # set variable to true since the main ui object is not on this level
            main_not_this_level = True

            # other highest level
            log, object_instances_dict, last_app_inst, last_web_inst, other_ui_obj_df, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols = identify_other_obj_inst(
                log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, value_term,
                local_other_ui_obj_cols_highest, val_att_cols, cont_att_cols, last_app_inst, last_web_inst,
                last_app_inst, last_second_obj_inst, last_third_obj_inst, main_not_this_level, part_of,
                other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols)

            # other second level
            log, object_instances_dict, last_second_obj_inst, last_web_inst, other_ui_obj_df, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols = identify_other_obj_inst(
                log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, value_term,
                local_other_ui_obj_cols_second, val_att_cols, cont_att_cols, last_second_obj_inst, last_web_inst,
                last_app_inst, last_second_obj_inst, last_third_obj_inst, main_not_this_level, part_of,
                other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols)

            # other third level
            log, object_instances_dict, last_third_obj_inst, last_web_inst, other_ui_obj_df, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols = identify_other_obj_inst(
                log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, value_term,
                local_other_ui_obj_cols_third, val_att_cols, cont_att_cols, last_third_obj_inst, last_web_inst,
                last_app_inst, last_second_obj_inst, last_third_obj_inst, main_not_this_level, part_of,
                other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols)

            # main fourth level
            log, object_instances_dict, last_fourth_obj_inst, last_web_inst, local_other_ui_obj_cols_fourth = identify_main_object_instances(
                log, object_instances_dict, row_index, value, value_term, obj_level, local_other_ui_obj_cols_fourth,
                local_unmatched_att_list, val_att_cols, cont_att_cols, last_fourth_obj_inst, last_web_inst,
                last_app_inst, last_second_obj_inst, last_third_obj_inst)

            # other fourth level
            # set variable to None since the main ui object is on this level
            main_not_this_level = None
            log, object_instances_dict, last_fourth_obj_inst, last_web_inst, other_ui_obj_df, part_of, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols = identify_other_obj_inst(
                log, object_hierarchy, other_ui_obj_df, object_instances_dict, row_index, value_term,
                local_other_ui_obj_cols_fourth, val_att_cols, cont_att_cols, last_fourth_obj_inst, last_web_inst,
                last_app_inst, last_second_obj_inst, last_third_obj_inst, main_not_this_level, part_of,
                other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols)

        # generate process object instances for the user-related objects
        process_obj_df, log = add_user_objects(log, process_obj_df, user_cols, row_index,
                                                            process_obj_inst_dict)

    return log, other_ui_obj_df, process_obj_df, other_ui_obj_df_val_att_cols, other_ui_obj_df_cont_att_cols
# </editor-fold>


# <editor-fold desc="3. Element Linkage">
def create_event_dict(log, val_att_cols, process_obj_df):
    """
    Creates a json file including the event instances of the log.

    :param log: A pandas DataFrame representing the UI log.
    :param val_att_cols: List of columns in the log that are of type value attribute.
    :param process_obj_df: A pandas DataFrame for the process object instances that is already in a json friendly format.
    :return: A dictionary for the event instances that is already in a json friendly format.
    """
    event_df = pd.DataFrame()  # df for event related data
    event_instances = []  # list for event instances
    event_val_att_cols = [] # list for the value attribute columns in the new event_df
    events_dict = {}  # event dictionary to achieve a json structure

    # save the process objects in a dictionary with the row_index as key
    process_obj_dict = process_obj_df.groupby('row index')['object instance'].apply(list).to_dict()

    # assign ids to events
    for x in range(1, len(log) + 1):
        event_instances.append(f'event_{x}')

    event_df['event id'] = event_instances  # add id column to event_df

    # the value attribute columns are needed because we want to save the value an activity triggers to be saved with the event
    for col_index in val_att_cols:
        col = log.columns[col_index]
        event_df[col] = log.iloc[:, col_index]
        event_val_att_col_index = event_df.columns.get_loc(col)
        event_val_att_cols.append(event_val_att_col_index)

    # restructure the df
    for col in log.columns:
        if 'activity' in col:
            event_df[col] = log[col]
        if 'timestamp' in col:
            event_df[col] = log[col]
        if 'object instance' in col:
            event_df[col] = log[col]
        if 'related ui object' in col:
            event_df[col] = log[col]

    # convert timestamp to string, so json can parse it
    event_df['timestamp'] = event_df['timestamp'].astype(str)

    for row_index, row in event_df.iterrows():
        val_att_dict = {}  # dictionary to save the value attribute value and the object the attribute belongs to
        process_obj_list = []
        related_ui_obj_list = []
        for col_index in event_val_att_cols:
            att_val = event_df.iloc[row_index, col_index] # value attribute value
            att_type = event_df.columns[col_index] # value attribute type
            if att_val is not np.NaN:
                val_att_dict[f"{row['object instance']}.{att_type}"] = str(att_val)

        # loop over process objects and add the ones with matching saved index to the list
        if row_index in process_obj_dict:
            for process_obj in process_obj_dict[row_index]:
                if not pd.isna(process_obj):
                    process_obj_list.append(str(process_obj))

        related_ui_obj = row["related ui object"]
        if not pd.isna(related_ui_obj):
            related_ui_obj_list.append(str(related_ui_obj))

        # add data to the dictionary
        events_dict[row["event id"]] = {
            "activity": str(row["activity"]),
            "timestamp": str(row["timestamp"]),
            "main object": str(row["object instance"]),
            "vmap": val_att_dict,
            "umap": related_ui_obj_list,
            "pmap": process_obj_list
        }

    return events_dict


def create_main_ui_obj_dict(log, cont_att_cols, val_att_cols):
    """
    Creates a dictionary for the main UI objects that is already in a json friendly format.

    :param log: A pandas DataFrame representing the UI log.
    :param cont_att_cols: List of columns in the log that are of type context attribute.
    :param val_att_cols: List of columns in the log that are of type value attribute.
    :return: A dictionary for the main UI objects that is already in a json friendly format.
    """
    object_df = copy.deepcopy(log) # copy log to keep the original one
    ui_objects_dict = {} # ui object dictionary to achieve a json structure

    # drop related ui object column because it is not relevant for the ui object
    object_df.drop('related ui object', axis=1, inplace=True)

    # drop duplicate object instances and keep only the once that occur latest in time
    object_df = object_df.sort_values('timestamp').drop_duplicates(['object instance'], keep='last').sort_index()

    # drop the timestamp column
    object_df.drop(['timestamp'], axis=1, inplace=True)

    # reset indices, so they start with zero again and don't have gaps
    object_df.reset_index(drop=True, inplace=True)

    # convert the df into a json readable format
    for row_index, row in object_df.iterrows():
        cont_att_dict = {} # dictionary for context attribute values and their type
        val_att_dict = {} # dictionary for value attribute values and their type
        part_of = [] # list for ui object instances the main ui object is part of

        for col_index in cont_att_cols:
            col_name = log.columns[col_index]
            cont_att_val = object_df.loc[row_index, col_name]  # context attribute value
            cont_att_type = col_name  # context attribute type
            if not pd.isna(cont_att_val):
                cont_att_dict[cont_att_type] = str(cont_att_val)
        for col_index in val_att_cols:
            col_name = log.columns[col_index]
            val_att_val = object_df.loc[row_index, col_name]  # value attribute value
            val_att_type = col_name  # value attribute type
            if not pd.isna(val_att_val):
                val_att_dict[val_att_type] = str(val_att_val)

        if not pd.isna(row["part of"]):
            part_of.append(str(row["part of"]))

        obj_type = row["main ui object type"]
        if pd.isna(obj_type):
            obj_type = 'unknown'

        ui_objects_dict[row["object instance"]] = {
            "type": str(obj_type),
            "cmap": cont_att_dict,
            "vmap": val_att_dict,
            "part of": part_of
        }

    return ui_objects_dict


# convert the df into a json readable format
def create_ui_obj_dict(ui_objects_dict, other_ui_obj_df, other_ui_obj_df_cont_att_cols, other_ui_obj_df_val_att_cols):
    """
    Creates a dictionary including the ui object instances of the log.

    :param ui_objects_dict: A dictionary for the main UI objects that is already in a json friendly format.
    :param other_ui_obj_df: DataFrame including object instances other than the main object instances.
    :param other_ui_obj_df_cont_att_cols: List of columns in the df that are of type context attribute.
    :param other_ui_obj_df_val_att_cols: List of columns in the df that are of type value attribute.
    :return: A dictionary for the UI object instances that is already in a json friendly format.
    """
    for row_index, row in other_ui_obj_df.iterrows():
        cont_att_dict = {} # dictionary for context attribute values and their type
        val_att_dict = {} # dictionary for value attribute values and their type
        part_of = [] # list for ui object instances the main ui object is part of

        for col_index in other_ui_obj_df_cont_att_cols:
            cont_att_val = other_ui_obj_df.iloc[row_index, col_index]  # context attribute value
            cont_att_type = other_ui_obj_df.columns[col_index]  # context attribute type
            if not pd.isna(cont_att_val):
                cont_att_dict[cont_att_type] = str(cont_att_val)
        for col_index in other_ui_obj_df_val_att_cols:
            val_att_val = other_ui_obj_df.iloc[row_index, col_index]  # value attribute value
            val_att_type = other_ui_obj_df.columns[col_index]  # value attribute type
            if not pd.isna(val_att_val):
                val_att_dict[val_att_type] = str(val_att_val)

        if not pd.isna(row["part of"]):
            part_of.append(str(row["part of"]))

        ui_objects_dict[row["object instance"]] = {
            "type": str(row["object type"]),
            "cmap": cont_att_dict,
            "vmap": val_att_dict,
            "part of": part_of
        }

    return ui_objects_dict


def create_process_obj_dict(process_obj_df):
    """
    Creates a dictionary including the process object instances of the log.

    :param process_obj_df: A pandas DataFrame for the process object instances and their attributes.
    :return: A dictionary with the process object instances ready to be converted into a json file.
    """
    process_obj_dict = {} # dictionary for process objects
    att_cols = [] # list for attribute column indices

    # starting at index three because the first column is the row index, the second the object instance, and the third the object type
    for x in range(3, len(process_obj_df.columns)):
        att_cols.append(x)

    for row_index, row in process_obj_df.iterrows():
        att_dict = {}  # dictionary for attribute values and their types
        for col_index in att_cols:
            att_val = process_obj_df.iloc[row_index, col_index]  # context attribute value
            att_type = process_obj_df.columns[col_index]  # context attribute type
            if not pd.isna(att_val):
                att_dict[att_type] = str(att_val)

        process_obj_dict[row["object instance"]] = {
            "type": str(row["object type"]),
            "amap": att_dict,
        }

    return process_obj_dict


def merge_dicts_and_create_json(events_dict, ui_obj_dict, process_obj_dict):
    """
    Merges the dictionaries and creates a json file to write the output dictionary to.

    :param events_dict: A dictionary for the event instances that is already in a json friendly format.
    :param ui_obj_dict: A dictionary for the UI object instances that is already in a json friendly format.
    :param process_obj_dict: A dictionary for the process object instances that is already in a json friendly format.
    """
    oc_dict = {} # object-centric event data dictionary that combines all other element type dictionaries
    oc_dict.setdefault('events', events_dict) # add event dictionary
    oc_dict.setdefault('ui_objects', ui_obj_dict) # add UI object dictionary
    oc_dict.setdefault('process_objects', process_obj_dict) # add process object dictionary

    # specify the subfolder name
    subfolder = 'output automated transformation'

    # specify file path for the JSON file in the subfolder
    json_file_path = os.path.join(subfolder, 'oc_student_record.json')

    # write the dictionary to the JSON file
    with open(json_file_path, 'w') as f:
        json.dump(oc_dict, f, indent=4)
# </editor-fold>

