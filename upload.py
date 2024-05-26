import os
import math
import time
from base64 import b64encode
import requests
import argparse

class Client:
    def __init__(self, api_url, max_byte_length, username, password, directory):
        self.api_url = api_url
        self.max_byte_length = max_byte_length
        self.username = username
        self.password = password
        self.directory = directory

    def upload_file(self, file_path):
        file_size = os.path.getsize(file_path)
        headers = {
            "Filename": os.path.basename(file_path),
            "Authorization": "Basic {}".format(
                b64encode(f"{self.username}:{self.password}".encode("utf-8")).decode("ascii")),
            "directory": self.directory,
            "finish": str(False),
            "replace":"false"
        }

        with open(file_path, 'rb') as file:
            start = 0
            chunk_count = math.ceil(float(file_size) / self.max_byte_length)
            print("Total chunk count:", chunk_count)
            retry_timeout = 1
            sent_chunk_count = 0

            while True:
                end = min(file_size, start + self.max_byte_length)
                headers['Range'] = "bytes={}-{}/{}".format(start, end, file_size)
                file.seek(start)
                data = file.read(self.max_byte_length)
                start = end

                try:
                    response = requests.post(self.api_url, headers=headers, data=data)
                    if response.ok:
                        print('{}. chunk sent to server'.format(sent_chunk_count + 1))
                        sent_chunk_count += 1
                    else:
                        print(f"Failed to send chunk: {response.text}")
                except requests.exceptions.RequestException as e:
                    print('Error while sending chunk to server: {}. Retrying in {} seconds'.format(e, retry_timeout))
                    time.sleep(retry_timeout)
                    if retry_timeout < 10:
                        retry_timeout += 1
                    continue

                if sent_chunk_count >= chunk_count:
                    headers["finish"] = str(True)
                    response = requests.post(self.api_url, headers=headers)
                    if response.ok:
                        print("Upload completed successfully.")
                        if "webdav_url" in str(response.text):
                            print(response.text)
                        return True
                    else:
                        print(f"Failed to complete upload: {response.text}")
                        return False

            return False

def main(api_url, file_path, username, password, directory):
    client = Client(api_url, 1024 * 1024 * 25, username, password, directory)
    print('Uploading file:', file_path)
    success = client.upload_file(file_path)
    if success:
        print("File uploaded successfully.")
    else:
        print("Failed to upload file.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Upload a file in chunks.")
    parser.add_argument("api_url", type=str, help="The endpoint URL for file upload.")
    parser.add_argument("file_path", type=str, help="The path to the file to be uploaded.")
    parser.add_argument("username", type=str, help="The username for authentication.")
    parser.add_argument("password", type=str, help="The password for authentication.")
    parser.add_argument("directory", type=str, help="The directory where the file will be stored.")
    args = parser.parse_args()
    main(args.api_url, args.file_path, args.username, args.password, args.directory)
