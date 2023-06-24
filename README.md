# Transformation of UI Logs Into Object-Centric Event Data
This repository includes the automated transformation of UI logs into object-centric event data.

# Technical Requirements
The project is tested for python 3.8.

# Installation 
1. Clone the project and navigate to the root folder of the project.
2. Install the necessary dependencies with the following command:
   pip install -r requirements.txt
3. Run the application with the following command:
   python main.py [<file_path> <threshold_ui_object> <threshold_activity> <threshold_attribute> <threshold_timestamp> <threshld_col_completeness>]   

# Parameters 
All thresholds are optional. Thresholds should range between 0.0 and 1.0. If no thresholds are given, the default thresholds are used. 
- threshold_ui_object: 0.2
- threshold_activity: 0.2
- threshold_attribute: 0.5
- threshold_timestamp: 1.0
- threshold_col_completeness: 0.9

Example logs that can be used as <file_path>: login_ui_log.xlsx or student_record.xlsx.

Threshold explanation: 
- threshold_ui_object: determines when a column in a UI log is considered a UI object column. If the uniqueness ratio of a column is less than the specified threshold, then that column is a potential candidate for a UI object type column. 
- threshold_activity: determines when a column in a UI log is considered an activity type column. If the uniqueness ratio of a column is less than the threshold, the column could be an activity type column.
- threshold_attribute: serves as a discriminator between context attribute columns and value attribute columns. The approach assigns the type context attribute to all attribute columns with ratios below the threshold and the type value attribute to those equal to or above the threshold.
- threshold_timestamp: defines a threshold to ensure the uniqueness of timestamp columns. A column can only be classified as a timestamp if its uniqueness ratio meets or exceeds the specified threshold. 
- threshold_col_completeness: helps to determine the main UI object type column. A column can only be of type main UI object type if the completeness ratio of the column is greater than the set threshold.

# UI Log Requirements
- The events in the UI log are ordered chronologically, starting with the oldest event.
- Each UI log has a column that contains the main UI object type.
- Each UI log has a column that contains the activity or event.
