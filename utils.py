import smbus2
import struct

bus = smbus2.SMBus(1)

model_id_to_name = {
    1: 'Sensirion SCD40',
    2: 'Panasonic SN-GCJA5'
}

def scan(force=False):
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


print(scan(True))