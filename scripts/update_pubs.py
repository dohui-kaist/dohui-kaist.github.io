from scholarly import scholarly
import os
import re
from datetime import datetime

# CONFIGURATION
SCHOLAR_ID = "irP5BeAAAAAJ" 
HTML_FILE_PATH = "publications.html"

# ==========================================
# RICH METADATA DICTIONARY
# ==========================================
PUB_DATA = {
    "ARGo: augmented reality-based mobile Go stone collision game": {
        "venue_short": "Virtual Reality",
        "venue_class": "badge-blue",
        "thumb": "paper_placeholder.png",
        "links": [
            {"name": "DOI", "url": "https://link.springer.com/article/10.1007/s10055-023-00919-4"},
            {"name": "Project Website", "url": "#"},
        ]
    }
}
DEFAULT_THUMB = "paper_placeholder.png"

# DEMONSTRATION DATA (will be used to populate the list for testing)
MANUAL_PUBS = [
    {
        "bib": {
            "title": "HapticGen: Generative Haptic Feedback for Virtual Reality",
            "author": "Dohui Lee, Sohyun Won, Jiwon Kim",
            "pub_year": "2024",
            "journal": "CHI Conference on Human Factors in Computing Systems",
        },
        "meta": {
            "venue_short": "CHI",
            "venue_class": "badge-pink",
            "thumb": "paper_placeholder.png",
            "links": [{"name": "PDF", "url": "#"}, {"name": "Video", "url": "#"}]
        }
    },
    {
        "bib": {
            "title": "ARGo: Augmented Reality-based Mobile Go Stone Collision Game",
            "author": "Dohui Lee, Sohyun Won, Jiwon Kim, Hyuk-Yoon Kwon",
            "pub_year": "2024",
            "journal": "Virtual Reality",
        },
        "meta": {
            "venue_short": "Virtual Reality",
            "venue_class": "badge-blue",
            "thumb": "paper_placeholder.png",
            "links": [{"name": "DOI", "url": "#"}]
        }
    },
    {
        "bib": {
            "title": "OmniTouch: Wearable Multitouch Interaction Everywhere",
            "author": "Chris Harrison, Hrvoje Benko, Andy Wilson",
            "pub_year": "2023",
            "journal": "UIST",
        },
        "meta": {
            "venue_short": "UIST",
            "venue_class": "badge-pink",
            "thumb": "paper_placeholder.png",
            "links": [{"name": "Project Page", "url": "#"}]
        }
    }
]

def fetch_publications(author_id):
    print(f"Fetching publications for author ID: {author_id}")
    author = scholarly.search_author_id(author_id)
    scholarly.fill(author, sections=['publications'])
    return author['publications']

def is_domestic(pub):
    bib = pub['bib']
    title = bib.get('title', '')
    venue = bib.get('journal') or bib.get('conference') or bib.get('publisher') or ""
    korean_pattern = re.compile(r'[가-힣]')
    if korean_pattern.search(title) or korean_pattern.search(venue):
        return True
    return False

def get_badge_info(pub):
    """
    Returns (short_name, badge_class)
    """
    bib = pub['bib']
    title = bib.get('title', '')
    venue = bib.get('journal') or bib.get('conference') or bib.get('publisher') or ""
    
    # 1. Check Overrides
    if title in PUB_DATA:
        meta = PUB_DATA[title]
        if "venue_short" in meta:
            return meta["venue_short"], meta.get("venue_class", "badge-gray")

    # 2. Heuristics
    venue_lower = venue.lower()
    
    if 'chi ' in venue_lower and 'conference' in venue_lower:
        return "CHI", "badge-pink"
    if 'uist' in venue_lower:
        return "UIST", "badge-pink"
    if 'cscw' in venue_lower:
        return "CSCW", "badge-pink"
    if 'virtual reality' in venue_lower or 'vr' in venue_lower:
        return "Virtual Reality", "badge-blue"
    if 'imwut' in venue_lower or 'ubicomp' in venue_lower:
        return "IMWUT", "badge-blue"
        
    words = venue.split()
    short_name = " ".join(words[:2]) if words else "Paper"
    return short_name, "badge-gray"

