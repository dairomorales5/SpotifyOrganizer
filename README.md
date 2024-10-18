# Spotify Organizer

Spotify Organizer helps you organize your liked songs by genre, mood, and more, using the power of AI. Simplify your music collection and enjoy better playlists tailored to your preferences.

## Key Features
- **AI-Powered Classification**: Automatically categorize your songs based on genre, mood, or any custom criteria.
- **Spotify Integration**: Grant access to your Spotify account, and we'll handle the rest.
- **Custom Playlists**: Provide a brief description to guide the AI in creating personalized playlists.
- **Seamless Scraping**: We gather and organize your playlist information directly from Spotify.
- **Hands-Free Experience**: After setting up, your playlists will be automatically organized.

## How It Works
1. **Authorize Access**: By locally saving your browser cookies into a `cookies.json` file, we can access your account, password-free!
2. **Provide an OpenAI API Key**: You'll need an OpenAI API key for song classification.
3. **Automatic Playlist Organization**: The AI analyzes your liked songs and creates curated playlists based on the song attributes.
4. **Extra Input (Optional)**: If you wish, add custom descriptions to further refine playlist creation.
5. **Enjoy**: Sit back and enjoy the improved playlists! We hope you can discover new songs with Spotify's playlists radios.

## Getting Started

### Step 1: Install the Required Packages
Ensure you have the necessary dependencies installed before proceeding. Run the following command:

```bash
pip install -r requirements.txt
```

### Step 2: Download Your Cookies JSON

Download your browser web page cookies by visiting [open.spotify.com](https://open.spotify.com/) and using a tool like [this browser extension](https://chromewebstore.google.com/detail/export-cookie-json-file-f/nmckokihipjgplolmcmjakknndddifde) to export the cookies into a `cookies.json` file. This will allow local access to your Spotify Web Player without needing a password.


### Step 3: Execute the Jupyter Notebook
Run the project by opening and executing the `SpotifyOrganizer.ipynb` notebook:

### Requirements
- A Spotify account
- OpenAI API Key
- Python 3.11 (recommended)
- Required Python libraries (installed via `requirements.txt`)

---
Enjoy better playlist organization with Spotify Organizer!