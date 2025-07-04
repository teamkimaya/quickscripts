import asyncio
import falcon.asgi
from pymodbus.client import AsyncModbusTcpClient
import uvicorn
import logging
import json # Import json for sending JSON strings

# Optional: enable logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)

# Modbus TCP Device Parameters
DEVICE_IP = "192.168.0.1"  # Replace with your Modbus device IP
PORT = 502
SLAVE_ID = 255
REGISTER_ADDRESS = 0
REGISTER_COUNT = 23

# WebSocket Handler
class ModbusWebSocketResource:
    def __init__(self):
        self.connections = set()
        self.client = None
        self.polling_task = None

    async def on_websocket(self, req, ws):
        await ws.accept()
        self.connections.add(ws)
        print("📡 WebSocket client connected.")

        # If polling hasn't started, start it
        if not self.polling_task:
            self.polling_task = asyncio.create_task(self.start_modbus_polling())
            print("🚀 Started Modbus polling background task.")

        try:
            # Keep the WebSocket open; client will disconnect when done
            while True:
                # You might want to process incoming messages from the WebSocket here
                # For this example, we just keep the connection alive
                await ws.receive_text() # Or receive_data() if expecting binary
        except Exception as e:
            print(f"WebSocket error: {e}")
        finally:
            self.connections.remove(ws)
            print("🔌 WebSocket client disconnected.")
            # Optional: if no more connections, you might want to stop polling
            # For simplicity, we keep it running once started.

    async def start_modbus_polling(self):
        self.client = AsyncModbusTcpClient(host=DEVICE_IP, port=PORT)
        await self.client.connect()

        print(f"🔌 Modbus client connected to {DEVICE_IP}:{PORT}")
        while True:
            if not self.connections:
                # If no clients are connected, you might choose to pause or stop polling
                # For this example, we'll keep polling even if no one is listening
                pass

            try:
                response = await self.client.read_input_registers(
                    address=REGISTER_ADDRESS, count=REGISTER_COUNT, slave=SLAVE_ID
                )

                if not response.isError():
                    data = response.registers
                    data = [x * 12 / 36306.925 for x in data]
                    payload = {
                        "timestamp": asyncio.get_event_loop().time(),
                        "values": data,
                    }

                    # Send to all connected WebSocket clients
                    for conn in list(self.connections):  # Use list to iterate over a copy
                        try:
                            # Falcon's WebSocket does not have send_json directly
                            await conn.send_text(json.dumps(payload))
                        except Exception as e:
                            print(f"Error sending to client: {e}")
                            self.connections.remove(conn)  # Remove broken connection
                else:
                    print(f"Modbus Error: {response}")
            except Exception as e:
                print(f"Modbus exception: {e}")

            await asyncio.sleep(0.051)

# Create ASGI Falcon App
modbus_ws_resource = ModbusWebSocketResource()
app = falcon.asgi.App()

# Add the WebSocket resource to the Falcon application
# Falcon uses add_route for all routes, including WebSockets.
# The `on_websocket` method will be automatically called when a WS connection is made.
app.add_route("/ws", modbus_ws_resource)

# Note: The middleware for starting polling is no longer strictly necessary
# as we initiate polling when the first WebSocket client connects in
# ModbusWebSocketResource.on_websocket. If you want polling to start immediately
# when the server launches, regardless of WebSocket connections, you can keep
# a similar middleware, but it needs to interact with the resource instance.
# However, for this specific use case (Modbus data via WebSocket), starting
# polling on first connection is often more efficient.

# To start polling immediately on app startup (alternative to starting on first WS connection):
# @falcon.asgi.middleware
# class ModbusStartupMiddleware:
#     def __init__(self, app):
#         self.app = app
#
#     async def process_request(self, req, resp, resource, params):
#         # This runs for every request, which isn't ideal for a single startup task.
#         # It's better to manage background tasks outside of per-request middleware.
#         pass
#
#     async def process_response(self, req, resp, resource, req_succeeded):
#         # This runs after the response
#         pass

# A cleaner way for app-wide background tasks in Falcon, if you don't want to start on first connection:
# You'd typically manage this with the uvicorn.run's on_startup or similar event hooks
# or within your main script if you're not using a specific ASGI server's lifecycle hooks.
# For simplicity and directly tying to the WebSocket, the current implementation in
# ModbusWebSocketResource.on_websocket is good.

# Start server using python3 main.py
if __name__ == "__main__":
    # Ensure this file is saved as `main.py` if you use "main:app"
    # Or, if your file is `modbus.py`, change to "modbus:app"
    uvicorn.run("modbus:app", host="0.0.0.0", port=8000, reload=False)