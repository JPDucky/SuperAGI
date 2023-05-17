import uuid

from superagi.vector_store.document import Document
from superagi.vector_store.base import VectorStore
from typing import Any, Callable, Optional, Iterable, List

from superagi.vector_store.embedding.openai import BaseEmbedding


class Pinecone(VectorStore):
    def __init__(
            self,
            index: Any,
            embedding_model: BaseEmbedding,
            text_field: str,
            namespace: Optional[str] = '',
    ):

        try:
            import pinecone
        except ImportError:
            raise ValueError("Please install pinecone to use this vector store.")

        if not isinstance(index, pinecone.index.Index):
            raise ValueError("Please provide a valid pinecone index.")

        self.index = index
        self.embedding_model = embedding_model
        self.text_field = text_field
        self.namespace = namespace

    def add_texts(
            self,
            texts: Iterable[str],
            metadatas: Optional[list[dict]] = None,
            ids: Optional[list[str]] = None,
            namespace: Optional[str] = None,
            batch_size: int = 32,
            **kwargs: Any,
    ) -> list[str]:
        """Add texts to the vector store."""
        if namespace is None:
            namespace = self.namespace

        vectors = []
        ids = ids or [str(uuid.uuid4()) for _ in texts]
        if len(ids) < len(texts):
            raise ValueError("Number of ids must match number of texts.")

        for text, id in zip(texts, ids):
            metadata = metadatas.pop(0) if metadatas else {}
            metadata[self.text_field] = text
            vectors.append((id, self.embedding_model.get_embedding(text), metadata))

        self.index.upsert(vectors, namespace=namespace, batch_size=batch_size)
        return ids

    def get_matching_text(self, query: str, top_k: int, **kwargs: Any) -> List[Document]:
        """Return docs most similar to query using specified search type."""
        namespace = kwargs.get("namespace", self.namespace)

        embed_text = self.embedding_model.get_embedding(query)
        res = self.index.query(embed_text, top_k=top_k, namespace=namespace, include_metadata=True)

        documents = []

        for doc in res['matches']:
            documents.append(
                Document(
                    text_content=doc.metadata[self.text_field],
                    metadata=doc.metadata,
                )
            )

        return documents
