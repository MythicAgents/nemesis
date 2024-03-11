import hmac
import hashlib
import base64
import requests
from requests.auth import HTTPBasicAuth
import datetime
import asyncio
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.exceptions import TransportQueryError
from graphql.error.graphql_error import GraphQLError
from mythic_container.logging import logger

from typing import Optional




class Credentials(object):
    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password


class NemesisClient(object):
    def __init__(self, url: str, credentials: Credentials, graphql: bool = True) -> None:
        self._url = url
        self._credentials = credentials
        self.headers = {
            "User-Agent": f"Nemesis_Agent/1.0",
            "Authorization": "Basic " + base64.b64encode(f"{self._credentials.username}:{self._credentials.password}".encode()).decode("ascii"),
            "Content-Type": "application/json"
        }
        self._graphql = graphql
        if graphql:
            self.transport = AIOHTTPTransport(url=self._url, timeout=10, headers=self.headers)
            self.client = Client(transport=self.transport, fetch_schema_from_transport=False, )
            self.session = None
        self.last_error = ""

    def __del__(self):
        if self._graphql:
            asyncio.create_task(self.client.close_async())

    async def graphql_query(self, query: gql, variable_values: Optional[dict] = None) -> dict[str, any]:
        if self.session is None:
            self.session = await self.client.connect_async(reconnecting=True)
        # Perform the request with the signed and expected headers
        try:
            result = await self.session.execute(query, variable_values=variable_values)
            self.last_error = ""
            return result
        except TimeoutError:
            logger.error(
                "Timeout occurred while trying to connect to Nemesis at %s",
                self._url
            )
            self.last_error = "timeout trying to connect to Nemesis"
            return None
        except TransportQueryError as e:
            logger.exception("Error encountered while fetching GraphQL schema: %s", e)
            payload = e.errors[0]
            self.last_error = f"GraphQL error: {payload['message']}"
            if "extensions" in payload:
                if "code" in payload["extensions"]:
                    if payload["extensions"]["code"] == "access-denied":
                        logger.error(
                            "Access denied for the provided Nemesis credentials! Check if it is valid, update your configuration, and restart")
                        self.last_error = f"Access denied for credentials"
                    if payload["extensions"]["code"] == "postgres-error":
                        logger.error(
                            "Nemesis's database rejected the query!")
                        self.last_error = f"Database error"
            return None
        except GraphQLError as e:
            logger.exception("Error with GraphQL query: %s", e)
            self.last_error = f"Graphql Error: {e}"
            return None
        except Exception as e:
            logger.exception(e)
            self.last_error = f"Unknown Error: {e}"
            return None

    async def nemesis_post_data(self, data):
        """
        Takes a json blob and POSTs it to the NEMESIS /data API endpoint.

        **Parameters**

        ``data``
            JSON formatted blob to post.

        **Returns**

        True if the request was successful, False otherwise.
        """
        try:
            basic = HTTPBasicAuth(self._credentials.username, self._credentials.password)
            logger.info(f"Posting Data: {data}")
            r = requests.post(f"{self._url}/api/data", auth=basic, json=data)
            if r.status_code != 200:
                raise Exception(r.text)
            else:
                return r.json()
        except Exception as e:
            logger.error(f"[nemesis_post_data] Error : {e}")
            raise e

    async def nemesis_post_file(self, file_bytes):
        """
        Takes a series of raw file bytes and POSTs it to the NEMESIS /file API endpoint.

        **Parameters**

        ``file_bytes``
            Bytes of the file we're uploading.

        **Returns**

        A new UUID string returned by the Nemesis API.
        """
        try:
            basic = HTTPBasicAuth(self._credentials.username, self._credentials.password)
            logger.info(f"Nemesis post to {self._url}/api/file")
            r = requests.request("POST", f"{self._url}/api/file", auth=basic, data=file_bytes, headers={"Content-Type": "application/octet-stream"})
            if r.status_code != 200:
                raise Exception(r.text)
            else:
                json_result = r.json()
                if "object_id" in json_result:
                    return json_result["object_id"]
                else:
                    raise Exception("[nemesis_post_file] Error retrieving 'object_id' field from result")
        except Exception as e:
            raise e