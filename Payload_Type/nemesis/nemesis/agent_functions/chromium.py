from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from nemesis.NemesisRequests import NemesisAPI
from gql import gql


class ChromiumArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
        ]

    async def parse_arguments(self):
        pass

    async def parse_dictionary(self, dictionary_arguments):
        pass


class Chromium(CommandBase):
    cmd = "chromium"
    needs_admin = False
    help_cmd = "chromium"
    description = "Get Chromium information from Nemesis"
    version = 2
    author = "@its_a_feature_"
    argument_class = ChromiumArguments
    supported_ui_features = ["nemesis:chromium"]
    browser_script = BrowserScript(script_name="chromium", author="@its_a_feature_")
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
        chromium_get_query = gql(
            """
            query NemesisChromium($project_id: String!) {
              nemesis_chromium_logins(where: {project_id: {_eq: $project_id}}) {
                agent_id
                browser
                password_value_dec
                signon_realm
                source
                user_data_directory
                username
                username_value
                project_id
              }
              nemesis_chromium_history(order_by: {last_visit_time: desc}, where: {project_id: {_eq: $project_id}}, limit: 50) {
                agent_id
                browser
                last_visit_time
                typed_count
                url
                username
                visit_count
                title
                source
              }
              nemesis_chromium_downloads(where: {project_id: {_eq: $project_id}}, order_by: {start_time: desc}) {
                browser
                download_path
                source
                timestamp
                total_bytes
                username
                url
              }
            }
            """
        )
        try:
            response_code, response_data = await NemesisAPI.query_graphql(taskData, query=chromium_get_query,
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
