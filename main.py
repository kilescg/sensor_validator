from fastapi import FastAPI
from data_model import *
from threading import Thread
from database import store_data
import time, datetime
import i2c_manager
from contextlib import asynccontextmanager

stop_threads = False

collecting_info = {
    "is_start": False,
    "interval": None,
    "total_round": None,
    "current_round": 0,
    "addresss": []
}

model_name_to_id = {
    'None' : 0,
    'Sensirion SCD40' : 1,
    'Panasonic SN-GCJA5' : 2
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    thread = Thread(target=collecting_data_loop)
    thread.start()
    yield
    # Clean up the ML models and release the resources
    global stop_threads
    stop_threads = True

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/i2c-devices")
async def list_i2c_devices():
    if collecting_info["is_start"]:
        return {
            "status": "fail",
            "message": "Please stop data collecting first."
        }
    
    data_frame = []
    i2c_addresses = i2c_manager.scan_all()
    for address in i2c_addresses:
        sensor_dict = i2c_manager.read_sensor(address)
        data_frame.append(
            {
                'address' : address,
                'sensor_model' : sensor_dict['sensor_model']
            }
        )
    return data_frame

@app.get("/i2c-devices/{address}")
async def read_data_from_given_address(address: int):
    if collecting_info["is_start"]:
        return {
            "status": "fail",
            "message": "Please stop data collecting first."
        }

    if i2c_manager.scan(address):
        return i2c_manager.read_sensor(address)
    return {"status": "fail",
            "message" : "Can't Read Data"}

@app.get("/auto-collecting/status")
def collecting_status_feedback():
    return collecting_info


@app.post("/auto-collecting/start")
async def start_data_collection(start_data: StartModel):
    global collecting_info
    if collecting_info["is_start"]:
        return {
            "status": "fail",
            "message": "Data collection already started. Please stop it first."
        }
    collecting_info["interval"] = start_data.interval
    collecting_info["total_round"] = start_data.total_round
    collecting_info["is_start"] = True
    return {
        "status": "success",
        "message": "Data collection has started."
    }

@app.post("/auto-collecting/stop")
async def start_data_collection():
    global collecting_info
    if collecting_info["is_start"]:
        collecting_info["is_start"] = False
        collecting_info["total_round"] = 0
        collecting_info['current_round'] = 0
        collecting_info['interval'] = None
        return {
            "status": "success",
            "message": "Data collection has stopped"
        }
    return {
        "status": "fail",
        "message": "Data collection didn't start yet."
    }

def collecting_data_loop():
    global collecting_info
    while(1):
        if stop_threads:
            break
        if not collecting_info["is_start"]:
            continue
        total_round = collecting_info["total_round"]
        interval = collecting_info["interval"]
        addresses = i2c_manager.scan_all()
        collecting_info["addresss"] = addresses
        prefix = datetime.datetime.now().strftime("%m%d-%H%M-")

        for cnt in range(total_round):
            collecting_info["current_round"] = cnt + 1
            if not collecting_info["is_start"] or stop_threads:
                break
            
            start_time = time.time()
        
            # Collecting data
            for address in addresses:
                sensor_dict = i2c_manager.read_sensor(address)
                data_name = f"{prefix}{address}_{model_name_to_id[sensor_dict['sensor_model']]}"
                dt_data = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                fieldname = ['name', 'pm1', 'pm2.5', 'pm10', 'date_time']
                data = [data_name, *sensor_dict['message'].values(), dt_data]
                store_data(fieldname, data)
                if not collecting_info["is_start"] or stop_threads:
                    break
            
            # Wait for the specified interval
            while (time.time() - start_time < interval):
                if not collecting_info["is_start"] or stop_threads:
                    break
        collecting_info["is_start"] = False
        collecting_info["total_round"] = 0
        collecting_info['current_round'] = 0
        collecting_info['interval'] = None