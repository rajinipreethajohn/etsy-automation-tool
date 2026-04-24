# MindfulYogiBoutique Etsy Automation Tool

A Streamlit-powered content generation and publishing system for MindfulYogiBoutique's Etsy shop. Generates SEO-optimized Etsy listings, Pinterest pins, and Instagram captions using a local LLM (Ollama + Llama 3.1), with direct social media publishing support.

---

## Project Overview & Purpose

This tool automates content creation for MindfulYogiBoutique's yoga flashcard products — a handcrafted range of mindfulness yoga cards for Toddlers, Early Childhood, Tweens, and Teens, rooted in Sanskrit and Kannada tradition and designed for screen-free play.

The tool generates three creative variants per product or pose, each with Etsy listing content (title, tags, description), Pinterest pin content, and Instagram captions — allowing you to compare, edit, and export or publish directly.

**Core goals:**

- Reduce time spent writing product listings
- Maintain consistent brand voice across age groups and platforms
- Generate SEO-optimized content that converts
- Streamline the full content-to-publishing workflow
- Scale to 60+ poses across 4 age groups (180+ pieces of content)

---

## Current Features & What Works Today

| Feature                                         | Status                            |
| ----------------------------------------------- | --------------------------------- |
| Generate 3 content variants per product         | ✅ Working                        |
| Etsy title, tags (13), and description          | ✅ Working                        |
| Pinterest title and description                 | ✅ Working                        |
| Instagram caption with hashtags                 | ✅ Working                        |
| Pre-built templates for 5 product types         | ✅ Working                        |
| Pose-level content (enter pose name as product) | ✅ Working                        |
| Tag validation (length, duplicates)             | ✅ Working                        |
| Export to Google Sheets (MYB Content Queue)     | ✅ Working                        |
| Download JSON/TXT files                         | ✅ Working                        |
| Copy-to-clipboard for Pinterest/Instagram       | ✅ Working                        |
| Post to Instagram                               | ✅ Working (tested April 23 2026) |
| Instagram auto-posts to Pinterest               | ✅ Working (accounts connected)   |
| Post directly to Pinterest via API              | ⚠️ API under review by Pinterest  |

---

## Tech Stack

| Component            | Technology                              | Purpose                              |
| -------------------- | --------------------------------------- | ------------------------------------ |
| **Frontend**         | Streamlit 1.56.0                        | Web UI, form handling, session state |
| **LLM**              | Ollama + Llama 3.1 (local)              | Content generation, zero API cost    |
| **Data Storage**     | Google Sheets API                       | Content queue and history            |
| **Social API**       | Pinterest API v5                        | Pin posting (pending approval)       |
| **Social API**       | Instagram Graph API v21.0               | Post publishing                      |
| **Image Generation** | ChatGPT (manual) / DALL-E API (planned) | Lifestyle and composite images       |
| **Auth**             | Google Service Account                  | Sheets authentication                |
| **Config**           | python-dotenv                           | Environment variable management      |
| **HTTP**             | requests 2.33.1                         | API calls                            |

---

## File Structure

```
etsy_automation/
├── app.py                      # Main Streamlit application
├── content_engine.py           # LLM prompt building & content generation
├── post_to_pinterest.py        # Pinterest API v5 integration
├── post_to_instagram.py        # Instagram Graph API integration
├── get_boards.py               # Pinterest board listing utility
├── requirements.txt            # Python dependencies
├── SMOKE_TEST.md               # Pre/post-refactor test checklist
├── assets/                     # (Planned) Product images by age group
│   ├── toddler/
│   ├── ec/
│   ├── tween/
│   ├── teen/
│   └── senior/
├── .env                        # Environment variables (not in git)
├── google_service_account.json # Google Sheets credentials (not in git)
└── README.md                   # This file
```

### File Descriptions

| File                   | Purpose                                                                      |
| ---------------------- | ---------------------------------------------------------------------------- |
| `app.py`               | Streamlit UI with forms, templates, variant tabs, export, and social posting |
| `content_engine.py`    | Builds prompts for Ollama, parses JSON responses, normalizes Etsy tags       |
| `post_to_pinterest.py` | Posts pins to Pinterest using v5 API with access token                       |
| `post_to_instagram.py` | Creates media containers and publishes to Instagram via Graph API            |
| `get_boards.py`        | Utility script to list Pinterest boards and find board IDs                   |
| `requirements.txt`     | All Python package dependencies                                              |
| `SMOKE_TEST.md`        | QA checklist for verifying the app works after changes                       |

---

## Setup Instructions

### 1. Clone and Navigate

```bash
cd /path/to/etsy_automation
```

### 2. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install and Run Ollama

```bash
# Install Ollama: https://ollama.com
ollama pull llama3.1
ollama serve  # Must be running before launching the app
ollama list   # Verify llama3.1:latest is shown
```

### 5. Configure Environment Variables

Create a `.env` file in the project root (never commit this file):

