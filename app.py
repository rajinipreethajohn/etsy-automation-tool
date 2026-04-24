import os
import time
import json
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
from content_engine import generate_campaign_variants
from post_to_instagram import post_to_instagram

load_dotenv()

st.set_page_config(page_title="Etsy Automation Tool", layout="wide")
st.title("🛍️ Etsy Automation Tool")
st.caption("Generate → Review → Compare Variants → Export → Post")

# ── Constants ────────────────────────────────────────────────────────────────

GOOGLE_SHEET_NAME = "MYB Content Queue"
GOOGLE_SHEET_WORKSHEET = "Sheet1"

GITHUB_RAW_BASE = (
    "https://raw.githubusercontent.com/"
    "rajinipreethajohn/etsy-automation-tool/main/assets"
)

ASSETS_DIR = Path(__file__).parent / "assets"

AGE_GROUP_FOLDERS = {
    "Toddler (1–3)": "toddler",
    "Early Childhood (4–7)": "ec",
    "Tween (8–12)": "tween",
    "Teen (13–17)": "teen",
    "Senior": "senior",
}

MAX_IMAGE_MB = 8

# ── Templates ────────────────────────────────────────────────────────────────

templates = {
    "Custom": {
        "product_name": "",
        "age_group": "Toddler",
        "product_type": "Yoga Flashcards",
        "angle": "",
        "description": "",
        "keywords": "",
    },
    "Toddler Deck": {
        "product_name": "Toddler Yoga Cards",
        "age_group": "Toddler",
        "product_type": "Yoga Flashcards",
        "angle": "Screen-Free Calm Play",
        "description": "Mindful yoga cards designed for toddlers ages 1-3.",
        "keywords": "toddler yoga, mindful play, screen free toddler, calm corner, movement",
    },
    "Early Childhood Deck": {
        "product_name": "Early Childhood Yoga Cards",
        "age_group": "Early Childhood",
        "product_type": "Yoga Flashcards",
        "angle": "Learning Through Movement",
        "description": "Yoga cards for ages 4-7 supporting movement and focus.",
        "keywords": "kids yoga, ages 4-7, mindfulness kids, homeschool, focus",
    },
    "Tween Deck": {
        "product_name": "Tween Yoga Cards",
        "age_group": "Tween",
        "product_type": "Yoga Flashcards",
        "angle": "Confidence & Wellness",
        "description": "Tween yoga cards for ages 8-12 building confidence and calm.",
        "keywords": "tween yoga, confidence, mindfulness, screen free tween, growing kids",
    },
    "Teen Deck": {
        "product_name": "Teen Yoga Cards",
        "age_group": "Teen",
        "product_type": "Yoga Flashcards",
        "angle": "Stress Relief & Strength",
        "description": "Teen yoga cards for stress relief, mobility, and confidence.",
        "keywords": "teen yoga, stress relief, teen wellness, confidence, posture",
    },
    "Bundle": {
        "product_name": "Kids Yoga Card Bundle",
        "age_group": "All Ages",
        "product_type": "Yoga Flashcard Bundle",
        "angle": "Grow With Your Child",
        "description": "Bundle of yoga cards covering multiple childhood stages.",
        "keywords": "yoga cards kids, family wellness, homeschool, gift, mindfulness",
    },
}

# ── Helper Functions ─────────────────────────────────────────────────────────

