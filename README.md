# RDT (Reliable Data Transfer) Protocol Implementation

## Introduction

This project is an implementation of a Reliable Data Transfer (RDT) protocol over UDP. It ensures reliable transmission of files from a server to a client, handling packet loss and reordering. The protocol implemented is a custom version of the Go-Back-N protocol.

## Features

- **Reliable File Transfer:** Ensures that files are transferred completely and correctly from server to client.
- **Packet Loss Detection and Recovery:** The server retransmits packets that are not acknowledged by the client within a certain time frame.
- **In-order Packet Delivery:** The client buffers out-of-order packets and writes them to the file in the correct sequence.
- **Sliding Window Protocol:** The server uses a sliding window to send multiple packets without waiting for an acknowledgment for each one, improving efficiency.

## File Structure

- `B123040031_hw3_server.py`: The server script that sends files to the client.
- `B123040031_hw3_client.py`: The client script that requests and receives files from the server.
- `server_dir/`: Directory where the files to be transferred are stored.
- `client_dir/`: Directory where the received files are saved.
- `detail_visualization.pdf`: Visualize the deatil of how the code works.

## Usage

1.  **Start the server:**
    ```bash
    python B123040031_hw3_server.py
    ```
    The server will start and wait for client connections.

2.  **Run the client:**
    ```bash
    python B123040031_hw3_client.py
    ```
    The client will prompt you to enter the name of the file you want to request.

3.  **Enter the filename:**
    When prompted, enter the name of the file you wish to transfer from the `server_dir/`. For example:
    ```
    file name
    test_0.jpg
    ```

4.  **File Transfer:**
    The client will request the file from the server, and the server will send it. The client will display the progress of the download and save the file in the `client_dir/`.

## Author

- **B123040031**
