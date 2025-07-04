# Slack-Directory-Email-Scraper

Simple [Playwright](https://playwright.dev/python/) script that launches your local Chrome browser to scrape names and contact information from a Slack workspace.

REQUIREMENTS:

Python3.7+
Playwright - pip3 install -r requirements.txt

##Setup & Usage:

1. **Install dependencies**

```bash
pip install -r requirements.txt
playwright install
```

2. **(Optional) Copy your Chrome profile to avoid conflicts:**

```bash
mkdir -p ~/playwright-chrome-profile
cp -R ~/Library/Application\ Support/Google/Chrome/Default ~/playwright-chrome-profile/Default
```

3. **Usage**
   
```bash
python3 code.py
```

data will be saved to
output.csv
