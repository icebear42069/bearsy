import datetime
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from scraper_utils import *


class ResyScraper:
    def __init__(self, url, date_str, time_range, party_size):
        self.url = url
        self.desired_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        start, end = time_range.split("-")
        self.start = parse_time(start)
        self.end   = parse_time(end)
        self.party_size = str(int(party_size))      # keep as string for <select>
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 20)


    def _visible_slots(self):
        """
        Return list of (time_str, WebElement) tuples.
        Also prints each time_str on its own line.
        """
        buttons = self.driver.find_elements(
            By.CSS_SELECTOR, ".ReservationButtonList .ReservationButton")
        out = []
        for btn in buttons:
            try:
                txt = btn.find_element(By.CLASS_NAME,
                                       "ReservationButton__time").text.strip()
                print(txt)  # <= ONLY the time text
                out.append((txt, btn))
            except Exception:
                pass
        return out


    def run(self):
        self.open_and_login()
        self.set_filters()
        self.hunt_and_book()
        self.driver.quit()


    def open_and_login(self):
        self.driver.get(self.url)
        self.driver.maximize_window()
        input("→ Log into Resy in the browser, then hit <Enter> here to continue…")


    def set_filters(self):
        # party size
        Select(self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "select#party_size"))
        )).select_by_value(self.party_size)

        # date (quick-picker buttons have aria-label with full date)
        btn_label = self.desired_date.strftime("%B %-d, %Y")
        date_btn  = self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, f"button[aria-label*='{btn_label}']"))
        )
        date_btn.click()


    def hunt_and_book(self):
        print("⏳ Scanning for slots …")
        while True:
            self.driver.refresh()
            print(self._visible_slots())
            # all visible reservation buttons
            buttons = self.driver.find_elements(By.CSS_SELECTOR,
                                                ".ReservationButtonList .ReservationButton")

            for b in buttons:
                time_txt = b.find_element(By.CLASS_NAME, "ReservationButton__time").text
                res_time = datetime.datetime.strptime(time_txt, "%I:%M %p").time()
                if self.start <= res_time <= self.end:
                    print(f"🎯 booking {time_txt}")
                    self.driver.execute_script("arguments[0].click();", b)
                    return

            print("…none in range – retrying in 5 s")
            sleep(60)

if __name__ == "__main__":
    # restaurant_url = input("Enter the restaurant reservation link: ")
    # reservation_date = input("Enter the reservation date (YYYY-MM-DD): ")
    # reservation_time = input("Enter the reservation time (e.g., 19:00): ")
    # party_size = int(input("Enter the party size: "))

    # scraper = ResyScraper(restaurant_url, reservation_date, reservation_time, party_size)

    scraper = ResyScraper('https://resy.com/cities/new-york-ny/venues/jing-li',
                          '2025-07-06',
                          '19:00-21:00', 4)
    scraper.run()
    input("Please log in manually, then press Enter to continue...")
