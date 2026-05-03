from langchain.tools import tool


def extract_section(text, section_name):
    lines = text.splitlines()
    capture = False
    section_lines = []

    for line in lines:
        stripped = line.strip()

        if stripped.lower().startswith(section_name.lower() + ":"):
            capture = True
            value = stripped[len(section_name) + 1:].strip()
            if value:
                section_lines.append(value)
            continue

        if capture:
            if (
                stripped.lower().startswith("hook:")
                or stripped.lower().startswith("caption:")
                or stripped.lower().startswith("hashtags:")
                or stripped.lower().startswith("call to action:")
                or stripped.lower().startswith("subject line:")
                or stripped.lower().startswith("body:")
            ):
                break
            section_lines.append(stripped)

    return " ".join(section_lines).strip()


def remove_flagged_phrases(text, flagged_list):
    cleaned_text = text
    for item in flagged_list:
        cleaned_text = cleaned_text.replace(item, "")
        cleaned_text = cleaned_text.replace(item.capitalize(), "")
        cleaned_text = cleaned_text.replace(item.title(), "")
    return " ".join(cleaned_text.split())


@tool
def brand_safety_checker(draft_content: str) -> str:
    """
    Use this tool to review marketing content for off-brand tone, risky wording,
    and unsupported claims before returning a final answer.
    This tool checks restricted phrases and some off-brand wording.
    """
    print("The agent is using brand_safety_checker tool")

    with open("tool_files/restricted_phrases.txt", "r", encoding="utf-8") as f:
        restricted_phrases = f.read()

    content_lower = draft_content.lower()
    flagged_items = []
    tone_warnings = []

    restricted_list = restricted_phrases.splitlines()
    for phrase in restricted_list:
        phrase = phrase.strip()
        if phrase and ":" not in phrase and phrase.lower() in content_lower:
            flagged_items.append(phrase)

    off_brand_words = [
        "crazy",
        "insane",
        "wildest",
        "life-changing",
        "miracle",
        "extreme",
        "perfect for everyone"
    ]

    for word in off_brand_words:
        if word in content_lower:
            tone_warnings.append(word)

    if len(flagged_items) == 0 and len(tone_warnings) == 0:
        result = "Brand Safety Check: Passed. No restricted phrases or major off-brand wording found."
        print(result)
        return result

    result_parts = []

    if len(flagged_items) > 0:
        result_parts.append("Restricted wording found -> " + ", ".join(flagged_items))

    if len(tone_warnings) > 0:
        result_parts.append("Off-brand tone wording found -> " + ", ".join(tone_warnings))

    result = "Brand Safety Check: Warning. " + " | ".join(result_parts)
    print(result)
    return result


@tool
def platform_formatter(platform: str, draft_content: str) -> str:
    """
    Use this tool to format marketing content for a specific platform.
    This tool adjusts structure, length, and style for Instagram, TikTok, or Email.
    """
    print("The agent is using platform_formatter tool")
    print("Platform selected:", platform)

    platform_lower = platform.lower()

    hook = extract_section(draft_content, "Hook")
    caption = extract_section(draft_content, "Caption")
    hashtags = extract_section(draft_content, "Hashtags")
    cta = extract_section(draft_content, "Call to Action")
    subject_line = extract_section(draft_content, "Subject Line")
    body = extract_section(draft_content, "Body")

    if not caption and body:
        caption = body

    if not body and caption:
        body = caption

    if not hook:
        hook = "Check this out"

    if not cta:
        if "email" in platform_lower:
            cta = "Shop now and learn more."
        else:
            cta = "Grab yours today."

    if "instagram" in platform_lower:
        if not hashtags:
            hashtags = "#VoltRush #CollegeLife #StudyFuel #ZeroSugar"

        hashtag_list = hashtags.split()
        hashtag_list = hashtag_list[:6]
        new_hashtags = " ".join(hashtag_list)

        formatted_content = (
            f"Hook: {hook}\n\n"
            f"Caption: {caption}\n\n"
            f"Hashtags: {new_hashtags}\n\n"
            f"Call to Action: {cta}"
        )

    elif "tiktok" in platform_lower:
        if not hashtags:
            hashtags = "#VoltRush #CampusLife #NewDrop"

        short_caption = caption
        if len(short_caption) > 140:
            short_caption = short_caption[:140].rstrip() + "..."

        hashtag_list = hashtags.split()
        hashtag_list = hashtag_list[:4]
        new_hashtags = " ".join(hashtag_list)

        formatted_content = (
            f"Hook: {hook}\n\n"
            f"Caption: {short_caption}\n\n"
            f"Hashtags: {new_hashtags}\n\n"
            f"Call to Action: {cta}"
        )

    elif "email" in platform_lower:
        if not subject_line:
            subject_line = "Big News From Volt Rush"

        formatted_content = (
            f"Subject Line: {subject_line}\n\n"
            f"Hook: {hook}\n\n"
            f"Body: {body}\n\n"
            f"Call to Action: {cta}"
        )

    else:
        formatted_content = draft_content

    print("Platform formatting complete.")
    return formatted_content


@tool
def claims_checker(draft_content: str) -> str:
    """
    Use this tool to scan marketing content for risky or unsupported claims.
    This tool identifies strong claim language that may need review.
    """
    print("The agent is using claims_checker tool")

    with open("tool_files/risky_claims.txt", "r", encoding="utf-8") as f:
        risky_claims = f.read()

    content_lower = draft_content.lower()
    flagged_claims = []

    claims_list = risky_claims.splitlines()
    for claim in claims_list:
        claim = claim.strip()
        if claim and ":" not in claim and claim.lower() in content_lower:
            flagged_claims.append(claim)

    if len(flagged_claims) == 0:
        result = "Claims Check: Passed. No risky claims found."
        print(result)
        return result

    unique_claims = list(dict.fromkeys(flagged_claims))
    result = "Claims Check: Warning. Risky claim wording found -> " + ", ".join(unique_claims)
    print(result)
    return result