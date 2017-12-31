# Use this to fetch the prices of various cryptocurrencies at the timestamps you provide.
#
# This could be used to determine the price of trades you made if you're missing that data, for tax purposes, maybe.
#
# To use, just run it, but make sure you create folders called files_to_read and files_written in its directory.
# The format for files in files_to_read/, that you should populate, are CSV files that have the 3-letter code for the
# cryptocurrency you want the price of and the unix time that you want it for.
# e.g.
# BTC,1509719100
# ETH,1482741480
# ETH,1480149480
# BCH,1509719100
# LTC,1448527080
# ...
# The result is a CSV file with the same name in files_written/ that appends a column to each row with the prices
# in USD those cryptocurrencies were worth at those times. If you would like something other than USD, you can
# change the hardcoded 'USD' values below.
#
# This file does not compute the unix time for you. I personally used openoffice for that.
# This is the formula I used: =(B11 - DATEVALUE("1/1/1970"))*86400
# There exist simple bash commands to do this as well.
#
# It uses cryptocompare's api to fetch the prices. Using this, prices should be accurate within 2 hours.
# I haven't seen any other apis that offer better resolution.
#
#
# Copy, edit, and redistribute at your will.
# I provide no guarantees nor hold no responsibility for anything related to this code.
# Some bullshit license reference goes here.
#
import requests
import os

# Get the absolute paths to the folders
script_dir = os.path.dirname(__file__)

read_folder = 'files_to_read/'
read_folder_path = os.path.join(script_dir, read_folder)

write_folder = 'files_written/'
write_folder_path = os.path.join(script_dir, write_folder)

# Loop through the files in files_to_read/
for filename in os.listdir(read_folder_path):
    print 'reading: ' + filename

    data = []

    with open(read_folder + '/' + filename, 'r') as fo:
        # Loop through each line of a file
        for line in fo:
            lineContents = line.strip().split(',')

            # Form the URL for the request to get the price with the line's data
            histohour_url = 'https://min-api.cryptocompare.com/data/histohour?fsym=' + lineContents[0] + '&tsym=USD&toTs=' + lineContents[1] + '&limit=1'
            histohour_page = requests.get(histohour_url)
            # Parse the data out of the response
            histohour_json = histohour_page.json()
            data_json = histohour_json['Data']
            # The responses include data for 2 time durations, and these times appear to straddle the time you request.
            # Use the average of the low and high price for the 2 time durations provided in the response
            average_of_histo_hours = (data_json[0]['low'] + data_json[0]['high'] +
                                      data_json[1]['low'] + data_json[1]['high']) / 4

            # (Temporary?) For now, compare with the daily historical price
            pricehistorical_url = 'https://min-api.cryptocompare.com/data/pricehistorical?fsym=' + lineContents[0] + '&tsyms=USD&PriceHistoricalCalculationType=MidHighLow&ts=' + lineContents[1]
            pricehistorical_page = requests.get(pricehistorical_url)
            pricehistorical_json = pricehistorical_page.json()

            day_average_price = pricehistorical_json[lineContents[0]]['USD']
            print str(average_of_histo_hours) + " " + str(day_average_price) + " " + str(average_of_histo_hours-day_average_price)

            # Save the data so it can be written to a file after we finish reading this file.
            data.append([lineContents[0], lineContents[1], average_of_histo_hours, day_average_price])

    # Write the new file with the old and new data
    with open(write_folder + '/' + filename, 'w') as wf:
        print 'writing: ' + filename
        wf.write('code,unixtime,price(accurate ~2 hours),price(accurate ~day)\n')
        for line in data:
            for item in line:
                wf.write('%s,' % item)
            wf.write('\n')

    print filename + ' written'



