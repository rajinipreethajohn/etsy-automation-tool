import json
import requests
from typing import Dict, List

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.1:latest"


def clean_keywords(keywords: List[str]) -> List[str]:
    return [k.strip() for k in keywords if k and k.strip()]


def call_ollama(prompt: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.8,
            "top_p": 0.9,
        },
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        raise ConnectionError("❌ Cannot connect to Ollama. Make sure Ollama is running.")
    except requests.exceptions.Timeout:
        raise TimeoutError("❌ Ollama took too long to respond. Try a smaller model or shorter prompt.")


def extract_json(raw: str) -> dict:
    cleaned = raw.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")
    end = cleaned.rfind("}") + 1
    if start != -1 and end > start:
        candidate = cleaned[start:end]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    raise ValueError(f"❌ Could not parse JSON from model response:\n\n{raw}")


def clean_tag_length(tag: str, max_len: int = 20) -> str:
    tag = " ".join(str(tag).strip().split())
    if not tag:
        return ""
    if len(tag) <= max_len:
        return tag

    words = tag.split()
    trimmed_words = []

    for word in words:
        candidate = " ".join(trimmed_words + [word])
        if len(candidate) <= max_len:
            trimmed_words.append(word)
        else:
            break

    if trimmed_words:
        return " ".join(trimmed_words).strip(" ,.-")

    return tag[:max_len].rstrip(" ,.-")


def looks_robotic_tag(tag: str) -> bool:
    if not tag:
        return True

    # Long single-token tags like "mindfulnessforkids" or
    # "movementforconfidence" look robotic and weak on Etsy.
    if " " not in tag and "-" not in tag and len(tag) >= 16:
        return True

    return False


def normalize_tags(tags: List[str], age_group: str) -> List[str]:
    cleaned_tags = []

    for t in tags:
        tag = clean_tag_length(str(t).strip().lower(), 20)

        if not tag:
            continue

        if looks_robotic_tag(tag):
            continue

        if tag not in cleaned_tags:
            cleaned_tags.append(tag)

        if len(cleaned_tags) == 13:
            break

    age_fallbacks = {
        "Toddler": [
            "toddler yoga",
            "mindful play",
            "screen free",
            "calm corner",
            "movement cards",
            "toddler activity",
            "kids yoga cards",
            "travel activity",
            "mindfulness kids",
            "wellness gift",
            "quiet time",
            "family activity",
            "sensory play",
        ],
        "Early Childhood": [
            "kids yoga",
            "ages 4 7",
            "mindfulness kids",
            "homeschool",
            "screen free",
            "calm corner",
            "yoga flashcards",
            "movement break",
            "focus activity",
            "travel activity",
            "wellness gift",
            "classroom movement",
            "mindful play",
        ],
        "Tween": [
            "tween yoga",
            "tween mindfulness",
            "screen free tween",
            "confidence boost",
            "calm corner",
            "growing kids",
            "movement break",
            "wellness gift",
            "yoga flashcards",
            "homeschool",
            "travel activity",
            "mindful play",
            "kids yoga cards",
        ],
        "Teen": [
            "teen yoga",
            "stress relief",
            "teen wellness",
            "confidence boost",
            "posture support",
            "movement break",
            "wellness gift",
            "yoga flashcards",
            "mindfulness teens",
            "travel activity",
            "screen free",
            "self care teens",
            "mobility work",
        ],
        "All Ages": [
            "kids yoga bundle",
            "all ages yoga",
            "family wellness",
            "mindfulness kids",
            "screen free",
            "homeschool",
            "travel activity",
            "yoga flashcards",
            "wellness gift",
            "family activity",
            "grow with child",
            "movement cards",
            "mindful play",
        ],
        "All 4 Decks": [
            "kids yoga bundle",
            "4 deck bundle",
            "all ages yoga",
            "family wellness",
            "screen free",
            "homeschool",
            "travel activity",
            "mindfulness kids",
            "yoga flashcards",
            "wellness gift",
            "movement cards",
            "family activity",
            "grow with child",
        ],
    }

    fallbacks = age_fallbacks.get(age_group, age_fallbacks["All Ages"])

    for fallback in fallbacks:
        fallback = clean_tag_length(fallback.lower().strip(), 20)
        if fallback and fallback not in cleaned_tags:
            cleaned_tags.append(fallback)
        if len(cleaned_tags) == 13:
            break

    return cleaned_tags[:13]


