from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from nemesis.NemesisRequests import NemesisAPI
from gql import gql


class UploadArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="file",
                type=ParameterType.File,
                parameter_group_info=[ParameterGroupInfo(
                    required=True,
                    ui_position=1,
                    group_name="Manually Upload New File"
                )]
            ),
            CommandParameter(
                name="filename",
                type=ParameterType.ChooseOne,
                dynamic_query_function=self.get_files,
                parameter_group_info=[ParameterGroupInfo(
                    required=True,
                    ui_position=1,
                    group_name="Select Mythic File to Upload"
                )]
            ),
            CommandParameter(
                name="remote_path",
                type=ParameterType.String,
                description="The absolute remote path on the target host where this file came from. If you're uploading a file that Mythic already has a path for, you can leave this blank and that path will automatically get used. Otherwise, you should specify the path. Certain files (DPAPI keys, Chrome data, etc) relies on the full paths within Nemesis.",
                default_value="",
                parameter_group_info=[
                    ParameterGroupInfo(
                        required=False,
                        ui_position=2,
                        group_name="Manually Upload New File"
                    ),
                    ParameterGroupInfo(
                        required=False,
                        ui_position=2,
                        group_name="Select Mythic File to Upload"
                    )
                ]
            ),
            #CommandParameter(
            #    name="domain_backup_key",
            #    type=ParameterType.Boolean,
            #    description="Specify that this is a domain backup key so that it can be processed and used to decrypt DPAPI Blobs",
            #    default_value=False,
            #    parameter_group_info=[
            #        ParameterGroupInfo(
            #            required=False,
            #            ui_position=2,
            #            group_name="Manually Upload New File"
            #        ),
            #        ParameterGroupInfo(
            #            required=False,
            #            ui_position=2,
            #            group_name="Select Mythic File to Upload"
            #        )
            #    ]
            #)
        ]

    async def parse_arguments(self):
        self.load_args_from_json_string(self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary=dictionary_arguments)

    async def get_files(self, callback: PTRPCDynamicQueryFunctionMessage) -> PTRPCDynamicQueryFunctionMessageResponse:
        response = PTRPCDynamicQueryFunctionMessageResponse()
        file_resp = await SendMythicRPCFileSearch(MythicRPCFileSearchMessage(
            CallbackID=callback.Callback,
            LimitByCallback=False,
            IsDownloadFromAgent=True,
            IsScreenshot=False,
            IsPayload=False,
            Filename="",
        ))
        if file_resp.Success:
            file_names = []
            for f in file_resp.Files:
                if f.Filename not in file_names:
                    file_names.append(f.Filename)
            response.Success = True
            response.Choices = file_names
            return response
        else:
            await SendMythicRPCOperationEventLogCreate(MythicRPCOperationEventLogCreateMessage(
                CallbackId=callback.Callback,
                Message=f"Failed to get files: {file_resp.Error}",
                MessageLevel="warning"
            ))
            response.Error = f"Failed to get files: {file_resp.Error}"
            return response


class Upload(CommandBase):
    cmd = "upload"
    needs_admin = False
    help_cmd = "upload"
    description = "Upload a new file to Nemesis for processing"
    version = 2
    author = "@its_a_feature_"
    argument_class = UploadArguments
    supported_ui_features = ["nemesis:upload"]
    # browser_script = BrowserScript(script_name="hashes", author="@its_a_feature_")
    attackmapping = []
    completion_functions = {
    }

    async def create_go_tasking(self,
                                taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=False,
            Completed=True,
            DisplayParams=f""
        )

        try:
            fileMetadata = None
            if taskData.args.get_parameter_group_name() == "Manually Upload New File":
                searchedFile = await SendMythicRPCFileSearch(MythicRPCFileSearchMessage(
                    AgentFileID=taskData.args.get_arg("file")
                ))
                if not searchedFile.Success:
                    raise Exception(searchedFile.Error)
                if len(searchedFile.Files) != 1:
                    raise Exception("Failed to get file back from Mythic")
                fileMetadata = searchedFile.Files[0]

            else:
                searchedFile = await SendMythicRPCFileSearch(MythicRPCFileSearchMessage(
                    TaskID=taskData.Task.ID,
                    Filename=taskData.args.get_arg("filename"),
                    LimitByCallback=False,
                    MaxResults=1
                ))
                if not searchedFile.Success:
                    raise Exception(searchedFile.Error)
                if len(searchedFile.Files) != 1:
                    raise Exception("Failed to get file back from Mythic")
                fileMetadata = searchedFile.Files[0]
            fileContentsResp = await SendMythicRPCFileGetContent(MythicRPCFileGetContentMessage(
                AgentFileId=fileMetadata.AgentFileId
            ))
            if not fileContentsResp.Success:
                raise Exception(fileContentsResp.Error)
            # register file contents with Nemesis and get back file_id
            registerFileResponseCode, registerFileResponseData = await NemesisAPI.post_file_api(taskData=taskData,
                                                                                                file_bytes=fileContentsResp.Content)
            if registerFileResponseCode != 200:
                return await NemesisAPI.process_standard_response(response_code=registerFileResponseCode,
                                                                  response_data=registerFileResponseData,
                                                                  taskData=taskData,
                                                                  response=response)
            # update file_id with additional metadata
            metadata = {}
            metadata["agent_id"] = taskData.Callback.AgentCallbackID
            metadata["agent_type"] = "mythic"
            metadata["automated"] = False
            metadata["data_type"] = "file_data"
            metadata["project"] = f"{taskData.Callback.OperationName}"
            metadata["timestamp"] = NemesisAPI.convert_timestamp(fileMetadata.Timestamp)
            metadata["expiration"] = NemesisAPI.convert_timestamp(fileMetadata.Timestamp, 90)
            file_data = {}
            if taskData.args.get_arg("remote_path") == "":
                file_data["path"] = fileMetadata.FullRemotePath
            else:
                file_data["path"] = taskData.args.get_arg("remote_path")
            if file_data["path"] == "":
                file_data["path"] = fileMetadata.Filename
            file_data["size"] = len(fileContentsResp.Content)
            file_data["object_id"] = registerFileResponseData
            response.DisplayParams = f"-remote_path {file_data['path']}"
            #if taskData.args.get_arg("domain_backup_key"):
            #    metadata = {
            #        "agent_id": taskData.Callback.OperatorUsername,
            #        "data_type": "raw_data",
            #        "agent_type": "submit_to_nemesis",
            #        "automated": False,
            #        "expiration": NemesisAPI.convert_timestamp(fileMetadata.Timestamp, 90),
            #        "project": f"{taskData.Callback.OperationName}",
            #        "timestamp": NemesisAPI.convert_timestamp(fileMetadata.Timestamp)
            #    }
            #    file_data = {
            #        "tags": ["dpapi_domain_backupkey"],
            #        "data": registerFileResponseData,
            #        "is_file": True
            #    }
            updateFileResponseCode, updateFileResponseData = await NemesisAPI.post_data_api(taskData=taskData,
                                                                                            data={
                                                                                                "metadata": metadata,
                                                                                                "data": [file_data]
                                                                                            })
            responseData = {
                "file_id": registerFileResponseData,
                "update_file": updateFileResponseData["object_id"]
            }

            return await NemesisAPI.process_standard_response(response_code=updateFileResponseCode,
                                                              response_data=responseData,
                                                              taskData=taskData,
                                                              response=response)
        except Exception as e:
            await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                TaskID=taskData.Task.ID,
                Response=f"{e}".encode("UTF8"),
            ))
            response.TaskStatus = "Error: Nemesis Access Error"
            response.Success = False
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
