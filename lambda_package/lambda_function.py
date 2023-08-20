
import os
import asyncio
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

async def get_content_async(document_id):
    creds = Credentials.from_service_account_file('get-survey-c8bf2f366d30.json', scopes=[
        'https://www.googleapis.com/auth/documents',
        'https://www.googleapis.com/auth/drive'
    ])
    service = build('docs', 'v1', credentials=creds)
    document = service.documents().get(documentId=document_id).execute()
    content = document['body']['content'][0]['paragraph']['elements'][0]['textRun']['content']
    return content.strip()

async def set_content_async(document_id, updated_content):
    creds = Credentials.from_service_account_file('get-survey-c8bf2f366d30.json', scopes=[
        'https://www.googleapis.com/auth/documents',
        'https://www.googleapis.com/auth/drive'
    ])
    service = build('docs', 'v1', credentials=creds)
    requests = [{
        'deleteContentRange': {
            'range': {
                'start_index': 1,
                'end_index': len(updated_content) + 1
            }
        }
    }, {
        'insertText': {
            'location': {
                'index': 1
            },
            'text': updated_content
        }
    }]
    service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()

def lambda_handler(event, context):
    headers = {
        'Access-Control-Allow-Headers': 'content-type',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,HEAD',
        'Access-Control-Allow-Credentials': True
    }

    # Preflight request. Reply successfully:
    if event['httpMethod'] == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': 'preflight successful'
        }

    # Extract document_id from the request
    document_id = event.get('queryStringParameters', {}).get('document_id') if event['httpMethod'] == 'GET' else json.loads(event.get('body', '{}')).get('document_id')
    if not document_id:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps('No document_id provided in the request')
        }

    if event['httpMethod'] == 'GET':
        loop = asyncio.get_event_loop()
        content = loop.run_until_complete(get_content_async(document_id))
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(content)
        }
    
    if event['httpMethod'] == 'POST' and 'body' in event:
        body = json.loads(event['body'])
        if 'text' not in body:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps('No text provided in the request body')
            }
        updated_content = body['text']
        loop = asyncio.get_event_loop()
        loop.run_until_complete(set_content_async(document_id, updated_content))
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps('Content updated in Google Doc')
        }
    return {
        'statusCode': 400,
        'headers': headers,
        'body': json.dumps('Invalid request method')
    }
