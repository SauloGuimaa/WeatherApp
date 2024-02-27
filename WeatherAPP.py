import requests
import json
import datetime
import urllib.parse

accuweatherAPIKey = 'Xh2G5GYoutPXQP7KPAPXGCOrTwunCyi6'
mapboxToken = 'pk.eyJ1Ijoic2F1bG9ndWltYWEiLCJhIjoiY2x0MndyaTI4MXFzNzJqcm83ZGpoZGJ5ZiJ9.C0_Z_7bl2RH89xM5robuXQ'
dias_semana = ['Domingo', 'Segunda-Feira', 'Terça-Feira', 'Quarta-Feira','Quinta-Feira', 'Sexta-Feira', 'Sábado']
def pegarCoordenadas():
    r =requests.get('http://www.geoplugin.net/json.gp')

    if (r.status_code != 200):
        print("Não foi possível obter a localização!")
        return None
    else:
        try:
            localizacao = json.loads(r.text)
            coordenadas = {}
            coordenadas['lat'] = localizacao['geoplugin_latitude']
            coordenadas['long'] = localizacao['geoplugin_longitude']
            return coordenadas
        except:
            return None
def pegarCodigoLocal(lat,long):
    LocationAPIURL = "http://dataservice.accuweather.com/locations/v1/cities/geoposition/" \
                      + "search?apikey=" + accuweatherAPIKey \
                      + "&q=" + lat + "%2C%20" + long + "&language=pt-br"

    r = requests.get(LocationAPIURL)
    if( r.status_code != 200):
        print('Não foi possível obter o código local')
        return None
    else:
        try:
            locationResponse = json.loads(r.text)
            infoLocal = {}
            infoLocal['nomeLocal'] = locationResponse['AdministrativeArea']['EnglishName'] + ", " \
                    + locationResponse['AdministrativeArea']['LocalizedName'] + ". " \
                    + locationResponse['Country']['LocalizedName']
            infoLocal['codigoLocal'] = locationResponse['Key']
            return infoLocal
        except:
            return None
def pegarTempoAgora(codigoLocal, nomeLocal):

    CurrentConditionsAPIUrl = ("http://dataservice.accuweather.com/currentconditions/v1/"
                               + codigoLocal + "?apikey=" + accuweatherAPIKey + "&language=pt-br")
    r = requests.get(CurrentConditionsAPIUrl)
    if (r.status_code != 200):
        print('Não foi possível obter o Clima atual do seu local')
        return None
    else:
        try:
            CurrentConditionsResponse = json.loads(r.text)
            infoClima = {}
            infoClima['textoClima'] = CurrentConditionsResponse[0]['WeatherText']
            infoClima['temperatura'] = CurrentConditionsResponse[0]['Temperature']['Metric']['Value']
            infoClima['nomeLocal'] = nomeLocal
            return infoClima
        except:
            return None
def pegarPrevisao5Dias(codigoLocal):

    DailyAPIUrl = ("http://dataservice.accuweather.com/forecasts/v1/daily/5day/"
                               + codigoLocal + "?apikey=" + accuweatherAPIKey + "&language=pt-br&metric=true")
    r = requests.get(DailyAPIUrl)
    if (r.status_code != 200):
        print('Não foi possível obter o Clima atual do seu local')
        return None
    else:
        try:
            DailyResponse = json.loads(r.text)
            infoClima5dias = []
            for dia in DailyResponse['DailyForecasts']:
                climaDia = {}
                climaDia['Max'] = dia['Temperature']['Maximum']['Value']
                climaDia['Min'] = dia['Temperature']['Minimum']['Value']
                climaDia['Clima'] = dia['Day']['IconPhrase']
                diaSemana = int(datetime.date.fromtimestamp(dia['EpochDate']).strftime('%w'))
                climaDia['Dia'] = dias_semana[diaSemana]
                infoClima5dias.append(climaDia)
            return infoClima5dias
        except:
            return None

def mostrarPrevisao(lat, long):
    try:
        local = pegarCodigoLocal(lat, long)
        climaAtual = pegarTempoAgora(local['codigoLocal'], local['nomeLocal'])
        print('Clima atual em: ' + climaAtual['nomeLocal'])
        print(climaAtual['textoClima'])
        print('Temperatura: ' + str(climaAtual['temperatura']) + "ºC")
    except:
        print('ERRO ao obter clima atual!!')

    opcao = input('\nDeseja ver a previsão para os próximos dias? (s ou n): ').lower()

    if opcao == "s":
        print('\nClima para hoje e para os próximos dias:\n')

        try:
            previsao5dias = pegarPrevisao5Dias(local['codigoLocal'])
            for dia in previsao5dias:
                print(dia['Dia'])
                print('Mínima: ' + str(dia['Min']) + "ºC")
                print('Máxima: ' + str(dia['Max']) + "ºC")
                print('Clima: ' + dia['Clima'])
                print('-------------------------')
        except:
            print('Erro ao obter a previsão para os próximos dias')

def pesquisarLocal(local):
    _local = urllib.parse.quote(local)
    mapboxGeocodeURL = 'https://api.mapbox.com/geocoding/v5/mapbox.places/' \
                        + _local + ".json?access_token=" + mapboxToken

    r = requests.get(mapboxGeocodeURL)
    if (r.status_code != 200):
        print('Não foi possível saber seu local!')
        return None
    else:
        try:
            mapBoxResponse = json.loads(r.text)
            coordenadasMapbox = {}
            coordenadasMapbox['long'] = str(mapBoxResponse['features'][0]['geometry']['coordinates'][0])
            coordenadasMapbox['lat'] = str(mapBoxResponse['features'][0]['geometry']['coordinates'][1])
            return coordenadasMapbox
        except:
            print("Erro na pesquisa do local!!!")

# Início do Programa
try:
    coordenadas = pegarCoordenadas()
    mostrarPrevisao(coordenadas['lat'], coordenadas['long'])

    continuar = 's'

    while continuar == 's':
        continuar = input('\nDeseja consultar a previsão de outro local? (s ou n): ').lower()
        if continuar != 's':
            break
        local = input('Digite a cidade e o estado: ')
        try:
            coordenadasMap = pesquisarLocal(local)
            mostrarPrevisao(coordenadasMap['lat'], coordenadasMap['long'])
        except:
            print('Não foi possível obter a previsão para este local!')

except:
    print('Erro ao processar a solicitação. Entre em contato com o suporte.')