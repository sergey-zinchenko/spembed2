import asyncio
from typing import Optional
import numpy as np
from faiss import normalize_L2
from injector import inject
from openai import AsyncOpenAI
from open_ai_api_wrapper_config import OpenAiApiWrapperConfig
import utils
import logging


class OpenAiApiWrapper:
    __config: OpenAiApiWrapperConfig
    __clients_queue: asyncio.Queue
    __logger: Optional[logging.Logger]

    @property
    def parallelism(self) -> int:
        return len(self.__config.servers)

    @inject
    def __init__(self,
                 config: OpenAiApiWrapperConfig, logger: Optional[logging.Logger]) -> None:
        if not config:
            raise ValueError("config cannot be empty")
        if not isinstance(config, OpenAiApiWrapperConfig):
            raise TypeError("config must be a AiWrapperConfig")
        if logger and not isinstance(logger, logging.Logger):
            raise TypeError("logger must be an instance of Logger")
        self.__config = config
        self.__clients_queue = asyncio.Queue()
        for server in config.servers:
            self.__clients_queue.put_nowait(AsyncOpenAI(base_url=server, api_key=config.api_key))
        self.__logger = logger

    async def __complete_core(self,  template: str, texts_parts: tuple[str, ...]) -> str:
        client = await self.__clients_queue.get()
        try:
            # noinspection PyArgumentList
            with utils.Timer() as timer:
                result = await client.chat.completions.create(
                    model=self.__config.completion_model,
                    temperature=self.__config.temperature,
                    messages=[
                        {"role": "system", "content": self.__config.system_message},
                        {"role": "user", "content": template.format(*texts_parts)}
                    ],
                    stream=False)
                completed = result.choices[0].message.content
            if self.__logger:
                self.__logger.debug(f"Completed template for {float(timer):.2f}s")
            return completed
        finally:
            self.__clients_queue.put_nowait(client)

    async def complete(self, template: str, texts: list[tuple[str, ...]]) -> list[str]:
        if not template:
            raise ValueError("template cannot be empty")
        if not isinstance(template, str):
            raise TypeError("template must be a string")
        if not texts:
            raise ValueError("texts cannot be empty")
        if not isinstance(texts, list) or not all(isinstance(tpl, tuple) for tpl in texts):
            raise TypeError("texts must be a list of tuple")
        tasks = [asyncio.create_task(self.__complete_core(template, tpl)) for tpl in texts]
        return list(await asyncio.gather(*tasks))

    async def __embed_core(self, texts: list[str]) -> list[list[float]]:
        client = await self.__clients_queue.get()
        try:
            results = await client.embeddings.create(
                input=[text.replace("\n", " ").replace("\t", " ") for text in texts],
                model=self.__config.embed_model)
            return [result.embedding for result in results.data]
        finally:
            self.__clients_queue.put_nowait(client)

    async def embed_normalize(self,
                              texts: list[str]) -> np.ndarray:
        if not texts:
            raise ValueError("texts cannot be empty")
        if not isinstance(texts, list) or not all(isinstance(item, str) for item in texts):
            raise TypeError("texts must be a list of strings")
        with utils.Timer() as timer:
            batches = utils.batch_list(texts, len(texts) // self.parallelism + 1)
            tasks = [asyncio.create_task(self.__embed_core(batch)) for batch in batches]
            results = await asyncio.gather(*tasks)
            # noinspection PyTypeChecker
            embeddings = np.concatenate(results, axis=0, dtype='float32')
            normalize_L2(embeddings)
        if self.__logger:
            self.__logger.debug(f"Embedded {len(embeddings)} sentences for {float(timer):.2f}s")
        return embeddings
