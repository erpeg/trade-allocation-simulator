import concurrent.futures

from fill_server import utils

number_of_servers = 3
fill_url = "http://localhost:8000/fill"

if __name__ == "__main__":
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for _ in range(number_of_servers):
            executor.submit(utils.send_request(fill_url))
