# https://api.nasdaq.com/api/calendar/earnings?date=2019-12-23

# example response
# {
#   "data": {
#     "headers": {
#       "lastYearRptDt": "Last Year's Report Date",
#       "lastYearEPS": "Last year's EPS*",
#       "time": "Time",
#       "symbol": "Symbol",
#       "name": "Company Name",
#       "marketCap": "Market Cap",
#       "fiscalQuarterEnding": "Fiscal Quarter Ending",
#       "epsForecast": "Consensus EPS* Forecast",
#       "noOfEsts": "# of Ests"
#     },
#     "rows": [
#       {
#         "lastYearRptDt": "12/11/2018",
#         "lastYearEPS": "($0.12)",
#         "time": "time-not-supplied",
#         "symbol": "PVTL",
#         "name": "Pivotal Software, Inc.",
#         "marketCap": "$4,216,602,795",
#         "fiscalQuarterEnding": "Oct/2019",
#         "epsForecast": "($0.11)",
#         "noOfEsts": "1"
#       },
#       {
#         "lastYearRptDt": "11/06/2018",
#         "lastYearEPS": "($1.51)",
#         "time": "time-not-supplied",
#         "symbol": "NIO",
#         "name": "NIO Inc.",
#         "marketCap": "$2,753,093,463",
#         "fiscalQuarterEnding": "Sep/2019",
#         "epsForecast": "($0.42)",
#         "noOfEsts": "1"
#       },
#       {
#         "lastYearRptDt": "NA",
#         "lastYearEPS": "NA",
#         "time": "time-not-supplied",
#         "symbol": "BRMK",
#         "name": "Broadmark Realty Capital Inc.",
#         "marketCap": "$1,630,380,742",
#         "fiscalQuarterEnding": "Sep/2019",
#         "epsForecast": "",
#         "noOfEsts": "0"
#       },
#       {
#         "lastYearRptDt": "NA",
#         "lastYearEPS": "($0.18)",
#         "time": "time-not-supplied",
#         "symbol": "CTXR",
#         "name": "Citius Pharmaceuticals, Inc.",
#         "marketCap": "$17,323,579",
#         "fiscalQuarterEnding": "Sep/2019",
#         "epsForecast": "($0.12)",
#         "noOfEsts": "2"
#       }
#     ]
#   },
#   "message": null,
#   "status": {
#     "rCode": 200,
#     "bCodeMessage": null,
#     "developerMessage": null
#   }
# }