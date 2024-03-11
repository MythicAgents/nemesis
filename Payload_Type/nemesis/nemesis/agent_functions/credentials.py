from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from nemesis.NemesisRequests import NemesisAPI
from gql import gql


class CredentialsArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
        ]

    async def parse_arguments(self):
        #self.load_args_from_json_string(self.command_line)
        pass

    async def parse_dictionary(self, dictionary_arguments):
        #self.load_args_from_dictionary(dictionary=dictionary_arguments)
        pass


class Credentials(CommandBase):
    cmd = "credentials"
    needs_admin = False
    help_cmd = "credentials"
    description = "Get credential information from Nemesis"
    version = 2
    author = "@its_a_feature_"
    argument_class = CredentialsArguments
    supported_ui_features = ["nemesis:credentials"]
    browser_script = BrowserScript(script_name="credentials", author="@its_a_feature_")
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
        triage_get_query = gql(
            """
            query NemesisAuthenticationData($project_id: String!) {
              nemesis_authentication_data(where: {project_id: {_eq: $project_id}}) {
                data
                username
                uri
                unique_db_id
                type
                timestamp
                source
                project_id
                originating_object_id
                notes
                is_file
                expiration
                agent_id
              }
            }
            """
        )
        try:
            response_code, response_data = await NemesisAPI.query_graphql(taskData, query=triage_get_query,
                                                                          variable_values={
                                                                              "project_id": taskData.Callback.OperationName
                                                                          })
            return await NemesisAPI.process_standard_response(response_code=response_code,
                                                              response_data=response_data,
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
