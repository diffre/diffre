import os
import getpass
import paramiko
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import tkinter as tk
from tkinter import filedialog


# Define the function for file encryption
def encrypt_file(file_path, public_key_path, recipient_hostname, recipient_username, recipient_password):
    try:
        # Create an SSH client
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the recipient's machine
        ssh.connect(recipient_hostname, username=recipient_username, password=recipient_password)

        # Open an SFTP session
        sftp = ssh.open_sftp()

        try:
            # Extract the file name from the file path
            file_name = os.path.basename(file_path)

            # Determine the destination path on the recipient's machine
            remote_path = "/path/to/destination/" + file_name

            # Generate a Diffie-Hellman key pair
            sender_dh = paramiko.DHGroup1()
            sender_dh.generate_key()
            sender_public_key = sender_dh.public_key

            # Save the sender's public key to a file
            public_key_file = sftp.open(public_key_path, "w")
            public_key_file.write(str(sender_public_key))
            public_key_file.close()

            # Load the recipient's public key
            recipient_public_key_file = sftp.open(public_key_path, "r")
            recipient_public_key = paramiko.DHPublicKey(recipient_public_key_file.read())
            recipient_public_key_file.close()

            # Perform Diffie-Hellman key exchange
            sender_shared_key = sender_dh.compute_shared_key(recipient_public_key)

            # Derive encryption key and IV from the shared key
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32 + 16,  # 32 bytes for the encryption key, 16 bytes for the IV
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            derived_key = kdf.derive(sender_shared_key)
            encryption_key = derived_key[:32]
            iv = derived_key[32:]

            # Encrypt the file
            cipher = Cipher(algorithms.AES(encryption_key), modes.CTR(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            with open(file_path, "rb") as src_file:
                with sftp.open(remote_path, "wb") as dest_file:
                    while True:
                        chunk = src_file.read(4096)
                        if not chunk:
                            break
                        encrypted_chunk = encryptor.update(chunk)
                        dest_file.write(encrypted_chunk)

            print("File sent successfully!")
        finally:
            # Close the SFTP session
            sftp.close()
    except paramiko.AuthenticationException:
        print("Authentication failed. Please check your credentials.")
    except paramiko.SSHException as e:
        print("SSH connection error:", str(e))
    except paramiko.sftp.SFTPError as e:
        print("SFTP error:", str(e))
    finally:
        # Close the SSH connection
        ssh.close()


# Define the function for file decryption
def decrypt_file(file_path, private_key_path, sender_hostname, sender_username, sender_password):
    try:
        # Create an SSH client
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the sender's machine
        ssh.connect(sender_hostname, username=sender_username, password=sender_password)

        # Open an SFTP session
        sftp = ssh.open_sftp()

        try:
            # Determine the source path on the sender's machine
            remote_path = "/path/to/source/" + file_path

            # Load the recipient's private key
            with open(private_key_path, "r") as private_key_file:
                sender_private_key = paramiko.DHPrivateKey(private_key_file.read())

            # Load the sender's public key
            sender_public_key_file = sftp.open(public_key_path, "r")
            sender_public_key = paramiko.DHPublicKey(sender_public_key_file.read())
            sender_public_key_file.close()

            # Perform Diffie-Hellman key exchange
            recipient_shared_key = sender_private_key.compute_shared_key(sender_public_key)

            # Derive encryption key and IV from the shared key
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32 + 16,  # 32 bytes for the encryption key, 16 bytes for the IV
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            derived_key = kdf.derive(recipient_shared_key)
            encryption_key = derived_key[:32]
            iv = derived_key[32:]

            # Decrypt the file
            cipher = Cipher(algorithms.AES(encryption_key), modes.CTR(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            with sftp.open(remote_path, "rb") as src_file:
                with open(file_path, "wb") as dest_file:
                    while True:
                        encrypted_chunk = src_file.read(4096)
                        if not encrypted_chunk:
                            break
                        chunk = decryptor.update(encrypted_chunk)
                        dest_file.write(chunk)

            print("File received successfully!")
        finally:
            # Close the SFTP session
            sftp.close()
    except paramiko.AuthenticationException:
        print("Authentication failed. Please check your credentials.")
    except paramiko.SSHException as e:
        print("SSH connection error:", str(e))
    except paramiko.sftp.SFTPError as e:
        print("SFTP error:", str(e))
    finally:
        # Close the SSH connection
        ssh.close()

# Define the function for sending a file
def send_file():
    file_path = filedialog.askopenfilename()
    public_key_path = filedialog.askopenfilename()

    recipient_hostname = recipient_hostname_entry.get()
    recipient_username = recipient_username_entry.get()
    recipient_password = recipient_password_entry.get()

    encrypt_file(file_path, public_key_path, recipient_hostname, recipient_username, recipient_password)


# Define the function for receiving a file
def receive_file():
    file_path = filedialog.askdirectory()
    private_key_path = filedialog.askopenfilename()

    sender_hostname = sender_hostname_entry.get()
    sender_username = sender_username_entry.get()
    sender_password = sender_password_entry.get()

    decrypt_file(file_path, private_key_path, sender_hostname, sender_username, sender_password)


# Define the function for selecting the sender's key
def select_sender_key():
    sender_key_path = filedialog.askopenfilename()
    sender_key_entry.delete(0, tk.END)
    sender_key_entry.insert(tk.END, sender_key_path)


# Define the function for selecting the receiver's key
def select_receiver_key():
    receiver_key_path = filedialog.askopenfilename()
    receiver_key_entry.delete(0, tk.END)
    receiver_key_entry.insert(tk.END, receiver_key_path)


# Main program
def main():
    window = tk.Tk()
    window.title("File Encryption/Decryption")
    window.geometry("900x500")

    recipient_hostname_label = tk.Label(window, text="Recipient's Hostname:")
    recipient_hostname_label.pack()
    recipient_hostname_entry = tk.Entry(window)
    recipient_hostname_entry.pack()

    recipient_username_label = tk.Label(window, text="Recipient's Username:")
    recipient_username_label.pack()
    recipient_username_entry = tk.Entry(window)
    recipient_username_entry.pack()

    recipient_password_label = tk.Label(window, text="Recipient's Password:")
    recipient_password_label.pack()
    recipient_password_entry = tk.Entry(window, show="*")
    recipient_password_entry.pack()

    sender_hostname_label = tk.Label(window, text="Sender's Hostname:")
    sender_hostname_label.pack()
    sender_hostname_entry = tk.Entry(window)
    sender_hostname_entry.pack()

    sender_username_label = tk.Label(window, text="Sender's Username:")
    sender_username_label.pack()
    sender_username_entry = tk.Entry(window)
    sender_username_entry.pack()

    sender_password_label = tk.Label(window, text="Sender's Password:")
    sender_password_label.pack()
    sender_password_entry = tk.Entry(window, show="*")
    sender_password_entry.pack()

    sender_key_label = tk.Label(window, text="Sender's Key:")
    sender_key_label.pack()
    sender_key_entry = tk.Entry(window)
    sender_key_entry.pack()
    sender_key_select_button = tk.Button(window, text="Select", command=select_sender_key)
    sender_key_select_button.pack()

    receiver_key_label = tk.Label(window, text="Receiver's Key:")
    receiver_key_label.pack()
    receiver_key_entry = tk.Entry(window)
    receiver_key_entry.pack()
    receiver_key_select_button = tk.Button(window, text="Select", command=select_receiver_key)
    receiver_key_select_button.pack()

    encrypt_button = tk.Button(window, text="Encrypt File", command=send_file)
    encrypt_button.pack()

    decrypt_button = tk.Button(window, text="Decrypt File", command=receive_file)
    decrypt_button.pack()

    # Start the GUI event loop
    window.mainloop()


if __name__ == "__main__":
    main()