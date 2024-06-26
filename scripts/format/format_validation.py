import os
import subprocess
import sys

FILES_DIRS = ["engine/Assets/Scripts"]
FILE_TARGETS = [".cs"]

def main():
    if sys.platform != "linux":
        print("Warning: This script was designed to be run by github action linux machines")

    files = []
    for dir in FILES_DIRS:
        for root, _, filenames in os.walk(dir):
            for filename in filenames:
                if os.path.splitext(filename)[1] in FILE_TARGETS:
                    files.append(os.path.abspath(os.path.join(root, filename)))

    exit_code = 0
    for file in files:
        with open(file, "r") as f:
            previous_file_state = f.readlines()

        subprocess.call(
            ["clang-format-16", "-i", "-style=file", file],
            bufsize=1,
            shell=False,
        )

        with open(file, "r") as f:
            new_file_state = f.readlines()

        for i, (previous_line, new_line) in enumerate(zip(previous_file_state, new_file_state)):
            if previous_line != new_line:
                print(f"File {file} is not formatted correctly!")
                print(f"Line: {i + 1}")
                exit_code = 1
                break

    if exit_code == 0:
        print("All files are formatted correctly!")

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
