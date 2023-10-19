#!/usr/bin/env python3

import smbus2
import time
import struct
import datetime
import csv
import os

READ_COUNT = 60
TIME_DELAY = 60

model_name_to_id = {
    'Sensirion SCD40' : 1,
    'Panasonic SN-GCJA5' : 2
}

bus = smbus2.SMBus(1)
sensor_field_names = ['name','pm1','pm2.5','pm10', 'date_time']
csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'sensor_db.csv')

def scan_all(force=False):
    devices = []
    for addr in range(0x03, 0x77 + 1):
        read = smbus2.SMBus.read_byte, (addr,), {'force':force}
        write = smbus2.SMBus.write_byte, (addr, 0), {'force':force}

        for func, args, kwargs in (read, write):
            try:
                with smbus2.SMBus(1) as bus:
                    data = func(bus, *args, **kwargs)
                    devices.append(addr)
                    break
            except OSError as expt:
                if expt.errno == 16:
                    # just busy, maybe permanent by a kernel driver or just temporary by some user code
                    pass

    return devices

def add_data_to_csv(file_path, fieldnames, data_list):
    if not os.path.exists(file_path):    
        with open(file_path, 'x', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(fieldnames)
    with open(file_path, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(data_list)

if __name__ == '__main__':
    prev_all_address = []
    while(1):
        all_address = scan(force=True)
        if prev_all_address != all_address:
            print(all_address)
            print("smt wrong")
        prev_all_address = all_address.copy()
        time.sleep(1)
    print('waiting sensor to calibrate')
    time.sleep(10)
    print('start!')
    prefix_name = datetime.datetime.now().strftime("%m%d-%H%M-")
    for cnt in range(READ_COUNT):
        print(f'Round : {cnt}')
        start_time = time.time()
        for address in all_address:
            data = bus.read_i2c_block_data(address, 0, 27)
            data_size = data[0]
            sensor_model = (data[1] << 8) + data[2]
            error_status = (data[5] << 24) + (data[6] << 16) + (data[7] << 8) + data[8]
            pm1_data = hex((data[11] << 24) + (data[12] << 16) + (data[13] << 8) + data[14])
            pm2_5_data = hex((data[17] << 24) + (data[18] << 16) + (data[19] << 8) + data[20])
            pm10_data = hex((data[23] << 24) + (data[24] << 16) + (data[25] << 8) + data[26])
            pm1_data = struct.unpack('!f', bytes(data[11:15]))[0]
            pm2_5_data = struct.unpack('!f', bytes(data[17:21]))[0]
            pm10_data = struct.unpack('!f', bytes(data[23:27]))[0]
            dt_data = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f'address : {address}')
            print(f'sensor_model : {sensor_model}')
            print(f'error status : {error_status}')
            print(f'pm1 : {pm1_data}')
            print(f'pm2.5 : {pm2_5_data}')
            print(f'pm10 : {pm10_data}')
            print(f'current : {dt_data}')
            print()
            name = prefix_name + str(address)
            filtered_data = [name, str(pm1_data), str(pm2_5_data), str(pm10_data), dt_data]
            add_data_to_csv(csv_path, sensor_field_names, filtered_data)
        print('waiting for the next round')
        while(time.time() - start_time < TIME_DELAY):
            pass
    print('test ended')
