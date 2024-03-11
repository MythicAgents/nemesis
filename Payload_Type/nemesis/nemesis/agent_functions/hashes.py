from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from nemesis.NemesisRequests import NemesisAPI
from gql import gql


class HashesArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
        ]

    async def parse_arguments(self):
        self.load_args_from_json_string(self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary=dictionary_arguments)


class Hashes(CommandBase):
    cmd = "hashes"
    needs_admin = False
    help_cmd = "hashes"
    description = "Get extracted hash information from Nemesis"
    version = 2
    author = "@its_a_feature_"
    argument_class = HashesArguments
    supported_ui_features = ["nemesis:hashes"]
    browser_script = BrowserScript(script_name="hashes", author="@its_a_feature_")
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
            query NemesisHashes($project_id: String!) {
              nemesis_extracted_hashes(where: {project_id: {_eq: $project_id}}) {
                agent_id
                checked_against_top_passwords
                cracker_cracked_time
                cracker_submission_time
                expiration
                hash_type
                hash_value
                hash_value_md5_hash
                hashcat_formatted_value
                is_cracked
                is_submitted_to_cracker
                jtr_formatted_value
                originating_object_id
                plaintext_value
                project_id
                source
                timestamp
                unique_db_id
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
