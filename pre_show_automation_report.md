# Automation Feasibility Report: FJHH Pre-Show Workflow

This report analyzes your 8-step pre-show setup process and details how you can transition it from a manual workflow to an automated Python toolchain.

---

## Executive Summary

Almost the entire workflow can be automated using Python. By combining image processing libraries, Google API clients, and the Mailchimp API, we can collapse the first six steps of this workflow into a **single 5-second command line run**.

Here is the automation feasibility matrix for each step:

| Step | Task | Automation Difficulty | Recommended Technology |
|---|---|---|---|
| **1** | Frame Grab from Last Video | **Low** | `ffmpeg-python` |
| **2** | Create Cover Slide | **Low** | Python Pillow (PIL) |
| **3** | Schedule YouTube Stream | **Medium** | Google Live Streaming API |
| **4** | Paste URL into Google Doc | **Low** | Google Docs API |
| **5** | Gmail Schedule (ULC list) | **Medium** | Google Apps Script / Gmail API |
| **6** | Mailchimp Campaign | **Medium** | Mailchimp API v3.0 |
| **7** | Facebook Event & Invites | **High** (Meta Restrictions) | Playwright (Semi-automated) |
| **8** | Schedule Bluesky Post | **Low** | AT Protocol SDK (`atproto`) |

---

## Detailed Step-by-Step Analysis

### Step 1: Still Frame Grab
*   **Current Process**: Open the previous stream's video file, find a good frame, and export it.
*   **Automation Plan**: We can use `ffmpeg` to extract a frame at a specific timestamp (e.g., 20 minutes in, when you are in the middle of a song) or slice a few candidate frames.
*   **Python Code Example**:
    ```python
    import ffmpeg
    # Grab 1 frame at the 25-minute mark
    (
        ffmpeg
        .input('last_show_recording.mp4', ss='00:25:00')
        .output('raw_frame.jpg', vframes=1)
        .run(overwrite_output=True)
    )
    ```

### Step 2: Create Cover Slide (PSD Template replacement)
*   **Current Process**: Combine the frame grab with a Photoshop template, edit text, and export.
*   **Automation Plan**: We can export your Photoshop graphical assets (borders, logos, overlays) once as transparent PNG files. A Python script using the **Pillow** image library can automatically crop the frame grab, place the transparent layout templates over it, and draw the date/episode text using your custom font (`Outfit`).
*   **Python Code Example**:
    ```python
    from PIL import Image, ImageDraw, ImageFont
    
    # 1. Open frame grab and templates
    background = Image.open('raw_frame.jpg').resize((1920, 1080))
    overlay = Image.open('psd_template_overlay.png')
    background.paste(overlay, (0, 0), overlay)
    
    # 2. Draw dynamic text
    draw = ImageDraw.Draw(background)
    font = ImageFont.truetype('Outfit-Bold.ttf', 72)
    draw.text((100, 800), "Episode 304", fill="white", font=font)
    draw.text((100, 900), "July 17, 2026", fill="white", font=font)
    background.save('cover_slide_304.jpg')
    ```

### Steps 3 & 4: Schedule YouTube Stream & Retrieve Link
*   **Current Process**: Schedule upcoming stream via YouTube Studio (reusing settings), upload cover slide, copy URL, and paste it into a Google Doc.
*   **Automation Plan**: We can use the **Google API Client** to interact with the YouTube Live Streaming API.
    1.  `liveBroadcasts.insert`: Creates a new broadcast with your title, description, and target timezone-aware start time.
    2.  `thumbnails.set`: Uploads the programmatically generated cover slide.
    3.  `Google Docs API`: Appends the returned stream watch URL (`https://youtu.be/BROADCAST_ID`) directly to your show notes Google Doc.

### Step 5: Gmail Scheduling (ULC list)
*   **Current Process**: Copy a draft email from Google Docs, schedule in Gmail to send Wednesday morning.
*   **Automation Plan**: The Gmail API allows creating drafts and sending messages, but does not natively support scheduling drafts via the public API (this is an interface-only Gmail feature). 
*   **Solution**: We can use **Google Apps Script** running on a weekly trigger, or a Python script connected to a scheduling service (like cron or GitHub Actions) to send the email directly on Wednesday morning using SMTP or the Gmail API send method.

### Step 6: Mailchimp Campaign Setup
*   **Current Process**: Duplicate the last campaign, change text (date, show number, slug), and schedule for Wednesday morning.
*   **Automation Plan**: The **Mailchimp API v3.0** fully supports duplicating and scheduling campaigns.
    1.  `POST /campaigns/{campaign_id}/action/replicate`: Duplicates the template campaign.
    2.  `PATCH /campaigns/{new_campaign_id}/content`: Injects the new stream URL and slug.
    3.  `POST /campaigns/{new_campaign_id}/action/schedule`: Schedules the email for Wednesday morning.

### Step 7: Facebook Event & Invites
*   **Current Process**: Create Facebook event, fill out metadata, invite suggested friends.
*   **Automation Plan**: Meta's Graph API is heavily restricted for personal profile events due to privacy policies. 
*   **Solution**: We can use a browser automation library like **Playwright** to log in, fill out the event form, and upload the cover slide. Inviting friends must remain manual (or semi-automated) as Facebook strictly limits automated invite scripts to prevent spam flagging.

### Step 8: Bluesky Post Scheduling
*   **Current Process**: Schedule a post for Friday noon with the URL and slug.
*   **Automation Plan**: Bluesky uses the decentralized **AT Protocol API**, which is fully open and has a Python SDK (`atproto`). A lightweight serverless function or cron job can post your update on Friday noon using the SDK.

---

## Recommended Architecture: "FJHH Orchestrator"

We can build a single Python automation script (e.g. `pre_show_setup.py`) that acts as a command-line utility.

### The Proposed Interface:
```bash
python3 pre_show_setup.py --video "last_week.mp4" --show 304 --date "2026-07-17" --slug "Join us for a swing and bossa nova set!"
```

### What this script will do in 5 seconds:
1.  **Extracts** a performance still frame using `ffmpeg`.
2.  **Draws** the cover slide JPEG overlaying the logos and episode text.
3.  **Authenticates** with Google and creates the YouTube live stream scheduled for Friday.
4.  **Uploads** the cover slide to YouTube.
5.  **Appends** the stream URL to your Google Doc.
6.  **Duplicates and schedules** the Mailchimp campaign.
7.  **Saves** the final URL and details to a local configuration file for the Bluesky/Facebook poster scripts.

---

## Next Steps

1.  **Extract Photoshop Assets**: Export the static graphical elements (frame borders, logos, fonts) of your cover slide template as PNGs.
2.  **API Credentials Setup**: We will need to set up credential files for:
    -   Google Cloud Console (for YouTube and Google Docs API).
    -   Mailchimp (API Key).
    -   Bluesky (App Password).
3.  If you would like to proceed, we can start by writing the **Cover Slide Generator** script to automate the image creation first!
