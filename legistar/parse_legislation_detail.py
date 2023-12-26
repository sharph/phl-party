from time import sleep
from datetime import date
import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_random_exponential

NICE_SECONDS = 1


@retry(stop=stop_after_attempt(10), wait=wait_random_exponential(multiplier=1, max=60))
def http_get(url):
    sleep(NICE_SECONDS)
    print(url)
    return requests.get(url).content


def parse_date(text):
    try:
        month, day, year = [int(x) for x in text.split("/")]
        return date(year, month, day)
    except (ValueError, AttributeError):
        return None


def get_ids_guids():
    url = "https://phila.legistar.com/Feed.ashx?M=L&ID=16523394&GUID=a977c9a4-9a4a-4058-b881-260e43aa3959&Title=City+of+Philadelphia+-+Legislation"
    soup = BeautifulSoup(http_get(url), "xml")
    links = soup.find_all("link")
    links = [x.string for x in links if x.string is not None and "Gateway" in x.string]
    links = [(x.split("&")[2].split("=")[1], x.split("=")[-1]) for x in links]
    return links


def get_legislation(leg_id, leg_guid):
    url = f"https://phila.legistar.com/LegislationDetail.aspx?ID={leg_id}&GUID={leg_guid}&Options=ID%7cText%7c&FullText=1"
    return parse_legislation_detail(http_get(url), leg_id, leg_guid)


def enhance_action(action, action_id, action_guid):
    url = f"https://phila.legistar.com/HistoryDetail.aspx?ID={action_id}&GUID={action_guid}"
    soup = BeautifulSoup(http_get(url), "html.parser")
    action["action"] = soup.find(
        "span", id="ctl00_ContentPlaceHolder1_lblAction"
    ).string
    action["action_text"] = soup.find(
        "span", id="ctl00_ContentPlaceHolder1_lblActionText"
    ).string
    action["mover"] = (
        soup.find("td", id="ctl00_ContentPlaceHolder1_tdMover2").get_text().strip()
    )
    action["seconder"] = (
        soup.find("td", id="ctl00_ContentPlaceHolder1_tdSeconder2").get_text().strip()
    )
    vote_table = soup.find("table", id="ctl00_ContentPlaceHolder1_tblVote2")
    votes = {}
    vote_table_body = vote_table.find("tbody")
    for row in vote_table_body.find_all("tr"):
        cols = row.find_all("td")
        if len(cols) == 1:
            return
        votes[cols[0].get_text().strip()] = cols[1].string
    action["votes"] = votes


def parse_legislation_actions(table):
    rows = table.find_all("tr")
    assert "Action" in str(rows[0])
    parsed_rows = []
    for row in rows:
        try:
            cols = row.find_all("td")
            parsed_row = {
                "date": parse_date(cols[0].string),
                "action_by": cols[2].get_text().strip(),
                "action": cols[3].get_text().strip(),
                "result": cols[4].get_text().strip(),
            }
            try:
                details_link = cols[6].find("a")["onclick"]
                action_id = details_link.split("&")[0].split("=")[1]
                action_guid = details_link.split("'")[1].split("=")[2]
                enhance_action(parsed_row, action_id, action_guid)
            except (TypeError, KeyError):
                pass
            parsed_rows.append(parsed_row)
        except IndexError:
            pass
    return parsed_rows


def parse_legislation_detail(html, leg_id, leg_guid):
    soup = BeautifulSoup(html, "html5lib")
    leg_file_no = soup.find("span", id="ctl00_ContentPlaceHolder1_lblFile2").string
    leg_title = soup.find("span", id="ctl00_ContentPlaceHolder1_lblTitle2").string
    leg_type = soup.find("span", id="ctl00_ContentPlaceHolder1_lblType2").string
    leg_status = soup.find("span", id="ctl00_ContentPlaceHolder1_lblStatus2").string
    try:
        leg_sponsors = soup.find(
            "span", id="ctl00_ContentPlaceHolder1_lblSponsors2"
        ).string.split(", ")
    except AttributeError:
        leg_sponsors = None
    leg_created = parse_date(
        soup.find("span", id="ctl00_ContentPlaceHolder1_lblIntroduced2").string
    )
    leg_final_action = parse_date(
        soup.find("span", id="ctl00_ContentPlaceHolder1_lblPassed2").string
    )
    leg_text = soup.find("div", id="ctl00_ContentPlaceHolder1_pageText")
    leg_actions_table = soup.find(
        "table", id="ctl00_ContentPlaceHolder1_gridLegislation_ctl00"
    )
    leg_actions = parse_legislation_actions(leg_actions_table)
    try:
        leg_indexes = soup.find(
            "span", id="ctl00_ContentPlaceHolder1_lblIndexes2"
        ).string.split(", ")
    except AttributeError:
        leg_indexes = None
    return {
        "file_number": leg_file_no,
        "title": leg_title,
        "type": leg_type,
        "status": leg_status,
        "created": leg_created,
        "final_action": leg_final_action,
        "sponsors": leg_sponsors,
        "indexes": leg_indexes,
        "actions": leg_actions,
        "text": leg_text.get_text(),
        "text_html": str(leg_text),
    }


def test():
    print(get_legislation(5663691, "DB5F30FB-BE83-47AF-A847-F1C2167BB947"))


if __name__ == "__main__":
    test()
