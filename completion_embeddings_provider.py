import utils
import numpy as np
from embeddings_provider import EmbeddingsProvider
from source_item import SourceItem
from open_ai_api_wrapper import OpenAiApiWrapper
from typing import TypeVar, Generic, Iterable

P = TypeVar('P', bound=SourceItem)


class CompletionEmbeddingsProvider(Generic[P], EmbeddingsProvider[P, np.ndarray]):
    __wrapper: OpenAiApiWrapper
    __completion_template: str
    __batch_size: int

    def __init__(self, completion_template: str,
                 wrapper: OpenAiApiWrapper,
                 batch_size: int = 100) -> None:
        if not completion_template:
            raise ValueError("completion_template is missing or empty")
        if not isinstance(completion_template, str):
            raise TypeError("completion_template must be a string")
        if not wrapper:
            raise ValueError("wrapper is missing or empty")
        if not isinstance(wrapper, OpenAiApiWrapper):
            raise TypeError("wrapper must be an instance of AIWrapper")
        if not batch_size:
            raise ValueError("batch_size is missing or empty")
        if not isinstance(batch_size, int):
            raise TypeError("batch_size must be an integer")
        self.__wrapper = wrapper
        self.__completion_template = completion_template
        self.__batch_size = batch_size

    async def complete(self, texts: list[str]) -> list[str]:
        return await self.__wrapper.complete(self.__completion_template, [(text,) for text in texts])

    async def get_embeddings(self, items: Iterable[P]) -> np.ndarray:
        self.raise_when_bad_items(items)
        batches = utils.batch_list(list([item.text_to_match for item in items]), self.__batch_size)
        embeddings = None
        for batch in batches:
            completed = await self.complete(batch)
            result = await self.__wrapper.embed_normalize(completed)
            if embeddings is None:
                embeddings = result
            else:
                embeddings = np.concatenate((embeddings, result))
        return embeddings
