import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datasketch import MinHash, MinHashLSH
from functools import lru_cache
import logging


logger = logging.getLogger(__name__)

class PlagiarismDetector:
    def __init__(self, threshold=0.75, use_minhash=False, min_text_length=30):
        self.threshold = threshold
        self.use_minhash = use_minhash
        self.min_text_length = min_text_length

        # Configurations des différents algorithmes
        self.vectorizer = TfidfVectorizer(
            stop_words=None,
            ngram_range=(1, 3),
            max_features=5000
        )
        
        if use_minhash:
            self.lsh = MinHashLSH(threshold=threshold, num_perm=128)
            self.minhashes = {}
        
        # Cache pour le prétraitement
        self._regex_cache = {
            'whitespace': re.compile(r'\s+'),
            'special_chars': re.compile(r'[^a-zàâçéèêëîïôûùüÿñæœ\s]')
        }

    @lru_cache(maxsize=1000)
    def preprocess_text(self, text):
        """Version optimisée avec cache"""
        if not text or not isinstance(text, str):
            return ""
        
        text = self._regex_cache['whitespace'].sub(' ', text.lower().strip())
        return self._regex_cache['special_chars'].sub('', text)

    def calculate_similarity(self, text1, text2):
        """Version optimisée pour comparaisons ponctuelles"""
        # Implémentation complète comme montré précédemment
        # ... (voir code section 2 des optimisations)

    def batch_compare(self, new_text, reference_texts):
        """Pour comparaisons groupées"""
        # Implémentation complète comme montré précédemment
        # ... (voir code section 3 des optimisations)

    # Méthodes MinHash (optionnelles)
    def add_to_index(self, doc_id, text):
        if not self.use_minhash:
            return
        words = self.preprocess_text(text).split()
        mh = MinHash(num_perm=128)
        for word in words:
            mh.update(word.encode('utf-8'))
        self.lsh.insert(doc_id, mh)
        self.minhashes[doc_id] = mh

    def query_similar(self, text):
        if not self.use_minhash:
            return []
        words = self.preprocess_text(text).split()
        mh = MinHash(num_perm=128)
        for word in words:
            mh.update(word.encode('utf-8'))
        return self.lsh.query(mh)

    def compare_texts(self, text1, text2):
        """Compare deux textes et retourne un score de similarité (TF-IDF + Cosine)."""
        # Prétraitement
        text1 = self.preprocess_text(text1)
        text2 = self.preprocess_text(text2)

        # Vérification longueur minimale (optionnelle)
        if len(text1.split()) < 5 or len(text2.split()) < 5:
            return 0.0

        # Vectorisation
        vectors = self.vectorizer.fit_transform([text1, text2])
        
        # Calcul similarité cosinus
        cosine_sim = cosine_similarity(vectors[0], vectors[1])
        
        # Extraction du score (sécurité avec flatten)
        similarity_score = cosine_sim.flatten()[0]
        
        return round(float(similarity_score), 4)

    
