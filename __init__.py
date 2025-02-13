from .nodes import EncodedPromptToFile, EncodedPromptFromFile, SampledLatentsToFile, SampledLatentsFromFile, IO_LoadImage


#  Map all your custom nodes classes with the names that will be displayed in the UI.
NODE_CLASS_MAPPINGS = {
    "EncodedPromptToFile": EncodedPromptToFile,
    "EncodedPromptFromFile": EncodedPromptFromFile,
    "SampledLatentsToFile": SampledLatentsToFile,
    "SampledLatentsFromFile": SampledLatentsFromFile,
    "IO_LoadImage": IO_LoadImage,
}

NODE_DISPLAY_NAMES = {
    "EncodedPromptToFile": "Encoded Prompt [to file] ►►► 💾",
    "EncodedPromptFromFile": "Encoded Prompt [from file] ◄◄◄ 📁",
    "SampledLatentsToFile": "Sampled Latents [to file] ►►► 💾",
    "SampledLatentsFromFile": "Sampled Latents [from file] ◄◄◄ 📁",
    "IO_LoadImage": "Load Image ◄◄◄ 📁",
}

WEB_DIRECTORY = "./web"


__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAMES', 'WEB_DIRECTORY']
