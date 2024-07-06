import requests

def fetch_ver_code(endpoint):
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        return response.json().get('verCode')
    except requests.RequestException as e:
        logger.error(f"Failed to fetch the latest version code: {e}")
        raise
