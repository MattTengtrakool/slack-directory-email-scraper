from playwright.sync_api import sync_playwright
import time
import csv
import os


CHROME_EXECUTABLE_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CHROME_PROFILE_PATH = os.path.expanduser("~/playwright-chrome-profile")
SLACK_PEOPLE_URL = "" #i.e https://app.slack.com/client/X1000000/people
OUTPUT_FILE = "output.csv"


def launch_browser(playwright):
    # persistant chrome user profs
    context = playwright.chromium.launch_persistent_context(
        user_data_dir=CHROME_PROFILE_PATH,
        executable_path=CHROME_EXECUTABLE_PATH,
        headless=False,
        slow_mo=150,
        args=["--profile-directory=Default"],
    )
    page = context.pages[0] if context.pages else context.new_page()
    return context, page


def extract_user_info(page):
    # extract name and email from sidebar
    page.wait_for_selector("span.p-r_member_profile__name__text", timeout=7000)
    page.wait_for_selector("div.p-rimeto_member_profile_field__value a[href^='mailto:']", timeout=7000)

    name = page.locator("span.p-r_member_profile__name__text").inner_text()
    email = page.locator("div.p-rimeto_member_profile_field__value a[href^='mailto:']").inner_text()
    return name, email


def process_page(page):
    # process all user cards gracefully
    results = []
    cardcount = page.locator("div.p-browse_page_member_card_entity").count()

    for idx in range(cardcount):
        try:
            card = page.locator("div.p-browse_page_member_card_entity").nth(idx)
            card.scroll_into_view_if_needed()
            card.click()

            name, email = extract_user_info(page)
            print(f"✅ {name} - {email}")
            results.append((name, email))

            page.keyboard.press("Escape")
            time.sleep(0.5)

        except Exception as e:
            print(f"❌ Error on card #{idx}: {e}")
            page.keyboard.press("Escape")
            time.sleep(0.5)

    return results


def go_to_next_page(page):
    # handle pagination 
    nextpage = page.locator("button[data-qa='c-pagination_forward_btn']")
    if nextpage.count() > 0 and nextpage.get_attribute("aria-disabled") != "true":
        nextpage.click()
        page.wait_for_selector("div.p-browse_page_member_card_entity", timeout=5000)
        page.wait_for_timeout(1000)
        return True
    return False


def save_to_csv(data, filename, append=False):
    # save data to csv 
    mode = "a" if append else "w"
    with open(filename, mode, newline="") as f:
        writer = csv.writer(f)
        if not append:
            writer.writerow(["Name", "Email"])
        writer.writerows(data)


def scrape_slack_directory():
    # main playwright logic
    with sync_playwright() as p:
        context, page = launch_browser(p)
        page.goto(SLACK_PEOPLE_URL)

        input("⏳ Already logged in? Press ENTER to start scraping...")

        totaloutput = []
        pnum = 1
        save_to_csv([], OUTPUT_FILE, append=False) 

        while True: 
            print(f"\n🔄 Processing Page {pnum}")
            page_results = process_page(page)
            totaloutput.extend(page_results)

            save_to_csv(page_results, OUTPUT_FILE, append=True)

            if go_to_next_page(page):
                pnum += 1
            else:
                print("✅ Reached last page.")
                break

        context.close()     
        print(f"\n📁 Done. {len(totaloutput)} emails saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    scrape_slack_directory()
