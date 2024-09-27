import json
from tlparser.config import Configuration
from tlparser.stats import Stats
import openpyxl
import os
from datetime import datetime

class Utils:

    def __init__(self, config: Configuration):
        self.config = config

    def read_formulas_from_json(self):
        with open(self.config.file_data_in, 'r') as file:
            data = json.load(file)
        parsed_formulas = []

        ids = [item['id'] for item in data]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate IDs found, abort...")

        for entry in data:
            if entry["status"] in self.config.only_with_status:
                for logic in entry["logics"]:
                    s = Stats(logic["f_code"])
                    parsed_formulas.append({
                        "id": entry['id'],
                        "logic": logic["type"],
                        "stats": s.get_stats()
                    })
        return parsed_formulas

    def write_to_excel(self, data):
        flattened_data = [self.flatten_dict(item) for item in data]

        # Get all unique headers
        headers = set()
        for item in flattened_data:
            headers.update(item.keys())
        headers = sorted(headers)  # Sort headers for consistent column order

        # Create a new workbook and select the active worksheet
        workbook = openpyxl.Workbook()
        sheet = workbook.active

        # Write the headers to the first row
        for col, header in enumerate(headers, start=1):
            sheet.cell(row=1, column=col, value=header)

        # Write the data to the sheet
        for row, item in enumerate(flattened_data, start=2):
            for col, header in enumerate(headers, start=1):
                value = item.get(header)
                if value is None or value == '' or (isinstance(value, set) and len(value) == 0):
                    sheet.cell(row=row, column=col, value=None)
                elif isinstance(value, int) or isinstance(value, float):
                    sheet.cell(row=row, column=col, value=value)
                elif isinstance(value, set):
                    sheet.cell(row=row, column=col, value=', '.join(value))
                else:
                    sheet.cell(row=row, column=col, value=str(value))

        # Save the workbook to a file
        os.makedirs(self.config.folder_data_out, exist_ok=True)
        prefix = self.extract_filename_without_suffix(self.config.file_data_in)
        out = os.path.join(self.config.folder_data_out, f'{prefix}_{self.get_unique_filename()}.xlsx')
        workbook.save(out)
        return out

    @staticmethod
    def flatten_dict(d, parent_key='', sep='.'):
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(Utils.flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    @staticmethod
    def get_unique_filename():
        now = datetime.now()
        return now.strftime('%y%m%d%H%M%S')

    @staticmethod
    def extract_filename_without_suffix(file_path):
        base_name = os.path.basename(file_path)
        return os.path.splitext(base_name)[0]
