import socket
import struct
import os
import time
def pack_header(seq, ack):
    return struct.pack('!II', seq, ack)
def unpack_header(header_bytes):
    return struct.unpack('!II', header_bytes)

X = 1
N = (X % 5) + 4 #window size
T = 0.5 + (X * 0.1) # Timeout Interval
MSS = 1024
MAX_SEQ = 2**32
global_server_seq = 0
loss_rate = 0.15
serverPort = 12000
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind(('', serverPort))

print('The server is ready to receive')
while True:
    serverSocket.setblocking(True)
    message, clientAddress = serverSocket.recvfrom(2048)
    header = message[:8]
    payload = message[8:]
    client_seq, client_ack = unpack_header(header)
    req_file = payload.decode().strip()
    print(f'Client asks for {req_file} with seq={client_seq}, ack={client_ack}')
    file_path = os.path.join("./server_dir", req_file)
    if not os.path.exists(file_path):
        print('file no found')
        error_message = 'file no found'
        server_seq = global_server_seq
        server_ack = (client_seq + len(payload)) % MAX_SEQ
        error_header = pack_header(server_seq, server_ack)
        error_packet = error_header + error_message.encode()
        serverSocket.sendto(error_packet, clientAddress)
        global_server_seq = (global_server_seq + len(error_message.encode())) % MAX_SEQ
        continue
    with open(file_path, 'rb') as f:
        file_data = f.read()

    file_size = len(file_data)
    packets = []
    file_ptr = 0
    server_ack = (client_seq + len(payload)) % MAX_SEQ

    while file_ptr < file_size:
        chunk = file_data[file_ptr : file_ptr + MSS]
        pkt_seq = (global_server_seq + file_ptr)% MAX_SEQ
        header = pack_header(pkt_seq, server_ack)
        packets.append((pkt_seq, header + chunk))
        file_ptr += len(chunk)

    total_packets = len(packets)
    base_idx = 0
    next_idx = 0
    serverSocket.setblocking(False)
    last_ack_time = time.time()

    while base_idx < total_packets:
        while next_idx < base_idx + N and next_idx < total_packets:
            pkt_seq, pkt_data = packets[next_idx]
            serverSocket.sendto(pkt_data, clientAddress)
            print(f"[SEND] Sent packet idx {next_idx}, Seq={pkt_seq}, Ack={server_ack}, Size={len(pkt_data)}")
            
            if base_idx == next_idx:
                last_ack_time = time.time()
            next_idx += 1
            
        
        try:
            ack_message, addr = serverSocket.recvfrom(2048)
            c_seq, c_ack = unpack_header(ack_message[:8])
            print(f"[ACK RECEIVED] Client expects next byte: {c_ack}")
            for i in range(base_idx, total_packets):
                pkt_end = (packets[i][0] + (len(packets[i][1]) - 8))% MAX_SEQ
                if c_ack == pkt_end:
                    base_idx = i + 1
                    last_ack_time = time.time()
        except BlockingIOError:
            pass

        if time.time() - last_ack_time > T:
            print(f"[TIMEOUT] Timer expired {T}s")
            next_idx = base_idx 
            last_ack_time = time.time()

    print(f"Successfully finished transmitting {req_file}!\n")
    global_server_seq = (global_server_seq + file_size) % MAX_SEQ