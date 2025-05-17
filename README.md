# Spotify API Server

Use this to login to Spotify and then access its APIs.

## Setup

You will need to have uv installed to run project: https://docs.astral.sh/uv/getting-started/installation/

```
uv venv
.venv\Scripts\activate
uv pip install .
```

# Configuration

```
PORT = 9000
CLIENT_ID = "<id>" # Get this from Spotify by Spotify application
REDIRECT_URI = f"http://127.0.0.1:{PORT}/callback"
```

## Usage

```
python .\spotify_api_server\main.py
```

Open http://localhost:9000/spotify/authentication

