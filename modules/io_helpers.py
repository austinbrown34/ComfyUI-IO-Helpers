# modules/io_helpers.py

import json
import torch
import gzip
import numpy as np
import os
import safetensors.torch
import dill

class Outputter:
    LATENT_OUTPUT_FORMATS = ["pt", "pth", "npy"]
    CONDITIONING_OUTPUT_FORMATS = ["pkl"]
    
    @staticmethod
    def serialize_custom(obj):
        if isinstance(obj, torch.Tensor):
            return {"__type__": "tensor", "data": obj.tolist()}
        elif isinstance(obj, list):
            return [Outputter.serialize_custom(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: Outputter.serialize_custom(value) for key, value in obj.items()}
        else:
            return obj
    
    @staticmethod
    def save_data(data, output_format, file_info):
        """
        Save data (a tensor or array) to disk using the specified format.
        Returns the file path of the saved file.
        """
        prompt = file_info.get("prompt")
        extra_pnginfo = file_info.get("extra_pnginfo")
        disable_metadata = file_info.get("disable_metadata")
        full_output_folder = file_info.get("full_output_folder")
        filename = file_info.get("filename")
        counter = file_info.get("counter")
        filename_prefix = file_info.get("filename_prefix")
        dynamic_filename_suffix = file_info.get("dynamic_filename_suffix")
        
        prompt_info = ""
        if prompt is not None:
            prompt_info = json.dumps(prompt)

        metadata = None
        if not disable_metadata:
            metadata = {"prompt": prompt_info}
            if extra_pnginfo is not None:
                for x in extra_pnginfo:
                    metadata[x] = json.dumps(extra_pnginfo[x])
        
        if dynamic_filename_suffix:
            file_path_pre = f"{filename}_{counter:05}"
            file_path = os.path.join(full_output_folder, f"{file_path_pre}.{output_format}")
        else:
            file_path = os.path.join(full_output_folder, f"{filename_prefix}.{output_format}")

        if output_format in ["pt", "pth"]:
            if metadata is not None:
                safetensors.torch.save_file(data, file_path, metadata=metadata)
            else:
                safetensors.torch.save_file(data, file_path)
        elif output_format == "npy":
            np.save(file_path, data, allow_pickle=True)
        elif output_format == "pkl":
            serialized_data = Outputter.serialize_custom(data)
            with open(file_path, "wb") as f:
                dill.dump(serialized_data, f)
        else:
            raise ValueError("Invalid output format")
        
        if metadata is not None:
            with open(file_path + ".json", "w") as f:
                json.dump(metadata, f)
        
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
    def deserialize_custom(obj):
        if isinstance(obj, dict):
            if "__type__" in obj:
                if obj["__type__"] == "tensor":
                    return torch.tensor(obj["data"])
            return {key: Inputter.deserialize_custom(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [Inputter.deserialize_custom(item) for item in obj]
        else:
            return obj
    
    @staticmethod
    def load_data(filepath):
        """
        Load data (a tensor or array) from the given file.
        Supports both compressed (.gz) and uncompressed files.
        """
        if filepath.endswith(".gz"):
            with gzip.open(filepath, "rb") as f:
                if filepath.endswith(".pt.gz") or filepath.endswith(".pth.gz"):
                    decompressed_data = f.read()
                    temp_filepath = filepath[:-3]
                    with open(temp_filepath, "wb") as temp_f:
                        temp_f.write(decompressed_data)
                    try:
                        return safetensors.torch.load_file(temp_filepath)
                    finally:
                        if os.path.exists(temp_filepath):
                            os.remove(temp_filepath)
                elif filepath.endswith(".npy.gz"):
                    return np.load(f, allow_pickle=True)
                elif filepath.endswith(".pkl.gz"):
                    data = dill.load(f)
                    return Inputter.deserialize_custom(data)
                else:
                    raise ValueError("Invalid file format")
        else:
            if filepath.endswith(".pt") or filepath.endswith(".pth"):
                return safetensors.torch.load_file(filepath)
            elif filepath.endswith(".npy"):
                return np.load(filepath, allow_pickle=True)
            elif filepath.endswith(".pkl"):
                with open(filepath, "rb") as f:
                    data = dill.load(f)
                    return Inputter.deserialize_custom(data)
            else:
                raise ValueError("Invalid file format")