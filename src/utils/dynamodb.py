import boto3

dynamodb = boto3.resource('dynamodb')

table = dynamodb.create_table(
    TableName='document-information',
    KeySchema=[
        {
            'AttributeName': 'Type',
            'KeyType': 'String'
        },
        {
            'AttributeName': 'Amendment',
            'KeyType': 'Boolean'
        },
        {
            'AttributeName': 'PeriodEnd',
            'KeyType': 'Date'
        },
        {
            'AttributeName': 'FiscalYear',
            'KeyType': 'String'
        },
        {
            'AttributeName': 'FiscalPeriod',
            'KeyType': 'String'
        },
        {
            'AttributeName': 'CompanyTicker',
            'KeyType': 'String'
        },
        {
            'AttributeName': 'CompanyName',
            'KeyType': 'String'
        },
        {
            'AttributeName': 'CompanyCIK',
            'KeyType': 'String'
        },
        {
            'AttributeName': 'FiscalYearEndDate',
            'KeyType': 'Date'
        },
        {
            'AttributeName': 'IsSeasonedIssuer',
            'KeyType': 'Boolean'
        },
        {
            'AttributeName': 'IsCurrentReportingStatus',
            'KeyType': 'Boolean'
        },
        {
            'AttributeName': 'IsVoluntary',
            'KeyType': 'Boolean'
        },
        {
            'AttributeName': 'CompanyCategory',
            'KeyType': 'String'
        },
        {
            'AttributeName': 'IsCompanySmall',
            'KeyType': 'Boolean'
        },
        {
            'AttributeName': 'IsStartup',
            'KeyType': 'Boolean'
        },
        {
            'AttributeName': 'IsShell',
            'KeyType': 'Boolean'
        }
    ]
)