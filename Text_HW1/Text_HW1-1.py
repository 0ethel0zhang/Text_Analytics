
# coding: utf-8

import re
import nltk.data


# # Import special date strings for usage

#days
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
#abbreviated days
s_days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
#abbreviated months
s_months = ['Jan',
 'Feb',
 'Mar',
 'Apr',
 'May',
 'Jun',
 'Jul',
 'Aug',
 'Sept?',
 'Oct',
 'Nov',
 'Dec']
#months
months = ['January',
 'February',
 'March',
 'April',
 'May',
 'June',
 'July',
 'August',
 'September',
 'October',
 'November',
 'December']
#time of day
time_of_day = ['morning','noon','afternoon','evening']
#holidays
holidays = ["New Year's Day",
 'Inauguration Day',
 'Martin Luther King, Jr. Day',
 'George Washington’s Birthday',
 'Memorial Day',
 'Independence Day',
 'Labor Day',
 'Columbus Day',
 'Veterans Day',
 'Thanksgiving Day',
 'Christmas Day']


# # Fixed Dates

# ## Pattern 1:
# - January 15, 2014

pattern_1 = "("+",?\s|".join(days) + ")?"+ "("+"|".join(months + s_months 
                                                           + [x+"." for x in s_months])+")"+"(\s)(\d{1,2}\w{0,2})(,?\s)?(\d{0,4})(,?\s\d{1,2}[ap][.]?m[.]?)?"


pattern_1


# ## Pattern 2:
# - the 21st of December

pattern_2 = "(the "+"\d{2}.." +" of )("+"|".join(months) +")"

pattern_2


# ## Pattern 3:
# - 01/15/2014

pattern_3 = '(0?[1-9]|1[0-2])/(0?[1-9]|[1-2][0-9]|3[0-1])/([1-9]\d{3}|\d{2})'

pattern_3


# ## Pattern 4:

# - 'Monday',
#  'Monday the 23rd',
#  'Monday, 2pm',
#  Monday afternoon

pattern_4 = "("+"|".join(days) + ")(\sthe\s" + "[1-3]\d.{2})?(,?\s\d{1,2}[ap][.]?m[.]?)?" + "(\s?"+"|\s?".join(time_of_day) + ")?"

pattern_4


# # Holidays
# 
# ## Pattern 5

pattern_5 = "("+"|".join(holidays)+")"


pattern_5


# # Test regex with input files

#read file function
def readfile(filename):
    """
    Read a txt file and parse it into a list of lines.
    
    filename (str): the path and name of the input file
    return (lst): non-empty lines in file
    """
    # set tokenizer
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    
    # open file
    try:
        fp = open(filename)
        data = fp.read()
    except:
        fp = open(filename, encoding='iso-8859-1')
        data = fp.read()
    
    #tockenize read file
    text = tokenizer.tokenize(data)
    fp.close()
    
    #break into lines
    lines = []
    for para in text:
        temp = para.splitlines()
        for line in temp:
            if len(line) == 0:
                temp.remove(line)
        lines += temp
        
    return lines


#find dates function
def findDates(lines, filename):
    """
    Find dates that fit into the pre-defined patterns and return a txt file with found dates.
    lines (lst): a list of lines read from a input file
    filename (str): name of output file
    return: None
    """
    # prep for output string
    output = ""
    
    # find dates
    print("Start to find dates\n-------------")
    for line in lines:
        matched = re.findall(pattern_1, line)
        if len(matched) > 0:
            print("".join(list(matched[0])))
            output += "".join(list(matched[0])) + "\n"
        else:
            matched = re.findall(pattern_2, line)
            if len(matched) > 0:
                print("".join(list(matched[0])))
                output += "".join(list(matched[0])) + "\n"
            else:
                matched = re.findall(pattern_3, line)
                if len(matched) > 0:
                    print("/".join(list(matched[0])))
                    output += "/".join(list(matched[0])) + "\n"
                else:
                    matched = re.findall(pattern_4, line)
                    if len(matched) > 0:
                        print("".join(list(matched[0])))
                        output += "".join(list(matched[0])) + "\n"
                    else:
                        matched = re.findall(pattern_5, line)
                        if len(matched) > 0:
                            print("".join(list(matched[0])))
                            output += "".join(list(matched[0])) + "\n"
    
    # write out dates in a txt file
    f = open(filename, 'w')
    f.write(output)
    f.close()
    print("-------------\nFinished writing output file")
    
    return None


# ## input1

#read file
lines = readfile("input.Hw1.txt")
#find dates
findDates(lines, "output.txt")


# ## Input 2

#read file
lines_2 = readfile("input2.txt")

#find dates
findDates(lines_2, "output2.txt")


# ## Input 3

#option to read another file

print("Would you like to test on another file?\nPlease enter the name of the file (with the path if not in current directory).\nOtherwise, enter 'N'.")

new_file = input()

#read and process file

if new_file != "N":
    print("The file is {}".format(new_file))
    try:
        lines_new = readfile(new_file)
        findDates(lines_new, "output_new.txt")
        print("Please fine the output file 'output_new.txt'. Goodbye.")
    except:
        print("Sorry, the file does not exist. Please try again.")
else:
    print("Goodbye.")
