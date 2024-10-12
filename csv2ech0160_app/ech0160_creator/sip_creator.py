import shutil
import os
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import pandas as pd
from datetime import datetime

class SIPCreator:
    
    def __init__(self, metadata, data_frame: pd.DataFrame, input, output, template_path):
        self.metadata= metadata
        self.data_frame = data_frame
        self.output = output
        self.input = input
        self.template_path = template_path

    def run(self):
        # prepare destination and copy template files
        sip_path = os.path.join(self.output, self.metadata['sipname'] + "_" + datetime.now().strftime("%Y%m%d%H%M%S"))
        shutil.copytree(os.path.join(self.template_path), sip_path)
        
        # render metadata.xml and write output
        file_loader = FileSystemLoader(self.template_path)
        env = Environment(loader=file_loader)
        template = env.get_template('./header/metadata.xml')
        output = template.render(data=self.data_frame, data_header=self.metadata)
        full_output_path = os.path.join(sip_path, 'header/metadata.xml')
        with open(full_output_path, 'w') as f:
            f.write(output)

        ## copy data content files
        content_folders_items = [folder for folder in Path(self.input).iterdir() if folder.is_dir()]
        for content_folder_item in content_folders_items:
            shutil.copytree(str(content_folder_item), os.path.join(sip_path, 'content', content_folder_item.name), dirs_exist_ok=True)