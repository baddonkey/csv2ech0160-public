import argparse
from csv2ech0160_app.csv.csv_reader import CSVReader
from csv2ech0160_app.ech0160_creator.sip_creator import SIPCreator

# Read arguments from the command line
parser = argparse.ArgumentParser(description="Generate eCH-160 SIP based on a csv and flat file struecture")
parser.add_argument('--template_path', type=str, help='Template path')
parser.add_argument('--input', type=str, help='Input Folder')
parser.add_argument('--csv', type=str, help='CSV file')
parser.add_argument('--output', type=str, help='Output Folder')
args = parser.parse_args()

# Read csv data
csv_reader = CSVReader(args.csv)
csv_reader.load_csv()

# Create SIP
sip_creator = SIPCreator(csv_reader.get_metadata(), csv_reader.get_dataframe(), args.input, args.output, args.template_path)
sip_creator.run()
