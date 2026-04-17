import json
import streamlit as st
from content_engine import generate_campaign

st.set_page_config(page_title="Etsy Automation Tool", layout="wide")

st.title("🛍️ Etsy Automation Tool")
st.caption("Generate → Review → Edit → Export")


# ---------- Templates ----------
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


# ---------- Helpers ----------
def auto_height(text: str, min_height: int = 120, line_px: int = 30) -> int:
    text = text or ""
    lines = text.splitlines() or [""]
    approx_wrapped_lines = sum(max(1, len(line) // 70 + 1) for line in lines)
    return max(min_height, approx_wrapped_lines * line_px)


def apply_template(template_name: str):
    selected = templates[template_name]
    st.session_state["product_name_input"] = selected["product_name"]
    st.session_state["age_group_input"] = selected["age_group"]
    st.session_state["product_type_input"] = selected["product_type"]
    st.session_state["angle_input"] = selected["angle"]
    st.session_state["description_input"] = selected["description"]
    st.session_state["keywords_input"] = selected["keywords"]


# ---------- Session defaults ----------
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


# ---------- Template Picker ----------
template_choice = st.selectbox(
    "Choose Template",
    list(templates.keys()),
    key="template_choice",
)

if st.button("Apply Template"):
    apply_template(template_choice)
    st.rerun()


# ---------- Input Form ----------
age_group_options = [
    "Toddler",
    "Early Childhood",
    "Tween",
    "Teen",
    "All Ages"
]

with st.form("generator_form"):
    product_name = st.text_input(
        "Product Name",
        key="product_name_input",
    )

    age_group = st.selectbox(
        "Age Group",
        age_group_options,
        index=age_group_options.index(st.session_state["age_group_input"]),
        key="age_group_input",
    )

    product_type = st.text_input(
        "Product Type",
        key="product_type_input",
    )

    angle = st.text_input(
        "Marketing Angle",
        key="angle_input",
    )

    description = st.text_area(
        "Short Description",
        key="description_input",
        height=120,
    )

    keywords = st.text_input(
        "Keywords (comma separated)",
        key="keywords_input",
    )

    submitted = st.form_submit_button("Generate Content")


# ---------- Generate ----------
if submitted:
    kw_list = [k.strip() for k in keywords.split(",") if k.strip()]

    with st.spinner("Generating content with Ollama..."):
        st.session_state.result = generate_campaign(
            product_name,
            age_group,
            product_type,
            kw_list,
            angle,
            description,
        )


# ---------- Output ----------
if "result" in st.session_state and st.session_state.result is not None:
    result = st.session_state.result
    st.success("Content generated. Review and edit below.")

    col1, col2 = st.columns(2)

    with col1:
        st.header("Etsy")

        etsy_title_val = result.get("etsy_title", "")
        etsy_title = st.text_area(
            "Etsy Title",
            etsy_title_val,
            height=auto_height(etsy_title_val, 80),
            key="etsy_title",
        )
        st.caption(f"Characters: {len(etsy_title)}/140")

        tags_val = ", ".join(result.get("etsy_tags", []))
        tags_text = st.text_area(
            "Etsy Tags (comma separated)",
            tags_val,
            height=auto_height(tags_val, 200),
            key="etsy_tags",
        )
        tag_items = [t.strip() for t in tags_text.split(",") if t.strip()]
        st.caption(f"Tags: {len(tag_items[:13])}/13")

        etsy_desc_val = result.get("etsy_description", "")
        etsy_description = st.text_area(
            "Etsy Description",
            etsy_desc_val,
            height=auto_height(etsy_desc_val, 260),
            key="etsy_desc",
        )

    with col2:
        st.header("Pinterest + Instagram")

        pin_title_val = result.get("pinterest_title", "")
        pinterest_title = st.text_area(
            "Pinterest Title",
            pin_title_val,
            height=auto_height(pin_title_val, 80),
            key="pin_title",
        )

        pin_desc_val = result.get("pinterest_description", "")
        pinterest_description = st.text_area(
            "Pinterest Description",
            pin_desc_val,
            height=auto_height(pin_desc_val, 220),
            key="pin_desc",
        )

        ig_val = result.get("instagram_caption", "")
        instagram_caption = st.text_area(
            "Instagram Caption",
            ig_val,
            height=auto_height(ig_val, 240),
            key="ig_caption",
        )

    keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]

    reviewed_data = {
        "product_name": product_name,
        "age_group": age_group,
        "product_type": product_type,
        "marketing_angle": angle,
        "keywords": keyword_list,
        "etsy_title": etsy_title,
        "etsy_tags": tag_items[:13],
        "etsy_description": etsy_description,
        "pinterest_title": pinterest_title,
        "pinterest_description": pinterest_description,
        "instagram_caption": instagram_caption,
    }

    json_output = json.dumps(reviewed_data, indent=2, ensure_ascii=False)

    txt_output = f"""
PRODUCT
-------
Product Name: {product_name}
Age Group: {age_group}
Product Type: {product_type}
Marketing Angle: {angle}
Keywords: {", ".join(keyword_list)}

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

    st.divider()
    d1, d2 = st.columns(2)

    with d1:
        st.download_button(
            label="Download JSON",
            data=json_output,
            file_name="etsy_campaign.json",
            mime="application/json",
        )

    with d2:
        st.download_button(
            label="Download TXT",
            data=txt_output,
            file_name="etsy_campaign.txt",
            mime="text/plain",
        )

elif "result" in st.session_state and st.session_state.result is None:
    st.error("No content was returned from generate_campaign(). Check content_engine.py")
    st.stop()