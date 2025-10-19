import dropbox

APP_KEY = "i1c1j9xehcdn8w9"
APP_SECRET = "s7fe7xa2tx5t7zz"

auth_flow = dropbox.DropboxOAuth2FlowNoRedirect(
    APP_KEY, APP_SECRET, token_access_type='offline'
)

authorize_url = auth_flow.start()
print("1. Go to:", authorize_url)
print("2. Click 'Allow' and copy the authorization code.")
auth_code = input("Enter the authorization code here: ")

oauth_result = auth_flow.finish(auth_code)

print("Access token:", oauth_result.access_token)
print("Refresh token:", oauth_result.refresh_token)
print("Expires at:", oauth_result.expires_in)

APP_SECRET = "s7fe7xa2tx5t7zz"

auth_flow = dropbox.DropboxOAuth2FlowNoRedirect(
    APP_KEY, APP_SECRET, token_access_type='offline'
)

authorize_url = auth_flow.start()
print("1. Go to:", authorize_url)
print("2. Click 'Allow' and copy the authorization code.")
auth_code = input("Enter the authorization code here: ")

oauth_result = auth_flow.finish(auth_code)

print("Access token:", oauth_result.access_token)
print("Refresh token:", oauth_result.refresh_token)
print("Expires in:", oauth_result.expires_in)
