import json
import requests
from typing import Dict, List

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.1:latest"


def clean_keywords(keywords: List[str]) -> List[str]:
    return [k.strip() for k in keywords if k and k.strip()]

def call_ollama(prompt: str) -> str:
    """Call local Ollama API and return the response text."""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.8,
            "top_p": 0.9,
        }
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            "❌ Cannot connect to Ollama. Make sure Ollama is running."
        )
    except requests.exceptions.Timeout:
        raise TimeoutError(
            "❌ Ollama took too long to respond. Try a smaller model or shorter prompt."
        )


def extract_json(raw: str) -> dict:
    """Robustly extract JSON from model output."""
    cleaned = raw.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    # Try direct parse first
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Fallback: extract first JSON object
    start = cleaned.find("{")
    end = cleaned.rfind("}") + 1
    if start != -1 and end > start:
        candidate = cleaned[start:end]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"❌ Could not parse JSON from model response.\n\n"
                f"Candidate JSON:\n{candidate}\n\n"
                f"Parser error: {e}"
            )

    raise ValueError(f"❌ Could not parse JSON from model response:\n\n{raw}")


def generate_campaign(
    product_name: str,
    age_group: str,
    product_type: str,
    keywords: List[str],
    angle: str,
    description: str,
) -> Dict[str, object]:
    keywords = clean_keywords(keywords)
    keyword_line = ", ".join(keywords) if keywords else "kids yoga, mindfulness, screen-free activity"

    prompt = f"""You are a top-performing Etsy conversion copywriter for premium children's wellness products.
You write copy that sounds warm, emotionally intelligent, specific, and giftable.
Avoid generic phrases, filler, repetition, and bland wording.
Every output should feel polished, natural, and worth paying for.

Brand tone:
- warm
- mindful
- premium but approachable
- parent-friendly
- encouraging, not pushy
- emotionally resonant
- never robotic

Your goal:
Create high-converting platform-specific content for this product that helps parents imagine buying it for their child.

Product details:
- Name: {product_name}
- Age Group: {age_group}
- Product Type: {product_type}
- Marketing Angle: {angle}
- Keywords: {keyword_line}
- Description: {description}

Return ONLY raw JSON.
Do not use markdown code fences.
Do not include any explanation before or after the JSON.

Return exactly this JSON structure:

{{
  "etsy_title": "SEO-optimized Etsy title under 140 characters",
  "etsy_tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8", "tag9", "tag10", "tag11", "tag12", "tag13"],
  "etsy_description": "Detailed Etsy description",
  "pinterest_title": "Pinterest title under 100 characters",
  "pinterest_description": "Pinterest description",
  "instagram_caption": "Instagram caption"
}}

Rules for each field:

1. etsy_title
- under 140 characters
- clear and searchable
- include product type, age group, and strongest buyer keywords
- should sound like a real Etsy listing, not keyword stuffing

2. etsy_tags
- exactly 13 tags
- each tag under 20 characters
- all lowercase
- high buyer intent
- focus on relevant search phrases, not vague terms
- avoid weak tags like "parenting tips" or "self-help tools"
- do not repeat tags
- do not use duplicate words unless necessary
- avoid generic tags like "yoga cards" more than once
- tags must be high buyer intent and varied
- prefer specific searchable phrases over broad generic terms

3. etsy_description
- 220 to 350 words
- open with a strong emotional hook for parents
- clearly explain benefits and use cases
- include natural keyword usage
- mention scenarios like calm corner, homeschool, screen-free time, travel, mindful routines, family bonding when relevant
- use short paragraphs
- use simple markdown bullet points for benefits
- sound warm, useful, and giftable
- end with a gentle call to action

4. pinterest_title
- under 100 characters
- searchable, clickable, curiosity-driven
- should feel like something a parent would want to save

5. pinterest_description
- 100 to 180 words
- warm, inspiring, and search-friendly
- highlight benefits and everyday use cases
- end with a soft save/click style call to action
- should feel more expansive than the Etsy title

6. instagram_caption
- warm and engaging
- use light emojis naturally
- include line breaks
- include a strong parent-focused hook in the first 1–2 lines
- mention benefits and lifestyle use
- end with 10 to 18 relevant hashtags

7. writing quality rules
- avoid generic phrases like "perfect for" too often
- use more vivid and natural language
- sound premium and emotionally resonant
- make parents imagine using this product in daily life
- do not sound like a template
- vary sentence openings

All string values must be valid JSON strings.
Escape line breaks as \\n inside JSON strings.
Do not output multi-line raw strings.
etsy_tags must contain exactly 13 items.

Overall content priorities:
- screen-free activity
- mindfulness
- movement and confidence
- calm routines
- homeschool and travel-friendly use
- wellness gift appeal
- premium but practical


Do not sound repetitive.
Do not sound AI-generated.
Make the copy feel unique and emotionally convincing.
"""

    raw = call_ollama(prompt)
    result = extract_json(raw)

    required_keys = [
        "etsy_title",
        "etsy_tags",
        "etsy_description",
        "pinterest_title",
        "pinterest_description",
        "instagram_caption",
    ]

    for key in required_keys:
        if key not in result:
            raise ValueError(f"❌ Missing key in model output: {key}")

    tags = result.get("etsy_tags", [])
    cleaned_tags = []

    for t in tags:
        tag = str(t).strip().lower()[:20]
        if tag and tag not in cleaned_tags:
            cleaned_tags.append(tag)

    fallback_tags = [
        "kids yoga cards",
        "mindfulness kids",
        "screen free",
        "calm corner",
        "homeschool",
        "travel activity",
        "yoga flashcards",
        "mindful play",
        "wellness gift",
        "confidence boost",
        "movement break",
        "family activity",
        "kids wellness",
    ]

    for fallback in fallback_tags:
        fallback = fallback[:20].lower().strip()
        if fallback not in cleaned_tags:
            cleaned_tags.append(fallback)
        if len(cleaned_tags) == 13:
            break

    result["etsy_tags"] = cleaned_tags[:13]
    if len(result.get("etsy_title", "")) > 140:
        result["etsy_title"] = result["etsy_title"][:140].rstrip()

    return result