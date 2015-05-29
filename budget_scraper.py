### Gaurav Verma
### Wikipedia Budget Scraper
### 5/26/15

from bs4 import BeautifulSoup
from prettytable import PrettyTable
import urllib2
import json
import sys
# coding: utf-8


# Retrieves the live exchange rate from 1 GBP to USD
# Returns a default of 1.5 if a connection cannot be made
def get_pound_to_dollar_rate():
    
    
    try:
        # Connection attempt to Yahoo Finance Exchange Rate API
        reader = urllib2.urlopen('https://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20yahoo.finance.xchange%20where%20pair%20in%20(%22GBPUSD%22)&format=json&diagnostics=true&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys&callback=')
        data = reader.read()
        parsed_data = json.loads(data)
        rate = float(parsed_data['query']['results']['rate']['Rate'])
    except urllib2.URLError:
        # Default rate of 1.5 assigned if no connection made
        rate = 1.5
    

    
    
    return rate

# Function that handles exceptions when trying to convert a string into a float
# Returns the original text if text cannot be converted
# Takes a string as argument and returns either a float or the original string
def convertNumber(text):
    
    try:
        number = float(text)
        return number
    except ValueError:
        return text
    
    

# Helper function to getBudgetNumber that extracts the budget number from a budget text
# Checks whether it is listed in millions, and checks whether listed in dollars or pounds
# Function takes a string as argument and returns a list with a float and two booleans describing
# the number, whether or not the budget is listed in dollars,
# and whether or not it is listed in millions respectively.
# The function returns the original text if no unit of currency is found.
def filterBudgetText(budgetText):
    
    # Searches for $ symbol in budget text
    dollarIndex = budgetText.find('$')
    dollars = True
    millions = True
    

    if (dollarIndex >= 0):
        firstIndex = dollarIndex
    else:
        # If dollar symbol not found, searches for pound symbol
        poundIndex = budgetText.find(u'\u00a3')
        if (poundIndex >= 0):
            firstIndex = poundIndex
            dollars = False
        else:
            #If neither found, assume budget not listed and return original text
            return budgetText
    
    # find where million is listed in the text and
    # return number between currency symbol and million if found
    millionIndex = budgetText.find('million', firstIndex)
    filteredText = ''
    
    if (millionIndex >= 0):
        filteredText = budgetText[(firstIndex+1):(millionIndex-1)]
    else:
        millions = False
        budget = budgetText[firstIndex+1:]

        # Enumerate from the currency symbol to the end of the string
        # and find where the sequence of numbers ends to filter out
        # the rest of the text if not listed in millions
        for index, item  in enumerate(budget):
            character = convertNumber(item)

            if (type(character) != float and character != ','):
                filteredText = budget[:index]
                break
        else:
            filteredText = budgetText[firstIndex+1:]
    
    
    return [filteredText, dollars, millions]

# Extracts dollar value of budget given text from a wikipedia page
# describing the budget (e.g. $2 million, $750,000, 200,000 pounds, etc.)
# Performs conversions necessary if listed in pounds.
# Takes a string as a argument and returns a either a float
# or the original string if no budget is found within the string
def getBudgetNumber(budgetText):
    
    # Helper function that filters the budget text to
    # categorize the formatting of the budget text
    filteredText = filterBudgetText(budgetText)
    
    if (type(filteredText) != list):
        return filteredText
    else:
        number = -999
        # get the number listed in the text
        text = filteredText[0]
        
        #get the boolean value if text is listed in millions
        millions = filteredText[2]
        
        #remove comma groupings in the text
        text = text.replace(',', '')
        number = convertNumber(text)
        
        #get the boolean value if text is listed in dollars
        dollars = filteredText[1]
        
        #make necessary conversions
        if (not millions):
            number = number/(10**6)
        
        if (not dollars):
            number = number * pound_to_dollar_rate
        
        return number

# Helper function for determineAverage that splits
# a string into two numbers if there is a special character between them.
# Takes a string as an argument and returns a list of
# two numbers if they are found
# Returns an empty list if no numbers are found
def findTokens(text):
    i = 0
    j = len(text)-1
    tokens = []
    
    #loop through left side until a non number character is found
    for i in range(len(text)):
        
        character = convertNumber(text[i])
        if (type(character) != float):
            if (i > 0):
                tokens.append( float(text[0:i]))
            
            break
    #loop through right side until a non number character is found
    for j in range(len(text)-1,0,-1):
        character = convertNumber(text[j])
        if (type(character) != float):
            if (j < len(text)-1):
                tokens.append( float(text[j+1:]))
            break

    return tokens

