import sys
import os
import splunk.Intersplunk
import json
import logging
import requests

def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(message)s',
        filename=os.path.join(os.environ['SPLUNK_HOME'], 'var', 'log', 'splunk', 'helloworld_command.log'),
        filemode='a'
    )
    return logging.getLogger(__name__)

logger = setup_logging()

def getinfo():
    return {
        'args': ['msg'],
        'description': 'Outputs a hello world message with an optional custom message.',
        'streaming': True
    }

def parse_args(results, keywords, argvals):
    logger.debug(f"Parsing keywords: {keywords}, argvals: {argvals}")

    # Get the first result (assuming there's at least one)
    if results:
        result = results[0]
        if 'payload' in result:
            json_string = result['payload']
            try:
                # Parse the JSON string
                return json.loads(json_string)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON: {json_string}")
            logger.error(f"JSON decode error: {str(e)}")

def post_to_ds(dashboard_payload):
    url = 'https://localhost:8089/servicesNS/-/-/my_rest'
    headers = {'Content-Type': 'application/json'}
    auth = ('admin', 'password')
    params = {'output_mode': 'json'}

    try:
        response = requests.post(
            url,
            headers=headers,
            json={'payload': json.dumps(dashboard_payload)},
            auth=auth,
            params=params,
            verify=False
        )
        response.raise_for_status()
        logger.debug(f"Response from DS: {response.json()}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending payload to DS: {str(e)}", exc_info=True)
        return False

# def post_to_ds(dashboard_payload):
#     logger.info("Posting to DS")
#     try:
#         url = "https://localhost:8088/servicesNS/-/-/my_rest"
#         headers = {
#             "Authorization": "Splunk eyJraWQiOiJzcGx1bmsuc2VjcmV0IiwiYWxnIjoiSFM1MTIiLCJ2ZXIiOiJ2MiIsInR0eXAiOiJzdGF0aWMifQ.eyJpc3MiOiJhZG1pbiBmcm9tIHNvMiIsInN1YiI6ImFkbWluIiwiYXVkIjoic2VsZl9zZXJ2aWNlIiwiaWRwIjoiU3BsdW5rIiwianRpIjoiNGM0Y2YxMTgyMGZhYmNmYjA1NWU3YmI5ZjE3ZmY3Y2Q3NzIzNzA4YjI1NjI2MWZmNDMwNzg5MjBmYTY3ZmM4NCIsImlhdCI6MTcyOTk2MzU5MywiZXhwIjoxNzMyNTU1NTkzLCJuYnIiOjE3Mjk5NjM1OTN9.fF19HAy14m29uEMMoTlv1lGEEuFBrb7ulKbPnrWSlct4OhFWanlXXGr6Y4syLyK0-K1tuYAOaZQtVyFXA1mRBg"
#         }
#         response = requests.post(url, headers=headers, json=dashboard_payload, verify=False)
#         response.raise_for_status()
#         logger.info(f"Successfully posted to DS: {response.status_code}")
#         return response.json()
#     except requests.exceptions.RequestException as e:
#         logger.error(f"Failed to post to DS: {str(e)}", exc_info=True)
#         raise

def stream(results, keywords, argvals):
    logger.info("Stream function called")
    try:
        dashboard_payload = parse_args(results, keywords, argvals)
        
        dashboard_payload = json.dumps(dashboard_payload, indent=2)
        logger.debug(f"Message: {dashboard_payload}")

        sent_payload = post_to_ds(dashboard_payload)
        logger.debug(f"Sent payload: {sent_payload}")


        for result in results:
            result['payload'] = f"dashboard_payload: {dashboard_payload}"
            yield result

    except Exception as e:
        logger.error(f"Error in stream function: {str(e)}", exc_info=True)
        raise

if __name__ == '__main__':
    try:
        logger.info("Script started")
        logger.debug(f"sys.argv: {sys.argv}")
        
        if len(sys.argv) > 1 and (sys.argv[1] == '--getinfo' or sys.argv[1] == '__GETINFO__'):
            logger.info(json.dumps(getinfo()))
            print(json.dumps(getinfo()))
            logger.info("Getinfo executed successfully")
        else:
            logger.info("Executing command in streaming mode")
            results, dummyresults, settings = splunk.Intersplunk.getOrganizedResults()
            keywords, argvals = splunk.Intersplunk.getKeywordsAndOptions()
            streaming_results = list(stream(results, keywords, argvals))
            splunk.Intersplunk.outputResults(streaming_results)
    except Exception as e:
        error_message = f"Error in script execution: {str(e)}"
        logger.error(error_message, exc_info=True)
        print(error_message)  # This will be captured by Splunk
        sys.exit(1)
