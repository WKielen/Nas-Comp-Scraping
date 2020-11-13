from selenium import webdriver
import time
import json


class CompetitionNas:
    """Library for automation of the NTTB Competitie Admin System (NAS)"""
    def __init__(self) -> object:

        try:
            self.browser = webdriver.Chrome()
            self.browser.set_page_load_timeout(10)
            self.browser.implicitly_wait(5)
        except Exception as e:
            raise Exception("Error starting browser: " + str(e))

        try:
            self.browser.get("https://midden.nttb.nl/competitie/competitie-via-nas/")

        except Exception as e:
            raise Exception("Open process failed: " + str(e))

    def choose_competition(self):
        competitienaam_xpath = '/html/body/table/tbody/tr[2]/td[1]/table[1]/tbody/tr[2]/td[2]'
        time.sleep(1)
        self.browser.find_element_by_xpath(competitienaam_xpath).click()


class Nas:
    """Library for automation of the NTTB Admin System (NAS)"""
    def __init__(self, userid: str, password: str) -> object:
        """ De constructor opent de browser en logged direct in.

        :return: object
        """

        try:
            self.browser = webdriver.Chrome()
            self.browser.set_page_load_timeout(10)
            self.browser.implicitly_wait(5)
        except Exception as e:
            raise Exception("Error starting browser: " + str(e))

        try:
            self.browser.get("https://www.nttb-administratie.nl")
            frame = self.browser.find_element_by_name('nttbadministratie_login')
            self.browser.switch_to.frame(frame)
            useridfield = self.browser.find_element_by_name('gebruikersnaam')
            useridfield.send_keys(userid)
            passwordfield = self.browser.find_element_by_name('wachtwoord')
            passwordfield.send_keys(password)
            login = self.browser.find_element_by_link_text('inloggen »»')
            login.click()

            try:
                # Switch naar het net geopende window
                window_after = self.browser.window_handles[1]
                self.browser.close()
                self.browser.switch_to.window(window_after)

                # naar het frame in het nieuwe window
                frame = self.browser.find_element_by_name('nas_content')
                self.browser.switch_to.frame(frame)
            except Exception as e:
                # Een foute login is best wel lastig af te vangen omdat de error pagina maar heel kort wordt gedisplayed.
                # Daarom doe ik een aanname dat als we niet naar het juiste frame kunnen er een foute login is.
                # Dit is natuurlijk niet waterdicht
                raise Exception("Wrong credentials")

        except Exception as e:
            raise Exception("Login process failed: " + str(e))

    def open_page_via_menu(self, menu_item: str) -> None:
        """ Navigeer naar een pagina en open deze. Navigatie via hoofd en submenu

        :return: None
        """

        try:
            leden_xpath = '/html/body/table/tbody/tr[2]/td[1]/table[1]/tbody/tr[2]/td[2]'
            leden_lid_aanmelden = '/html/body/table/tbody/tr[2]/td[1]/table[1]/tbody/tr[3]/td/table/tbody/tr[1]/td[2]'

            overzicht_bekijken_xpath = '/html/body/table/tbody/tr[2]/td[1]/table[1]/tbody/tr[3]/td[2]'
            ledenlijst_xpath = '/html/body/table/tbody/tr[2]/td[1]/table[1]/tbody/tr[4]/td/table/tbody/tr[1]/td[2]'

            if menu_item == 'ledenlijst':
                mainmenu_xpath = overzicht_bekijken_xpath
                submenu_xpath = ledenlijst_xpath
            elif menu_item == 'lidaanmelden':
                mainmenu_xpath = leden_xpath
                submenu_xpath = leden_lid_aanmelden
            else:
                raise Exception("Invalid menu item chosen: " + menu_item)

            time.sleep(1)
            self.browser.find_element_by_xpath(mainmenu_xpath).click()

            time.sleep(1)
            self.browser.find_element_by_xpath(submenu_xpath).click()

        except Exception as e:
            raise Exception("Menu navigeren naar " + menu_item + "in NAS mislukt: " + str(e))

    def grab_data_from_ledenlijst_page(self) -> str:
        """ Leest ledenlijst data van de pagina

        :return: JSON string
        """

        try:
            time.sleep(1)
            self.browser.find_element_by_link_text('overzicht op het scherm »»').click()

            time.sleep(1)
            leden_table_xpath = '//*[@id="tekstContainer"]/tbody/tr/td/table'
            leden_table = self.browser.find_element_by_xpath(leden_table_xpath)

            lines = leden_table.text.replace('   ', '|').split('\n')  # op de site staan 3 spaties tussen iedere kolom

            headers = ["Nr"]  # De header van de eerste kolom bevat spaties daarom voegen we hem zelf toe aan de header lijst

            h = lines[0].strip().split(' ')  # de eerste rij is anders. spaties + 'Bondsnr'
            headers.append(h[1])
