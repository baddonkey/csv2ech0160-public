import base64
import hashlib
import json
import uuid
import pandas as pd
import os

class CSVReader:
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.dataframe = None
        self.metadata = None
        self.directory = './data'

    def generate_unique_id(self):

        uid = uuid.uuid4()
        uid_b64 = base64.urlsafe_b64encode(uid.bytes).decode('utf-8')
        uid_b64 = uid_b64.rstrip('=')
        return f"_{uid_b64[:7]}{uid_b64[7:14]}{uid_b64[14:21]}"

    def generate_md5(self, file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def generate_file_list_with_metadata(self, sub_path):
        file_metadata_list = []
        for file_name in os.listdir(sub_path):
            file_path = os.path.join(sub_path, file_name)
            
            if os.path.isfile(file_path):  # Ensure it's a file

                new_id = self.generate_unique_id()
                md5_hash = self.generate_md5(file_path)  # Get the MD5 hash
                
                file_metadata = {
                    'file_name': file_name,
                    'id': new_id,
                    'md5_hash': md5_hash
                }
                file_metadata_list.append(file_metadata)
        
        return file_metadata_list

    def get_dossier_id(self, row):
        return self.generate_unique_id()

    def get_file_list_for_row(self, row):
        sub_path = os.path.join(self.directory, row.dossier_folder)
        return self.generate_file_list_with_metadata(sub_path)

    def read_csv_with_metadata(self, file_path, comment_char='#'):
        metadata = ''
        data_start_row = 0

        # Read header with comments assembling a json 
        with open(file_path, 'r') as file:
            for i, line in enumerate(file):
                if line.startswith(comment_char):
                    metadata += line.lstrip(comment_char).strip()
                    metadata += '\n'
                else:
                    data_start_row = i  # Determine where the actual data starts
                    break
        
        # Load the CSV data, skipping the metadata rows
        df = pd.read_csv(file_path, skiprows=data_start_row)

        df['Files'] = df.apply(self.get_file_list_for_row, axis=1)
        df['dossier_id'] = df.apply(self.get_dossier_id, axis=1)

        # Transponse 'zusatz_' columns to a name/value pair and re-add them 
        zusatz_columns = [col for col in df.columns if col.startswith('zusatz_')]
        df['zusatz'] = df.apply(lambda row: [{'name': col, 'value': row[col]} for col in zusatz_columns], axis=1)

        return json.loads(metadata), df

    def load_csv(self):
        if os.path.exists(self.file_path):
            try:
                self.metadata, self.dataframe = self.read_csv_with_metadata(self.file_path)
                print(f"CSV with metadata loaded successfully from {self.file_path}")
            except Exception as e:
                print(f"Error occurred while reading the CSV file: {e}")
        else:
            print(f"File not found: {self.file_path}")

    def show_head(self, n=5):
        if self.dataframe is not None:
            print(self.dataframe.head(n))
        else:
            print("Data not loaded. Use the 'load_csv' method to load the data.")

    def get_dataframe(self):
        return self.dataframe

    def get_metadata(self):
        return self.metadata