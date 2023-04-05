import json
import logging
import sys
import greengrasssdk

# Logging
logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# SDK Client
client = greengrasssdk.client("iot-data")

max_co2 = {}
def lambda_handler(event, context):
    global max_co2
    # TODO1: Get your data
    device_id = event['device_id']
    logger.info(f'Message from: {device_id} , {event}')
    prev_reading = max_co2.get(device_id, 0)
    new_reading = event.get('vehicle_CO2', 0)

    # TODO2: Calculate max CO2 emission
    if new_reading > prev_reading:
        max_co2[device_id] = new_reading

    # TODO3: Return the result
    client.publish(
        topic=f"device/resp/{device_id}",
        payload=json.dumps(
            {"max_vehicle_CO2": max_co2.get(device_id, 0)}
        ),
    )

    return