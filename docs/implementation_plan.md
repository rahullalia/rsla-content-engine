# One-Click Remix Implementation Plan

## Goal Description
Integrate Anthropic's Claude API to automatically rewrite viral video transcripts into the user's specific "Rahul" voice/style with a single click.

## User Review Required
> [!IMPORTANT]
> **API Key Security**: The API key will be input in the UI or an env var. For this local tool, UI input (session state) is easiest but requires re-entry on restart. I will add a `.env` loader for persistence if desired, but start with UI input for safety.
> **Voice Guidelines**: I will hardcode the core "Rahul Voice" prompt based on `voice_and_style.md` into the tool, but allow it to be editable in the UI.

## Proposed Changes

### Core Logic (`src/remix_engine.py`)
#### [NEW] [remix_engine.py](file:///Users/rahullalia/Developer/antigravity/content_engine/src/remix_engine.py)
- **Class `Remixer`**:
    - Method `remix_content(transcript, api_key)`:
    - Uses `anthropic` library.
    - System Prompt: Derived from `voice_and_style.md` (Em dashes, extended vowels, "et al", humble tone).

### UI (`src/app.py`)
#### [MODIFY] [app.py](file:///Users/rahullalia/Developer/antigravity/content_engine/src/app.py)
- **Sidebar**: Add "Claude API Key" input field.
- **Remix Station**:
    - Replace the "Copy Prompt" text area with a **" ✨ Magic Remix"** button.
    - Show the *Result* in a text area (editable).

### Dependencies
- Install `anthropic` library.

## Verification Plan
### Automated Tests
- `tests/test_remix.py`: Mock the API call to verify prompt construction and response handling.

### Manual Verification
- Input API Key.
- Click "Magic Remix".
- Verify the output sounds like Rahul (uses em dashes, "so...", "then...", no corporate buzzwords).