# hier zip onderzoeken
            for i in range(1, len(lines) - 1):  # de andere rijen bevatten een header
                h = lines[i].strip().split(' ')  # de naam header bevat gek karakter. Daarom split op spatie
                if h[0][0] == '1':  # Als de regel met 1 begint zijn de headers voorbij dus stopprn
                    break
                headers.append(h[0])  # het gekke teken zit in h[1] dus die wordt nu genegeerd

            rows = []
            for line in lines:
                colums = line.split('|')  # regels worden gesplitst in kolommen
                if len(colums) <= 2:  # de headers zitten ook in regels. Hiermee slaan we ze over
                    continue
                mydict = {}  # we maken een dict van de kolommen
                for i in range(1, len(headers)):
                    mydict[headers[i]] = colums[i]

                rows.append(mydict)  # we maken een array van dictionaries
            return json.dumps(rows)

        except Exception as e:
            raise Exception("Parsen NAS leden tabel mislukt: " + str(e))

    def meldt_lid_aan(self, memberdata: dict) -> None:
        """ Voegt een lid toe aan het NAS

        :return: None
        """

        radio_vrouw = '//*[@id="tekstContainer"]/tbody/tr/td/form/table/tbody/tr[11]/td[3]/input[2]'
        radio_man = '//*[@id="tekstContainer"]/tbody/tr/td/form/table/tbody/tr[11]/td[3]/input[1]'
        radio_cg = '//*[@id="tekstContainer"]/tbody/tr/td/form/table/tbody/tr[4]/td[3]/input[1]'
        radio_niet_cg = '//*[@id="tekstContainer"]/tbody/tr/td/form/table/tbody/tr[4]/td[3]/input[2]'

        try:
            self.dict = self.__add_missing_entries_to_dict(memberdata)

            self.browser.find_element_by_link_text('volgende »»').click()

            self.browser.find_element_by_name('achternaam').send_keys(self.dict['Achternaam'])
            self.browser.find_element_by_name('voorvoegsel').send_keys(self.dict['Voorvoegsel'])
            self.browser.find_element_by_name('voorletters').send_keys(self.dict['Voorletters'])
            self.browser.find_element_by_name('voornaam').send_keys(self.dict['Voornaam'])
            self.browser.find_element_by_name('dag').send_keys(self.dict['Dag'])
            self.browser.find_element_by_name('maand').send_keys(self.dict['Maand'])
            self.browser.find_element_by_name('jaar').send_keys(self.dict['Jaar'])

            if self.dict['Geslacht'] == 'V':
                self.browser.find_element_by_xpath(radio_vrouw).click()
            else:
                self.browser.find_element_by_xpath(radio_man).click()
            self.browser.find_element_by_link_text('volgende »»').click()

            time.sleep(1)
            self.browser.find_element_by_link_text('volgende »»').click()  # Land invullen

            time.sleep(1)
            self.browser.find_element_by_name('postcode').send_keys(self.dict['Postcode'])
            self.browser.find_element_by_name('huisnr').send_keys(self.dict['Huisnr'])
            self.browser.find_element_by_link_text('volgende »»').click()

            time.sleep(1)
            self.browser.find_element_by_link_text('volgende »»').click()

            time.sleep(1)
            tel = self.browser.find_element_by_name('telefoon')
            tel.clear()
            tel.send_keys(self.dict['Telefoon'])
            mob = self.browser.find_element_by_name('mobiel')
            mob.clear()
            mob.send_keys(self.dict['Mobiel'])
            self.browser.find_element_by_name('email').send_keys(self.dict['Email'])
            self.browser.find_element_by_link_text('volgende »»').click()

            time.sleep(1)
            if self.dict['CG'] == 'J':
                self.browser.find_element_by_xpath(radio_cg).click()
            else:
                self.browser.find_element_by_xpath(radio_niet_cg).click()
            self.browser.find_element_by_link_text('volgende »»').click()

        except Exception as e:
            raise Exception("Toevoegen lid in NAS mislukt: " + str(e))

    def __add_missing_entries_to_dict(self, member_dict:dict) -> dict:
        """ Sommige gegevens die nodig zijn om een lid aan NAS toe te voegen zitten niet in onze eigen admin.
        Daarom leiden we ze hier af.

        :return: dict
        """
        try:
            self.dict = member_dict
            self.dict['Voorletters'] = member_dict['Voornaam'][0].upper() + '.'
            self.dict['Dag'] = member_dict['GeboorteDatum'].split('-')[0]
            self.dict['Maand'] = member_dict['GeboorteDatum'].split('-')[1]
            self.dict['Jaar'] = member_dict['GeboorteDatum'].split('-')[2]
            self.dict['Postcode'] = member_dict['Postcode'].replace(' ', '')
            r = member_dict['Adres'].split(' ')
            self.dict['Huisnr'] = r[len(r) - 1]
            return self.dict

        except Exception as e:
            raise Exception("Toevoegen lid in NAS mislukt: " + str(e))

    def __del__(self):
        self.browser.close()
