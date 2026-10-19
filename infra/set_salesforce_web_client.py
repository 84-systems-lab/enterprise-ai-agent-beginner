"""Store web client credentials through no-echo prompts, only in a book secret."""
import argparse
import getpass
import json
import re
import boto3

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--secret-id',required=True)
    args=parser.parse_args()
    if not re.fullmatch(r'eos-book-[a-z0-9-]+/salesforce-web-client-dev',args.secret_id):
        raise SystemExit('The target must be a new eos-book web-client secret name.')
    print('Verify the active AWS profile and account before entering credentials.')
    client_id=getpass.getpass('Salesforce Consumer Key (hidden): ').strip()
    client_secret=getpass.getpass('Salesforce Consumer Secret (hidden): ').strip()
    if not client_id or not client_secret: raise SystemExit('Both values are required.')
    boto3.client('secretsmanager').put_secret_value(SecretId=args.secret_id,
        SecretString=json.dumps({'client_id':client_id,'client_secret':client_secret}))
    print('Credential stored. Values were not printed.')
if __name__=='__main__': main()
