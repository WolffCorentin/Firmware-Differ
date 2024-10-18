# Firmware Differ

`fwdiffer` is a command-line tool designed to compare two versions of firmware by analyzing their file contents. This tool leverages fuzzy hashing to detect modifications, added files, and removed files between two firmware images, making it a valuable asset for developers and security researchers working with embedded systems and firmware.

### Responsible Laboratory
- **Laboratory Manager**: [@qkaiser](https://github.com/qkaiser)

## Features

- **Fuzzy Hashing**: Compares binary files using fuzzy hashing (SSDEEP) to identify modified files.
- **File Type Identification**: Supports analysis of ELF Executables and Kernel Modules.
- **Detailed Output**: Outputs modified, added, and deleted files with detailed information.
- **Debug Mode**: Provides verbose logging of the comparison process for troubleshooting.
- **Output to File**: Option to save results to a specified output file.

## Requirements

To use `fwdiffer`, ensure you have the following dependencies installed:

### Installation with `requirements.txt`

1. Clone the repository:

```bash
git clone https://github.com/WolffCorentin/fwdiffer.git
