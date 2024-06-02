import yaml


class OpenAiApiWrapperConfig:
    __servers: list[str]
    __completion_model: str
    __embed_model: str
    __api_key: str
    __system_message: str
    __temperature: float

    @property
    def servers(self) -> list[str]:
        return self.__servers

    @property
    def completion_model(self) -> str:
        return self.__completion_model

    @property
    def embed_model(self) -> str:
        return self.__embed_model

    @property
    def api_key(self) -> str:
        return self.__api_key

    @property
    def system_message(self) -> str:
        return self.__system_message

    @property
    def temperature(self) -> float:
        return self.__temperature

    def __init__(self, config: dict) -> None:
        self.__servers = config.get('servers', [])
        self.__completion_model = config.get('completion_model', '')
        self.__embed_model = config.get('embed_model', '')
        self.__api_key = config.get('api_key', '')
        self.__system_message = config.get('system_message', '')
        self.__temperature = config.get('temperature', 0.7)

        if (not self.__servers or len(self.__servers) == 0 or not self.__completion_model or not self.__embed_model
                or not self.__api_key or not self.__system_message or not self.__temperature):
            raise ValueError("One or more required config fields are missing or empty")

    @classmethod
    def read_config(cls, file_name: str) -> 'OpenAiApiWrapperConfig':
        if not file_name:
            raise ValueError("File name cannot be empty")
        with open(file_name, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            return cls(config)
