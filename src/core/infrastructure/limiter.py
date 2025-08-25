from slowapi import Limiter
from slowapi.util import get_remote_address

# Create a Limiter instance that will be shared across the application.
# It uses the client's IP address as the key for tracking requests.
limiter = Limiter(key_func=get_remote_address)
