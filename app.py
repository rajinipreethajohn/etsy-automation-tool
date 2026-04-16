import json
import streamlit as st
from content_engine import generate_campaign

st.set_page_config(page_title="Etsy Automation Tool", layout="wide")

st.title("🛍️ Etsy Automation Tool")
st.caption("Generate → Review → Edit → Export")


# ---------- Helpers ----------
def auto_height(text: str, min_height: int = 120, line_px: int = 30) -> int:
    text = text or ""
    lines = text.splitlines() or [""]
    approx_wrapped_lines = sum(max(1, len(line) // 70 + 1) for line in lines)
    return max(min_height, approx_wrapped_lines * line_px)


# ---------- Input Form ----------
with st.form("generator_form"):
    product_name = st.text_input("Product Name", "Tween Yoga Cards")
    age_group = st.selectbox("Age Group", ["Toddler", "Early Childhood", "Tween", "Teen"])
    product_type = st.text_input("Product Type", "Yoga Flashcards")
    angle = st.text_input("Marketing Angle", "Screen-Free Activity")
    description = st.text_area(
        "Short Description",
        "Mindful yoga cards for kids.",
        height=120,
    )
    keywords = st.text_input(
        "Keywords (comma separated)",
        "kids yoga, mindfulness, calm corner",
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

    # Build reviewed/exportable data
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