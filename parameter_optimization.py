import subprocess
import numpy as np
from evaluation import *

# define the threshold ranges and step size
threshold_ranges = {
    'threshold_ui_obj': (0.1, 0.8, 0.1),
    'threshold_act': (0.1, 0.8, 0.1),
    'threshold_att': (0.1, 0.8, 0.1),
    'threshold_compl': (1.0, 1.1, 0.1)
}

f1_scores = []

# Iterate through all threshold combinations
for threshold_ui_obj in np.arange(*threshold_ranges['threshold_ui_obj']):
    for threshold_act in np.arange(*threshold_ranges['threshold_act']):
        for threshold_att in np.arange(*threshold_ranges['threshold_att']):
            for threshold_compl in np.arange(*threshold_ranges['threshold_compl']):
                try:
                    threshold_timestamp = 1.0
                    # Construct the command to run your main.py file with the current threshold combination
                    command = [
                        'python',
                        'main.py',
                        'student_record.xlsx',
                        str(threshold_ui_obj),
                        str(threshold_act),
                        str(threshold_att),
                        str(threshold_timestamp),
                        str(threshold_compl)
                    ]

                    # execute the command and capture the output if needed
                    output = subprocess.check_output(command, universal_newlines=True)

                except subprocess.CalledProcessError as e:
                    print(
                        f"Error occurred with thresholds: {threshold_ui_obj}, {threshold_act}, {threshold_att}, {threshold_timestamp}, {threshold_compl}")
                    print("Error:", e)
                    continue

                # get f1 score
                f1 = get_log_micro_f1()
                print(f1)


                # Store the F1 score and threshold combination
                f1_scores.append({
                    'threshold_ui_obj': threshold_ui_obj,
                    'threshold_act': threshold_act,
                    'threshold_att': threshold_att,
                    'threshold_timestamp': threshold_timestamp,
                    'threshold_compl': threshold_compl,
                    'f1_score': f1
                })

# create a DataFrame from the F1 scores list
df_f1_scores = pd.DataFrame(f1_scores)

# rearrange the columns for the desired order
df_f1_scores = df_f1_scores[['threshold_ui_obj', 'threshold_act', 'threshold_att', 'threshold_timestamp', 'threshold_compl', 'f1_score']]

# save the F1 scores to an Excel file
df_f1_scores.to_excel('evaluation results/f1_scores_parameter_optimization.xlsx', index=False)
