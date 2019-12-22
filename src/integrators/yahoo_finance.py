import pandas as pd
import moment

# by date
# https://finance.yahoo.com/calendar/earnings?from=2019-12-22&to=2019-12-28&day=2019-12-23

# by ticker
# https://finance.yahoo.com/calendar/earnings?symbol=rost

earnings_format_date = {
	'Symbol': 'ticker',					# Short-form name of the company releasing earnings
	'Company': 'company',				# Long-form name of the company releasing earnings
	'Earnings Call Time': 'callTime',	# The expected time for the earnings call to take place
										# Note: this is different than the datetime returned from the ticker endpoint... see earnings_format_ticker.releaseDate
	'EPS Estimate': 'epsEstimate',		# An earnings estimate is an analyst's estimate for a company's future quarterly or annual earnings per share 
	'Reported EPS': 'epsReported',		# Earnings per share (EPS) is calculated as a company's profit divided by the outstanding shares of its common stock
										# The higher a company's EPS, the more profitable it is considered
	'Surprise(%)': 'surprisePercent'	# An earnings surprise occurs when a company's reported quarterly or annual profits are above or below analysts' expectations
}

# Earnings Call Time
# 	Before Market Open
# 	After Market Close
# 	TAS (Transfer Agent System) -- https://www.sec.gov/fast-answers/answerstransferagenthtm.html
#	Time Not Supplied

earnings_format_ticker = earnings_format_date
del earnings_format_ticker['Earnings Call Time']
earnings_format_date['Earnings Call Time'] = 'callTime'

# this is a value which will almost always be in
# the past, but for bigger companies can be provided
# much further in advance
earnings_format_ticker['Earnings Date'] = 'releaseTime'

date_format = 'YYYY-MM-DD'


def get_earnings_calendar_by_day(date=None):
	# the api only returns values if you give it a range of at
	# least 3 days even if only looking at a day of data
	start = moment.date(date).subtract(day=1).format(date_format)
	end = moment.date(date).add(day=1).format(date_format)

	earnings_link = 'https://finance.yahoo.com/calendar/earnings?from={}&to={}&day={}'.format(start, end, date)
	print(earnings_link)

	tables = pd.read_html(earnings_link)
	earnings_calendar = tables[0]

	earnings_calendar.rename(columns=earnings_format_date, inplace=True)
	del earnings_calendar['company']

	return earnings_calendar.to_json(orient='records')


def get_earnings_calendar_by_ticker(ticker=None):
	earnings_link = 'https://finance.yahoo.com/calendar/earnings?symbol={}'.format(ticker)
	print(earnings_link)

	tables = pd.read_html(earnings_link)
	earnings_calendar = tables[0]

	earnings_calendar.rename(columns=earnings_format_ticker, inplace=True)
	del earnings_calendar['company']

	# reformat the release time to a unix timestamp
	earnings_calendar['releaseTime'] = earnings_calendar['releaseTime'].apply(lambda x: moment.date(x.replace('EST', ' EST')).date)

	return earnings_calendar.to_json(orient='records')