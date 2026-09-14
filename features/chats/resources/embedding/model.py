# <!--===================================
#   EMBBEDING MODELS
# =====================================-->

model_bge_en = "BAAI/bge-large-en-v1.5"  # lang (EN)
model_all_miniLM_V2 = "all-MiniLM-L6-v2"  # lang (EN)
model_bge_m3 = "BAAI/bge-m3"  # lang (MY)
model_fb = "facebook/xglm-1.7B"

from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer(model_all_miniLM_V2, device="cuda")
