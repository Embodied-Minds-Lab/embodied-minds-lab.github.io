#!/usr/bin/env python3
"""
Scraper to extract publication data from Yilun Du's website
"""
import requests
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urljoin
import re
from pathlib import Path

def clean_filename(filename):
    """Clean filename to be filesystem safe"""
    return re.sub(r'[^\w\-_.]', '_', filename)

def scrape_publications():
    url = "https://yilundu.github.io/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    publications = []
    
    # Find all publication entries - they are in a specific structure
    # Each publication is typically in a row with an image on the left and text on the right
    # Let's look for the pattern more carefully
    
    # Strategy: Find all h5 elements (publication titles) and work from there
    pub_headers = soup.find_all('h5')
    
    for idx, header in enumerate(pub_headers):
        try:
            # Get title
            title = header.get_text(strip=True)
            
            # Skip if this is not a publication (e.g., section headers)
            if title in ['News', 'Research Highlights', 'Publications']:
                continue
            
            # Get the next sibling which should be h6 with authors
            authors_elem = header.find_next_sibling('h6')
            authors = []
            if authors_elem:
                authors_text = authors_elem.get_text(strip=True)
                # Split by comma and clean up
                authors = [a.strip() for a in authors_text.split(',')]
            
            # Get links (Website, Paper, Code, etc.)
            links = {}
            links_elem = header.find_next_sibling('p')
            if links_elem:
                for link in links_elem.find_all('a'):
                    link_text = link.get_text(strip=True)
                    link_url = link.get('href', '')
                    links[link_text.lower().replace(' ', '_').replace('/', '_')] = link_url
            
            # Get venue and year from the first paragraph
            venue_elem = header.find_next('p')
            venue = ""
            year = 2024  # default
            
            if venue_elem:
                venue_text = venue_elem.get_text(strip=True)
                # Try to extract year
                year_match = re.search(r'(20\d{2})', venue_text)
                if year_match:
                    year = int(year_match.group(1))
                # Venue is the text before links
                venue = venue_text.split('/')[0].strip() if '/' in venue_text else venue_text
            
            # Find associated image - look in the parent container
            # Publications are typically in a structure where image and text are siblings
            image_url = None
            
            # Try to find parent container (often a row/column structure)
            parent = header.find_parent()
            if parent:
                # Look for img in the parent or previous siblings
                img = parent.find('img')
                if img and img.get('src'):
                    image_url = urljoin(url, img['src'])
                else:
                    # Try looking in previous sibling of parent
                    prev_sibling = parent.find_previous_sibling()
                    if prev_sibling:
                        img = prev_sibling.find('img')
                        if img and img.get('src'):
                            image_url = urljoin(url, img['src'])
            
            # If still no image, try looking for the nearest preceding image
            if not image_url:
                # Walk backwards through elements to find an image
                current = header
                for _ in range(10):  # Look at most 10 elements back
                    current = current.find_previous()
                    if not current:
                        break
                    if current.name == 'img' and current.get('src'):
                        image_url = urljoin(url, current['src'])
                        break
                    img = current.find('img')
                    if img and img.get('src'):
                        image_url = urljoin(url, img['src'])
                        break
            
            pub_data = {
                'title': title,
                'authors': authors,
                'venue': venue,
                'year': year,
                'links': links,
                'image_url': image_url,
                'id': f"pub_{idx:03d}"
            }
            
            publications.append(pub_data)
            
        except Exception as e:
            print(f"Error processing publication {idx}: {e}")
            continue
    
    return publications

def download_images(publications, output_dir="public/publications"):
    """Download publication images"""
    os.makedirs(output_dir, exist_ok=True)
    
    for pub in publications:
        if pub.get('image_url'):
            try:
                img_response = requests.get(pub['image_url'], timeout=10)
                if img_response.status_code == 200:
                    # Get extension from URL
                    ext = pub['image_url'].split('.')[-1].split('?')[0]
                    if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                        ext = 'jpg'
                    
                    filename = f"{pub['id']}.{ext}"
                    filepath = os.path.join(output_dir, filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(img_response.content)
                    
                    # Update pub data with local path
                    pub['image'] = f"/publications/{filename}"
                    print(f"Downloaded image for: {pub['title'][:50]}...")
            except Exception as e:
                print(f"Error downloading image for {pub['title']}: {e}")

def create_markdown_files(publications, output_dir="src/content/publications/en"):
    """Create markdown files for each publication"""
    os.makedirs(output_dir, exist_ok=True)
    
    for pub in publications:
        # Create safe filename from id
        filename = f"{pub['id']}.md"
        filepath = os.path.join(output_dir, filename)
        
        # Build frontmatter
        frontmatter = f"""---
title: "{pub['title'].replace('"', '\\"')}"
authors:
{chr(10).join(f'  - "{author}"' for author in pub['authors'])}
venue: "{pub['venue']}"
year: {pub['year']}
image: "{pub.get('image', '')}"
"""
        
        # Add links if available
        if pub['links']:
            if pub['links'].get('paper'):
                frontmatter += f'paper: "{pub["links"]["paper"]}"\n'
            if pub['links'].get('website') or pub['links'].get('project_page'):
                website = pub['links'].get('website') or pub['links'].get('project_page')
                frontmatter += f'website: "{website}"\n'
            if pub['links'].get('code'):
                frontmatter += f'code: "{pub["links"]["code"]}"\n'
        
        frontmatter += "draft: false\n---\n\n"
        
        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(frontmatter)
        
        print(f"Created: {filename}")

def main():
    print("Scraping publications from https://yilundu.github.io/...")
    publications = scrape_publications()
    print(f"Found {len(publications)} publications")
    
    # Save raw data as JSON for reference
    with open('publications_data.json', 'w', encoding='utf-8') as f:
        json.dump(publications, f, indent=2, ensure_ascii=False)
    print("Saved raw data to publications_data.json")
    
    # Download images
    print("\nDownloading images...")
    download_images(publications)
    
    # Create markdown files
    print("\nCreating markdown files...")
    create_markdown_files(publications)
    
    print("\nDone!")

if __name__ == "__main__":
    main()

