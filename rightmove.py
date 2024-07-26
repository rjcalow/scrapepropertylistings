import requests
from bs4 import BeautifulSoup
import random
from urllib.parse import urljoin
import pathlib
import pickle


class Houseforsale:
    def __init__(self, address, url):
        self.address = address
        self.url = url


class Rightmove:
    def __init__(self, url):
        self.savefile = pathlib.Path(__file__).parent.resolve() / "rightmove_data"
        self.url = url
        self.properties = []
        self.previoushouses = self.loadsavefile()

        # List of user agents
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0",
            "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36",
        ]

        selected_user_agent = random.choice(user_agents)

        # Example request using the selected user agent
        headers = {"User-Agent": selected_user_agent}

        r = requests.get(url, headers=headers)

        base_url = "https://www.rightmove.co.uk"
        # print(r.content)
        soup = BeautifulSoup(r.content, "html.parser")
        # Step 6: Find the <a> tags with the specific class

        # Find all property card details divs
        property_card_details = soup.find_all("div", class_="propertyCard-details")

        # Loop through each property card
        for card in property_card_details:
            # Find the anchor tag within the current card
            link_element = card.find("a", class_="propertyCard-link")

            # Check if link element exists (it might not be present in all cards)
            if link_element:

                # Extract the title (address)
                title = link_element.find("address").text.strip()

                # Extract the link (href attribute)
                link = link_element["href"]
                link = urljoin(base_url, link)
                # print(link)

                if self.search(link) == False:
                    print(f"found new house at {title}")
                    self.properties.append(
                        Houseforsale("".join(title.splitlines()), link)
                    )

        self.updatesavefile(
            self.properties + self.previoushouses
        )  # combine both lists and save

    def new(self):
        return self.properties

    def loadsavefile(self):
        """Loads the set of houses from a pickle file (if it exists)."""

        if self.savefile.exists():
            with self.savefile.open("rb") as f:
                try:
                    previoushouses = pickle.load(f)
                    print("loaded save file")

                except (pickle.UnpicklingError, EOFError):
                    print("loaded from scratch")
                    previoushouses = set()
        else:
            previoushouses = set()

        print(f"loaded {len(previoushouses)}")

        return previoushouses

    def updatesavefile(self, properties):
        MAX = 400
        """Saves the set of seen titles to a pickle file, handling overflow."""
        if len(self.properties) > MAX:
            # Remove the oldest title (assuming insertion order reflects age)
            properties.discard(next(iter(self.properties)))
        with open(self.savefile, "wb") as f:
            pickle.dump(properties, f)

    def search(self, url):
        count = 0
        for h in self.previoushouses:
            if h.url == url:
                count += 1

        for p in self.properties:
            if p.url == url:
                print("duplicate found in list")
                count += 1

        if count == 0:
            return False
        else:
            return True


# useage
# url = "https://www.rightmove.co.uk/property-for-sale/find.html?locationIdent...."
# rm = Rightmove (url)
