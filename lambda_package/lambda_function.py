import os
import asyncio
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

async def append_text_async(document_id, text_to_append):
    creds = Credentials.from_service_account_file('get-survey-c8bf2f366d30.json', scopes=[
        'https://www.googleapis.com/auth/documents',
        'https://www.googleapis.com/auth/drive'
    ])
    service = build('docs', 'v1', credentials=creds)

    document = service.documents().get(documentId=document_id).execute()

    requests = [
        {
            'insertText': {
                'location': {
                    'index': document['body']['content'][-1]['endIndex']-1,
                },
                'text': text_to_append
            }
        }
    ]

    service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()

def lambda_handler(event, context):
    headers = {
        'Access-Control-Allow-Headers': 'content-type',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,HEAD',
        'Access-Control-Allow-Credentials' : True
    }

    # Preflight request. Reply successfully:
    if event['httpMethod'] == 'OPTIONS' :
        return {
            'statusCode': 200,
            'headers': headers,
            'body': 'preflight successful'
        }

    # Check if 'body' is in the event and try to extract 'text' and 'document_id'
    if 'body' not in event:
        print("No 'body' in event")
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps('No body provided in the request')
        }
    else:
        body = json.loads(event['body'])
        if 'text' not in body or 'document_id' not in body:
            print("No 'text' or 'document_id' in body")
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps('No text or document_id provided in the request body')
            }
        else:
            text_to_append = body['text']
            document_id = body['document_id']
            loop = asyncio.get_event_loop()
            loop.run_until_complete(append_text_async(document_id, text_to_append))

            message = "Text added to Google Doc file"
            print(message)
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps(message)
            }