# WhatsApp Group Contact Extractor

This script extracts contact information from WhatsApp groups using Selenium and WhatsApp Web.

## Features

- Extracts participant names, phone numbers, and admin status from WhatsApp groups
- Uses persistent Chrome session to avoid scanning QR code repeatedly
- Mimics human behavior with random delays and smooth scrolling
- Displays results in a clean table format
- Handles multiple groups from a CSV file

## Requirements

- Python 3.7+
- Chrome browser installed
- Required Python packages (install using `pip install -r requirements.txt`):
  - selenium
  - webdriver-manager
  - prettytable
  - pandas

## Setup

1. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `group.csv` file with one group name per line:
   ```
   Group Name 1
   Group Name 2
   ```

## Usage

1. Run the script:
   ```bash
   python whatsapp_contact_extractor.py
   ```

2. On first run, scan the QR code when prompted
3. The script will process each group in the CSV file and display the results

## Notes

- The script creates a `chrome_profile` directory to maintain the session
- Make sure the group names in `group.csv` exactly match the WhatsApp group names
- The script includes random delays to mimic human behavior
- Phone numbers may not be available for all participants

## Error Handling

The script includes comprehensive error handling for:
- Missing elements
- Timeout errors
- Missing group names
- Network issues

## Security

- Never share your `chrome_profile` directory as it contains your WhatsApp session
- The script does not store any extracted data permanently
