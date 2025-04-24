import json
import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class EmailNotifier:
    def __init__(self, mailgun_api_key=None, mailgun_domain=None):
        self.mailgun_api_key = mailgun_api_key or os.getenv("MAILGUN_API_KEY")
        self.mailgun_domain = mailgun_domain or os.getenv("MAILGUN_DOMAIN")
        self.from_email = f"notifier@{self.mailgun_domain}"

        # Validate required credentials
        if not self.mailgun_api_key or not self.mailgun_domain:
            raise ValueError("Mailgun API key or domain not provided")

        # Use US region API (default for sandbox domains)
        self.api_base_url = os.getenv("MAILGUN_REGION", "https://api.mailgun.net/v3")

    def send_email(self, to_email, subject, text_body, html_body=None):
        """Send an email using the Mailgun API with plain text and optional HTML."""
        url = f"{self.api_base_url}/{self.mailgun_domain}/messages"
        data = {
            "from": self.from_email,
            "to": to_email,
            "subject": subject,
            "text": text_body,
        }
        if html_body:
            data["html"] = html_body

        try:
            response = requests.post(
                url,
                auth=("api", self.mailgun_api_key),
                data=data,
                timeout=10,
            )
            response.raise_for_status()
            print(f"Email sent to {to_email} via Mailgun")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Failed to send email via Mailgun: {e}")
            if "response" in locals():
                print(f"Response: {response.text}")
            return False

    def check_and_notify(
        self,
        search_string,
        json_file="play_titles.json",
        to_email="bogdan.varzaru@mail.com",
    ):
        """Check if search_string is present in title lines of json_file and include title and link."""
        matches = []
        try:
            with open(json_file, "r") as f:
                current_title = None
                current_link = None
                for line in f:
                    line = line.strip()
                    if '"title":' in line and search_string.lower() in line.lower():
                        # Extract title from line
                        try:
                            title = line.split(":", 1)[1].strip().strip('",')
                            current_title = title
                        except IndexError:
                            continue
                    elif '"link":' in line and current_title:
                        # Extract link from line
                        try:
                            link = line.split(":", 1)[1].strip().strip('",')
                            current_link = link
                        except IndexError:
                            continue
                    # If we have both title and link, store the match
                    if current_title and current_link:
                        matches.append({"title": current_title, "link": current_link})
                        current_title = None
                        current_link = None

            if matches:
                # Build plain text body
                text_body = f"The following events matching '{search_string}' were found in {json_file}:\n\n"
                for match in matches:
                    text_body += f"Title: {match['title']}\nLink: {match['link']}\n\n"

                # Build HTML body with clickable links
                html_body = f"<h3>The following events matching '{search_string}' were found in {json_file}:</h3>"
                for match in matches:
                    html_body += f"<p><strong>Title:</strong> {match['title']}<br>"
                    html_body += f"<strong>Link:</strong> <a href='{match['link']}'>{match['link']}</a></p>"

                subject = f"FOUND {len(matches)} EVENT(S) MATCHING '{search_string}'"
                return self.send_email(to_email, subject, text_body, html_body)
            else:
                print(f"'{search_string}' not found in {json_file}")
                return False

        except FileNotFoundError:
            print(f"Error: {json_file} not found")
            return False
        except Exception as e:
            print(f"Error reading {json_file}: {e}")
            return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        search_string = sys.argv[1]
    else:
        print("Please provide a search string as a command line argument.")
        print('Usage: python email_notifier.py "Name of Play"')
        sys.exit(1)

    notifier = EmailNotifier()
    notifier.check_and_notify(search_string)
