import smbus2
import struct

bus = smbus2.SMBus(1)

model_id_to_name = {
    1: 'Sensirion SCD40',
    2: 'Panasonic SN-GCJA5'
}

def scan(addr, force=False):
    read = smbus2.SMBus.read_byte, (addr,), {'force':force}
    write = smbus2.SMBus.write_byte, (addr, 0), {'force':force}
    print(read)
    for func, args, kwargs in (read, write):
        try:
            with smbus2.SMBus(1) as bus:
                data = func(bus, *args, **kwargs)
                return True
                break
        except OSError as expt:
            if expt.errno == 16:
                # just busy, maybe permanent by a kernel driver or just temporary by some user code
                pass
    return False

def scan_all(force=False):
    devices = []
    for addr in range(0x03, 0x77 + 1):
        read = smbus2.SMBus.read_byte, (addr,), {'force':force}
        write = smbus2.SMBus.write_byte, (addr, 0), {'force':force}
        print(read)
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

def read_sensor(address):
    data = bus.read_i2c_block_data(address, 0, 27)
    data_size = data[0]
    model_id = (data[1] << 8) + data[2]
    error_status = (data[5] << 24) + (data[6] << 16) + (data[7] << 8) + data[8]
    pm1_data = hex((data[11] << 24) + (data[12] << 16) + (data[13] << 8) + data[14])
    pm2_5_data = hex((data[17] << 24) + (data[18] << 16) + (data[19] << 8) + data[20])
    pm10_data = hex((data[23] << 24) + (data[24] << 16) + (data[25] << 8) + data[26])
    pm1_data = struct.unpack('!f', bytes(data[11:15]))[0]
    pm2_5_data = struct.unpack('!f', bytes(data[17:21]))[0]
    pm10_data = struct.unpack('!f', bytes(data[23:27]))[0]
    sensor_data = {
        'sensor_model': model_id_to_name[model_id],
        'error_status': error_status,
        'message' : {
            'pm1_data': pm1_data,
            'pm2_5_data': pm2_5_data,
            'pm10_data': pm10_data
        }
    }
    return sensor_data