```env
# Google Sheets
GOOGLE_SERVICE_ACCOUNT_PATH=google_service_account.json

# Pinterest API (pending approval)
PINTEREST_ACCESS_TOKEN=your_access_token_here
PINTEREST_BOARD_ID=your_board_id_here

# Instagram Graph API
INSTAGRAM_ACCESS_TOKEN=your_access_token_here
INSTAGRAM_USER_ID=your_user_id_here
```

### 6. Set Up Google Sheets

1. Create a Google Service Account in Google Cloud Console
2. Download JSON credentials → save as `google_service_account.json`
3. Create a Google Sheet named **"MYB Content Queue"**
4. Share the sheet with your service account email
5. Ensure a worksheet named **"Sheet1"** exists

### 7. Run the App

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`

---

## Current Workflow

### Product-Level Content (Campaigns)

1. Launch: `streamlit run app.py`
2. Choose template: Custom, Toddler Deck, Early Childhood, Tween Deck, Teen Deck, or Bundle
3. Click **Apply Template** to pre-fill fields
4. Customize inputs as needed
5. Click **Generate 3 Variants** (30–60 seconds via Ollama)
6. Review 3 tabs: SEO Safe / Emotional Parent Hook / Premium Brand Voice
7. Edit any field in the text areas
8. Export: Google Sheets, JSON, TXT, or copy to clipboard
9. Post to Instagram directly from the app

### Pose-Level Content (Individual Poses)

The existing form works for pose-level content today:

- **Product Name:** `Warrior II Pose – Teen Yoga Card`
- **Marketing Angle:** `Build Strength & Focus for Teens`
- **Short Description:** Describe the pose and its benefits
- **Keywords:** pose-specific keywords

This generates pose-specific Etsy, Pinterest, and Instagram content with benefits in the description.

### Publishing Flow

```
Generate content in Streamlit
        ↓
Post to Instagram (working ✅)
        ↓
Auto-posts to Pinterest (via connected accounts ✅)
```

---

## Content Brand System

### Core Principle

One brand. Four emotional worlds. Keep structure consistent while adapting mood, setting, and tone by age group.

**Consistent elements across all age groups:**

- Earthy palette (sage green, beige, cream, warm brown)
- Clean premium layouts
- Friendly elegant typography
- Clear product visibility
- Warm natural lighting
- MindfulYogiBoutique footer branding

---

### Age Group Mood Guides

#### Toddlers (Ages 1–3)

- **Mood:** Cozy, safe, joyful
- **Setting:** Nursery, playroom, sunny living room
- **Props:** Soft toys, woven baskets, warm sunlight
- **Copy style:** Playful, gentle, screen-free fun
- **Emotional world:** Nurturing

#### Kids (Ages 4–7)

- **Mood:** Playful, imaginative, energetic
- **Setting:** Colorful room, garden, classroom, backyard
- **Props:** Rainbow accents, movement, adventure
- **Copy style:** Fun learning, movement games
- **Emotional world:** Playful

#### Tweens (Ages 8–12)

- **Mood:** Confidence, independence, self-expression
- **Setting:** Modern bedroom, rooftop, studio, park
- **Props:** Capable, cool, balanced
- **Copy style:** Confidence, focus, strength
- **Emotional world:** Confident

#### Teens (Ages 13–17)

- **Mood:** Empowerment, wellness, calm strength
- **Setting:** Sunrise balcony, clean gym studio, bedroom sanctuary, nature deck
- **Props:** Mindful, strong, aspirational
- **Copy style:** Stress relief, resilience, performance
- **Emotional world:** Empowered

---

### Pinterest Pin Strategy

**Purpose:** Traffic + saves + discovery + Etsy clicks

**Standard Pin Layout:**

1. Strong headline at top
2. Lifestyle hero image (child doing the pose, mood-matched)
3. Divider banner: _"Yoga Poses • Big Benefits • Little Moments"_
4. Product cards — front (left) + back (right)
5. Benefits strip (4 icons)
6. MindfulYogiBoutique footer

**Pin Formula:** Headline + Emotional photo + Product proof + Benefits + Brand

**ChatGPT Prompt Template (fill variables each time):**

```
Create a premium Pinterest vertical pin (1000x1500 ratio) for MindfulYogiBoutique.

STYLE: Warm, natural, cozy, sunlit family home. Earthy tones (sage green, beige, cream, brown).
Premium Pinterest-worthy lifestyle photography mixed with clean product collage.

TOP SECTION:
Child aged [AGE GROUP] doing [POSE NAME] on a yoga mat in a cozy room.
Headline: "Yoga Flashcards for [AGE GROUP] — Screen-Free • Mindful • Fun"
Side bubble: "Build Strength & Joy"

MIDDLE: Brushstroke banner — "Yoga Poses • Big Benefits • Little Moments"

BOTTOM: Two flashcards — LEFT = front card (uploaded, untouched), RIGHT = back card (uploaded, untouched)
Sage green bubble labels: "Front" and "Back"

BOTTOM STRIP: Builds Strength | Improves Focus | Supports Confidence | Encourages Joy
FOOTER: MindfulYogiBoutique

Variables: [AGE GROUP] = Toddlers / Kids 4–7 / Tweens / Teens
           [POSE NAME] = Frog Pose / Tree Pose / Warrior II / etc.
