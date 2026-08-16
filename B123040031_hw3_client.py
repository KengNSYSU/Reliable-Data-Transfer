from socket import *
import struct
import random
import os
def pack_header(seq, ack):
    return struct.pack('!II', seq, ack)
def unpack_header(header_bytes):
    return struct.unpack('!II', header_bytes)
MAX_SEQ = 2**32
loss_rate = 0.15
MSS = 1024
serverName = '127.0.0.1'
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)

req_file = input('file name\n').strip()
ack = 0
seq = 0
while True:
    req_header = pack_header(seq, ack)
    request_packet = req_header + req_file.encode()
    clientSocket.sendto(request_packet, (serverName, serverPort))
    seq = (seq + len(req_file.encode())) % MAX_SEQ
    print(f"Sent request for {req_file} (Seq={seq}, Ack={ack})")
    received_chunks = {}
    expected_seq = ack 
    start_seq_for_file = ack
    total_file_data = b""

    while True:
        packet, addr = clientSocket.recvfrom(2048)

        if random.random() < loss_rate:
            print("[PACKET LOSS]")
            continue

        header_bytes = packet[:8]
        payload_bytes = packet[8:]

        s_seq, s_ack = unpack_header(header_bytes)
        if b'file no found' == payload_bytes:
            print('file no found')
            ack = (ack + len(payload_bytes)) % MAX_SEQ
            req_file = input('file name\n').strip()
            break
        
        if s_seq == expected_seq:
            print(f'[RECEIVE PACKET] Received expected Seq={s_seq}, Size={len(payload_bytes)} bytes.')
            received_chunks[s_seq] = payload_bytes
            expected_seq = (expected_seq + len(payload_bytes)) % MAX_SEQ
            ack = expected_seq
            client_header = pack_header(seq, expected_seq)
            clientSocket.sendto(client_header, addr)
            print(f"[ACK SENT] SEQ={seq}, ACK={expected_seq}")

        else:
            print(f"[OUT OF ORDER] Received Seq={s_seq}, expected Seq={expected_seq}.")
            client_header = pack_header(seq, expected_seq)
            clientSocket.sendto(client_header, addr)
            print(f"[ACK RESENT] SEQ={seq}, ACK={expected_seq}")

        previous_expected = (expected_seq - len(payload_bytes)) % MAX_SEQ
        if len(payload_bytes) < MSS and s_seq == previous_expected:
            print("[REVEIVING FINISH] Writing file")
            file_path = os.path.join('./client_dir', req_file)

            with open(file_path, 'wb') as f:
                current_write_bytes = 0
                while len(received_chunks) > 0:
                    target_seq = (start_seq_for_file + current_write_bytes) % MAX_SEQ
                    if target_seq in received_chunks:
                        f.write(received_chunks[target_seq])
                        current_write_bytes += len(received_chunks[target_seq])
                        del received_chunks[target_seq]
                    else:
                        break
            
            print('[ALL FINISH]')
            ack = expected_seq
            break
    req_file = input('file name\n').strip()