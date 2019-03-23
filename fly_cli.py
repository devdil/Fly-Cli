from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
import requests


cities = {

    "Bangalore" : "BLR",
    "Calcutta" : "CCU"
}

airlines = {
    "Indigo" : "IndiGo",
    "SpiceJet" : "Spicejet",
    "AirIndia" : "Air India",
    "Vistara" : "Vistara",
    "GoAir" : "GoAir",
    "Jet Airways" : "Jet Airways",
    "AirAsia India" : "AirAsia India"
}

token_ibibocommand_map = {
    "from" : "source",
    "to" : "destination",
    "on" : "departure",
    "class" : "seatingclass",
    "adults" : "adults",
    "children" : "children",
    "infants" : "infants",
    "domestic" : "100",
    "international": "0"

}

filters = ['with_airline', 'non_stop']

Options = WordCompleter([u'fly', u'from', u'to', u'on', u'with_airline', u'non_stop', u'order_by', u'adults',\
                         u'children', u'adults']\
                        + map(lambda x: unicode(x, 'utf-8'), cities.keys()) +\
                         map(lambda x: unicode(x, 'utf-8'), airlines.keys()), ignore_case=True)


style = Style.from_dict({
    'completion-menu.completion': 'bg:#008888 #ffffff',
    'completion-menu.completion.current': 'bg:#00aaaa #000000',
    'scrollbar.background': 'bg:#88aaaa',
    'scrollbar.button': 'bg:#222222',
})


def construct_request_url(**kwargs):
    if kwargs:
        keys = kwargs.keys()
        final_kwargs = {}

        # update the new data structure

        for key in keys:
            if key not in token_ibibocommand_map:
                print "Invalid Command {}".format(key)
                return False
            else:
                final_kwargs[token_ibibocommand_map[key]] = kwargs.get(key)

        #update the citi with IATA code

        for item in final_kwargs.keys():
            if item in ['source', 'destination']:
                source_city_name = final_kwargs[item]
                if source_city_name not in cities:
                    print " Source/Destination {} not in database or Invalid source/destination name".format(source_city_name)
                    return
                else:
                    final_kwargs[item] = cities[final_kwargs[item]]


        #return the final url

        api_url = 'http://developer.goibibo.com/api/search/?app_id=61eb1b22&app_key=34b01b047ae88ae6e924855f5c0a522d&format=json' \
                  '&source={source}&destination={destination}&dateofdeparture={departure}&seatingclass=E&adults={adults}&children={children}&infants={infants}&counter=100'.format(**final_kwargs)
        
        return api_url

    else:
        print "Arguments are empty! Cannot proceed with request"

def process_input(input_string):
    """
    Validates and returns the fare charges
    :param input_string: the input string
    :return: fare_charges string
    """
    if input_string:
        tokens = input_string.strip().split(' ')
        token_map = {}

        for token in tokens:
            key, value = token.split('=')
            if key and value:
                token_map[key] = value

        print "Getting information ..."
        constucted_url = construct_request_url(**token_map)

        if constucted_url:

            req = requests.get(constucted_url)
            if req.status_code == 200:
                result = req.json()
                onward_flights = result['data']['onwardflights']
                prettyPrint(onward_flights)
                return
            else:
                print "Failed to contact the flight servers! Try Again"




def prettyPrint(data):
    column_titles = ["Airline", "Seats Available", "Duration", "Fare", "Stops", "Departure Date", "Arrival Date", "Booking Class", "Refundable"]

    total_characters_in_column_titles = reduce(lambda x, y: +x+y , map(lambda x : len(x), column_titles))

    row_items = []

    columns_interested = ['airline', 'seatsavailable', 'duration', 'fare', 'stops', 'depdate', 'arrdate', 'bookingclass', 'warnings']
    nested_keys_interested = ["fare"]

    max_length_per_column = []

    for item in data:

        row_item = []
        for index in xrange(len(columns_interested)):
            if columns_interested[index]  in nested_keys_interested:
                nested_key = columns_interested[index]
                if nested_key == "fare":
                    row_item.append(str(item[nested_key]['totalfare']))
            else:
                row_item.append(item[columns_interested[index]])
            if max_length_per_column:
                max_length_per_column[index] = (max(len(item[columns_interested[index]]), (max_length_per_column[index])))

        row_items.append(row_item)

        if not max_length_per_column:
            max_length_per_column = map(lambda x: len(x), row_item)

    max_length_per_column = map(lambda x: max(max_length_per_column[x], len(column_titles[x])), range(len(column_titles)))

    # 1 for last | and 3 = 1 for | and 2 for spaces before and after the word

    total_characters_in_column_titles = reduce(lambda x, y: x+y, max_length_per_column) + (3 * len(max_length_per_column)) + 1

    print "-" * total_characters_in_column_titles

    formatted_title = ""
    for index in xrange(len(column_titles)):
        formatted_title += "| {}{}".format(column_titles[index], " "*((max_length_per_column[index]-len(column_titles[index]))+1))
    formatted_title += "|"

    print formatted_title

    print "-" * total_characters_in_column_titles

    #show data


    for row_item in row_items:
        formatted_row = ""
        index = 0
        for column in row_item:
            formatted_row += "| {}{}".format(column, " "*((max_length_per_column[index]-len(column))+1))
            index = index + 1
        formatted_row += "|"
        print formatted_row


    #last line
    print "-" * total_characters_in_column_titles



while True:
    # run forever
    user_input = prompt(u'fly>', history=FileHistory('history.txt'), auto_suggest=AutoSuggestFromHistory(),
                        completer=Options, style=style)
    if user_input:
        process_input(user_input)
    else:
        continue