# Determines the average budget in millions of budgets given
# a list of either strings or floats.
# Accounts for cases where a budget may potentially be written in the form of '6-7'
# in which case the the two numbers are averaged to find a numeric value for the budget.
# If a budget was not listed, then it is not counted as part of the average.
# The function returns a float giving the average of the budgets.
def determineAverage(averageTable):
    budgetSum = 0
    total = 0
    for k in averageTable:
        #checks if the listed budget is already a float
        if (type(k) != float):
            # See if string can be easily split into two numbers that can be averaged
            tokens = k.split('-')
            
            if (len(tokens) > 1):
                averageBudget = (float(tokens[0])+float(tokens[1]))/2
                
                budgetSum += averageBudget
                total += 1
            else:
                # Call helper method that splits string into two numbers
                # if a special character is listed between the two numbers
                tokens = findTokens(k)
                
                
                if (len(tokens)):
                    averageBudget = sum(tokens)/len(tokens)
                    
                    budgetSum += averageBudget
                    total+=1
        else:

            budgetSum += k
            total += 1
    
    return [budgetSum/total, total]


# Find the conversion rate for GBP to USD
pound_to_dollar_rate = get_pound_to_dollar_rate()

# Construct the URL for the wikipedia page
mainWikiSite = "https://en.wikipedia.org/wiki/"
academyAwardPage = "Academy_Award_for_Best_Picture"
actionText = "?action=render"

fullSite = mainWikiSite+academyAwardPage+actionText

# Read from wikipedia page, exit if unsuccessful
try:
    siteReader = urllib2.urlopen(fullSite)
except urllib2.URLError:
    print "Cannot connect to Wikipedia site " + fullSite
else:

    siteText = siteReader.read()

    siteReader.close()

    # Utilize BeautifulSoup function to parse HTML file
    siteHTML = BeautifulSoup(siteText)


    #find winners and nominees section
    winnerSection = siteHTML.find(id='Winners_and_nominees')


    winnerSectionParentElement  = winnerSection.parent

    # Get a list of all of the table elements
    # in the winners and nominees section
    movieTables = winnerSectionParentElement.find_next_siblings(class_='wikitable')

    # Create a PrettyTable object with headers
    # Year, Title, and Budget listed in millions of $
    informationTable = PrettyTable(["Year", "Title", "Budget (in $Millions)"])

    numberOfMovies = len(movieTables)
    print "%d Movies Listed" % numberOfMovies

    print "Retrieving..."

    averageTable = []

    # Enumerate through the list of tables
    for index, table in enumerate(movieTables):
        
        

        # Capture movie year from table information and
        # account for listings that have multiple years listed
        movieYears = [yearElement.text for yearElement in  table.caption.big.findAll('a', recursive = False)]
        if (len(movieYears) > 1):
            movieYear = '/'.join(movieYears)
        else:
            movieYear = ''.join(movieYears)

        movieLink = table.findAll('tr')[1].findAll('td')[0].a
        movieTitle = movieLink.text
        movieSite = movieLink['href']
        
        # Create movie page URL
        movieSite = "https:"+movieSite
        
        # Attempt to connect to movie page, handle error if unsuccessful
        try:
            movieSiteReader = urllib2.urlopen(movieSite)
        except urllib2.URLError:
            print "Could not connect to page for movie: " + movieTitle + " at site: " + movieSite
            sys.stdout.flush()
            budgetAmountText = "Could not connect"
        except urllib2.HTTPError:
            print "Page not found for movie: " +movieTitle + " at site: " + movieSite
            sys.stdout.flush()
            budgetAmountText = "Page not found"
        else:
            
            movieSiteText = movieSiteReader.read()
            movieSiteHTML = BeautifulSoup(movieSiteText)
            movieInfoTable = movieSiteHTML.find('table', 'infobox vevent')
            
            # Retrieve budget from main table on movie page, assing default if not listed
            budgetElement = movieInfoTable.find(text = 'Budget')
            if (budgetElement):
                
                budgetAmountText = budgetElement.parent.parent.td.text
            
            else:
                budgetAmountText = "Budget Not Listed"

            movieSiteReader.close()

        # Get a budget number or string depending
        # on budget text listed on wikipedia page
        budget = getBudgetNumber(budgetAmountText)
        information = [movieYear, movieTitle, budget]

        # Add to PrettyTable object
        informationTable.add_row(information)

        # Add budget to list of averages
        averageTable.append(budget)

        # Print counter for keeping track of movie number retrieved
        print index+1,
        sys.stdout.flush()
        

    print
    print informationTable


    average = determineAverage(averageTable)
    print("# Movies used to determine average: %d" % average[1])
    print("The average budget is %f million" % average[0])






