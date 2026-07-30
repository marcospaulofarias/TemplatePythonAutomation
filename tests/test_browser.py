from resources.Browser import Browser

if __name__ == '__main__':
    browser = Browser(process_id="0000001", process_type="create_report", process_machine="COOP_MACHINE_01")

    browser.get_site(url_site='https://www.youtube.com')
