import requests
import sys
import os

WEBSITE_DOMAIN = os.getenv("WEBSITE_DOMAIN")
DISCORD_HEALTH_CHECK_WEBHOOK_URL = os.getenv("DISCORD_HEALTH_CHECK_WEBHOOK_URL")
DISCORD_ALERTS_WEBHOOK_URL = os.getenv("DISCORD_ALERTS_WEBHOOK_URL")
TIMEOUT_SECONDS=5

if not WEBSITE_DOMAIN:
    print("❌ WEBSITE_DOMAIN environment variable must be set.")
    sys.exit(1)
if not DISCORD_HEALTH_CHECK_WEBHOOK_URL:
    print("❌ DISCORD_HEALTH_CHECK_WEBHOOK_URL environment variable must be set.")
    sys.exit(1)
if not DISCORD_ALERTS_WEBHOOK_URL:
    print("❌ DISCORD_ALERTS_WEBHOOK_URL environment variable must be set.")
    sys.exit(1)

def check_website_status(url):
    try:
        response = requests.get(
            url, 
            timeout=TIMEOUT_SECONDS,
            headers={"User-Agent": f"Mozilla/5.0 (compatible; HealthCheckMonitor/1.0; +https://{WEBSITE_DOMAIN})"}
        )
        if response.status_code == 200:
            return "ok"
        else:
            return f"status_{response.status_code}"
    except requests.exceptions.Timeout:
        return "timeout"
    except requests.exceptions.ConnectionError:
        return "connection_error"
    except Exception as e:
        return str(e)


def send_discord_notification(webhook_url, message):
    payload = {
        "content": message
    }

    try:
        response = requests.post(webhook_url, json=payload)
    except Exception as e:
        print("❌ Failed to send Discord notification: {e}")

if __name__ == "__main__":
    subdomains = [
        "admin",
        "www",
    ]

    for subdomain in subdomains:
        url = f"https://{subdomain}.{WEBSITE_DOMAIN}"
        print(f"🔎 Checking **{url}**...")

        website_status = check_website_status(f"{url}/health")

        if website_status == "ok":
            message = f"✅ **{url}** is UP."
        elif website_status == "timeout":
            message = f"⚠️ **{url}** timed out."
        elif website_status == "connection_error":
            message = f"⚠️ **{url}** is unreachable."
        elif str(website_status).startswith("status_"):
            code = website_status.split("_")[1]
            message = f"⚠️ **{url}** returned HTTP status `{code}`."
        else:
            message = f"❓ **{url}** unknown error: `{website_status}`"

        send_discord_notification(DISCORD_HEALTH_CHECK_WEBHOOK_URL, message)

        if website_status != "ok":
            send_discord_notification(DISCORD_ALERTS_WEBHOOK_URL, message)

        print(message)
    
    sys.exit(0)

    
