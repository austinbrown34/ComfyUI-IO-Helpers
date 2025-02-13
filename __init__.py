from .nodes import *


#  Map all your custom nodes classes with the names that will be displayed in the UI.
NODE_CLASS_MAPPINGS = {
    "Encoded Prompt to File": EncodedPromptToFile,
    "Encoded Prompt from File": EncodedPromptFromFile,
    "Sampled Latents to File": SampledLatentsToFile,
    "Sampled Latents from File": SampledLatentsFromFile,
}


__all__ = ['NODE_CLASS_MAPPINGS']