def build_prompt(
    product_name: str,
    age_group: str,
    product_type: str,
    keyword_line: str,
    angle: str,
    description: str,
    style_name: str,
    style_instructions: str,
) -> str:
    return f"""You are a top-performing Etsy conversion copywriter for premium children's wellness products.

Brand voice:
- warm
- mindful
- emotionally intelligent
- premium but approachable
- parent-friendly
- never robotic

Style mode: {style_name}

Style instructions:
{style_instructions}

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
All string values must be valid JSON strings.
Escape line breaks as \\n inside JSON strings.
etsy_tags must contain exactly 13 items.

Return exactly this JSON structure:

{{
  "etsy_title": "SEO-optimized Etsy title under 140 characters",
  "etsy_tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8", "tag9", "tag10", "tag11", "tag12", "tag13"],
  "etsy_description": "Detailed Etsy description",
  "pinterest_title": "Pinterest title under 100 characters",
  "pinterest_description": "Pinterest description",
  "instagram_caption": "Instagram caption"
}}

Rules:
1. etsy_title
- under 140 characters
- clear and searchable
- should sound like a real Etsy listing, not keyword stuffing

2. etsy_tags
- exactly 13 tags
- each tag under 20 characters
- all lowercase
- high buyer intent
- do not repeat tags
- avoid weak generic tags

3. etsy_description
- 220 to 350 words
- open with a strong hook
- clearly explain benefits and use cases
- use short paragraphs
- use simple markdown bullet points for benefits
- end with a gentle call to action

4. pinterest_title
- under 100 characters
- searchable and clickable

5. pinterest_description
- 100 to 180 words
- warm, inspiring, and search-friendly
- end with a soft call to action

6. instagram_caption
- warm and engaging
- use light emojis naturally
- include line breaks
- end with 10 to 18 relevant hashtags

Content priorities:
- screen-free activity
- mindfulness
- calm routines
- confidence through movement
- homeschool and travel-friendly use
- gift appeal

Do not sound repetitive.
Do not sound AI-generated.
"""


def generate_campaign_variant(
    product_name: str,
    age_group: str,
    product_type: str,
    keywords: List[str],
    angle: str,
    description: str,
    style_name: str,
    style_instructions: str,
) -> Dict[str, object]:
    keywords = clean_keywords(keywords)
    keyword_line = ", ".join(keywords) if keywords else "kids yoga, mindfulness, screen-free activity"

    prompt = build_prompt(
        product_name=product_name,
        age_group=age_group,
        product_type=product_type,
        keyword_line=keyword_line,
        angle=angle,
        description=description,
        style_name=style_name,
        style_instructions=style_instructions,
    )

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

    result["etsy_tags"] = normalize_tags(result.get("etsy_tags", []), age_group)

    if len(result.get("etsy_title", "")) > 140:
        result["etsy_title"] = result["etsy_title"][:140].rstrip()

    if len(result.get("pinterest_title", "")) > 100:
        result["pinterest_title"] = result["pinterest_title"][:100].rstrip()

    return result


def generate_campaign_variants(
    product_name: str,
    age_group: str,
    product_type: str,
    keywords: List[str],
    angle: str,
    description: str,
) -> Dict[str, Dict[str, object]]:
    styles = {
        "SEO Safe": """
Focus on clear keywords, searchability, buyer intent, and practical usefulness.
Keep the language straightforward, useful, and Etsy-friendly.
""",
        "Emotional Parent Hook": """
Focus on the parent's feelings, daily struggles, calm routines, confidence-building, and the emotional benefit to the child.
Make the copy feel comforting, supportive, and relatable.
""",
        "Premium Brand Voice": """
Use elevated, polished, boutique-style wording.
Make the product feel giftable, intentional, beautiful, and high quality without sounding snobbish.
""",
    }

    variants = {}
    for style_name, style_instructions in styles.items():
        variants[style_name] = generate_campaign_variant(
            product_name=product_name,
            age_group=age_group,
            product_type=product_type,
            keywords=keywords,
            angle=angle,
            description=description,
            style_name=style_name,
            style_instructions=style_instructions,
        )

    return variants