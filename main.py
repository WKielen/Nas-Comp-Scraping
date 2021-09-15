from nas import CompetitionNas
from AgendaItem import AgendaItem, createDatum
import json
import requests
from ttvnapi import TtvnApi
import yaml


def main():
    result = ''
    nas = CompetitionNas()
    print('we gaan de competitie groepen ophalen')
    groepen = nas.get_competition_types()
    for groep in groepen:
        print('de poules ophalen voor groep: ', groep)
        poules = nas.get_teams_in_competition_type(groep)
        for poule in poules:
            print('het programma ophalen voor: ', groep, poule)
            result += nas.get_programs(groep, poule)
    f = open("output.txt", "w")
    f.write(result)
    print(result)


def main2():
    result = ''
    groepen = ["Duo competitie", "Jeugd", "Senioren", "Starters"]
    nas = CompetitionNas()

    for groep in groepen:
        result += nas.get_results(groep)

    f = open("output.txt", "w")
    f.write(result)
    print(result)


def verwerkinput():
    try:
        with open("config.yml", 'r') as ymlfile:
            cfg = yaml.load(ymlfile, Loader=yaml.BaseLoader)
            logondata = cfg['website']
            userid = logondata['userid']
            password = logondata['password']

            other = cfg['other']
            database = other['database']

    except Exception as err:
        print('Read config.yml failed!')
        print(err)
    print('Yaml ingelezen', password)
    # logon to get the token
    api = TtvnApi()
    api.logon(userid, password, database)
    print('ingelogd in database')
    # remove all AgendaItems from type C  (Competitie)
    agendaList = api.getall()

    for agendaItem in agendaList:
        if not agendaItem.get('Type') == 'C':
            continue
        id = agendaItem.get('Id')
        api.delete(id)

    # Add all newly read records to de db
    f = open("data.txt", "r")
    lines = f.readlines()
    for line in lines:
        regel = line[:-1]
        # skip lege regels
        if not regel:  # laatste karakter is eol
            continue
        # nu gaan we kijken of de regel begeint met een wedstrijdnummer
        regelparts = regel.split(' ')
        if not regelparts[0].isdecimal():
            continue
        # staat er TTVN in de regel?
        if not ('TTVN' in regel):
            continue
        if len(regelparts) > 60:
            continue

        agendaitem = AgendaItem()
        agendaitem.Datum = createDatum(regelparts[3], regelparts[4])
        agendaitem.Tijd = regelparts[5]
        thuisteam = regel[24:48].strip()
        uitteam = regel[51:75].strip()

        agendaitem.EvenementNaam = (thuisteam + ' - ' + uitteam).replace(' Nieuwegein', '')
        api.insert(agendaitem)


if __name__ == '__main__':
    verwerkinput()

