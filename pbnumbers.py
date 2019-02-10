# Global imports
import urllib.request
import json
import datetime
from bs4 import BeautifulSoup as bs

# Global Vars
year = datetime.datetime.now().year

def logmsg(msg):
    log_time = datetime.datetime.now().strftime("%Y-%m-%d - %X")
    # Log File extension is only year and month since only ran twice a week
    log_file_date = datetime.datetime.now().strftime("%Y%m")
    
    with open("pbnumbers.{}".format(log_file_date), 'a') as f:
        log_msg = log_time + "\t" + msg + "\n"
        f.write(log_msg)

def latest_drawing():

    logmsg("Obtaining latest drawing.")
    numbers = []
    powerballs = []
    dates = []
    tmp = []
    out = {}

    url = "https://www.lottonumbers.com/powerball"
    
    # Set variable to HTML
    logmsg("Opening {}.".format(url))
    raw_html = urllib.request.urlopen(url)
    
    # Create BS object for parsing
    logmsg("Creating BS object for parsing.")
    html = bs(raw_html, features='html.parser')
    
    logmsg("Looping through HTML to find data.")
    for li in html.find('ul', class_='balls -lg -cn').find_all('li'):
        if not li.get('class'):
            tmp.append(li.get_text().strip())
        elif li.get('class')[0] == 'powerball':
            powerballs.append(li.get_text().strip())
        elif li.get('class')[0] == 'power-play':
            pass
    
    # Reformat numbers into groups of five
    logmsg("Reformatting numbers into groups of five.")
    for num in range(0, len(tmp), 5):
        numbers.append(tmp[num:num+5])

    # Get Draw Dates
    logmsg("Looing through HTML to find date.")
    for new_date in html.select('td[colspan]'):
        if 'Wednesday' in new_date.text.strip() or 'Saturday' in new_date.text.strip():
            # Date Number:
            dnum = new_date.text.strip().split(' ')[1][0:-2]
            # Month:
            mon = new_date.text.strip().split(' ')[2]
            month = {'January': '01', 'February': '02', 'March': '03', 'April': '04',
                     'May': '05', 'June': '06', 'July': '07', 'August': '08',
                     'September': '09', 'October': '10', 'November': '11', 'December': '12'}
            # Format date to match others:
            form_date = "{0}{1}{2}{1}{3}".format(year, '-', month[mon], dnum.zfill(2))
            dates.append(form_date)

    # Put them all together
    logmsg("Adding found numbers to dictionary.")
    for item in range(len(powerballs)):
        out[dates[item]] = {"numbers": "-".join(numbers[item]), "powerball": powerballs[item]}
    
    logmsg("Returning Dictionary for processing.")
    return out

def load_drawings():
    # Open numbers.json and load to variable
    logmsg("Opening numbers.json to compare new numbers with.")
    with open('numbers.json') as f:
        data = json.load(f)

    logmsg("Returning json data for processing.")
    return data

def check_numbers(new, old):
    # Iterate through new dict
    logmsg("Checking if new values exist in saved data.")
    for i in new:
        # If 'new' date is in old data
        if i in old:
            logmsg("Date ({}) found in saved data.".format(i))
            pass
        # If 'new' date is not in old data
        else:
            # Add new to old
            logmsg("Date ({}) not found in saved data. Adding to dictionary.".format(i))
            for i in new:
                old[i] = new[i]

            # Write new dict to numbers.json
            logmsg("Writing new date and data to dictionary.")
            with open('numbers.json', 'w') as f:
                json.dump(old, f, sort_keys=True, indent=2)
            
# Main entry point
if __name__ == "__main__":
    # Get latest drawing from www.lottonumbers.com
    new_numbers = latest_drawing()
    # Get old/saved numbers
    saved_numbers = load_drawings()
    # Check if new numbers in old numbers and add if not
    check_numbers(new_numbers, saved_numbers)