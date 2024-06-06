import json
import os
import pandas as pd

def merge_excel_files(directory, output_file, file_pattern, start, end):
    combined_df = pd.DataFrame()

    for i in range(start, end + 1):
        input_file = os.path.join(directory, file_pattern.format(i))
        if os.path.exists(input_file):
            df = pd.read_excel(input_file)
            combined_df = pd.concat([combined_df, df], ignore_index=True)
        else:
            print(f"File {input_file} does not exist and will be skipped.")

    output_path = os.path.join(directory, output_file)
    combined_df.to_excel(output_path, index=False)

def merge_jsonl_files(directory, output_file, file_pattern, start, end):
    output_path = os.path.join(directory, output_file)
    with open(output_path, 'w', encoding='UTF-8') as outfile:
        for i in range(start, end + 1):
            input_file = os.path.join(directory, file_pattern.format(i))
            if os.path.exists(input_file):
                with open(input_file, 'r', encoding='UTF-8') as infile:
                    for line in infile:
                        outfile.write(line)
            else:
                print(f"File {input_file} does not exist and will be skipped.")

merge_excel_files('abs path', 'merged_output.xlsx', 'test{}.xlsx', 0, 5)

merge_jsonl_files('abs path', 'merged_output.jsonl', 'test{}.jsonl', 0, 5)



                