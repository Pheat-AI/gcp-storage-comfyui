from google.cloud import storage
import folder_paths
from PIL import Image
import json
import os
import numpy as np

# Optional: You can load additional configuration from a file if needed.
config_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gcp_config.json')

class upload_to_gcp_storage:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.compress_level = 4

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "file_name": ("STRING", {"default": "file", "multiline": False}),
                "bucket_name": ("STRING", {"default": "bucket", "multiline": False}),
                "bucket_folder_prefix": ("STRING", {"multiline": False}),
                "gcp_service_json": ("STRING", {"default": "path", "multiline": False}),
                "local_file_path": ("STRING", {"default": "", "multiline": False}),
            },
            "optional": {
                # If images are provided, they'll be processed and saved as PNG.
                "images": ("IMAGE", ),
                # If a file is already produced by the workflow (e.g. an .mp4), provide its full local path.
            
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "upload_to_gcp_storage"
    OUTPUT_NODE = True
    CATEGORY = "image"  # You might choose to change this if needed.

    def upload_to_gcp_storage(self, images, file_name, bucket_name, bucket_folder_prefix, gcp_service_json, local_file_path=""):
        # Set up the GCP credentials
        print(f"Setting [GOOGLE_APPLICATION_CREDENTIALS] to {gcp_service_json}..")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = gcp_service_json

        # Determine which file to upload:
        # 1. If a local file path is provided and exists, use that.
        # 2. Otherwise, if images are provided, process and save them.
        if local_file_path and os.path.exists(local_file_path):
            print(f"Using provided local file path: {local_file_path}")
            file = os.path.basename(local_file_path)
            full_file_path = local_file_path
            results = None
        elif images is not None and len(images) > 0:
            print("No valid file path provided; processing images input...")
            results = save_images(self, images, file_name)
            # Assume the first saved image is the one we want to upload.
            file = results[0]["filename"]
            full_file_path = os.path.join(self.output_dir, results[0]["subfolder"], file)
            print(f"Processed images; file to upload: {full_file_path}")
        else:
            raise Exception("No valid input provided: please supply either images or a local_file_path.")

        # Upload the file to GCP Cloud Storage
        print(f"Uploading file '{file}' from '{full_file_path}' to bucket '{bucket_name}' in folder '{bucket_folder_prefix}'...")
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(f"{bucket_folder_prefix}/{file}")
        blob.upload_from_filename(full_file_path)
        print("Upload complete.")

        # Return the result structure; if we processed images, return that info.
        if results is not None:
            return {"ui": {"images": results}}
        else:
            return {"ui": {"file": file}}

def save_images(self, images, filename_prefix="ComfyUI"):
    # Get the full output folder and a unique filename using your folder_paths utility.
    full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(filename_prefix, self.output_dir, images[0].shape[1], images[0].shape[0])
    results = list()
    for (batch_number, image) in enumerate(images):
        # Convert the tensor to a numpy array and then to an image.
        i = 255. * image.cpu().numpy()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
        metadata = None
        file = f"{filename}.png"
        img.save(os.path.join(full_output_folder, file), pnginfo=metadata, compress_level=self.compress_level)
        results.append({
            "filename": file,
            "subfolder": subfolder,
            "type": self.type
        })
    return results

NODE_CLASS_MAPPINGS = {
    "StorageGCP": upload_to_gcp_storage,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "StorageGCP": "Storage GCP",
}
