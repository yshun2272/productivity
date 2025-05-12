# File Organizer for Pictures & Videos

A simple yet powerful system to organize pictures and videos using markdown files and Stream Deck buttons.

## Overview

This project provides two separate scripts:

1. **Picture Organizer** - Organizes numbered JPG files using a markdown table
2. **Video Organizer** - Organizes numbered MP4 files using a markdown table

Both scripts read from markdown files to rename files, add metadata, and sort them into folders - all with the press of a button on your Stream Deck.

## Features

- **Simple Numeric File Handling**: Works with simple numbered files (1.jpg, 2.jpg, 3.mp4, etc.)
- **Flexible File Number Formats**: Handles simple numbers ("1"), numbers with leading zeros ("01"), or numbers with extensions ("1.jpg")
- **Metadata Addition**: Adds date and tags to your files using ExifTool
- **Folder Organization**: Creates folders based on "Area" and moves files accordingly
- **Error Tracking**: Provides detailed error information for any files that couldn't be processed
- **Case-Insensitive Headers**: Works with any capitalization in column headers
- **Tag Organization**: Uses semicolon-separated tags for better readability

## Required Files

### For Pictures (`C:\Users\yshun\OneDrive\Pictures`)

1. `organize_pictures.py` - Python script for organizing pictures
2. `organize_pictures.bat` - Batch file to run from Stream Deck
3. `pictures.md` - Markdown file listing pictures to organize

### For Videos (`C:\Users\yshun\OneDrive\Videos`)

1. `organize_videos.py` - Python script for organizing videos
2. `organize_videos.bat` - Batch file to run from Stream Deck
3. `videos.md` - Markdown file listing videos to organize

## Markdown File Format

Your markdown files should follow this format:

```markdown
| Current File Name | Suggested File Name | Date | Tags | Area |
|-------------------|---------------------|------|------|------|
| 1 | Beach sunset | 2025-05-01 | vacation; beach | Hawaii Trip |
| 2 | Family dinner | 2025-05-02 | family; dinner | Hawaii Trip |
```

## How to Use

1. **Set Up Your Files**:
   - Place the Python and batch files in their respective folders
   - Create and update your markdown files with file information

2. **Configure Stream Deck**:
   - Set up one button to run `organize_pictures.bat`
   - Set up another button to run `organize_videos.bat`

3. **Organize Files**:
   - Press the appropriate Stream Deck button
   - The script will process files according to your markdown file
   - Errors will be reported on screen and in an error log file

## Requirements

- Python 3.x
- ExifTool (must be installed and in your PATH)
- Stream Deck (optional, but recommended for one-button operation)

## Error Handling

If errors occur during processing:
- A summary will be displayed on screen
- Details will be saved to `picture_errors.txt` or `video_errors.txt`
- This makes it easy to identify and fix any problems

## Tips

- You can run the scripts manually without Stream Deck by double-clicking the batch files
- Update your markdown files regularly as you add new files to organize
- Check the log files for detailed processing information
- The "Date" and "Tags" columns are optional
