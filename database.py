import os, csv

csv_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'sensor_db.csv')

def store_data(fieldnames, data_list):
    if not os.path.exists(csv_file_path):    
        with open(csv_file_path, 'x', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(fieldnames)
    with open(csv_file_path, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(data_list)