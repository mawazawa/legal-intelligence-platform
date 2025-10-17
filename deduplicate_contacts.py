#!/usr/bin/env python3
"""
Contact Deduplication Script
Removes duplicate entries from persons-log.csv, handling cases where the same person has multiple email addresses.
"""

import csv
import re
from collections import defaultdict
from typing import Dict, List, Set

def normalize_name(name: str) -> str:
    """Normalize name for comparison by removing extra spaces and converting to lowercase."""
    return re.sub(r'\s+', ' ', name.strip().lower())

def merge_contact_info(contacts: List[Dict]) -> Dict:
    """Merge multiple contact entries for the same person."""
    merged = {
        'name': contacts[0]['Name'],
        'emails': set(),
        'phones': set(),
        'roles': set()
    }
    
    for contact in contacts:
        if contact['Email'] != 'N/A':
            merged['emails'].add(contact['Email'])
        if contact['Phone'] != 'N/A':
            merged['phones'].add(contact['Phone'])
        if contact['Role'] != 'N/A':
            merged['roles'].add(contact['Role'])
    
    return merged

def deduplicate_contacts(input_file: str, output_file: str):
    """Deduplicate contacts in CSV file."""
    contacts_by_name = defaultdict(list)
    
    # Read the CSV file
    with open(input_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            normalized_name = normalize_name(row['Name'])
            contacts_by_name[normalized_name].append(row)
            print(f"Added: {row['Name']} -> {normalized_name}")
    
    print(f"Total groups: {len(contacts_by_name)}")
    for name, contacts in contacts_by_name.items():
        if len(contacts) > 1:
            print(f"Duplicate found: {name} ({len(contacts)} entries)")
    
    # Process duplicates and merge information
    deduplicated_contacts = []
    
    for normalized_name, contacts in contacts_by_name.items():
        if len(contacts) == 1:
            # No duplicates, keep as is
            contact = contacts[0]
            deduplicated_contacts.append({
                'Name': contact['Name'],
                'Email': contact['Email'],
                'Phone': contact['Phone'],
                'Role': contact['Role']
            })
        else:
            # Multiple entries for same person, merge them
            print(f"Found {len(contacts)} entries for '{contacts[0]['Name']}':")
            for contact in contacts:
                print(f"  - {contact['Email']} | {contact['Phone']} | {contact['Role']}")
            
            merged = merge_contact_info(contacts)
            
            # Create merged entry
            primary_email = contacts[0]['Email'] if contacts[0]['Email'] != 'N/A' else list(merged['emails'])[0] if merged['emails'] else 'N/A'
            primary_phone = contacts[0]['Phone'] if contacts[0]['Phone'] != 'N/A' else list(merged['phones'])[0] if merged['phones'] else 'N/A'
            primary_role = contacts[0]['Role'] if contacts[0]['Role'] != 'N/A' else list(merged['roles'])[0] if merged['roles'] else 'N/A'
            
            # If multiple emails, combine them
            if len(merged['emails']) > 1:
                primary_email = ', '.join(sorted(merged['emails']))
            
            deduplicated_contacts.append({
                'Name': contacts[0]['Name'],
                'Email': primary_email,
                'Phone': primary_phone,
                'Role': primary_role
            })
            print(f"  -> Merged into: {contacts[0]['Name']} | {primary_email} | {primary_phone} | {primary_role}")
            print()
    
    # Sort by name
    deduplicated_contacts.sort(key=lambda x: x['Name'].lower())
    
    # Write deduplicated CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Name', 'Email', 'Phone', 'Role']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(deduplicated_contacts)
    
    print(f"Deduplication complete. {len(deduplicated_contacts)} unique contacts saved to {output_file}")

if __name__ == "__main__":
    input_file = "/Users/mathieuwauters/Downloads/legal-intelligence-platform/persons-log.csv"
    output_file = "/Users/mathieuwauters/Downloads/legal-intelligence-platform/persons-log.csv"
    
    print("Starting contact deduplication...")
    deduplicate_contacts(input_file, output_file)
