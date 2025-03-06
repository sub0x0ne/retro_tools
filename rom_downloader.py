import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, unquote
import time
import threading
from queue import Queue

def download_file(file_url, file_path, failed_downloads_file, max_retries=3, retry_delay=5):
    """Downloads a single .zip file with retries, logs failures."""
    for attempt in range(max_retries):
        try:
            print(f"Downloading '{os.path.basename(file_path)}' (Attempt {attempt + 1}/{max_retries})...")
            file_response = requests.get(file_url, stream=True)
            file_response.raise_for_status()

            with open(file_path, 'wb') as file:
                for chunk in file_response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"'{os.path.basename(file_path)}' downloaded successfully.")
            return True  # Indicate success

        except requests.exceptions.RequestException as e:
            print(f"Error downloading '{os.path.basename(file_path)}' (Attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"Failed to download '{os.path.basename(file_path)}' after {max_retries} attempts.")
                # --- Log the failed download ---
                with open(failed_downloads_file, "a") as f:
                    f.write(f"{os.path.basename(file_path)}\n")
                return False
        except Exception as e:
            print(f"An unexpected error occurred when downloading '{os.path.basename(file_path)}' (Attempt {attempt+1}): {e}")
            if attempt < max_retries -1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"Failed to download '{os.path.basename(file_path)}' after {max_retries} attempts.")
                with open(failed_downloads_file, "a") as f:
                    f.write(f"{os.path.basename(file_path)}\n")
                return False
    return False

def worker(queue, download_dir, failed_downloads_file, max_retries, retry_delay):
    """Thread worker function."""
    while True:
        file_url, file_name = queue.get()
        if file_url is None:
            break
        file_path = os.path.join(download_dir, file_name)
        if not os.path.exists(file_path) and file_name.endswith('.zip'):
            download_file(file_url, file_path, failed_downloads_file, max_retries, retry_delay)
        elif os.path.exists(file_path):
            print(f"Skipping '{file_name}' (already downloaded)")

        queue.task_done()


def download_files_from_page(url, download_dir, region_filter="All", max_retries=3, retry_delay=5):
    """Downloads .zip files from a webpage, logs failures."""

    failed_downloads_file = "failed_downloads.txt"  # File to store failed downloads

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error accessing the URL: {e}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')

    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    links = soup.find_all('a', href=True)

    while True:
        try:
            num_threads = int(input("Enter the number of simultaneous downloads: "))
            if num_threads > 0:
                break
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    download_queue = Queue()

    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=worker, args=(download_queue, download_dir, failed_downloads_file, max_retries, retry_delay))
        threads.append(thread)
        thread.start()

    for link in links:
        href = link['href']
        if not href.endswith('/') and href != "../" and href.endswith(".zip"):
            file_name = unquote(os.path.basename(href))
            if region_filter.lower() == "all" or region_filter.lower() in file_name.lower():
                file_url = urljoin(url, href)
                download_queue.put((file_url, file_name))

    download_queue.join()

    for _ in range(num_threads):
        download_queue.put((None, None))
    for thread in threads:
        thread.join()

    print("Download process completed (or encountered errors).")


if __name__ == "__main__":
    target_url = input("Enter the target URL: ")
    download_dir = input("Enter the download directory (leave blank for 'downloads'): ")
    if not download_dir:
        download_dir = "downloads"

    valid_regions = ["USA", "Europe", "Japan", "World", "All"]
    while True:
        region_filter = input(f"Enter region filter ({', '.join(valid_regions)}), default is All: ").strip()
        if not region_filter:
            region_filter = "All"
            break
        elif region_filter.lower() in [r.lower() for r in valid_regions]:
            break
        else:
            print("Invalid region.  Please choose from:", ", ".join(valid_regions))

    download_files_from_page(target_url, download_dir, region_filter)
