from mythic_container.PayloadBuilder import *
from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *


class Nemesis(PayloadType):
    name = "nemesis"
    file_extension = ""
    author = "@its_a_feature_"
    supported_os = [
        SupportedOS("nemesis")
    ]
    wrapper = False
    wrapped_payloads = []
    note = """
    This payload communicates with an existing Nemesis instance. In your settings, add your Nemesis Username and Password as a secret with the keys "NEMESIS_USERNAME" and "NEMESIS_PASSWORD".
    """
    supports_dynamic_loading = False
    mythic_encrypts = True
    translation_container = None
    agent_type = "service"
    agent_path = pathlib.Path(".") / "nemesis"
    agent_icon_path = agent_path / "agent_functions" / "nemesis.svg"
    agent_code_path = agent_path / "agent_code"
    build_parameters = [
        BuildParameter(name="URL",
                       description="Nemesis URL",
                       parameter_type=BuildParameterType.String,
                       default_value="https://127.0.0.1:8080"),
    ]
    c2_profiles = []

    async def build(self) -> BuildResponse:
        # this function gets called to create an instance of your payload
        resp = BuildResponse(status=BuildStatus.Success)
        ip = "127.0.0.1"
        create_callback = await SendMythicRPCCallbackCreate(MythicRPCCallbackCreateMessage(
            PayloadUUID=self.uuid,
            C2ProfileName="",
            User="Nemesis",
            Host="Nemesis",
            Ip=ip,
            IntegrityLevel=3,
        ))
        if not create_callback.Success:
            logger.info(create_callback.Error)
        else:
            logger.info(create_callback.CallbackUUID)
        return resp
