import os
import shutil
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
#Script by Fewffwa
#Uses GCRebuilder functionality
def pick_iso_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select a GameCube ISO",
        filetypes=[("GameCube ISO", "*.iso"), ("All files", "*.*")]
    )
    return file_path

def fix_loop(file):
    f = open(file, 'r+b')
    data = f.read()
    length = len(data)
    mo = length % 32
    diff = 32 - mo
    f.write(bytearray(1024 + diff))
    if ((length + diff) % 64) == 0:
        f.write(bytearray(32))
    print("fixed loop for" + file)



def clean_directory(directory):
    """Clean the directory if it already exists."""
    if os.path.isdir(directory):
        print(f"Cleaning existing directory: {directory}")
        shutil.rmtree(directory)

def extract_iso(gcr_path, iso_path, extract_path):
    # Ensure the paths are quoted to handle spaces or special characters
    iso_path_quoted = f'"{iso_path}"'
    extract_path_quoted = f'"{extract_path}"'

    print(f"Extracting {iso_path_quoted} to {extract_path_quoted}...")

    result = subprocess.run([gcr_path, iso_path, "root", "e", extract_path])


    if result.returncode != 0:
        raise RuntimeError(f"Failed to extract ISO:\n{result.stderr}")
    print(f"Extraction complete!")

def rebuild_iso_gcr(gcr_path, input_folder, output_iso):
    result = subprocess.run([gcr_path, os.path.join(input_folder, "root"), output_iso])
    if result.returncode != 0:
        raise RuntimeError(f"Gcr failed:\n{result.stderr}")
    print("ISO rebuild complete!")

def replace_stm_files(extracted_iso_dir):
    stream_path = os.path.join(extracted_iso_dir, "root", "sound","stream")
    if not os.path.isdir(stream_path):
        raise FileNotFoundError(f"Expected path not found: {stream_path}")

    replaced = []
    for file in os.listdir():
        if file.endswith(".stm") and os.path.isfile(file):
            fix_loop(file)
            target_file = os.path.join(stream_path, file)
            if os.path.exists(target_file):
                shutil.copy2(file, target_file)
                replaced.append(file)
    return replaced

def main():
    iso_path = pick_iso_file()
    if not iso_path:
        print("No ISO selected.")
        return
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    gcr_path = os.path.join(os.getcwd(), "gcrebuilder", "gcr.exe")
    if not gcr_path:
        print("No exe selected")

    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"Created temporary directory: {tmpdir}")


        try:
            # Extract ISO to the temporary directory
            extract_iso(gcr_path, iso_path, tmpdir)
        except Exception as e:
            messagebox.showerror("Extraction Error", str(e))
            return

        try:
            replaced = replace_stm_files(tmpdir)
            if replaced:
                print("Replaced files:")
                for f in replaced:
                    print(f"  - {f}")
            else:
                print("No matching .STM files found to replace.")
        except Exception as e:
            messagebox.showerror("File Replacement Error", str(e))
            return

        output_iso = iso_path.replace(".iso", "_music.iso")
        try:
            rebuild_iso_gcr(gcr_path, tmpdir, output_iso)
            messagebox.showinfo("Success", f"Modified ISO saved as:\n{output_iso}")
        except Exception as e:
            messagebox.showerror("Rebuild Error", str(e))

if __name__ == "__main__":
    main()
