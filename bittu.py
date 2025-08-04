import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Google Business API scope
SCOPES = ['https://www.googleapis.com/auth/business.manage']

def authenticate():
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=8080)
    return creds

def get_accounts_and_locations(creds):
    account_mgmt = build('mybusinessaccountmanagement', 'v1', credentials=creds)
    accounts = account_mgmt.accounts().list().execute()
    account_name = accounts['accounts'][0]['name']

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
            "url": "https://your-website.com"
        }
    }

    try:
        post_service.accounts().locations().localPosts().create(
            parent=f"{account_name}/locations/{location_id}",
            body=post_body
        ).execute()
        print(f"[✓] Posted to: {account_name}/locations/{location_id}")
    except Exception as e:
        print(f"[!] Error posting to {location_id}: {e}")

def main():
    creds = authenticate()

    # Get update text
    message = input("Enter the update message to post: ")

    # Fetch accounts & locations
    account_name, locations = get_accounts_and_locations(creds)

    if not locations:
        print("[!] No business profiles found.")
        return

    print("\n[+] Found the following locations:")
    for idx, loc in enume
