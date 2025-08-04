import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/business.manage']

def authenticate():
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=8080)
    return creds

def get_accounts_and_locations(creds):
    account_mgmt = build('mybusinessaccountmanagement', 'v1', credentials=creds)
    accounts = account_mgmt.accounts().list().execute()
    account_name = accounts['accounts'][0]['name']  # e.g., "accounts/123456789"

    info_service = build('mybusinessbusinessinformation', 'v1', credentials=creds)
    locations = info_service.accounts().locations().list(parent=account_name).execute().get('locations', [])

    return account_name, locations

def post_to_location(creds, account_name, location_id, message):
    post_service = build('mybusiness', 'v4', credentials=creds)
    post_body = {
        "languageCode": "en",
        "summary": message,
        "callToAction": {
            "actionType": "LEARN_MORE",
            "url": "https://your-website.com"  # Optional: Change to your target link
        }
    }

    try:
        post_service.accounts().locations().localPosts().create(
            parent=f"{account_name}/locations/{location_id}",
            body=post_body
        ).execute()
        print(f"[✓] Posted to: {account_name}/locations/{location_id}")
    except Exception as e:
        print(f"[!] Failed to post to {location_id}: {e}")

def main():
    creds = authenticate()

    message = input("\nEnter the update message to post: ").strip()
    if not message:
        print("[!] Message cannot be empty.")
        return

    account_name, locations = get_accounts_and_locations(creds)

    if not locations:
        print("[!] No business profiles found.")
        return

    print("\n[+] Found the following locations:")
    for idx, loc in enumerate(locations):
        loc_id = loc['name'].split('/')[-1]
        loc_title = loc.get('locationName', 'Unnamed Location')
        print(f"{idx + 1}. {loc_title} (ID: {loc_id})")

    print("\n0. Post to ALL locations")

    try:
        choice = int(input("Choose a location number or 0 to post to all: "))
    except ValueError:
        print("[!] Invalid input. Enter a number.")
        return

    if choice == 0:
        for loc in locations:
            loc_id = loc['name'].split('/')[-1]
            post_to_location(creds, account_name, loc_id, message)
    elif 1 <= choice <= len(locations):
        loc_id = locations[choice - 1]['name'].split('/')[-1]
        post_to_location(creds, account_name, loc_id, message)
    else:
        print("[!] Invalid selection.")

if __name__ == '__main__':
    main()
