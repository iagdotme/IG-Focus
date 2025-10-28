#!/usr/bin/env python3
"""
Example: Login to Instagram with 2FA support
"""

from instagrapi import Client
from instagrapi.exceptions import TwoFactorRequired
from pathlib import Path

def login_with_2fa(username: str, password: str):
    """Login to Instagram with 2FA support"""

    cl = Client()
    session_file = Path("session.json")

    # Try loading saved session first
    if session_file.exists():
        print("Found saved session, attempting to load...")
        try:
            cl.load_settings(session_file)
            cl.login(username, password)
            print("✓ Logged in using saved session (no 2FA needed)")
            return cl
        except Exception as e:
            print(f"Saved session didn't work: {e}")
            print("Will perform fresh login...")

    # Fresh login with 2FA handling
    print("\nAttempting login...")
    try:
        cl.login(username, password)
        print("✓ Logged in successfully (no 2FA required)")

    except TwoFactorRequired:
        print("\n🔐 Two-Factor Authentication Required!")
        print("=" * 60)
        print("Instagram sent a verification code to your phone/email.")
        print("Check your:")
        print("  • Authentication app (Google Authenticator, Authy, etc.)")
        print("  • SMS messages")
        print("  • Email")
        print("=" * 60)

        # Get 2FA code from user
        verification_code = input("\nEnter the 6-digit verification code: ").strip()

        if not verification_code or len(verification_code) != 6:
            raise ValueError("Invalid code. Must be 6 digits.")

        # Login with 2FA code
        print("Verifying code...")
        cl.login(username, password, verification_code=verification_code)
        print("✓ 2FA verification successful!")

    # Save session for future use
    cl.dump_settings(session_file)
    print(f"✓ Session saved to {session_file}")
    print("  (Next time you won't need 2FA if you use the saved session)")

    return cl


def main():
    print("=" * 60)
    print("Instagram Login with 2FA Support".center(60))
    print("=" * 60)

    # Get credentials
    username = input("\nInstagram Username: ").strip()
    password = input("Instagram Password: ").strip()

    if not username or not password:
        print("✗ Username and password are required!")
        return

    try:
        # Login with 2FA support
        cl = login_with_2fa(username, password)

        # Test the connection by getting account info
        print("\nFetching your account info...")
        user_id = cl.user_id_from_username(username)
        user_info = cl.user_info(user_id)

        print("\n" + "=" * 60)
        print("Account Information".center(60))
        print("=" * 60)
        print(f"Username: @{user_info.username}")
        print(f"Full Name: {user_info.full_name}")
        print(f"Followers: {user_info.follower_count:,}")
        print(f"Following: {user_info.following_count:,}")
        print(f"Posts: {user_info.media_count:,}")
        print(f"Biography: {user_info.biography if user_info.biography else 'None'}")
        print("=" * 60)

        print("\n✓ Login successful! You can now use the feed_reader.py script.")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
