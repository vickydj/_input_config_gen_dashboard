import sys
import os
import splunk.Intersplunk
import json
import logging

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
    
    

def stream(results, keywords, argvals):
    logger.info("Stream function called")
    try:
        dashboard_payload = parse_args(results, keywords, argvals)
        
        dashboard_payload = json.dumps(dashboard_payload, indent=2)
        logger.debug(f"Message: {dashboard_payload}")

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
