#!/bin/python
# pip install pyModbusTCP
from pyModbusTCP.server import ModbusServer, DataBank
from time import sleep
from random import uniform
import win32ui, dde
import re


def launch_ModbusTCP():
    max_retries = 3
    retry_delay = 30  # seconds
    server = None
    DDE_server = None
    DDE_client = None
    
    for attempt in range(max_retries):
        try:
            # Connect to DDE server
            DDEserver_name = 'MLDdeSrvr'
            DDE_server = dde.CreateServer()
            DDE_server.Create(DDEserver_name)

            # Create a conversation between client and server
            DDE_client = dde.CreateConversation(DDE_server)
            DDE_client.ConnectTo('MLDdeSrvr', 'data')
            if DDE_client.Connected() == 1:
                print('connection established')

            # Create an instance of ModbusServer
            server = ModbusServer("127.0.0.1", 502, no_block=True)
            
            # Function for convert data between DDE Server and Modbus TCP Server
            def DDE_2_MODBUS(Modbus_address,Tag_in):
                requested_data = DDE_client.Request(Tag_in)
                data1 = re.findall(r'[\d]*[.][\d]+', requested_data)
                data2 = re.findall(r'[\d]+', requested_data)
                if data1==[]:
                    if data2==[]:
                        Tag_out=0
                    else:
                        Tag_out= float(data2[0])*10
                else:
                    Tag_out= float(data1[0])*10
                server.data_bank.set_holding_registers(Modbus_address, [Tag_out])
                return(Tag_out)

            print('START LOOP')
            print(f"Attempt {attempt + 1} of {max_retries} to launch CX2000 ModbusTCP...")
            
            print("Start server...")
            server.start()
            print("Server is online")

            while True:
                CH01 = DDE_2_MODBUS(0, "TAG0001")
                CH02 = DDE_2_MODBUS(1, "TAG0002")
                CH03 = DDE_2_MODBUS(2, "TAG0003")
                CH04 = DDE_2_MODBUS(3, "TAG0004")
                CH05 = DDE_2_MODBUS(4, "TAG0005")
                CH06 = DDE_2_MODBUS(5, "TAG0006")
                CH07 = DDE_2_MODBUS(6, "TAG0007")
                CH08 = DDE_2_MODBUS(7, "TAG0008")
                CH09 = DDE_2_MODBUS(8, "TAG0009")
                CH10 = DDE_2_MODBUS(9, "TAG0010")
                CH11 = DDE_2_MODBUS(10, "TAG0011")
                CH12 = DDE_2_MODBUS(11, "TAG0012")
                CH13 = DDE_2_MODBUS(12, "TAG0013")
                CH14 = DDE_2_MODBUS(13, "TAG0014")
                CH15 = DDE_2_MODBUS(14, "TAG0015")
                CH16 = DDE_2_MODBUS(15, "TAG0016")
                CH17 = DDE_2_MODBUS(16, "TAG0017")
                CH18 = DDE_2_MODBUS(17, "TAG0018")
                CH19 = DDE_2_MODBUS(18, "TAG0019")
                CH20 = DDE_2_MODBUS(19, "TAG0020")

                sleep(1)
            
        except Exception as e:
            error_message = f"Error on attempt {attempt + 1}: {str(e)}"
            print(error_message)
            
            # Clean up resources
            try:
                if server:
                    print("Stopping Modbus server...")
                    server.stop()
            except Exception as se:
                print(f"Error stopping server: {se}")
                
            try:
                if DDE_server:
                    print("Destroying DDE server...")
                    DDE_server.Destroy()
            except Exception as dse:
                print(f"Error destroying DDE server: {dse}")
            
            if attempt < max_retries - 1:
                print(f"Waiting {retry_delay} seconds before next attempt...")
                sleep(retry_delay)
            else:
                print("All retry attempts failed")
                return False
    return True

if __name__ == "__main__":
    launch_ModbusTCP()