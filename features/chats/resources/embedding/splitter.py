#<!--=====================================================
#   SENETENCE SPLITTER FRAMEWORK (llAMA INDEX)
#=======================================================-->

from llama_index.core.node_parser import SentenceSplitter

sentence_splitter = SentenceSplitter(
    chunk_size=1200,
    chunk_overlap=20
)