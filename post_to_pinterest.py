import os
import requests
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

PINTEREST_API_URL = "https://api.pinterest.com/v5/pins"


def post_to_pinterest(
    title: str,
    description: str,
    link: str,
    image_url: str,
    board_id: str = None,
) -> Dict[str, any]:
    """
    Post a pin to Pinterest using the v5 API.

    Args:
        title: Pin title (required)
        description: Pin description (required)
        link: URL to link to (typically Etsy listing)
        image_url: URL of the image for the pin
        board_id: Pinterest board ID. If not provided, uses PINTEREST_BOARD_ID env var.

    Returns:
        Dict with keys:
        - success: bool
        - pin_id: str (if successful)
        - message: str (status message)
        - status_code: int
        - error_detail: str (if failed)
    """
    token = os.getenv("PINTEREST_ACCESS_TOKEN")
    if not token:
        return {
            "success": False,
            "message": "Missing PINTEREST_ACCESS_TOKEN in environment",
            "error_detail": "Set PINTEREST_ACCESS_TOKEN in .env file",
            "status_code": None,
        }

    if not board_id:
        board_id = os.getenv("PINTEREST_BOARD_ID")

    if not board_id:
        return {
            "success": False,
            "message": "Missing Pinterest board ID",
            "error_detail": "Provide board_id or set PINTEREST_BOARD_ID in .env file",
            "status_code": None,
        }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    payload = {
        "board_id": board_id,
        "title": title,
        "description": description,
        "link": link,
        "media_source": {
            "source_type": "image_url",
            "url": image_url,
        },
    }

    try:
        response = requests.post(PINTEREST_API_URL, json=payload, headers=headers, timeout=10)

        if response.status_code in [200, 201]:
            result = response.json()
            return {
                "success": True,
                "pin_id": result.get("id"),
                "message": "Pin posted successfully",
                "status_code": response.status_code,
            }
        else:
            error_msg = response.text
            try:
                error_data = response.json()
                error_msg = error_data.get("message", error_msg)
            except:
                pass

            return {
                "success": False,
                "message": f"Failed to post pin (Status {response.status_code})",
                "error_detail": error_msg,
                "status_code": response.status_code,
            }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "message": "Request timeout",
            "error_detail": "Pinterest API took too long to respond",
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