def append_variants_to_google_sheet(product_name, age_group, product_type, marketing_angle, variants):
    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError as exc:
        raise RuntimeError("Run: pip install gspread google-auth") from exc

    credentials_path = Path(os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH", "google_service_account.json"))
    if not credentials_path.exists():
        raise FileNotFoundError(f"Credentials not found at '{credentials_path}'.")

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    credentials = Credentials.from_service_account_file(str(credentials_path), scopes=scopes)
    client = gspread.authorize(credentials)
    worksheet = client.open(GOOGLE_SHEET_NAME).worksheet(GOOGLE_SHEET_WORKSHEET)

    rows = []
    for variant_name, result in variants.items():
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rows.append([
            timestamp, product_name, age_group, product_type, marketing_angle, variant_name,
            result.get("etsy_title", ""),
            ", ".join(result.get("etsy_tags", [])),
            result.get("etsy_description", ""),
            result.get("pinterest_title", ""),
            result.get("pinterest_description", ""),
            result.get("instagram_caption", ""),
            "", "", "Draft", "No", "No", "",
        ])
    worksheet.append_rows(rows, value_input_option="USER_ENTERED")


def auto_height(text: str, min_height: int = 120, line_px: int = 32, chars_per_line: int = 55) -> int:
    text = text or ""
    lines = text.splitlines() or [""]
    wrapped_lines = sum(max(1, (len(line) // chars_per_line) + 1) for line in lines)
    return max(min_height, wrapped_lines * line_px)


def tag_status(tag_items):
    cleaned = [t.strip() for t in tag_items if t and t.strip()]
    lowered = [t.lower() for t in cleaned]
    return {
        "count": len(cleaned),
        "too_long": [t for t in cleaned if len(t) > 20],
        "duplicates": sorted({t for t in lowered if lowered.count(t) > 1}),
    }


def apply_template(template_name: str):
    selected = templates[template_name]
    for key in ["product_name", "age_group", "product_type", "angle", "description", "keywords"]:
        st.session_state[f"{key}_input"] = selected[key]


def get_assets_in_folder(folder_name: str) -> list:
    folder = ASSETS_DIR / folder_name
    if not folder.exists():
        return []
    return sorted([
        f.name for f in folder.iterdir()
        if f.suffix.lower() in {".png", ".jpg", ".jpeg"}
    ])


def build_github_raw_url(folder_name: str, filename: str) -> str:
    return f"{GITHUB_RAW_BASE}/{folder_name}/{filename}"


def post_carousel_to_instagram(caption: str, image_urls: list) -> dict:
    """Post a carousel (multiple images) to Instagram."""
    access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    user_id = os.getenv("INSTAGRAM_USER_ID")
    api_base = "https://graph.instagram.com/v21.0"

    if not access_token or not user_id:
        return {
            "success": False,
            "message": "Missing INSTAGRAM_ACCESS_TOKEN or INSTAGRAM_USER_ID in .env",
            "error_detail": "Set both variables in your .env file.",
            "status_code": None,
        }

    try:
        # Step 1 — Create individual media containers (no caption here)
        child_ids = []
        for url in image_urls:
            resp = requests.post(
                f"{api_base}/{user_id}/media",
                data={"image_url": url, "is_carousel_item": "true", "access_token": access_token},
                timeout=15,
            )
            if resp.status_code not in [200, 201]:
                return {
                    "success": False,
                    "message": f"Failed to create media container for {url}",
                    "error_detail": resp.text,
                    "status_code": resp.status_code,
                }
            child_ids.append(resp.json().get("id"))

        # Step 2 — Create carousel container
        carousel_resp = requests.post(
            f"{api_base}/{user_id}/media",
            data={
                "media_type": "CAROUSEL",
                "children": ",".join(child_ids),
                "caption": caption,
                "access_token": access_token,
            },
            timeout=15,
        )
        if carousel_resp.status_code not in [200, 201]:
            return {
                "success": False,
                "message": "Failed to create carousel container",
                "error_detail": carousel_resp.text,
                "status_code": carousel_resp.status_code,
            }
        carousel_id = carousel_resp.json().get("id")

        # Step 3 — Publish
        publish_resp = requests.post(
            f"{api_base}/{user_id}/media_publish",
            data={"creation_id": carousel_id, "access_token": access_token},
            timeout=15,
        )
        if publish_resp.status_code in [200, 201]:
            return {
                "success": True,
                "post_id": publish_resp.json().get("id"),
                "message": "Carousel posted successfully to Instagram!",
                "status_code": publish_resp.status_code,
            }
        return {
            "success": False,
            "message": f"Failed to publish carousel (Status {publish_resp.status_code})",
            "error_detail": publish_resp.text,
            "status_code": publish_resp.status_code,
        }

    except requests.exceptions.Timeout:
        return {"success": False, "message": "Request timeout", "error_detail": "Instagram API took too long", "status_code": None}
    except Exception as e:
        return {"success": False, "message": "Unexpected error", "error_detail": str(e), "status_code": None}


# ── Session State Defaults ───────────────────────────────────────────────────

for key, value in {
    "product_name_input": "",
    "age_group_input": "Toddler",
    "product_type_input": "Yoga Flashcards",
    "angle_input": "",
    "description_input": "",
    "keywords_input": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ── Main Tabs ────────────────────────────────────────────────────────────────

main_tab1, main_tab2 = st.tabs(["🛍️ Content Generator", "📌 Post to Instagram"])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — Content Generator
# ════════════════════════════════════════════════════════════════════════════

with main_tab1:
    template_choice = st.selectbox("Choose Template", list(templates.keys()), key="template_choice")
    if st.button("Apply Template"):
        apply_template(template_choice)
        st.rerun()

    age_group_options = ["Toddler", "Early Childhood", "Tween", "Teen", "All Ages", "All 4 Decks"]

    with st.form("generator_form"):
        product_name = st.text_input("Product Name", key="product_name_input")
        age_group = st.selectbox(
            "Age Group",
            age_group_options,
            index=age_group_options.index(st.session_state["age_group_input"]),
            key="age_group_input",
        )
        product_type = st.text_input("Product Type", key="product_type_input")
        angle = st.text_input("Marketing Angle", key="angle_input")
        description = st.text_area("Short Description", key="description_input", height=120)
        keywords = st.text_input("Keywords (comma separated)", key="keywords_input")
        submitted = st.form_submit_button("Generate 3 Variants")

    if submitted:
        kw_list = [k.strip() for k in keywords.split(",") if k.strip()]
        start_time = time.time()
        with st.spinner("Generating 3 variants with Ollama..."):
            st.session_state.variants = generate_campaign_variants(
                product_name=product_name,
                age_group=age_group,
                product_type=product_type,
                keywords=kw_list,
                angle=angle,
                description=description,
            )
        st.session_state.generation_time = time.time() - start_time

    if "variants" in st.session_state and st.session_state.variants:
        st.success("3 variants generated. Compare and choose your favorite.")

        if st.button("Send 3 Variants to Google Sheet"):
            try:
                append_variants_to_google_sheet(
                    product_name=st.session_state.get("product_name_input", ""),
                    age_group=st.session_state.get("age_group_input", ""),
                    product_type=st.session_state.get("product_type_input", ""),
                    marketing_angle=st.session_state.get("angle_input", ""),
                    variants=st.session_state.variants,
                )
                st.success("Sent 3 variants to MYB Content Queue.")
            except Exception as exc:
                st.error(f"Could not send variants to Google Sheet: {exc}")

        tabs = st.tabs(list(st.session_state.variants.keys()))
        if "generation_time" in st.session_state:
            st.caption(f"Generated in {st.session_state.generation_time:.1f} seconds")

        for tab_name, tab in zip(st.session_state.variants.keys(), tabs):
            with tab:
                result = st.session_state.variants[tab_name]
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Etsy")
                    etsy_title_val = result.get("etsy_title", "")
                    etsy_title = st.text_area("Etsy Title", etsy_title_val, height=auto_height(etsy_title_val, 80), key=f"{tab_name}_etsy_title")
                    st.caption(f"Characters: {len(etsy_title)}/140")

                    tags_val = ", ".join(result.get("etsy_tags", []))
                    tags_text = st.text_area("Etsy Tags (comma separated)", tags_val, height=auto_height(tags_val, 160), key=f"{tab_name}_etsy_tags")
                    raw_tag_items = [t.strip() for t in tags_text.split(",") if t.strip()]
                    status = tag_status(raw_tag_items)
                    tag_items = raw_tag_items[:13]
                    st.caption(f"Tags: {len(tag_items)}/13")
                    st.caption("Final Etsy tags:")
                    st.code("\n".join([f"{tag} ({len(tag)}/20)" for tag in tag_items]), language=None)
                    if status["too_long"]:
                        st.warning("Some tags are longer than Etsy's 20-character limit.")
                    if status["duplicates"]:
                        st.warning("Some tags are duplicated.")
                    if status["count"] > 13:
                        st.warning("Only the first 13 tags will be kept for Etsy.")

                    etsy_desc_val = result.get("etsy_description", "")
                    etsy_description = st.text_area("Etsy Description", etsy_desc_val, height=auto_height(etsy_desc_val, 280), key=f"{tab_name}_etsy_desc")

                with col2:
                    st.subheader("Pinterest + Instagram")
                    pin_title_val = result.get("pinterest_title", "")
                    pinterest_title = st.text_area("Pinterest Title", pin_title_val, height=auto_height(pin_title_val, 80), key=f"{tab_name}_pin_title")
                    pin_desc_val = result.get("pinterest_description", "")
                    pinterest_description = st.text_area("Pinterest Description", pin_desc_val, height=auto_height(pin_desc_val, min_height=260, line_px=32, chars_per_line=55), key=f"{tab_name}_pin_desc")
                    ig_val = result.get("instagram_caption", "")
                    instagram_caption = st.text_area("Instagram Caption", ig_val, height=auto_height(ig_val, min_height=320, line_px=34, chars_per_line=50), key=f"{tab_name}_ig_caption")

                reviewed_data = {
                    "variant": tab_name, "product_name": product_name, "age_group": age_group,
                    "product_type": product_type, "marketing_angle": angle,
                    "keywords": [k.strip() for k in keywords.split(",") if k.strip()],
                    "etsy_title": etsy_title, "etsy_tags": tag_items[:13],
                    "etsy_description": etsy_description, "pinterest_title": pinterest_title,
                    "pinterest_description": pinterest_description, "instagram_caption": instagram_caption,
                }

                json_output = json.dumps(reviewed_data, indent=2, ensure_ascii=False)
                txt_output = f"""VARIANT\n-------\n{tab_name}\n\nPRODUCT\n-------\nProduct Name: {product_name}\nAge Group: {age_group}\nProduct Type: {product_type}\nMarketing Angle: {angle}\nKeywords: {keywords}\n\nETSY\n----\nTitle:\n{etsy_title}\n\nTags:\n{", ".join(tag_items[:13])}\n\nDescription:\n{etsy_description}\n\nPINTEREST\n---------\nTitle:\n{pinterest_title}\n\nDescription:\n{pinterest_description}\n\nINSTAGRAM\n---------\nCaption:\n{instagram_caption}""".strip()

                d1, d2 = st.columns(2)
                with d1:
                    st.download_button(label=f"Download {tab_name} JSON", data=json_output, file_name=f"{tab_name.lower().replace(' ', '_')}_campaign.json", mime="application/json", key=f"{tab_name}_json_download")
                with d2:
                    st.download_button(label=f"Download {tab_name} TXT", data=txt_output, file_name=f"{tab_name.lower().replace(' ', '_')}_campaign.txt", mime="text/plain", key=f"{tab_name}_txt_download")


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — Post to Instagram
# ════════════════════════════════════════════════════════════════════════════

with main_tab2:
    st.header("📌 Post to Instagram")
    st.caption("Select images → write caption → post single or carousel (auto-posts to Pinterest via connected accounts)")
    st.divider()

    # ── Step 1: Image Selection ──────────────────────────────────────────────
    st.subheader("Step 1 — Choose your image(s)")

    img_source = st.radio(
        "Image source",
        ["📁 Select from assets folder", "📱 Upload from device (mobile / desktop)"],
        horizontal=True,
    )

    image_urls = []

    if img_source == "📁 Select from assets folder":
        selected_label = st.selectbox("Age group folder", list(AGE_GROUP_FOLDERS.keys()))
        folder_name = AGE_GROUP_FOLDERS[selected_label]
        files = get_assets_in_folder(folder_name)

        if files:
            selected_files = st.multiselect(
                "Select image(s) — select multiple for a carousel (up to 10, order matters)",
                files,
                help="First selected = Slide 1. Select in the order you want them to appear on Instagram.",
            )
            if selected_files:
                if len(selected_files) > 10:
                    st.error("❌ Instagram allows maximum 10 images per carousel.")
                else:
                    image_urls = [build_github_raw_url(folder_name, f) for f in selected_files]
                    st.caption(f"✅ {len(image_urls)} image(s) selected")
                    for i, url in enumerate(image_urls):
                        st.caption(f"Slide {i+1}: `{url}`")
        else:
            st.warning(f"No images in `assets/{folder_name}/`. Add images and push to GitHub.")

    else:
        uploaded_files = st.file_uploader(
            "Upload image(s) — upload multiple for a carousel",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=True,
            help="On mobile: tap to open camera roll. Select multiple for carousel.",
        )
        if uploaded_files:
            all_ok = True
            for f in uploaded_files:
                size_mb = f.size / (1024 * 1024)
                if size_mb > MAX_IMAGE_MB:
                    st.error(f"❌ {f.name} is {size_mb:.1f}MB — over 8MB limit.")
                    all_ok = False
            if all_ok:
                st.info(f"✅ {len(uploaded_files)} file(s) OK.")
                st.warning("⚠️ To post via API, save these to `assets/` folder, push to GitHub, then use 'Select from assets folder'.")
                cols = st.columns(min(len(uploaded_files), 3))
                for i, (col, f) in enumerate(zip(cols, uploaded_files)):
                    with col:
                        st.image(f, caption=f"Slide {i+1}: {f.name}", use_container_width=True)

    # ── Image Preview ────────────────────────────────────────────────────────
    if image_urls:
        st.divider()
        st.subheader("Preview")
        if len(image_urls) == 1:
            st.image(image_urls[0], width=400)
        else:
            st.caption(f"Carousel — {len(image_urls)} slides (shown left to right)")
            cols = st.columns(min(len(image_urls), 3))
            for i, (col, url) in enumerate(zip(cols, image_urls)):
                with col:
                    st.image(url, caption=f"Slide {i+1}", use_container_width=True)

    # ── Step 2: Caption ──────────────────────────────────────────────────────
    st.divider()
    st.subheader("Step 2 — Write your caption")

    prefilled_caption = ""
    if "variants" in st.session_state and st.session_state.variants:
        if st.checkbox("Use caption from generated variants"):
            variant_choice = st.selectbox("Choose variant", list(st.session_state.variants.keys()))
            prefilled_caption = st.session_state.variants[variant_choice].get("instagram_caption", "")

    caption = st.text_area(
        "Instagram caption (with hashtags)",
        value=prefilled_caption,
        height=200,
        placeholder="Write your caption here...",
    )
    st.caption(f"{len(caption)} characters")

    # ── Step 3: Post ─────────────────────────────────────────────────────────
    st.divider()
    st.subheader("Step 3 — Post")

    if not image_urls:
        st.info("👆 Select image(s) above to enable posting.")
    elif not caption.strip():
        st.info("👆 Write a caption above to enable posting.")
    else:
        post_type = "carousel" if len(image_urls) > 1 else "single image"
        st.caption(f"Ready to post: **{post_type}** ({len(image_urls)} image(s))")

        if st.button("🚀 Post to Instagram", type="primary"):
            with st.spinner(f"Posting {post_type} to Instagram..."):
                if len(image_urls) == 1:
                    result = post_to_instagram(caption=caption, image_url=image_urls[0])
                else:
                    result = post_carousel_to_instagram(caption=caption, image_urls=image_urls)

            if result["success"]:
                st.success(f"✅ {result['message']} Post ID: {result.get('post_id', 'N/A')}")
                st.balloons()
                st.info("📌 Will auto-post to Pinterest via your connected accounts.")
            else:
                st.error(f"❌ {result['message']}")
                if result.get("error_detail"):
                    st.caption(f"Detail: {result['error_detail']}")

    # ── Image Specs Reminder ─────────────────────────────────────────────────
    with st.expander("📐 ChatGPT image specs for Instagram"):
        st.markdown("""
**Ask ChatGPT to generate images with these specs:**

| Format | Size | Ratio |
|--------|------|-------|
| Square post | 1080 × 1080px | 1:1 |
| Portrait post | 1080 × 1350px | 4:5 ✅ recommended |
| Story / Reel cover | 1080 × 1920px | 9:16 |

**Requirements:** JPG or PNG · Max 8MB · Min 320px wide

**Add to your ChatGPT prompt:**
> *"Export at 1080x1350px, JPG format, under 5MB"*

**Carousel naming convention:**
```
assets/toddler/1.png  ← Slide 1 (Hook)
assets/toddler/2.png  ← Slide 2 (Product)
assets/toddler/3.png  ← Slide 3 (Benefits)
```
Simply number your images in posting order.
        """)