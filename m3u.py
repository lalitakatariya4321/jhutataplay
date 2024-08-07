import requests
import json

# Set the URLs of the APIs
json_url = 'https://fox.toxic-gang.xyz/tata/channels'  # Replace with your actual JSON API URL
hmac_url = 'https://fox.toxic-gang.xyz/tata/hmac'  # HMAC API URL

# Fetch the HMAC data from the API
try:
    hmac_response = requests.get(hmac_url)
    hmac_response.raise_for_status()
    hmac_data = hmac_response.json()
except requests.RequestException as e:
    print(f'Failed to fetch HMAC data: {e}')
    exit(1)

# Extract the hdntl value
hdntl = hmac_data.get('data', {}).get('hdntl', '')
if not hdntl:
    print('Failed to retrieve hdntl value.')
    exit(1)

# Fetch the JSON data from the API
try:
    json_response = requests.get(json_url)
    json_response.raise_for_status()
    data = json_response.json()
except requests.RequestException as e:
    print(f'Failed to fetch JSON data: {e}')
    exit(1)

# Initialize the M3U playlist content
m3u_content = "#EXTM3U x-tvg-url=\"https://raw.githubusercontent.com/mitthu786/tvepg/main/tataplay/epg.xml.gz\"\n"

# Iterate over the channels in the data
for channel in data.get('data', []):
    # Extract necessary fields
    id = channel.get('id', '')
    title = channel.get('title', '')
    logo = channel.get('logo', '')
    initial_url = channel.get('initialUrl', '')
    genre = channel.get('genre', '')

    # Initialize license key
    license_key = ''

    # Check if 'base64' key exists and has 'keys'
    if 'base64' in channel and 'keys' in channel['base64'] and channel['base64']['keys']:
        first_key = channel['base64']['keys'][0]
        if 'k' in first_key:
            license_key = json.dumps({
                'keys': [{
                    'kty': first_key.get('kty', ''),
                    'k': first_key.get('k', ''),
                    'kid': first_key.get('kid', '')
                }],
                'type': 'temporary'
            })

    # Add the channel to the M3U playlist
    m3u_content += f"#EXTINF:-1 tvg-id=\"{id}\" tvg-logo=\"{logo}\", group-title=\"{genre}\", {title}\n"
    m3u_content += "#KODIPROP:inputstream.adaptive.license_type=clearkey\n"
    if license_key:
        m3u_content += f"#KODIPROP:inputstream.adaptive.license_key={license_key}\n"
    m3u_content += "#EXTVLCOPT:http-user-agent=Mozilla/5.0\n"
    m3u_content += f"#EXTHTTP:{{\"cookie\":\"{hdntl}\"}}\n"
    m3u_content += f"{initial_url}|cookie:{hdntl}\n\n"

# Define the file path for the M3U playlist
playlist_file = 'playlist.m3u'

# Write the M3U content to the file
try:
    with open(playlist_file, 'w') as file:
        file.write(m3u_content)
    print(f"M3U playlist has been saved as '{playlist_file}'.")
except IOError as e:
    print(f'Failed to write M3U playlist to file: {e}')
    exit(1)
