#===============================================================================

import argparse
import re
import logging
import os
import json
from deepdiff import DeepDiff
import ast

#===============================================================================

class FlatmapCompare:
    def __init__(self, var_args):
        self.__production = var_args.get('production')
        self.__plog = var_args.get('plog')
        self.__staging = var_args.get('staging')
        self.__slog = var_args.get('slog')
        self.__report_file = var_args.get('output')
        
    def __compare_log(self):
        def sorted_str(string):
            pattern = r"(?<=\[)[^[\]]+(?=\])|(?<={)[^{}]+(?=})|(?<=\()[^()]+(?=\))"
            matches = re.findall(pattern, string)
            for i, match in enumerate(matches):
                matches[i] = ', '.join(sorted(match.split(', ')))
            return re.sub(pattern, lambda match: matches.pop(0), string)
        with open(self.__plog, 'r') as f:
            p_logs = [sorted_str(log[24:].strip()) for log in f.readlines() if len(log[24:].strip()) > 0]
        with open(self.__slog, 'r') as f:
            s_logs = [sorted_str(log[24:].strip()) for log in f.readlines() if len(log[24:].strip()) > 0]
        p_logs_diff = sorted(list(set(p_logs)-set(s_logs)))
        s_logs_diff = sorted(list(set(s_logs)-set(p_logs)))
        return DeepDiff(p_logs_diff, s_logs_diff)

    def __compare_file(self, file_name):
        def filter_by_str(val):
            try:
                parsed_list = ast.literal_eval(val)
            except:
                parsed_list = val
            if isinstance(parsed_list, str):
                return True
            return False
        p_file = os.path.join(self.__production, file_name)
        s_file = os.path.join(self.__staging, file_name)
        with open(p_file, 'r') as f:
            p_index = json.load(f)
        with open(s_file, 'r') as f:
            s_index = json.load(f)
        diff = DeepDiff(p_index, s_index, ignore_order=True, ignore_numeric_type_changes=True)
        for diff_type in diff:
            diff[diff_type] = {key:val for key, val in diff[diff_type].items() if filter_by_str(val)}
        return diff
                
            
    def compare_flatmap(self):
        self.__log_diff = self.__compare_log()
        self.__index_diff = self.__compare_file('index.json')
        self.__style_diff = self.__compare_file('style.json')

    def __save2xlsx(self):
        # xlsx setup
        import xlsxwriter
        workbook = xlsxwriter.Workbook(self.__report_file)
        # Define pastel colors (RGB values)
        colors = {
            'pink': (255, 204, 204),  # Light pink
            'green': (204, 255, 204),  # Light green
            'blue': (204, 204, 255)   # Light blue
        }
        # Convert RGB values to hexadecimal strings
        hex_colors = {key:f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}' for key, rgb in colors.items()}
        col_format = workbook.add_format({'text_wrap':True, 'bold':True, 'bg_color':hex_colors['pink'], 'align':'center'})
        source_format = workbook.add_format({'text_wrap':True, 'bold':True, 'bg_color':hex_colors['blue']})
        type_format = workbook.add_format({'text_wrap':True, 'bold':True, 'bg_color':hex_colors['green']})
        body_format = workbook.add_format({'text_wrap': True})
        # Setup worksheet and column header
        worksheet = workbook.add_worksheet()
        worksheet.write('A1', '#', col_format)
        worksheet.write('B1', 'Production', col_format)
        worksheet.write('C1', 'Staging', col_format)
        # Set column widths
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 100)
        worksheet.set_column('C:C', 100)

        current_row = 2
        # write to xslx now
        def write_diff(current_row, source_text, data_diff):
            worksheet.merge_range(f'A{current_row}:C{current_row}', source_text, source_format)
            current_row += 1
            for e_type, diffs in data_diff.items():
                if len(diffs) > 0:
                    worksheet.merge_range(f'A{current_row}:C{current_row}', e_type.replace('_', ' ').capitalize(), type_format)
                    current_row += 1
                    if e_type == 'values_changed':
                        for num, line in enumerate(diffs.values(), start=1):
                            worksheet.write(f'A{current_row}', num)
                            worksheet.write(f'B{current_row}', line['old_value'], body_format)
                            worksheet.write(f'C{current_row}', line['new_value'], body_format)
                            current_row += 1
                    else:
                        for num, line in enumerate(diffs.values(), start=1):
                            worksheet.write(f'A{current_row}', num)
                            col = 'B' if e_type == 'iterable_item_removed' else 'C'
                            worksheet.write(f'{col}{current_row}', line, body_format)
                            current_row += 1
            return current_row
        # Print logs
        current_row = write_diff(current_row, 'Log data', self.__log_diff)
        # Print style
        current_row = write_diff(current_row, 'Style data', self.__style_diff)
        # Print index
        current_row = write_diff(current_row, 'Index data', self.__index_diff)

        workbook.close()

    def __save2json(self):
        def replace_keys(data_diff):
            if 'values_changed' in data_diff:    
                for path, diff in data_diff['values_changed'].items():
                    diff['production'] = diff.pop('old_value')
                    diff['staging'] = diff.pop('new_value')
            return data_diff
                
        combine_diff = {
            'log': replace_keys(self.__log_diff),
            'style': replace_keys(self.__style_diff),
            'index': replace_keys(self.__index_diff)
        }
        with open(self.__report_file, 'w') as f:
            json.dump(combine_diff, f)

    def __save2csv(self):
        import csv
        data_rows = [['file source', 'difference type', 'path', 'production', 'staging']]
        combine_diff = {
            'log': self.__log_diff,
            'style': self.__style_diff,
            'index': self.__index_diff
        }
        for source, var_sources in combine_diff.items():
            for e_type, var_source in var_sources.items():
                for location, vals in var_source.items():
                    if e_type == 'values_changed':
                        data_rows += [[source, e_type, location, vals['old_value'], vals['new_value']]]
                    elif e_type == 'iterable_item_removed':
                        data_rows += [[source, e_type, location, vals, '']]
                    elif e_type == 'iterable_item_added':
                        data_rows += [[source, e_type, location, '', vals]]
        # Write the data to the CSV file
        with open(self.__report_file, 'w', newline='') as f:
            writer = csv.writer(f)
            for line in data_rows:
                writer.writerow(line)

    def save_and_close(self):
        # save report to an appropriate format
        report_type = self.__report_file.split('.')[-1]
        if report_type == 'xlsx':
            self.__save2xlsx()
        elif report_type == 'json':
            self.__save2json()
        elif report_type == 'csv':
            self.__save2csv()
        
        else:
            logging.error(f'File format is not recognised ({self.__report_file})')

def main():
    parser = argparse.ArgumentParser(description='Generate a flatmap from its source manifest.')
    parser.add_argument('--production',
                        help='URL or path to flatmap with production SCKAN')
    parser.add_argument('--plog',
                        help='URL or path to flatmap log with production SCKAN')
    parser.add_argument('--staging',
                        help='URL or path to flatmap with staging SCKAN')
    parser.add_argument('--slog',
                        help='URL or path to flatmap log with staging SCKAN')
    parser.add_argument('--output', required=True,
                        help="a file path and name to store comparison results (xlsx, json)")

    args = parser.parse_args()
    fcompare = FlatmapCompare(vars(args))
    fcompare.compare_flatmap()
    fcompare.save_and_close()
    

if __name__ == '__main__':
    main()
