import time
import json
import streamlit as st
from content_engine import generate_campaign_variants

st.set_page_config(page_title="Etsy Automation Tool", layout="wide")

st.title("🛍️ Etsy Automation Tool")
st.caption("Generate → Review → Compare Variants → Export")


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


def auto_height(text: str, min_height: int = 120, line_px: int = 32, chars_per_line: int = 55) -> int:
    text = text or ""
    lines = text.splitlines() or [""]
    wrapped_lines = 0

    for line in lines:
        wrapped_lines += max(1, (len(line) // chars_per_line) + 1)

    return max(min_height, wrapped_lines * line_px)

def tag_status(tag_items):
    cleaned = [t.strip() for t in tag_items if t and t.strip()]
    lowered = [t.lower() for t in cleaned]
    duplicates = sorted({t for t in lowered if lowered.count(t) > 1})
    too_long = [t for t in cleaned if len(t) > 20]
    return {
        "count": len(cleaned),
        "too_long": too_long,
        "duplicates": duplicates,
    }

def apply_template(template_name: str):
    selected = templates[template_name]
    st.session_state["product_name_input"] = selected["product_name"]
    st.session_state["age_group_input"] = selected["age_group"]
    st.session_state["product_type_input"] = selected["product_type"]
    st.session_state["angle_input"] = selected["angle"]
    st.session_state["description_input"] = selected["description"]
    st.session_state["keywords_input"] = selected["keywords"]


defaults = {
    "product_name_input": "",
    "age_group_input": "Toddler",
    "product_type_input": "Yoga Flashcards",
    "angle_input": "",
    "description_input": "",
    "keywords_input": "",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


template_choice = st.selectbox(
    "Choose Template",
    list(templates.keys()),
    key="template_choice",
)

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

    elapsed = time.time() - start_time
    st.session_state.generation_time = elapsed


if "variants" in st.session_state and st.session_state.variants:
    st.success("3 variants generated. Compare and choose your favorite.")

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
                etsy_title = st.text_area(
                    "Etsy Title",
                    etsy_title_val,
                    height=auto_height(etsy_title_val, 80),
                    key=f"{tab_name}_etsy_title",
                )
                st.caption(f"Characters: {len(etsy_title)}/140")

                tags_val = ", ".join(result.get("etsy_tags", []))
                tags_text = st.text_area(
                    "Etsy Tags (comma separated)",
                    tags_val,
                    height=auto_height(tags_val, 160),
                    key=f"{tab_name}_etsy_tags",
                )

                raw_tag_items = [t.strip() for t in tags_text.split(",") if t.strip()]
                status = tag_status(raw_tag_items)
                tag_items = raw_tag_items[:13]

                st.caption(f"Tags: {len(tag_items)}/13")
                st.caption("Final Etsy tags:")
                st.code("\n".join([f"{tag} ({len(tag)}/20)" for tag in tag_items]), language=None)

                if status["too_long"]:
                    st.warning("Some tags are longer than Etsy's 20-character limit. Shorten them before publishing.")

                if status["duplicates"]:
                    st.warning("Some tags are duplicated. Consider making them more varied.")

                if status["count"] > 13:
                    st.warning("Only the first 13 tags will be kept for Etsy.")

                etsy_desc_val = result.get("etsy_description", "")
                etsy_description = st.text_area(
                    "Etsy Description",
                    etsy_desc_val,
                    height=auto_height(etsy_desc_val, 280),
                    key=f"{tab_name}_etsy_desc",
                )

            with col2:
                st.subheader("Pinterest + Instagram")

                pin_title_val = result.get("pinterest_title", "")
                pinterest_title = st.text_area(
                    "Pinterest Title",
                    pin_title_val,
                    height=auto_height(pin_title_val, 80),
                    key=f"{tab_name}_pin_title",
                )

                pin_desc_val = result.get("pinterest_description", "")
                pinterest_description = st.text_area(
                "Pinterest Description",
                pin_desc_val,
                height=auto_height(pin_desc_val, min_height=260, line_px=32, chars_per_line=55),
                key=f"{tab_name}_pin_desc",
                )

                ig_val = result.get("instagram_caption", "")
                instagram_caption = st.text_area(
                "Instagram Caption",
                ig_val,
                height=auto_height(ig_val, min_height=320, line_px=34, chars_per_line=50),
                key=f"{tab_name}_ig_caption",
                )

            reviewed_data = {
                "variant": tab_name,
                "product_name": product_name,
                "age_group": age_group,
                "product_type": product_type,
                "marketing_angle": angle,
                "keywords": [k.strip() for k in keywords.split(",") if k.strip()],
                "etsy_title": etsy_title,
                "etsy_tags": tag_items[:13],
                "etsy_description": etsy_description,
                "pinterest_title": pinterest_title,
                "pinterest_description": pinterest_description,
                "instagram_caption": instagram_caption,
            }

            json_output = json.dumps(reviewed_data, indent=2, ensure_ascii=False)

            txt_output = f"""
VARIANT
-------
{tab_name}

PRODUCT
-------
Product Name: {product_name}
Age Group: {age_group}
Product Type: {product_type}
Marketing Angle: {angle}
Keywords: {keywords}

ETSY
----
Title:
{etsy_title}

Tags:
{", ".join(tag_items[:13])}

Description:
{etsy_description}

PINTEREST
---------
Title:
{pinterest_title}

Description:
{pinterest_description}

INSTAGRAM
---------
Caption:
{instagram_caption}
""".strip()

            d1, d2 = st.columns(2)

            with d1:
                st.download_button(
                    label=f"Download {tab_name} JSON",
                    data=json_output,
                    file_name=f"{tab_name.lower().replace(' ', '_')}_campaign.json",
                    mime="application/json",
                    key=f"{tab_name}_json_download",
                )

            with d2:
                st.download_button(
                    label=f"Download {tab_name} TXT",
                    data=txt_output,
                    file_name=f"{tab_name.lower().replace(' ', '_')}_campaign.txt",
                    mime="text/plain",
                    key=f"{tab_name}_txt_download",
                )