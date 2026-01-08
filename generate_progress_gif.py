#!/usr/bin/env python3
"""
Script to generate an animated progress.gif for the British Days application.
Creates a spinning circular progress indicator.
"""
from PIL import Image, ImageDraw
import math
import os
import sys


def create_progress_gif(filename='assets/progress.gif', size=64, frames=20, duration=50):
    """
    Create an animated progress GIF.
    
    Args:
        filename: Output filename
        size: Size of the GIF (width and height in pixels)
        frames: Number of animation frames
        duration: Duration of each frame in milliseconds
    """
    images = []
    center = size // 2
    radius = size // 3
    
    for i in range(frames):
        # Create new image with transparent background
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw background circle (light)
        draw.ellipse(
            [center - radius, center - radius, center + radius, center + radius],
            outline='#BDC3C7',
            width=4
        )
        
        # Calculate arc angle for this frame
        angle = (360 / frames) * i
        
        # Draw animated arc (colored)
        # Note: PIL's arc method uses degrees
        start_angle = angle - 90  # Start from top
        end_angle = start_angle + 270  # 3/4 circle
        
        draw.arc(
            [center - radius, center - radius, center + radius, center + radius],
            start=start_angle,
            end=end_angle,
            fill='#3498DB',
            width=5
        )
        
        # Add center dot
        dot_radius = 4
        draw.ellipse(
            [center - dot_radius, center - dot_radius, 
             center + dot_radius, center + dot_radius],
            fill='#3498DB'
        )
        
        images.append(img)
    
    # Save as animated GIF
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    images[0].save(
        filename,
        save_all=True,
        append_images=images[1:],
        duration=duration,
        loop=0,  # Infinite loop
        transparency=0,
        disposal=2
    )
    
    print(f"✓ Created {filename}")
    print(f"  Size: {size}x{size} pixels")
    print(f"  Frames: {frames}")
    print(f"  Frame duration: {duration}ms")
    print(f"  Total animation time: {frames * duration}ms")


def create_spinning_loading_gif(filename='assets/progress.gif', size=64, frames=12, duration=80):
    """
    Create a spinning loading indicator (like a spinner).
    """
    images = []
    center = size // 2
    
    for i in range(frames):
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw multiple dots in a circle
        num_dots = 8
        dot_radius = size // 8
        circle_radius = size // 3
        
        for j in range(num_dots):
            angle = (360 / num_dots) * j + (360 / frames) * i
            angle_rad = math.radians(angle)
            
            # Calculate dot position
            x = center + circle_radius * math.cos(angle_rad)
            y = center + circle_radius * math.sin(angle_rad)
            
            # Calculate opacity based on position (leading dots are brighter)
            opacity = int(255 * (j / num_dots))
            color = (52, 152, 219, opacity)  # Blue with varying alpha
            
            # Draw dot
            draw.ellipse(
                [x - dot_radius, y - dot_radius, x + dot_radius, y + dot_radius],
                fill=color
            )
        
        images.append(img)
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    images[0].save(
        filename,
        save_all=True,
        append_images=images[1:],
        duration=duration,
        loop=0,
        transparency=0,
        disposal=2
    )
    
    print(f"✓ Created spinning loader {filename}")


def create_bouncing_dots_gif(filename='assets/progress.gif', size=64, frames=30, duration=60):
    """
    Create bouncing dots animation.
    """
    images = []
    center = size // 2
    dot_radius = size // 10
    
    for i in range(frames):
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Three dots
        for dot_idx in range(3):
            # Calculate bounce offset
            phase = (i + dot_idx * frames // 3) % frames
            bounce_height = abs(math.sin(phase * math.pi / frames)) * (size // 4)
            
            x = center - size // 4 + dot_idx * size // 4
            y = center + size // 4 - bounce_height
            
            color = '#3498DB' if dot_idx == 1 else '#2C3E50'
            
            draw.ellipse(
                [x - dot_radius, y - dot_radius, x + dot_radius, y + dot_radius],
                fill=color
            )
        
        images.append(img)
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    images[0].save(
        filename,
        save_all=True,
        append_images=images[1:],
        duration=duration,
        loop=0,
        transparency=0,
        disposal=2
    )
    
    print(f"✓ Created bouncing dots {filename}")


if __name__ == '__main__':
    print("Generating progress GIF animations...\n")
    
    # Get correct path (works for both script and exe)
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    assets_dir = os.path.join(base_path, 'assets')
    
    # Create assets directory if it doesn't exist
    os.makedirs(assets_dir, exist_ok=True)
    print(f"Assets directory: {assets_dir}\n")
    
    # Option 1: Circular arc progress (default)
    print("1. Circular arc progress indicator:")
    create_progress_gif(os.path.join(assets_dir, 'progress.gif'), size=64, frames=20, duration=50)
    
    print("\n2. Spinning loader (alternative):")
    create_spinning_loading_gif(os.path.join(assets_dir, 'progress_spinner.gif'), size=64, frames=12, duration=80)
    
    print("\n3. Bouncing dots (alternative):")
    create_bouncing_dots_gif(os.path.join(assets_dir, 'progress_dots.gif'), size=64, frames=30, duration=60)
    
    print("\n" + "="*60)
    print("All progress GIF animations created successfully!")
    print("="*60)
    print("\nFiles created in:", assets_dir)
    print("\nTo use a different style, rename the file:")
    print("  - progress.gif (default - circular arc)")
    print("  - progress_spinner.gif (spinning dots)")
    print("  - progress_dots.gif (bouncing dots)")
    print("\nYou can adjust the multiplier in main.py:")
    print("  self.progress_gif_multiplier = 2.0  # Double size")
    print("  self.progress_gif_multiplier = 0.5  # Half size")