def create_pub_html(pub):
    bib = pub['bib']
    title = bib.get('title', 'Untitled')
    
    # Metadata
    meta = PUB_DATA.get(title, {})
    thumb_path = meta.get("thumb", DEFAULT_THUMB)

    # Authors
    authors = bib.get('author', 'Unknown Author')
    authors = authors.replace("D Lee", "<strong>Dohui Lee</strong>")
    authors = authors.replace("Dohui Lee", "<strong>Dohui Lee</strong>") 

    # Venue Full
    venue_original = bib.get('journal') or bib.get('conference') or bib.get('publisher') or "Preprint"
    year = bib.get('pub_year', '')
    venue_text = f"In {venue_original}" if venue_original else ""
    if year:
        venue_text += f", {year}"

    # Links
    custom_links = meta.get("links", [])
    
    links_html = ""
    if custom_links:
        for link in custom_links:
            links_html += f'<a href="{link["url"]}" class="btn-outline" target="_blank">{link["name"]}</a>\n'
    else:
        url = pub.get('pub_url', '#')
        links_html = f'<a href="{url}" class="btn-outline" target="_blank">PDF</a>'

    # Badge Info
    badge_text, badge_class = get_badge_info(pub)

    return f"""
    <div class="publication-item">
        <!-- Left: Thumbnail + Badge Overlay -->
        <div class="pub-thumbnail">
            <div class="venue-badge {badge_class}">{badge_text}</div>
            <img src="{thumb_path}" alt="{title} thumbnail">
        </div>
        
        <!-- Right: Info -->
        <div class="pub-info">
            <a href="#" class="pub-title">{title}</a>
            <span class="pub-authors">{authors}</span>
            <span class="pub-venue">{venue_text}</span>
            <div class="pub-buttons">
                {links_html}
            </div>
        </div>
    </div>
    """

def generate_html_content(pubs):
    # Sort by year (descending)
    sorted_pubs = sorted(pubs, key=lambda p: int(p['bib'].get('pub_year', 0) or 0), reverse=True)
    
    # Group by Year
    pubs_by_year = {}
    
    # 1. Process Fetched Pubs
    for pub in sorted_pubs:
        scholarly.fill(pub)
        if is_domestic(pub):
            continue
            
        year = pub['bib'].get('pub_year', 'Unknown')
        if year not in pubs_by_year:
            pubs_by_year[year] = []
        pubs_by_year[year].append(pub)

    # 2. Add Manual Pubs (For Demo/Missing items)
    # Note: In production, you might want to deduplicate based on title
    for m_pub in MANUAL_PUBS:
        year = m_pub['bib'].get('pub_year', 'Unknown')
        if year not in pubs_by_year:
            pubs_by_year[year] = []
            
        # Check for duplicates (simple title check)
        is_dup = False
        for existing in pubs_by_year[year]:
            if existing['bib'].get('title') == m_pub['bib']['title']:
                is_dup = True
                break
        if not is_dup:
             # Inject metadata into PUB_DATA momentarily for get_badge_info to work easily if needed,
             # or better, just attach it to the pub object distinctively.
             # But create_pub_html relies on PUB_DATA or the pub object.
             # Let's augment PUB_DATA temporarily for these manual ones.
             PUB_DATA[m_pub['bib']['title']] = m_pub['meta']
             pubs_by_year[year].append(m_pub)
        
    # Generate HTML
    final_output = ""
    
    # Sort years desc
    sorted_years = sorted(pubs_by_year.keys(), reverse=True, key=lambda x: int(x) if str(x).isdigit() else 0)
    
    for year in sorted_years:
        final_output += f'<h2 class="year-header">{year}</h2>\n'
        for pub in pubs_by_year[year]:
            final_output += create_pub_html(pub)
            
    return final_output

def update_html_file(content):
    with open(HTML_FILE_PATH, 'r', encoding='utf-8') as f:
        file_content = f.read()

    start_marker = "<!-- PUBLICATIONS_START -->"
    end_marker = "<!-- PUBLICATIONS_END -->"

    if start_marker not in file_content or end_marker not in file_content:
        print("Markers not found in HTML file.")
        return

    start_index = file_content.find(start_marker) + len(start_marker)
    end_index = file_content.find(end_marker)

    new_file_content = file_content[:start_index] + "\n" + content + "\n" + file_content[end_index:]

    with open(HTML_FILE_PATH, 'w', encoding='utf-8') as f:
        f.write(new_file_content)
    print("Updated publications.html")

if __name__ == "__main__":
    try:
        pubs = fetch_publications(SCHOLAR_ID)
        html_snippet = generate_html_content(pubs)
        update_html_file(html_snippet)
    except Exception as e:
        print(f"An error occurred: {e}")
