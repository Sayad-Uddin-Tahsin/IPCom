# IPCom
IPCom is an offline messaging application that allows users to send messages without an internet connection. It uses the same Wi-Fi connection to send messages between devices. This makes it ideal for situations where there is no internet connection available but you still need to communicate with others. There matter is to have on same Wi-Fi/Hotspot!

## How it works?
It needs a server to work. When the server is online anyone with the same wi-fi will able to connect with the server and send message with others connected with the same server. Say `You` and 3 of your friends are connected on a server, the communication is done as this diagram shows:

```mermaid
graph TD;
    A["You"]
    B["Server"]
    C["Friend A"]
    D["Friend B"]
    E["Friend C"]
    A-->B;
    B-->C;
    B-->D;
    B-->E;

```

## Installation
Currently, no executable release is available. However, you can download the source code and run the application manually. Please note that Python needs to be installed on your system.

To run the application:

1. Clone or download this repository to your local machine.
2. Open a terminal or command prompt and navigate to the project directory.
3. Run the IPCom Server using the following command:
  ```bash
python server.py
```
4. Run the IPCom application also to join yourself using the following command:
```bash
python ipcom.py
```
Make sure you have Python installed on your system.

## License
This project is licensed under the [MIT License](./LICENSE).
