from fastapi import FastAPI
from data_model import *
from threading import Thread
import time, datetime
import i2c_manager

collecting_info = {
    "is_start": False,
    "interval": None,
    "quantity": None
}

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/i2c-devices")
async def list_i2c_devices():
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

@app.get("/i2c-device/{address}")
async def read_data_from_given_address(address: int):
    if i2c_manager.scan(address):
        return i2c_manager.read_sensor(address)
    return {"message" : "Can't Read Data"}

@app.post("/start")
async def start_data_collection(start_data: StartModel):
    global collecting_info
    if collecting_info["is_start"]:
        return {
            "status": "fail",
            "message": "Data collection already started. Please stop it first."
        }
    collecting_info["interval"] = start_data.interval
    collecting_info["quantity"] = start_data.quantity
    collecting_info["is_start"] = True
    return {
        "status": "success",
        "message": "Data collection has started."
    }

@app.post("/stop")
async def start_data_collection():
    global collecting_info
    if collecting_info["is_start"]:
        collecting_info["is_start"] = False
        return {
            "status": "success",
            "message": "Data collection has stopped"
        }
    return {
        "status": "fail",
        "message": "Data collection didn't start yet."
    }

@app.on_event("startup")
async def startup_event():
    thread = Thread(target=collecting_data_loop)
    thread.start()

def collecting_data_loop(quantity, interval, i2c_manager):
    if not collecting_info["is_start"]:
        return

    addresses = i2c_manager.scan_all()
    
    for _ in range(quantity):
        if not collecting_info["is_start"]:
            break
        
        start_time = time.time()
        
        # Collecting data
        for address in addresses:
            i2c_manager.read_sensor(address)
            if not collecting_info["is_start"]:
                break
        
        # Wait for the specified interval
        while (time.time() - start_time < interval):
            if not collecting_info["is_start"]:
                break