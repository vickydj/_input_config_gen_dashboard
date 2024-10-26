import sys
import os
import splunk.Intersplunk
import json
import logging
import traceback

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
    }

def execute():
    try:
        logger.info("Executing helloworld command")
        keywords, options = splunk.Intersplunk.getKeywordsAndOptions()

        msg = options.get('msg', '')
        logger.debug(f"Message: {msg}")
        results = [{'message': f"Hello World: {msg}"}]
        splunk.Intersplunk.outputResults(results)
        logger.info("Command executed successfully")
    except Exception as e:
        logger.error(f"Error executing command: {str(e)}", exc_info=True)
        splunk.Intersplunk.generateErrorResults(str(e))

if __name__ == '__main__':
    try:
        logger.info("Script started")
        logger.debug(f"sys.argv: {sys.argv}")

        if(len(sys.argv)>1):
            execute()
        else:
            print("No arguments provided.")
        
        
    except Exception as e:
        error_message = f"Error in script execution: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_message)
        print(error_message)  # This will be captured by Splunk
        sys.exit(1)