```

---

### Instagram Carousel Strategy

**Purpose:** Engagement + trust + saves + shares

**3-Slide Core Format:**

| Slide                       | Content                                                                 | Purpose         |
| --------------------------- | ----------------------------------------------------------------------- | --------------- |
| **Slide 1 — Hook**          | Lifestyle image + pose name + age group + emotional hook                | Stop the scroll |
| **Slide 2 — Product Proof** | Front/back flashcards on clean background                               | Build trust     |
| **Slide 3 — Value**         | 3 benefits / routine / affirmation / quick guide + "Save for later" CTA | Drive saves     |

**Carousel Content Themes:**

- 3 Benefits of [Pose]
- 3 Calm Moves Before Bed
- Confidence Poses for Tweens
- Teen Stress Relief Yoga
- Screen-Free Movement Ideas
- After School Reset Flow

**Carousel Formula:** Hook + Proof + Value

---

### Content Scale

|            | Toddler | Kids 4–7 | Tween | Teen |
| ---------- | ------- | -------- | ----- | ---- |
| 15 poses × | ⬜      | ⬜       | ⬜    | ⬜   |

**60 pose × age group combinations**
**× 3 assets each (pin + carousel + caption)**
**= 180 pieces of evergreen content**

At 2–3 pieces/day = **2–3 months of scheduled content** from existing assets.

---

### Production Rhythm

- **Daily target:** 2–3 pieces
- **Per session output:** 1 Pinterest pin + 1 carousel set + 1 caption
- **Monthly result:** 60–90 evergreen assets

---

## Planned: Image Pipeline

```
ChatGPT generates lifestyle image (pose + age group mood)
        ↓
Save to assets/[age_group]/[pose_name]_slide1.png
        ↓
Streamlit reads assets/ folder → file picker dropdown
        ↓
Select image → generate caption → post to Instagram
        ↓
Auto-posts to Pinterest via connected accounts
```

**Folder naming convention:**

```
assets/
  toddler/frog_pose_slide1.png, frog_pose_slide2.png ...
  ec/tree_pose_slide1.png ...
  tween/warrior_pose_slide1.png ...
  teen/crow_pose_slide1.png ...
  senior/mountain_pose_slide1.png ...
```

---

## Roadmap

| Feature                                 | Priority   | Status  | Notes                                          |
| --------------------------------------- | ---------- | ------- | ---------------------------------------------- |
| Pose Pin Creator tab                    | 🔥 High    | Planned | Auto-fills ChatGPT prompt by pose + age group  |
| Image folder system                     | 🔥 High    | Planned | `assets/` folder, file picker in Streamlit     |
| Full Instagram posting flow with images | 🔥 High    | Planned | Image URL → caption → post                     |
| Pinterest API approval                  | ⏳ Waiting | Pending | Application submitted                          |
| DALL-E API integration                  | Medium     | Planned | ~$0.08/image, Phase 2                          |
| Content session tracker                 | Medium     | Planned | Track which poses have been posted             |
| Batch generation                        | Low        | Planned | Generate all 4 age groups for one pose at once |

---

## Pinterest API Status

The Pinterest API application is **under review**. The "Post to Pinterest" button exists in the UI but returns an error until approved.

**Current workaround:** Instagram and Pinterest accounts are connected — posting to Instagram auto-posts to Pinterest. ✅

**Once approved:**

1. Generate access token at [developers.pinterest.com](https://developers.pinterest.com)
2. Run `get_boards.py` to find your board IDs
3. Add `PINTEREST_ACCESS_TOKEN` and `PINTEREST_BOARD_ID` to `.env`

---

## Known Issues & Limitations

| Issue                                    | Impact                        | Workaround                                              |
| ---------------------------------------- | ----------------------------- | ------------------------------------------------------- |
| Pinterest API pending                    | Cannot post pins directly     | Instagram → Pinterest via connected accounts            |
| Ollama must be running                   | App won't generate without it | Run `ollama serve` before launching                     |
| No image upload in app                   | Must use public image URLs    | Host images on Etsy CDN or use assets/ folder (planned) |
| Tag truncation at 20 chars               | Long tags cut off             | Edit tags manually before publishing                    |
| No content history                       | Session-only                  | Export to Google Sheets                                 |
| `**Benefits:**` markdown in descriptions | Shows raw markdown in Etsy    | Edit manually or fix prompt in `content_engine.py`      |

---

## Troubleshooting

### Ollama Not Running

```
❌ Cannot connect to Ollama
```

Run: `ollama serve`

### Google Sheets Auth Error

```
Could not find Google service account credentials
```

Ensure `google_service_account.json` exists and path is set in `.env`

### Pinterest 403

```
Pinterest API access denied
```

API not yet approved. Post manually or via Instagram connection.

### Instagram 401

```
Authentication failed
```

Token expired. Regenerate at [developers.facebook.com](https://developers.facebook.com)

---

## Security Notes

- Never commit `.env` or `google_service_account.json` — both are in `.gitignore`
- Regenerate tokens if accidentally exposed
- GitHub push protection will block commits containing secrets

---

## License

Internal tool for MindfulYogiBoutique. Not for public distribution.
