from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from nemesis.NemesisRequests import NemesisAPI
from gql import gql


class TriageArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="value",
                default_value="both",
                type=ParameterType.ChooseOne,
                choices=["useful", "notuseful", "both"],
                parameter_group_info=[
                    ParameterGroupInfo(required=False)
                ]
            )
        ]

    async def parse_arguments(self):
        self.load_args_from_json_string(self.command_line)
        if self.get_arg("value") is None:
            if self.command_line == "":
                self.set_arg("value", "both")
            else:
                self.set_arg("value", self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary=dictionary_arguments)


class Triage(CommandBase):
    cmd = "triage"
    needs_admin = False
    help_cmd = "triage"
    description = "Get information about which files have already been triaged in nemesis and marked useful or not"
    version = 2
    author = "@its_a_feature_"
    argument_class = TriageArguments
    supported_ui_features = ["nemesis:triage"]
    browser_script = BrowserScript(script_name="triage", author="@its_a_feature_")
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
            query NemesisTriage($project_id: String!) {
              nemesis_triage(where: {file_data_enriched: {project_id: {_eq: $project_id}}}) {
                value
                operator
                expiration
                file_data_enriched {
                  project_id
                  magic_type
                  name
                  nemesis_file_type
                  tags
                }
              }
            }
            """
        )
        try:
            response_code, response_data = await NemesisAPI.query_graphql(taskData, query=triage_get_query,
                                                                          variable_values={
                                                                              "project_id": taskData.Callback.OperationName
                                                                          })
            if response_code == 500:
                return await NemesisAPI.process_standard_response(response_code=response_code,
                                                                  response_data=response_data,
                                                                  taskData=taskData,
                                                                  response=response)
            results = [x for x in response_data["nemesis_triage"] if taskData.args.get_arg("value") == "both" or taskData.args.get_arg("value") == x["value"]]
            return await NemesisAPI.process_standard_response(response_code=response_code,
                                                              response_data=results,
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
