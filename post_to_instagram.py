import os
import requests
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

INSTAGRAM_API_URL = "https://graph.instagram.com/v21.0"


def post_to_instagram(
    caption: str,
    image_url: str,
) -> Dict[str, any]:
    """
    Post an image to Instagram using the Graph API.

    Args:
        caption: Post caption including hashtags
        image_url: Public URL of the image to post

    Returns:
        Dict with keys:
        - success: bool
        - post_id: str (if successful)
        - message: str (status message)
        - status_code: int
        - error_detail: str (if failed)
    """
    access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    user_id = os.getenv("INSTAGRAM_USER_ID")

    if not access_token:
        return {
            "success": False,
            "message": "Missing INSTAGRAM_ACCESS_TOKEN in environment",
            "error_detail": "Set INSTAGRAM_ACCESS_TOKEN in .env file",
            "status_code": None,
        }

    if not user_id:
        return {
            "success": False,
            "message": "Missing INSTAGRAM_USER_ID in environment",
            "error_detail": "Set INSTAGRAM_USER_ID in .env file",
            "status_code": None,
        }

    try:
        # Step 1 — Create media container
        container_response = requests.post(
            f"{INSTAGRAM_API_URL}/{user_id}/media",
            data={
                "image_url": image_url,
                "caption": caption,
                "access_token": access_token,
            },
            timeout=10,
        )

        if container_response.status_code not in [200, 201]:
            error_msg = container_response.text
            try:
                error_data = container_response.json()
                error_msg = error_data.get("error", {}).get("message", error_msg)
            except:
                pass
            return {
                "success": False,
                "message": f"Failed to create media container (Status {container_response.status_code})",
                "error_detail": error_msg,
                "status_code": container_response.status_code,
            }

        container_id = container_response.json().get("id")

        # Step 2 — Publish media container
        publish_response = requests.post(
            f"{INSTAGRAM_API_URL}/{user_id}/media_publish",
            data={
                "creation_id": container_id,
                "access_token": access_token,
            },
            timeout=10,
        )

        if publish_response.status_code in [200, 201]:
            result = publish_response.json()
            return {
                "success": True,
                "post_id": result.get("id"),
                "message": "Post published successfully to Instagram!",
                "status_code": publish_response.status_code,
            }
        else:
            error_msg = publish_response.text
            try:
                error_data = publish_response.json()
                error_msg = error_data.get("error", {}).get("message", error_msg)
            except:
                pass
            return {
                "success": False,
                "message": f"Failed to publish post (Status {publish_response.status_code})",
                "error_detail": error_msg,
                "status_code": publish_response.status_code,
            }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "message": "Request timeout",
            "error_detail": "Instagram API took too long to respond",
            "status_code": None,
        }
    except requests.exceptions.ConnectionError as e:
        return {
            "success": False,
            "message": "Connection error",
            "error_detail": str(e),
            "status_code": None,
        }
    except Exception as e:
        return {
            "success": False,
            "message": "Unexpected error",
            "error_detail": str(e),
            "status_code": None,
        }