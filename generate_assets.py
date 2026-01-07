#!/usr/bin/env python3
"""
Script to generate PNG assets for the British Days application.
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_background(width, height, filename):
    """Create background image."""
    img = Image.new('RGB', (width, height), color='#2C3E50')
    draw = ImageDraw.Draw(img)
    
    # Add Union Jack inspired stripes
    draw.rectangle([0, 0, width, 50], fill='#C8102E')
    draw.rectangle([0, height-50, width, height], fill='#012169')
    
    img.save(filename)
    print(f"Created {filename}")

def create_button(width, height, text, filename, bg_color='#3498DB', text_color='white'):
    """Create button image."""
    img = Image.new('RGBA', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Add border
    draw.rectangle([0, 0, width-1, height-1], outline='#2C3E50', width=2)
    
    # Add text
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
    except:
        font = ImageFont.load_default()
    
    # Calculate text position (center)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    draw.text((x, y), text, fill=text_color, font=font)
    
    img.save(filename)
    print(f"Created {filename}")

def create_panel(width, height, filename, color='#ECF0F1'):
    """Create panel background."""
    img = Image.new('RGBA', (width, height), color=color)
    draw = ImageDraw.Draw(img)
    
    # Add subtle border
    draw.rectangle([0, 0, width-1, height-1], outline='#BDC3C7', width=1)
    
    img.save(filename)
    print(f"Created {filename}")

def create_logo(size, filename):
    """Create a simple logo."""
    img = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw Union Jack inspired design
    # Blue background
    draw.rectangle([0, 0, size, size], fill='#012169')
    
    # White cross
    draw.rectangle([size//2-10, 0, size//2+10, size], fill='white')
    draw.rectangle([0, size//2-10, size, size//2+10], fill='white')
    
    # Red cross
    draw.rectangle([size//2-5, 0, size//2+5, size], fill='#C8102E')
    draw.rectangle([0, size//2-5, size, size//2+5], fill='#C8102E')
    
    img.save(filename)
    print(f"Created {filename}")

if __name__ == '__main__':
    assets_dir = 'assets'
    os.makedirs(assets_dir, exist_ok=True)
    
    # Create assets
    create_background(800, 600, f'{assets_dir}/background.png')
    create_button(150, 50, 'Search', f'{assets_dir}/btn_search.png', '#27AE60')
    create_button(150, 50, 'Refresh', f'{assets_dir}/btn_refresh.png', '#3498DB')
    create_button(150, 50, 'Exit', f'{assets_dir}/btn_exit.png', '#E74C3C')
    create_panel(700, 400, f'{assets_dir}/panel_main.png')
    create_logo(100, f'{assets_dir}/logo.png')
    
    print("\nAll PNG assets created successfully!")
