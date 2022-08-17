import requests
import json
import time
import logging
import sys

log = logging.getLogger()
log.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
streamHandler = logging.StreamHandler(sys.stdout)
log.addHandler(streamHandler)

pipelines_url = "http://localhost:8080/pipelines"
headers = {"Content-Type": "application/json"}


def check_pipeline_server():
    """
    Checks the status of the running Pipeline Server.
    Tries for 20 Seconds for Pipeline Server to come up.
    """
    exit_count = 0
    while True:
        time.sleep(1)
        exit_count += 1
        try:
            response = requests.request("GET", pipelines_url, headers=headers)
            log.info(
                "Checking the status of pipeline server : {}".format(
                    response.status_code
                )
            )
            if response.status_code == 200:
                log.info("\n*** Running default Pipeline ***\n")
                return True

        except Exception as e:
            if exit_count > 20:
                log.error("Pipeline Server APIs not available {}. Exiting ".format(e))
                return False
            continue


def trigger_pipelines():
    """
    Get the URLs and Payload specified in the configuration File.
    """
    try:
        data = json.load(open("config.json", "r"))
        pipelines = data["configs"]
        for pipeline in pipelines:
            pipeline_version = pipeline["pipeline_version"]
            pipeline_name = pipeline["pipeline"]
            payload = pipeline["payload"]
            url = "{0}/{1}/{2}".format(pipelines_url, pipeline_name, pipeline_version)
            log.info("Pipeline request URL : {0}\n".format(url))
            log.info(
                "Pipeline request Payload :\n {} \n".format(
                    json.dumps(payload, indent=4, sort_keys=True)
                )
            )
            response = requests.request(
                "POST", url, headers=headers, data=json.dumps(payload)
            )
            log.info("Pipeline ID : {}".format(response.text))
    except (ValueError, FileNotFoundError) as err:
        log.error("Configuration file is not correct, {}. Exiting.".format(err))


def main():
    """
    Function to trigger the default Pipeline.
    """
    if check_pipeline_server():
        trigger_pipelines()
    else:
        sys.exit()


if __name__ == "__main__":
    main()
