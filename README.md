✅ Step 1: Create a Reddit App
Go to: https://www.reddit.com/prefs/apps

Scroll down to the "Developed Applications" section.

Click the "Create App" or "Create Another App" button.

Fill in the form:

Name: Enter your app name (e.g., "Reddit Scraper").

App Type: Select "script" (for personal use).

Description: Optional.

About URL: Leave it blank or use a placeholder.

Redirect URI: Enter http://localhost:8080 (required, even if not used in scripts).

Permissions: Not applicable here (since it's a script-based app).

Click "Create app".

After creation, you will see:

client ID (displayed below the app name)

client secret (beside "secret")

✅ Step 2: Add Redirect URL
Make sure the Redirect URI is set to:
http://localhost:8080
(This is mandatory even for scripts, although it won't actually open a web browser for this purpose.)

✅ Step 3: Run the Python Scraper Script
Ensure you have a Python script named Scraper.py.
This script should use the praw library (Python Reddit API Wrapper).
