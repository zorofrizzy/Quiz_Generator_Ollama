"""
metadata_by_llm.py

In many cases, especially with long documents, a chunk of text may lack the context 
necessary to disambiguate the chunk from other similar chunks of text. One method of 
addressing this is manually labelling each chunk in our dataset or knowledge base. 
However, this can be labour intensive and time consuming for a large number or 
continually updated set of documents.

To combat this, we use LLMs to extract certain contextual information relevant to the 
document to better help the retrieval and language models disambiguate similar-looking passages.

"""


import nest_asyncio
import os

nest_asyncio.apply()
from llama_index.llms.ollama import Ollama
from llama_index.core.schema import MetadataMode

from llama_index.core.extractors import (
    SummaryExtractor,
    QuestionsAnsweredExtractor,
    TitleExtractor,
    KeywordExtractor,
    BaseExtractor,
)
from llama_index.extractors.entity import EntityExtractor
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core import SimpleDirectoryReader
from llama_index.core.ingestion import IngestionPipeline


llm = Ollama(model="basic_model", request_timeout=120.0, json_mode=True)

text_splitter = TokenTextSplitter(
    separator=" ", chunk_size=512, chunk_overlap=128
)


class CustomExtractor(BaseExtractor):
    def extract(self, nodes):
        metadata_list = [
            {
                "custom": (
                    node.metadata["document_title"]
                    + "\n"
                    + node.metadata["excerpt_keywords"]
                )
            }
            for node in nodes
        ]
        return metadata_list


extractors = [
    TitleExtractor(nodes=5, llm=llm),
    # QuestionsAnsweredExtractor(questions=3, llm=llm),
    # EntityExtractor(prediction_threshold=0.5),
    # SummaryExtractor(summaries=["prev", "self"], llm=llm),
    KeywordExtractor(keywords=10, llm=llm),
    # CustomExtractor()
]

transformations = [text_splitter] + extractors


# Note the uninformative document file name, which may be a common scenario in a production setting
uber_docs = SimpleDirectoryReader(input_files=["sample_story.pdf"]).load_data()

pipeline = IngestionPipeline(transformations=transformations)

uber_nodes = pipeline.run(documents=uber_docs)



print(uber_nodes[1].metadata)




