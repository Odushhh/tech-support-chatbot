import logging
from typing import List, Dict, Any, Tuple
import numpy as np
import faiss
import re
from sentence_transformers import SentenceTransformer
from backend.app.core.config import settings
from backend.app.utils.helpers import sanitize_input

logger = logging.getLogger(__name__)

class SemanticSearch:
    def __init__(self):
        self.model = SentenceTransformer(settings.SENTENCE_TRANSFORMER_MODEL)
        self.index = None
        self.documents = []

    def build_index(self, documents: List[Dict[str, Any]]):
        """
        Build the FAISS index from the given documents.
        """
        try:
            self.documents = documents
            embeddings = self.model.encode([doc['content'] for doc in documents])
            dimension = embeddings.shape[1]
            
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(embeddings.astype('float32'))
            
            logger.info(f"Built index with {len(documents)} documents")
        except Exception as e:
            logger.error(f"Error building index: {str(e)}")

    def clear_index(self):
        """
        Clear the FAISS index and the stored documents.
        """
        try:
            self.index = None
            self.documents = []
            logger.info("Cleared the index and documents.")
        except Exception as e:
            logger.error(f"Error clearing index: {str(e)}")

    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform semantic search on the indexed documents.
        """
        try:
            if not self.index:
                raise ValueError("Index not built. Call build_index() first.")
            
            query_vector = self.model.encode([query])
            distances, indices = self.index.search(query_vector.astype('float32'), k)
            
            results = []
            for i, idx in enumerate(indices[0]):
                if idx != -1:  # FAISS returns -1 for empty slots
                    result = self.documents[idx].copy()
                    result['score'] = 1 / (1 + distances[0][i])  # Convert distance to similarity score
                    results.append(result)
            
            return results
        except Exception as e:
            logger.error(f"Error performing search: {str(e)}")
            return []

    def add_document(self, document: Dict[str, Any]):
        """
        Add a single document to the index.
        """
        try:
            if not self.index:
                raise ValueError("Index not built. Call build_index() first.")
            
            embedding = self.model.encode([document['content']])
            self.index.add(embedding.astype('float32'))
            self.documents.append(document)
            
            logger.info(f"Added document to index. Total documents: {len(self.documents)}")
        except Exception as e:
            logger.error(f"Error adding document to index: {str(e)}")

    def remove_document(self, document_id: str):
        """
        Remove a document from the index by its ID.
        """
        try:
            if not self.index:
                raise ValueError("Index not built. Call build_index() first.")
            
            doc_idx = next((i for i, doc in enumerate(self.documents) if doc['id'] == document_id), None)
            if doc_idx is not None:
                # Remove from documents list
                del self.documents[doc_idx]
                
                # Rebuild index
                self.build_index(self.documents)
                
                logger.info(f"Removed document {document_id} from index. Total documents: {len(self.documents)}")
            else:
                logger.warning(f"Document {document_id} not found in index.")
        except Exception as e:
            logger.error(f"Error removing document from index: {str(e)}")

    def update_document(self, document: Dict[str, Any]):
        """
        Update an existing document in the index.
        """
        try:
            if not self.index:
                raise ValueError("Index not built. Call build_index() first.")
            
            doc_idx = next((i for i, doc in enumerate(self.documents) if doc['id'] == document['id']), None)
            if doc_idx is not None:
                # Update in documents list
                self.documents[doc_idx] = document
                
                # Rebuild index
                self.build_index(self.documents)
                
                logger.info(f"Updated document {document['id']} in index.")
            else:
                logger.warning(f"Document {document['id']} not found in index. Adding as new document.")
                self.add_document(document)
        except Exception as e:
            logger.error(f"Error updating document in index: {str(e)}")

    def get_similar_documents(self, document_id: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Find documents similar to a given document by its ID.
        """
        try:
            if not self.index:
                raise ValueError("Index not built. Call build_index() first.")
            
            doc = next((doc for doc in self.documents if doc['id'] == document_id), None)
            if doc is None:
                raise ValueError(f"Document {document_id} not found in index.")
            
            query_vector = self.model.encode([doc['content']])
            distances, indices = self.index.search(query_vector.astype('float32'), k + 1)  # +1 to exclude the document itself
            
            results = []
            for i, idx in enumerate(indices[0]):
                if idx != -1 and self.documents[idx]['id'] != document_id:
                    result = self.documents[idx].copy()
                    result['score'] = 1 / (1 + distances[0][i])
                    results.append(result)
            
            return results[:k]  # Ensure we return at most k results
        except Exception as e:
            logger.error(f"Error finding similar documents: {str(e)}")
            return []

    def get_document_embedding(self, document_id: str) -> np.ndarray:
        """
        Get the embedding of a document by its ID.
        """
        try:
            if not self.index:
                raise ValueError("Index not built. Call build_index() first.")
            
            doc = next((doc for doc in self.documents if doc['id'] == document_id), None)
            if doc is None:
                raise ValueError(f"Document {document_id} not found in index.")
            
            return self.model.encode([doc['content']])[0]
        except Exception as e:
            logger.error(f"Error getting document embedding: {str(e)}")
            return np.array([])

    def calculate_similarity(self, doc1_id: str, doc2_id: str) -> float:
        """
        Calculate the cosine similarity between two documents.
        """
        try:
            emb1 = self.get_document_embedding(doc1_id)
            emb2 = self.get_document_embedding(doc2_id)
            
            if emb1.size == 0 or emb2.size == 0:
                return 0.0
            
            return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        except Exception as e:
            logger.error(f"Error calculating document similarity: {str(e)}")
            return 0.0

    def cluster_documents(self, n_clusters: int = 5) -> List[List[str]]:
        """
        Cluster the documents using K-means.
        """
        try:
            if not self.index:
                raise ValueError("Index not built. Call build_index() first.")
            
            embeddings = self.model.encode([doc['content'] for doc in self.documents])
            kmeans = faiss.Kmeans(d=embeddings.shape[1], k=n_clusters, niter=20)
            kmeans.train(embeddings.astype('float32'))
            
            _, labels = kmeans.index.search(embeddings.astype('float32'), 1)
            
            clusters = [[] for _ in range(n_clusters)]
            for i, label in enumerate(labels.flatten()):
                clusters[label].append(self.documents[i]['id'])
            
            return clusters
        except Exception as e:
            logger.error(f"Error clustering documents: {str(e)}")
            return []

# Instantiate the SemanticSearch
semantic_search = SemanticSearch()

