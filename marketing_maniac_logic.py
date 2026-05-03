from openai import OpenAI
import os
from dotenv import load_dotenv
from marketing_tools import brand_safety_checker, platform_formatter, claims_checker

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY", "").replace("Bearer ", "").strip()
os.environ["OPENAI_API_KEY"] = api_key

client = OpenAI(api_key=api_key)

MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """
You are Marketing Maniac, an AI marketing assistant.

Your job is to help small businesses, student entrepreneurs, and social media managers create marketing content.
You help with captions, hooks, hashtags, calls to action, and simple campaign ideas.

How you should respond:
- Be creative, clear, and helpful
- Keep responses concise and easy to use
- Match the user's requested platform when possible
- Avoid unsupported claims
- Avoid sounding too generic
- Do not overuse emojis
- Only use emojis if the user asks for them or if they fit naturally
- Format marketing content in a clean way that is easy to copy

Platform response rules:
- For Instagram and TikTok, format the response with:
  Hook:
  Caption:
  Hashtags:
  Call to Action:

- For Email, format the response with:
  Subject Line:
  Hook:
  Body:
  Call to Action:

If the user asks for only one specific thing, then only give that part.
"""

def initialize_messages():
    return [{"role": "system", "content": SYSTEM_PROMPT}]

def detect_platform(user_prompt):
    prompt_lower = user_prompt.lower()

    if "instagram" in prompt_lower:
        return "Instagram"
    elif "tiktok" in prompt_lower:
        return "TikTok"
    elif "email" in prompt_lower:
        return "Email"
    else:
        return "General"

def get_platform_instructions(user_prompt):
    prompt_lower = user_prompt.lower()

    if "instagram" in prompt_lower:
        return """
Format for Instagram:
- Make the caption polished and engaging
- Include 4 to 8 relevant hashtags
- Include a strong call to action
- Keep it visually clean and easy to post
- Use this exact structure:
Hook:
Caption:
Hashtags:
Call to Action:
"""
    elif "tiktok" in prompt_lower:
        return """
Format for TikTok:
- Make the hook short and attention-grabbing
- Keep the tone more casual and energetic
- Keep the caption shorter than Instagram
- Include only a few hashtags
- Make it sound natural for short-form content
- Use this exact structure:
Hook:
Caption:
Hashtags:
Call to Action:
"""
    elif "email" in prompt_lower:
        return """
Format for Email:
- Make the tone more professional
- Write a subject line
- Write a short hook
- Write a clear body paragraph
- Do not include hashtags
- End with a strong call to action
- Use this exact structure:
Subject Line:
Hook:
Body:
Call to Action:
"""
    else:
        return """
Use the best format based on the user's request.
"""

def get_response(messages):
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages
    )
    return response.choices[0].message.content

def chat_with_scout(user_prompt, messages):
    platform = detect_platform(user_prompt)
    platform_instructions = get_platform_instructions(user_prompt)

    messages.append({"role": "user", "content": user_prompt})

    temp_messages = messages.copy()
    temp_messages[-1] = {
        "role": "user",
        "content": user_prompt + "\n\n" + platform_instructions
    }

    assistant_reply = get_response(temp_messages)

    formatted_reply = platform_formatter.invoke({
        "platform": platform,
        "draft_content": assistant_reply
    })

    safety_result = brand_safety_checker.invoke({
        "draft_content": formatted_reply
    })

    claims_result = claims_checker.invoke({
        "draft_content": formatted_reply
    })

    cleaned_reply = formatted_reply
    was_revised = False

    replacements = {
        "guaranteed energy boost": "great energy for busy days",
        "guarantees an energy boost": "delivers great energy for busy days",
        "guarantees energy": "delivers strong energy",
        "instant focus": "a focused, ready-to-go feeling",
        "guaranteed focus": "strong focus for busy days",
        "no crash guaranteed": "made for smooth, easy enjoyment",
        "guaranteed": "reliable",
        "guarantees": "delivers",
        "instant": "quick",
        "instantly": "quickly",
        "cures": "helps with",
        "clinically tested": "carefully developed",
        "scientifically proven": "designed for busy students",
        "medically proven": "made for everyday routines",
        "doctor approved": "made with students in mind",
        "medical-grade": "high-quality",
        "works immediately": "works well for busy days",
        "best on the market": "a strong option for students"
    }

    if "Warning" in safety_result or "Warning" in claims_result:
        for old_text, new_text in replacements.items():
            if old_text in cleaned_reply.lower():
                was_revised = True

            cleaned_reply = cleaned_reply.replace(old_text, new_text)
            cleaned_reply = cleaned_reply.replace(old_text.title(), new_text)
            cleaned_reply = cleaned_reply.replace(old_text.capitalize(), new_text)
            cleaned_reply = cleaned_reply.replace(old_text.upper(), new_text.upper())

    final_reply = cleaned_reply + "\n\nReview Results:\n"

    if was_revised:
        final_reply += "Initial review found risky wording. Content was revised for a safer final version.\n"
    else:
        final_reply += "No major safety issues were found.\n"

    final_reply += safety_result + "\n" + claims_result

    messages.append({"role": "assistant", "content": final_reply})

    return final_reply, messages