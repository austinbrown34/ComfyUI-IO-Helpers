"""
nodes.py

This module defines custom nodes for ComfyUI to save and load intermediate
data for the prompt encoding and sampling stages. It uses the Inputter and Outputter
helper classes (from modules/io_helpers.py) and updates progress via a ProgressBar.
"""

from comfy.utils import ProgressBar
from .modules.io_helpers import Inputter, Outputter


class EncodedPromptToFile:
    def __init__(self, conditioning, filename_prefix, output_format="pt", compress=True, output_filepath=False):
        self.conditioning = conditioning
        self.filename_prefix = filename_prefix
        self.output_format = output_format
        self.compress = compress
        self.output_filepath = output_filepath

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "conditioning": ("CONDITIONING", ),
                "filename_prefix": ("STRING", ),
                "output_format": (Outputter.OUTPUT_FORMATS, {"tooltip": "The format to save the data in."}),
                "compress": ("BOOLEAN", {"default": True}),
                "output_filepath": ("BOOLEAN", {"default": False, "tooltip": "If True, outputs the filepath for use in other nodes"})
            }
        }
    
    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("filepath", )
    FUNCTION = "output_encoded_prompt_to_file"
    OUTPUT_NODE = True
    CATEGORY = "encoded/outputter"
    DESCRIPTION = "Save the encoded prompt to a file. If `compress` is True, the file will be compressed with gzip. Can optionally output the filepath."

    def output_encoded_prompt_to_file(self, conditioning, filename_prefix, output_format="pt", compress=True, output_filepath=False):
        pb = ProgressBar()
        pb.update(0)
        
        # Save the data using Outputter
        file_path = Outputter.save_data(conditioning, filename_prefix, output_format)
        pb.update(50)
        
        if compress:
            file_path = Outputter.compress_file(file_path)
            pb.update(100)
        else:
            pb.update(100)
            
        if output_filepath:
            return (file_path,)
        return None


class EncodedPromptFromFile:
    def __init__(self, filepath):
        self.filepath = filepath

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "filepath": ("STRING", ),
            }
        }
    
    RETURN_TYPES = ("CONDITIONING", )
    OUTPUT_TOOLTIPS = ("The conditioning tensor loaded from the file.", )
    FUNCTION = "load_encoded_prompt_from_file"
    CATEGORY = "encoded/inputter"
    DESCRIPTION = "Load the encoded prompt from a file."

    def load_encoded_prompt_from_file(self, filepath):
        pb = ProgressBar()
        pb.update(0)
        
        data = Inputter.load_data(filepath)
        pb.update(100)
        return data


class SampledLatentsToFile:
    def __init__(self, latents, filename_prefix, output_format="pt", compress=True, output_filepath=False):
        self.latents = latents
        self.filename_prefix = filename_prefix
        self.output_format = output_format
        self.compress = compress
        self.output_filepath = output_filepath

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "latents": ("LATENT", ),
                "filename_prefix": ("STRING", ),
                "output_format": (Outputter.OUTPUT_FORMATS, {"tooltip": "The format to save the data in."}),
                "compress": ("BOOLEAN", {"default": True}),
                "output_filepath": ("BOOLEAN", {"default": False, "tooltip": "If True, outputs the filepath for use in other nodes"})
            }
        }
    
    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("filepath", )
    FUNCTION = "output_sampled_latents_to_file"
    OUTPUT_NODE = True
    CATEGORY = "latent/outputter"
    DESCRIPTION = "Save the sampled latents to a file. If `compress` is True, the file will be compressed with gzip. Can optionally output the filepath."

    def output_sampled_latents_to_file(self, latents, filename_prefix, output_format="pt", compress=True, output_filepath=False):
        pb = ProgressBar()
        pb.update(0)
        
        file_path = Outputter.save_data(latents, filename_prefix, output_format)
        pb.update(50)
        
        if compress:
            file_path = Outputter.compress_file(file_path)
            pb.update(100)
        else:
            pb.update(100)
            
        if output_filepath:
            return (file_path,)
        return None


class SampledLatentsFromFile:
    def __init__(self, filepath):
        self.filepath = filepath

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "filepath": ("STRING", ),
            }
        }
    
    RETURN_TYPES = ("LATENT", )
    OUTPUT_TOOLTIPS = ("The latents tensor loaded from the file.", )
    FUNCTION = "load_sampled_latents_from_file"
    CATEGORY = "latent/inputter"
    DESCRIPTION = "Load the sampled latents from a file."

    def load_sampled_latents_from_file(self, filepath):
        pb = ProgressBar()
        pb.update(0)
        
        data = Inputter.load_data(filepath)
        pb.update(100)
        return data