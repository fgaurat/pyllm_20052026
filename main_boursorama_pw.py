from pprint import pprint
import time
from playwright.sync_api import sync_playwright



def main():

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        url = f"https://www.boursorama.com/"
        page.goto(url,wait_until="networkidle")

        
        screenshot = page.screenshot(path="screenshot.png")

if __name__=='__main__':
    main()
