# modules/io_helpers.py

import torch
import gzip
import numpy as np
import os

class Outputter:
    OUTPUT_FORMATS = ["pt", "pth", "npy"]
    @staticmethod
    def save_data(data, filename_prefix, output_format):
        """
        Save data (a tensor or array) to disk using the specified format.
        Returns the file path of the saved file.
        """
        if output_format in ["pt", "pth"]:
            file_path = f"{filename_prefix}.{output_format}"
            torch.save(data, file_path)
        elif output_format == "npy":
            # np.save automatically appends the .npy extension if not provided
            file_path = f"{filename_prefix}.npy"
            np.save(filename_prefix, data)
        else:
            raise ValueError("Invalid output format")
        return file_path

    @staticmethod
    def compress_file(file_path):
        """
        Compress the given file using gzip.
        Returns the new file path ending with '.gz'.
        """
        compressed_file_path = file_path + ".gz"
        with open(file_path, "rb") as f_in:
            with gzip.open(compressed_file_path, "wb") as f_out:
                f_out.writelines(f_in)
        os.remove(file_path)
        return compressed_file_path


class Inputter:
    @staticmethod
    def load_data(filepath):
        """
        Load data (a tensor or array) from the given file.
        Supports both compressed (.gz) and uncompressed files.
        """
        if filepath.endswith(".gz"):
            with gzip.open(filepath, "rb") as f:
                if filepath.endswith(".pt.gz") or filepath.endswith(".pth.gz"):
                    return torch.load(f)
                elif filepath.endswith(".npy.gz"):
                    return np.load(f)
                else:
                    raise ValueError("Invalid file format")
        else:
            if filepath.endswith(".pt") or filepath.endswith(".pth"):
                return torch.load(filepath)
            elif filepath.endswith(".npy"):
                return np.load(filepath)
            else:
                raise ValueError("Invalid file format")