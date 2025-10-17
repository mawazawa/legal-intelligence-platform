#!/usr/bin/env python3
"""
Email Contact Extractor Script
Extracts contact information from .mbox email files and creates a CSV file.
"""

import os
import re
import csv
import mailbox
from collections import defaultdict
from typing import Dict, Set, List, Tuple

def extract_phone_numbers(text: str) -> List[str]:
    """Extract phone numbers from text using various patterns."""
    phone_patterns = [
        r'\((\d{3})\)\s*(\d{3})-(\d{4})',  # (123) 456-7890
        r'(\d{3})-(\d{3})-(\d{4})',        # 123-456-7890
        r'(\d{3})\.(\d{3})\.(\d{4})',      # 123.456.7890
        r'(\d{3})\s+(\d{3})\s+(\d{4})',   # 123 456 7890
        r'1-(\d{3})-(\d{3})-(\d{4})',     # 1-123-456-7890
    ]
    
    phones = []
    for pattern in phone_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if len(match) == 3:
                phone = f"{match[0]}-{match[1]}-{match[2]}"
                phones.append(phone)
    return phones

def extract_role_from_signature(text: str) -> str:
    """Extract role/title from email signature."""
    role_patterns = [
        r'(Attorney|Lawyer|Partner|Associate|Counsel)',
        r'(CPA|Accountant)',
        r'(Manager|Director|CEO|President)',
        r'(Listing Partner)',
    ]
    
    for pattern in role_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return "N/A"

def parse_mbox_file(filepath: str) -> Dict[str, Dict]:
    """Parse a single .mbox file and extract contact information."""
    contacts = {}
    
    try:
        mbox = mailbox.mbox(filepath)
        for message in mbox:
            # Extract sender information
            from_header = message.get('From', '')
            if not from_header:
                continue
                
            # Parse name and email
            name_match = re.match(r'^(.+?)\s*<(.+?)>$', from_header)
            if name_match:
                name = name_match.group(1).strip().strip('"')
                email = name_match.group(2).strip()
            else:
                # Try to extract email from the header
                email_match = re.search(r'<(.+?)>', from_header)
                if email_match:
                    email = email_match.group(1)
                    name = from_header.replace(f'<{email}>', '').strip().strip('"')
                else:
                    continue
            
            # Skip system emails and no-reply addresses
            if any(skip in email.lower() for skip in ['noreply', 'no-reply', 'donotreply', 'no_reply']):
                continue
                
            # Extract phone numbers from message body
            body = ""
            if message.is_multipart():
                for part in message.walk():
                    if part.get_content_type() == "text/plain":
                        body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
            else:
                body = message.get_payload(decode=True).decode('utf-8', errors='ignore')
            
            phones = extract_phone_numbers(body)
            role = extract_role_from_signature(body)
            
            # Store contact information
            if email not in contacts:
                contacts[email] = {
                    'name': name,
                    'email': email,
                    'phones': set(phones),
                    'role': role
                }
            else:
                # Merge phone numbers
                contacts[email]['phones'].update(phones)
                # Update role if we found a better one
                if role != "N/A" and contacts[email]['role'] == "N/A":
                    contacts[email]['role'] = role
                    
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
    
    return contacts

def main():
    """Main function to extract contacts from all .mbox files."""
    takeout_dir = "/Users/mathieuwauters/Downloads/Takeout/Mail"
    output_file = "/Users/mathieuwauters/Downloads/legal-intelligence-platform/persons-log.csv"
    
    all_contacts = {}
    
    # Process all .mbox files
    for filename in os.listdir(takeout_dir):
        if filename.endswith('.mbox'):
            filepath = os.path.join(takeout_dir, filename)
            print(f"Processing {filename}...")
            contacts = parse_mbox_file(filepath)
            all_contacts.update(contacts)
    
    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Name', 'Email', 'Phone', 'Role'])
        
        # Sort contacts by name
        sorted_contacts = sorted(all_contacts.items(), key=lambda x: x[1]['name'])
        
        for email, contact in sorted_contacts:
            phone = ', '.join(contact['phones']) if contact['phones'] else 'N/A'
            writer.writerow([
                contact['name'],
                contact['email'],
                phone,
                contact['role']
            ])
    
    print(f"Extracted {len(all_contacts)} unique contacts to {output_file}")

if __name__ == "__main__":
    main()
