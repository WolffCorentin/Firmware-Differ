#!/usr/bin/env python3
import hashlib
import argparse
from pathlib import Path
import ssdeep
import magic
from termcolor import colored
import sys
import pyfiglet


def display_title():
    title = pyfiglet.figlet_format("fwdiffer", font="slant")
    print(colored(title, 'red'))  # Use 'yellow' for the orange-like effect
    print("Comparing firmware versions...\n")


def display_progress_bar(percentage):
    # Create a compact progress bar
    progress_bar_length = 100  # Length of the progress bar
    block = int(round(progress_bar_length * (percentage / 100)))
    bar = f"[{'─' * block}{' ' * (progress_bar_length - block)}] {percentage:.0f}%"    
    print(f"\r{bar}", end='', flush=True)  # Overwrite the line in the terminal


def calculate_md5(file_path):
    hash_obj = hashlib.md5()
    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


def scan_directory(dir_path):
    files_map = {}
    dir_path = Path(dir_path)
    for file_path in dir_path.rglob('*'):
        if file_path.is_file() and not file_path.is_symlink():
            files_map[file_path.name] = str(file_path)  # Convert Path object to string for compatibility
    return files_map


def identify_file_type(file_path):
    mime = magic.Magic(mime=True)
    file_type = mime.from_file(file_path)
    if 'application/x-executable' in file_type or 'application/x-sharedlib' in file_type:
        return 'ELF Executable'
    elif file_path.endswith('.ko'):
        return 'Kernel Module'
    else:
        return 'Other'


def calculate_fuzzy_hash(file_path):
    with open(file_path, "rb") as f:
        file_data = f.read()
    return ssdeep.hash(file_data)


def compare_firmwares(first_firmware, second_firmware, similarity_threshold=30, enable_debug=False):
    mod_files = []
    new_files = list(second_firmware.keys() - first_firmware.keys())
    removed_files = list(first_firmware.keys() - second_firmware.keys())
    common_files = first_firmware.keys() & second_firmware.keys()

    total_files = len(common_files)  # Total files to compare
    processed_files = 0  # Counter for processed files

    for filename in common_files:
        full_path_first = first_firmware[filename]  # This is a string path
        full_path_second = second_firmware[filename]  # This is a string path

        file_type_first = identify_file_type(full_path_first)
        file_type_second = identify_file_type(full_path_second)

        if file_type_first == file_type_second and file_type_first in ['ELF Executable', 'Kernel Module']:
            fuzzy_hash_first = calculate_fuzzy_hash(full_path_first)
            fuzzy_hash_second = calculate_fuzzy_hash(full_path_second)
            similarity = ssdeep.compare(fuzzy_hash_first, fuzzy_hash_second)

            if enable_debug:
                print(f"Debug: Comparing {filename}:")
                print(f"  {full_path_first} -> Fuzzy Hash: {fuzzy_hash_first}")
                print(f"  {full_path_second} -> Fuzzy Hash: {fuzzy_hash_second}")
                print(f"  Similarity: {similarity}%")

            if similarity <= similarity_threshold:
                mod_files.append((full_path_first, full_path_second, similarity, file_type_first, filename))

        # Update processed files and print progress
        processed_files += 1
        percentage_done = (processed_files / total_files) * 100
        display_progress_bar(percentage_done)  # Display the progress bar

    print()  # Print a newline after progress is complete
    return mod_files, new_files, removed_files


def format_output(modified, added, deleted):
    output_lines = []
    separator_length = 100  # Fixed width for the separators

    # Separate modified files into ELF Executables and Kernel Modules
    elf_executables = [entry for entry in modified if entry[3] == 'ELF Executable']
    kernel_modules = [entry for entry in modified if entry[3] == 'Kernel Module']

    # Handle modified files
    output_lines.append(colored(f"Modified files ({len(modified)}) :", 'cyan', attrs=['bold']))
    output_lines.append("─" * separator_length)  # Separator line
    output_lines.append(f"{'File Name':<40} {'Similarity (%)':<20} {'Type':<20} {'Path'}")
    output_lines.append("─" * separator_length)  # Header separator

    seen_files = set()  # To track unique filenames

    # Output ELF Executables first
    for full_path_first, full_path_second, similarity, file_type, filename in elf_executables:
        # Check for valid filename and uniqueness
        if filename and (filename, file_type) not in seen_files:
            seen_files.add((filename, file_type))  # Track the filename and type
            output_lines.append(f"{filename:<40} {similarity:<20} {file_type:<20} {full_path_second}")

    # Output Kernel Modules next
    for full_path_first, full_path_second, similarity, file_type, filename in kernel_modules:
        # Check for valid filename and uniqueness
        if filename and (filename, file_type) not in seen_files:
            seen_files.add((filename, file_type))  # Track the filename and type
            output_lines.append(f"{filename:<40} {similarity:<20} {file_type:<20} {full_path_second}")

    output_lines.append('\n' + "─" * separator_length)

    # Handle added files
    if added:
        output_lines.append(colored("Added files:", 'green', attrs=['bold']))
        output_lines.append("─" * separator_length)  # Separator line
        for file in added:
            output_lines.append(f"  {file}")
    else:
        output_lines.append(colored("No new files found.", 'yellow'))

    output_lines.append('\n' + "─" * separator_length)

    # Handle deleted files
    if deleted:
        output_lines.append(colored("Deleted files:", 'red', attrs=['bold']))
        output_lines.append("─" * separator_length)  # Separator line
        for file in deleted:
            output_lines.append(f"  {file}")
    else:
        output_lines.append(colored("No deleted files found.", 'yellow'))

    return "\n".join(output_lines)


def main():
    display_title()  # Display the title

    parser = argparse.ArgumentParser(description="Compares two firmware versions by file contents.")
    parser.add_argument("firmware_a", help="Path to the first extracted firmware directory (OLD ONE)")
    parser.add_argument("firmware_b", help="Path to the second extracted firmware directory (RECENT ONE)")
    parser.add_argument("-debug", action="store_true", help="Enables detailed hash comparison logs")
    parser.add_argument("-count_changes", action="store_true", help="Displays the total number of modified, added, and deleted files")
    parser.add_argument("-similarity_threshold", type=int, default=30, help="Similarity threshold for fuzzy hashing (default: 70)")
    parser.add_argument("-output", help="Path to a file where results should be saved")
    args = parser.parse_args()

    firmware_a_map = scan_directory(args.firmware_a)
    firmware_b_map = scan_directory(args.firmware_b)

    modified, added, deleted = compare_firmwares(firmware_a_map, firmware_b_map, args.similarity_threshold, enable_debug=args.debug)
    output = format_output(modified, added, deleted)

    if args.count_changes:
        output += f"\n-----\nTotal Modified Files: {len(modified)}"
        output += f"\nTotal Added Files: {len(added)}"
        output += f"\nTotal Deleted Files: {len(deleted)}"

    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Results saved to {args.output}")
    else:
        print(output)

if __name__ == "__main__":
    main()