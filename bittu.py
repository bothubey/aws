import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/contacts.readonly',
    'https://www.googleapis.com/auth/contacts.other.readonly',
    'https://www.googleapis.com/auth/contacts'
]

def authenticate():
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_console()
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def get_all_contacts(service):
    results = service.people().connections().list(
        resourceName='people/me',
        pageSize=1000,
        personFields='names,emailAddresses,phoneNumbers,metadata'
    ).execute()
    return results.get('connections', [])

def print_contact_summary(contacts):
    for idx, person in enumerate(contacts):
        names = person.get('names', [])
        name = names[0]['displayName'] if names else "No Name"
        email = person.get('emailAddresses', [{}])[0].get('value', 'No Email')
        phone = person.get('phoneNumbers', [{}])[0].get('value', 'No Phone')
        print(f"[{idx}] Name: {name} | Email: {email} | Phone: {phone}")

def update_contact(service, resource_name, update_text):
    contact_data = service.people().get(resourceName=resource_name, personFields="biographies").execute()
    contact_data['biographies'] = [{
        'value': update_text,
        'contentType': 'TEXT_PLAIN'
    }]
    service.people().updateContact(
        resourceName=resource_name,
        updatePersonFields='biographies',
        body=contact_data
    ).execute()

def main():
    creds = authenticate()
    service = build('people', 'v1', credentials=creds)

    print("\nFetching your contacts...\n")
    contacts = get_all_contacts(service)

    if not contacts:
        print("No contacts found.")
        return

    print_contact_summary(contacts)

    choice = input("\nDo you want to update [1] a specific contact or [2] all contacts? (1/2): ").strip()
    update_text = input("Enter the text to add/update in the contact note: ").strip()

    if choice == "1":
        try:
            selected_index = int(input("Enter the contact index number to update: ").strip())
            person = contacts[selected_index]
            update_contact(service, person['resourceName'], update_text)
            print(f"✅ Contact [{selected_index}] updated successfully.")
        except (IndexError, ValueError):
            print("❌ Invalid index. Aborting.")
    elif choice == "2":
        for idx, person in enumerate(contacts):
            try:
                update_contact(service, person['resourceName'], update_text)
                print(f"✅ Contact [{idx}] updated.")
            except Exception as e:
                print(f"⚠️ Failed to update contact [{idx}]: {e}")
    else:
        print("❌ Invalid choice.")

if __name__ == '__main__':
    main()
