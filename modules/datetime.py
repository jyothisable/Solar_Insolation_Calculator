
def convert(date, time):
    '''
    time from IST to time in UTC
    nth day of the year to DDMMMYYYY_HHMM
    '''
    # convert time format  # todo use datetime module to do this
    t = int(time*100)-550
    min = str(int(((t % 100)/100)*60))
    if min == '0':
        min = '00'
    time_UTC = '0'+str(t//100) + min if t//100 < 10 else str(t//100) + min

    d = int(day)
    if d <= 31:
        d = str(d) + 'JAN'
    elif d <= 60:
        d = str(d - 31) + 'FEB'
    elif int(day) <= 91:
        d = str(d - 60) + 'MAR'
    if len(d) == 4:
        d = '0'+str(d)

    return d+'2020_' + time_UTC
