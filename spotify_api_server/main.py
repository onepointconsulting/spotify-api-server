import random
import string
import hashlib
import base64

from urllib.parse import quote


from aiohttp import web, ClientSession

# Configuration
PORT = 9000
CLIENT_ID = "<id>" # Get this from Spotify by Spotify application. Replace this
REDIRECT_URI = f"http://127.0.0.1:{PORT}/callback"

routes = web.RouteTableDef()


@routes.get("/")
async def hello(request):
    return web.json_response({"status": "OK"}, status=200)


@routes.get("/spotify/authentication")
async def spotify(request):
    """
    Redirects to Spotify login
    Example: http://localhost:9000/spotify/authentication
    """
    # Replace this with the actual URL including client_id, redirect_uri, etc.
    spotify_auth_url = "https://accounts.spotify.com/authorize"
    global verifier
    verifier = generate_code_verifier(128)
    challenge = await generate_code_challenge(verifier)
    response_type = "code"
    redirect_uri = f"http://127.0.0.1:{PORT}/callback"
    scope = "user-read-private user-read-email"
    code_challenge_method = "S256"

    # Redirect the client to Spotify's authorization page
    raise web.HTTPFound(
        location=f"{spotify_auth_url}?code_challenge={quote(challenge)}&client_id={CLIENT_ID}&response_type={response_type}&redirect_uri={REDIRECT_URI}&scope={scope}&code_challenge_method={code_challenge_method}"
    )


def generate_code_verifier(length: int) -> str:
    possible = string.ascii_letters + string.digits
    return "".join(random.choice(possible) for _ in range(length))


async def generate_code_challenge(code_verifier: str) -> str:
    # Step 1: UTF-8 encode the code verifier
    data = code_verifier.encode('utf-8')
    
    # Step 2: SHA-256 hash
    digest = hashlib.sha256(data).digest()
    
    # Step 3: Base64 encode, make it URL-safe, and remove padding
    code_challenge = base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')
    
    return code_challenge


@routes.get("/callback")
async def callback(request):
    code = request.rel_url.query["code"]
    access_token = await get_access_token(verifier, code)
    headers = { "Authorization": f"Bearer {access_token}" }
    result = {}
    async with ClientSession() as session:
        async with session.get("https://api.spotify.com/v1/me", headers=headers) as resp:
            resp.raise_for_status()  # Raise an error for 4xx/5xx responses
            result = await resp.json()
    return web.json_response({"status": "OK", "access_token": access_token, "profile": result}, status=200)


async def get_access_token(verifier: str, code: str) -> str:
    # Prepare the URL-encoded body
    data = {
        "client_id": CLIENT_ID,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "code_verifier": verifier,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    url = "https://accounts.spotify.com/api/token"
    async with ClientSession() as session:
        async with session.post(url, data=data, headers=headers) as resp:
            resp.raise_for_status()  # Raise an error for 4xx/5xx responses
            result = await resp.json()
            return result["access_token"]

def main():
    app = web.Application()
    app.add_routes(routes)
    web.run_app(
        app,
        host="0.0.0.0",
        port=PORT,
    )


if __name__ == "__main__":
    main()
