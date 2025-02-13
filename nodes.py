"""
nodes.py

This module defines custom nodes for ComfyUI to save and load intermediate
data for the prompt encoding and sampling stages. It uses the Inputter and Outputter
helper classes (from modules/io_helpers.py) and updates progress via a ProgressBar.
"""

from comfy.cli_args import args
import folder_paths
from comfy.comfy_types import IO
from .modules.io_helpers import Inputter, Outputter


class EncodedPromptToFile:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "conditioning": (IO.CONDITIONING, {"tooltip": "The conditioning tensor to save."}),
                "filename_prefix": (IO.STRING, {"default": "IO-Helpers", "tooltip": "The prefix for the file to save. This may include formatting information such as %date:yyyy-MM-dd% or other values from nodes."}),
                "output_format": (Outputter.OUTPUT_FORMATS, {"default": "pt", "tooltip": "The format to save the data in."}),
                "compress": (IO.BOOLEAN, {"default": True, "tooltip": "If True, compresses the file with gzip."})
            },
            "hidden": {
                "prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }
    
    RETURN_TYPES = (IO.STRING,)
    RETURN_NAMES = ("filepath",)
    FUNCTION = "output_encoded_prompt_to_file"
    OUTPUT_NODE = True
    CATEGORY = "export"
    DESCRIPTION = "Save the encoded prompt to a file. If `compress` is True, the file will be compressed with gzip."

    def output_encoded_prompt_to_file(self, conditioning, filename_prefix, output_format="pt", compress=True, prompt=None, extra_pnginfo=None):
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(filename_prefix, self.output_dir)

        file_info = {
            "prompt": prompt,
            "extra_pnginfo": extra_pnginfo,
            "disable_metadata": args.disable_metadata,
            "full_output_folder": full_output_folder,
            "filename": filename,
            "counter": counter,
            "subfolder": subfolder,
            "filename_prefix": filename_prefix
        }

        # Save the data using Outputter
        file_path = Outputter.save_data(conditioning, output_format, file_info)
        
        if compress:
            file_path = Outputter.compress_file(file_path)
            
        return (file_path,)


class EncodedPromptFromFile:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "filepath": (IO.STRING, {"tooltip": "The path to the file to load the data from."})
            }
        }
    
    RETURN_TYPES = (IO.CONDITIONING, )
    RETURN_NAMES = ("conditioning", )
    OUTPUT_TOOLTIPS = ("The conditioning tensor loaded from the file.", )
    FUNCTION = "load_encoded_prompt_from_file"
    CATEGORY = "import"
    DESCRIPTION = "Load the encoded prompt from a file."

    def load_encoded_prompt_from_file(self, filepath):
        data = Inputter.load_data(filepath)
        return data


class SampledLatentsToFile:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "latents": (IO.LATENT, {"tooltip": "The latents tensor to save."}),
                "filename_prefix": (IO.STRING, {"default": "IO-Helpers", "tooltip": "The prefix for the file to save. This may include formatting information such as %date:yyyy-MM-dd% or other values from nodes."}),
                "output_format": (Outputter.OUTPUT_FORMATS, {"default": "pt", "tooltip": "The format to save the data in."}),
                "compress": (IO.BOOLEAN, {"default": True, "tooltip": "If True, compresses the file with gzip."})
            },
            "hidden": {
                "prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }
    
    RETURN_TYPES = (IO.STRING,)
    RETURN_NAMES = ("filepath", )
    FUNCTION = "output_sampled_latents_to_file"
    OUTPUT_NODE = True
    CATEGORY = "export"
    DESCRIPTION = "Save the sampled latents to a file. If `compress` is True, the file will be compressed with gzip."

    def output_sampled_latents_to_file(self, latents, filename_prefix, output_format="pt", compress=True, prompt=None, extra_pnginfo=None):
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(filename_prefix, self.output_dir)

        file_info = {
            "prompt": prompt,
            "extra_pnginfo": extra_pnginfo,
            "disable_metadata": args.disable_metadata,
            "full_output_folder": full_output_folder,
            "filename": filename,
            "counter": counter,
            "subfolder": subfolder,
            "filename_prefix": filename_prefix
        }

        # Save the data using Outputter
        file_path = Outputter.save_data(latents, output_format, file_info)
        
        if compress:
            file_path = Outputter.compress_file(file_path)
            
        return (file_path,)


class SampledLatentsFromFile:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "filepath": (IO.STRING, {"tooltip": "The path to the file to load the data from."})
            }
        }
    
    RETURN_TYPES = (IO.LATENT, )
    RETURN_NAMES = ("latents", )
    OUTPUT_TOOLTIPS = ("The latents tensor loaded from the file.", )
    FUNCTION = "load_sampled_latents_from_file"
    CATEGORY = "import"
    DESCRIPTION = "Load the sampled latents from a file."

    def load_sampled_latents_from_file(self, filepath):
        data = Inputter.load_data(filepath)
        return data