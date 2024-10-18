# fwdiffer

`fwdiffer` is a command-line tool designed to compare two versions of firmware by analyzing their file contents. This tool leverages fuzzy hashing to detect modifications, added files, and removed files between two firmware images, making it a valuable asset for developers and security researchers working with embedded systems and firmware.

## Features

- **Fuzzy Hashing**: Compares binary files using fuzzy hashing (SSDEEP) to identify modified files.
- **File Type Identification**: Supports analysis of ELF Executables and Kernel Modules.
- **Progress Display**: Displays a progress bar during the comparison process.
- **Detailed Output**: Outputs modified, added, and deleted files with detailed information.
- **Debug Mode**: Provides verbose logging of the comparison process for troubleshooting.
- **Output to File**: Option to save results to a specified output file.

## Requirements

To use `fwdiffer`, ensure you have the following dependencies installed:

- Python 3.x
- Required Python packages:
  - `ssdeep`
  - `python-magic`
  - `termcolor`
  - `pyfiglet`

You can install the required Python packages using pip:

```bash
pip install ssdeep python-magic termcolor pyfiglet
