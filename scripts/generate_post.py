"""
HomeFixGuide Auto Post Generator
Generates SEO-optimized home improvement articles using OpenAI GPT API
and commits them to the blog repository.
"""

from openai import OpenAI
import datetime
import os
import random
import re

# High CPC keyword categories for home improvement
TOPIC_POOLS = {
    "diy_projects": [
        "How to Build a DIY Bookshelf for Under $50",
        "{number} Easy DIY Projects to Upgrade Your Home This Weekend",
        "DIY Floating Shelves: A Beginner's Complete Guide",
        "How to Install Crown Molding Like a Pro",
        "DIY Kitchen Backsplash Installation Step by Step",
        "How to Build a Custom Closet Organizer on a Budget",
        "{number} Home Improvement Projects That Add the Most Value in {year}",
    ],
    "plumbing": [
        "How to Fix a Leaky Faucet in {number} Easy Steps",
        "Unclogging a Drain Without Calling a Plumber",
        "How to Replace a Toilet: Complete DIY Guide",
        "Running Toilet Fix: {number} Common Causes and Solutions",
        "How to Install a New Kitchen Faucet Yourself",
        "Water Heater Maintenance Tips Every Homeowner Needs in {year}",
        "How to Fix Low Water Pressure in Your Home",
    ],
    "electrical": [
        "How to Replace a Light Switch Safely",
        "Installing a Ceiling Fan: Step-by-Step Guide for {year}",
        "How to Install Dimmer Switches in Any Room",
        "{number} Electrical Safety Tips Every Homeowner Must Know",
        "How to Replace an Electrical Outlet: Beginner Guide",
        "Smart Home Wiring Basics for Beginners in {year}",
        "How to Install Under-Cabinet LED Lighting",
    ],
    "painting": [
        "How to Paint a Room Like a Pro: Complete Guide",
        "Best Interior Paint Colors for {year}: Top {number} Picks",
        "How to Paint Kitchen Cabinets Without Sanding",
        "Exterior House Painting Tips for a Professional Finish",
        "How to Fix Paint Drips and Brush Marks",
        "{number} Painting Mistakes Beginners Always Make",
        "How to Choose the Right Paint Finish for Every Room",
    ],
    "organization": [
        "{number} Genius Garage Organization Ideas for {year}",
        "How to Organize a Small Closet on a Budget",
        "Kitchen Organization Hacks That Actually Work",
        "How to Declutter Your Home Room by Room",
        "Best Storage Solutions for Small Spaces in {year}",
        "DIY Pantry Organization: {number} Steps to a Perfect Pantry",
        "How to Organize Your Tool Collection Like a Pro",
    ],
    "tools": [
        "Best Power Tools for Beginners: {year} Buying Guide",
        "{number} Essential Tools Every Homeowner Needs",
        "Cordless Drill Buying Guide: How to Choose the Right One",
        "Table Saw vs Miter Saw: Which Do You Need First",
        "How to Maintain Your Power Tools for Longer Life",
        "Best Multi-Tools for Home Repair in {year}",
        "Hand Tools vs Power Tools: When to Use Each",
    ],
    "outdoor": [
        "How to Build a DIY Deck on a Budget",
        "Best Lawn Care Tips for a Green Yard in {year}",
        "How to Install a Paver Patio Step by Step",
        "DIY Fence Installation: Complete Guide for Beginners",
        "{number} Easy Landscaping Ideas to Boost Curb Appeal",
        "How to Build a Raised Garden Bed for Under $30",
        "Pressure Washing Tips: How to Clean Your Home Exterior",
    ],
}

SYSTEM_PROMPT = """You are an expert home improvement writer for a blog called HomeFixGuide.
Write SEO-optimized, informative, and engaging blog posts about DIY projects, home repairs, and improvements.

Rules:
- Write in a friendly, encouraging but knowledgeable tone
- Use short paragraphs (2-3 sentences max)
- Include practical, step-by-step instructions where applicable
- Use headers (##) to break up sections
- Include bullet points and numbered lists where appropriate
- Write between 1200-1800 words
- Naturally include the main keyword 3-5 times
- Include a compelling introduction that hooks the reader
- End with a clear conclusion/call-to-action
- Do NOT include any AI disclaimers or mentions of being AI-generated
- Write as if you are an experienced contractor sharing expertise with homeowners
- Include safety warnings where appropriate
- Mention specific materials, tools, and approximate costs when relevant
- Include time estimates for projects
- Do NOT use markdown title (# Title) - just start with the content
"""


def pick_topic():
    """Select a random topic from the pools."""
    year = datetime.datetime.now().year
    number = random.choice([3, 5, 7, 10, 12, 15])
    category = random.choice(list(TOPIC_POOLS.keys()))
    title_template = random.choice(TOPIC_POOLS[category])
    title = title_template.format(year=year, number=number)
    return title, category


def generate_post_content(title, category):
    """Generate a blog post using OpenAI GPT API."""
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=4000,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Write a comprehensive blog post with the title: \"{title}\"\n\nCategory: {category.replace('_', ' ')}\n\nRemember to write 1200-1800 words, use ## for section headers, and make it SEO-friendly with practical advice.",
            },
        ],
    )

    return response.choices[0].message.content


def slugify(title):
    """Convert title to URL-friendly slug."""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    return slug


def get_repo_root():
    """Get the repository root directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(script_dir)


def get_existing_titles():
    """Get titles of existing posts to avoid duplicates."""
    posts_dir = os.path.join(get_repo_root(), '_posts')
    titles = set()
    if os.path.exists(posts_dir):
        for filename in os.listdir(posts_dir):
            if filename.endswith('.md'):
                title_part = filename[11:-3]
                titles.add(title_part)
    return titles


def create_post():
    """Generate and save a new blog post."""
    existing = get_existing_titles()

    # Try up to 10 times to find a non-duplicate topic
    for _ in range(10):
        title, category = pick_topic()
        slug = slugify(title)
        if slug not in existing:
            break
    else:
        title, category = pick_topic()
        slug = slugify(title) + f"-{random.randint(100, 999)}"

    print(f"Generating post: {title}")
    print(f"Category: {category}")

    content = generate_post_content(title, category)

    # Create the post file
    today = datetime.datetime.now()
    date_str = today.strftime('%Y-%m-%d')
    filename = f"{date_str}-{slug}.md"

    posts_dir = os.path.join(get_repo_root(), '_posts')
    os.makedirs(posts_dir, exist_ok=True)

    filepath = os.path.join(posts_dir, filename)

    # Create frontmatter
    frontmatter = f"""---
layout: post
title: "{title}"
date: {today.strftime('%Y-%m-%d %H:%M:%S')} +0000
categories: [{category.replace('_', '-')}]
description: "{title} - Practical home improvement tips and step-by-step guides for every homeowner."
---

{content}
"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(frontmatter)

    print(f"Post saved: {filepath}")
    return filepath, filename

if __name__ == '__main__':
    # Every 5th post: generate a Gumroad promo post
    from promo_post import should_write_promo, create_promo_post
    if should_write_promo():
        print("Generating promotional post...")
        filepath, filename = create_promo_post()
    else:
        filepath, filename = create_post()
    print(f"Done! Post generated: {filename}")
