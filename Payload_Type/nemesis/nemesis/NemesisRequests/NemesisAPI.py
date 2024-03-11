from mythic_container.MythicCommandBase import *
from nemesis.NemesisRequests.NemesisAPIClasses import *
from mythic_container.MythicRPC import *
from gql import gql
from datetime import datetime, timedelta

NEMESIS_USERNAME = "NEMESIS_USERNAME"
NEMESIS_PASSWORD = "NEMESIS_PASSWORD"


def check_valid_values(username, password, url) -> bool:
    if username == "" or username is None:
        logger.error("missing username")
        return False
    if password == "" or password is None:
        logger.error("missing password")
        return False
    if url == "" or url is None:
        logger.error("missing url")
        return False
    return True


def convert_timestamp(timestamp, days_to_add=0):
    """
    Strips off the microseconds from a timestamp and reformats to our unified format.

    **Parameters**

    ``timestamp``
        The timestamp string to reformat.

    **Returns**

    A reformatted timestamp string.
    """

    dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")

    if days_to_add != 0:
        dt = dt + timedelta(days=days_to_add)

    return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")


async def query_graphql(taskData: PTTaskMessageAllData, query: gql, uri: str = '/hasura/v1/graphql',
                        variable_values: dict = None) -> (int, dict):
    username = None
    password = None
    url = None
    for buildParam in taskData.BuildParameters:
        if buildParam.Name == "URL":
            url = buildParam.Value
    if NEMESIS_USERNAME in taskData.Secrets:
        username = taskData.Secrets[NEMESIS_USERNAME]
    if NEMESIS_PASSWORD in taskData.Secrets:
        password = taskData.Secrets[NEMESIS_PASSWORD]
    if not check_valid_values(username, password, url):
        return 500, f"Missing {NEMESIS_USERNAME} or {NEMESIS_PASSWORD} in User settings or missing Nemesis URL"
    try:
        credentials = Credentials(username=username, password=password)
        client = NemesisClient(url=url.rstrip("/") + uri, credentials=credentials)
        response = await client.graphql_query(query=query, variable_values=variable_values)
        logger.info(f"Nemesis Query: {uri}")
        if response is not None:
            return 200, response
        else:
            return 500, client.last_error
    except Exception as e:
        logger.exception(f"[-] Failed to query Nemesis: \n{e}\n")
        raise Exception(f"[-] Failed to query Nemesis: \n{e}\n")


async def post_data_api(taskData: PTTaskMessageAllData, data: dict) -> (int, dict):
    username = None
    password = None
    url = None
    for buildParam in taskData.BuildParameters:
        if buildParam.Name == "URL":
            url = buildParam.Value
    if NEMESIS_USERNAME in taskData.Secrets:
        username = taskData.Secrets[NEMESIS_USERNAME]
    if NEMESIS_PASSWORD in taskData.Secrets:
        password = taskData.Secrets[NEMESIS_PASSWORD]
    if not check_valid_values(username, password, url):
        return 500, f"Missing {NEMESIS_USERNAME} or {NEMESIS_PASSWORD} in User settings or missing Nemesis URL"
    try:
        credentials = Credentials(username=username, password=password)
        client = NemesisClient(url=url.rstrip("/"), credentials=credentials, graphql=False)
        response = await client.nemesis_post_data(data=data)
        if response is not None:
            return 200, response
        else:
            return 500, client.last_error
    except Exception as e:
        logger.exception(f"[-] Failed to post data to Nemesis: \n{e}\n")
        raise Exception(f"[-] Failed to post data to Nemesis: \n{e}\n")


async def post_file_api(taskData: PTTaskMessageAllData, file_bytes: bytes) -> (int, str):
    username = None
    password = None
    url = None
    for buildParam in taskData.BuildParameters:
        if buildParam.Name == "URL":
            url = buildParam.Value
    if NEMESIS_USERNAME in taskData.Secrets:
        username = taskData.Secrets[NEMESIS_USERNAME]
    if NEMESIS_PASSWORD in taskData.Secrets:
        password = taskData.Secrets[NEMESIS_PASSWORD]
    if not check_valid_values(username, password, url):
        return 500, f"Missing {NEMESIS_USERNAME} or {NEMESIS_PASSWORD} in User settings or missing Nemesis URL"
    try:
        credentials = Credentials(username=username, password=password)
        client = NemesisClient(url=url.rstrip("/"), credentials=credentials, graphql=False)
        response = await client.nemesis_post_file(file_bytes=file_bytes)
        if response is not None:
            return 200, response
        else:
            return 500, client.last_error
    except Exception as e:
        logger.exception(f"[-] Failed to post file to Nemesis: \n{e}\n")
        raise Exception(f"[-] Failed to post file to Nemesis: \n{e}\n")


async def process_standard_response(response_code: int, response_data: any,
                                    taskData: PTTaskMessageAllData, response: PTTaskCreateTaskingMessageResponse) -> \
        PTTaskCreateTaskingMessageResponse:
    if response_code == 200:
        await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
            TaskID=taskData.Task.ID,
            Response=json.dumps(response_data).encode("UTF8"),
        ))
        response.Success = True
    else:
        await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
            TaskID=taskData.Task.ID,
            Response=f"{response_data}".encode("UTF8"),
        ))
        response.TaskStatus = "Error: Nemesis Query Error"
        response.Success = False
    return response
