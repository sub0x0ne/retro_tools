import os
import zipfile
import subprocess
import shutil

def process_zip_files(folder_path, chd_output_path, remove_zip, chdman_path):
    """
    Extracts .zip files, processes ISO/BIN/CUE files within using chdman,
    and then deletes the extracted files and original zip archives.
    """
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".zip"):
            zip_path = os.path.join(folder_path, filename)
            extract_folder = os.path.join(folder_path, filename[:-4])
            try:
                os.makedirs(extract_folder, exist_ok=True)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_folder)
                process_images(extract_folder, chd_output_path, chdman_path)

                if chd_output_path is None or chd_output_path == "":
                    # If chd_output_path is the same as extracted folder, delete all except .chd
                    for item in os.listdir(extract_folder):
                        item_path = os.path.join(extract_folder, item)
                        if not item.lower().endswith(".chd"):
                            if os.path.isfile(item_path):
                                os.remove(item_path)
                            elif os.path.isdir(item_path):
                                shutil.rmtree(item_path)
                    if not os.listdir(extract_folder):
                        os.rmdir(extract_folder) #remove empty directory
                else:
                    shutil.rmtree(extract_folder)

                if remove_zip:
                    os.remove(zip_path)
                    print(f"Processed and deleted: {filename}")
                else:
                    print(f"Processed: {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

def process_images(folder_path, chd_output_path, chdman_path):
    """Processes ISO/BIN/CUE files."""
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if filename.lower().endswith((".iso", ".cue")):
            chd_filename = os.path.splitext(filename)[0] + ".chd"
            if chd_output_path:
                chd_path = os.path.join(chd_output_path, chd_filename)
            else:
                chd_path = os.path.join(folder_path, chd_filename)
            try:
                command = [chdman_path, "createcd", "-i", file_path, "-o", chd_path]
                result = subprocess.run(command, check=True, capture_output=True, text=True)
                print(result.stdout)
                print(result.stderr)
                os.remove(file_path)
                print(f"Created CHD: {chd_filename}")
            except subprocess.CalledProcessError as e:
                print(f"Error processing {filename}: chdman failed - {e}")
                print(e.stderr)
            except FileNotFoundError:
                print(f"chdman not found at: {chdman_path}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    folder_path = input("Enter the folder path containing .zip files: ")
    chd_output_path = input("Enter the path to write .chd files (leave blank for same folder): ").strip()
    remove_zip_input = input("Remove original .zip archives after processing? (y/n): ").lower()
    remove_zip = remove_zip_input == "y"
    chdman_path = input("Enter the path to the chdman executable (leave blank for /usr/bin/mame/chdman): ").strip()

    if not chdman_path:
        chdman_path = "/usr/bin/mame/chdman"

    if chd_output_path:
        if not os.path.exists(chd_output_path):
            try:
                os.makedirs(chd_output_path)
            except OSError as e:
                print(f"Error creating output directory: {e}")
                exit()
    else:
        chd_output_path = ""

    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        process_zip_files(folder_path, chd_output_path, remove_zip, chdman_path)
        print("Processing complete.")
    else:
        print("Invalid folder path.")