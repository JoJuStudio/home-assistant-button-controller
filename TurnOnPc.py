#!/usr/bin/env python3
import requests
import keyring
import argparse
import sys
from urllib.parse import urlparse
from getpass import getpass
from keyring.errors import KeyringLocked

# Constants
SERVICE_NAME = "home_assistant"
BUTTON_PREFIX = "button_"
VALID_STATUS_CODES = range(200, 299)
DEFAULT_TIMEOUT = 10
VERSION = "1.0.0"

def validate_url(url):
    """Validate URL format"""
    parsed = urlparse(url)
    if not (parsed.scheme and parsed.netloc):
        raise ValueError("Invalid URL format")
    return url.strip("/")

def verify_connection(ha_url, token):
    """Test connection to Home Assistant"""
    if not ha_url or not token:
        print("Missing required credentials")
        return False

    try:
        response = requests.get(
            f"{ha_url}/api/",
            headers={"Authorization": f"Bearer {token}"},
            timeout=DEFAULT_TIMEOUT,
            verify=True
        )
        if response.status_code in VALID_STATUS_CODES:
            return True
        print(f"Connection failed (HTTP {response.status_code}): {response.text[:200]}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {str(e)}")
        return False

def list_buttons():
    """List configured buttons using SecretService backend"""
    try:
        import secretstorage
        connection = secretstorage.dbus_init()
        collection = secretstorage.get_default_collection(connection)
        
        if collection.is_locked():
            print("Keyring locked! Unlock through your system keyring manager")
            return []
            
        items = collection.search_items({"service": SERVICE_NAME})
        buttons = []
        
        for item in items:
            try:
                attrs = item.get_attributes()
                username = attrs.get("username", "")
                if username.startswith(BUTTON_PREFIX):
                    buttons.append(username[len(BUTTON_PREFIX):])
            except Exception as e:
                print(f"Error reading item: {str(e)}")
        
        return sorted(buttons)
    
    except ImportError:
        print("Listing requires secretstorage package. Install with:")
        print("pip install secretstorage")
        return []
    except Exception as e:
        print(f"Listing error: {str(e)}")
        return []

def manage_buttons():
    """Handle button configuration"""
    while True:
        try:
            current_buttons = list_buttons()
            action = input("\n[a] Add  [r] Remove  [l] List  [q] Quit\nChoice: ").lower().strip()

            if action == "a":
                label = input("Button label: ").strip()
                if not label:
                    print("Error: Label cannot be empty")
                    continue
                
                entity_id = input("Entity ID (e.g., button.office_pc): ").strip()
                if not entity_id.startswith("button."):
                    print("Warning: Entity ID should start with 'button.'")

                try:
                    keyring.set_password(SERVICE_NAME, f"{BUTTON_PREFIX}{label}", entity_id)
                    print(f"Saved '{label}' successfully")
                except KeyringLocked:
                    print("Keyring locked - changes not saved")

            elif action == "r":
                label = input("Button label to remove: ").strip()
                try:
                    keyring.delete_password(SERVICE_NAME, f"{BUTTON_PREFIX}{label}")
                    print(f"Removed '{label}'")
                except keyring.errors.PasswordDeleteError:
                    print(f"Button '{label}' not found")
                except KeyringLocked:
                    print("Keyring locked - removal failed")

            elif action == "l":
                if buttons := list_buttons():
                    print("\nConfigured Buttons:")
                    for btn in buttons:
                        print(f"  - {btn}")
                else:
                    print("\nNo buttons configured")

            elif action in ("q", ""):
                break

        except KeyboardInterrupt:
            print("\nOperation cancelled")
            break

def setup():
    """Interactive setup wizard"""
    try:
        current_url = keyring.get_password(SERVICE_NAME, "api_url")
        current_token = keyring.get_password(SERVICE_NAME, "api_token")
    except KeyringLocked:
        current_url = current_token = None
        print("Keyring locked - entering new credentials")

    # Get URL
    while True:
        url = input(f"Home Assistant URL [{current_url}]: ").strip() or current_url
        try:
            validated_url = validate_url(url)
            break
        except ValueError:
            print("Invalid URL format! Example: http://homeassistant.local:8123")

    # Get Token
    while True:
        token = getpass("API token (Enter to keep current): ") or current_token
        if token:
            break
        if current_token:
            break
        print("API token is required!")

    # Verify connection
    if not verify_connection(validated_url, token):
        print("Setup aborted due to connection issues")
        return

    # Save credentials
    try:
        keyring.set_password(SERVICE_NAME, "api_url", validated_url)
        keyring.set_password(SERVICE_NAME, "api_token", token)
        print("Credentials saved successfully")
    except KeyringLocked:
        print("Failed to save - keyring locked")
        return

    # Button management
    manage_buttons()
    print("\nSetup complete!")

def press_button(button_label):
    """Execute button press"""
    try:
        entity_id = keyring.get_password(SERVICE_NAME, f"{BUTTON_PREFIX}{button_label}")
        ha_url = keyring.get_password(SERVICE_NAME, "api_url")
        token = keyring.get_password(SERVICE_NAME, "api_token")
        
        if None in (entity_id, ha_url, token):
            print("Missing configuration. Run setup first")
            return

        response = requests.post(
            f"{ha_url}/api/services/button/press",
            headers={"Authorization": f"Bearer {token}"},
            json={"entity_id": entity_id},
            timeout=DEFAULT_TIMEOUT
        )
        
        if response.status_code in VALID_STATUS_CODES:
            print("Button pressed successfully!")
        else:
            print(f"Failed with status {response.status_code}: {response.text[:200]}")
            
    except KeyringLocked:
        print("Keyring locked - cannot access credentials")
    except requests.exceptions.RequestException as e:
        print(f"Network error: {str(e)}")

def main():
    parser = argparse.ArgumentParser(
        description="Home Assistant Button Controller",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("-s", "--setup", action="store_true", 
                      help="Configure Home Assistant connection")
    parser.add_argument("-p", "--press", metavar="LABEL", 
                      help="Press a configured button")
    parser.add_argument("-l", "--list", action="store_true", 
                      help="List configured buttons")
    parser.add_argument("-V", "--verify", action="store_true", 
                      help="Test connection to Home Assistant")
    # Add version argument
    parser.add_argument("-v", "--version", action="version",
                      version=f"%(prog)s {VERSION}",
                      help="Show program version and exit")

    args = parser.parse_args()

    if args.setup:
        setup()
    elif args.press:
        press_button(args.press)
    elif args.list:
        if buttons := list_buttons():
            print("Configured buttons:")
            for btn in buttons:
                print(f"  - {btn}")
        else:
            print("No buttons configured")
    elif args.verify:
        try:
            url = keyring.get_password(SERVICE_NAME, "api_url")
            token = keyring.get_password(SERVICE_NAME, "api_token")
            if verify_connection(url, token):
                print("Connection successful!")
            else:
                print("Connection failed")
        except KeyringLocked:
            print("Keyring locked - cannot verify")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()