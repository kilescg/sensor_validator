from fastapi import FastAPI
import i2c_manager

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/i2c-devices")
async def list_i2c_devices():
    data_frame = []
    i2c_addresses = i2c_manager.scan()
    for address in i2c_addresses:
        sensor_dict = i2c_manager.read_sensor(address)
        data_frame.append(
            {
                'address' : address,
                'sensor_model' : sensor_dict['sensor_model']
            }
        )
    return data_frame

# @app.get("/i2c-device/{address}")
# async def read_data_from_given_address(address: int):
#     sensor_dict = i2c_manager.read_sensor(address)
#     return sensor_dict