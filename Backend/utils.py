from fastapi import HTTPException
import requests
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("API_KEY")


def upload_img(image):
    try:
        with open(image, "rb") as image_file:
            files = {
                "source": (os.path.basename(image), image_file, "image/jpeg")
            }
            data = {
                "key": api_key
            }
            print("Uploading image to external service...")
            response = requests.post(
                "https://imgcdn.dev/api/1/upload",
                files=files,
                data=data,
            )
            response.raise_for_status
            image_url = response.text
            if not image_url:
                raise HTTPException(
                    status_code=500, detail="Image upload failed, no URL returned."
                )
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500, detail=f"Error uploading image to external service: {e}"
        )
    return image_url