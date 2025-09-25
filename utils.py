import pandas as pd

from typing import List, Dict, Union
from dataclasses import dataclass, field
from collections import Counter, defaultdict



@dataclass(slots=True)
class PrefixTreeNode:
    children: Dict[str, "PrefixTreeNode"] = field(default_factory=dict)
    is_end_of_word: bool = False


class PrefixTree:
    def __init__(self, vocabulary: List[str]):
        self.root = PrefixTreeNode()
        for word in set(vocabulary):
            if word:
                self._insert(word)

    def _insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, PrefixTreeNode())
        node.is_end_of_word = True

    def search_prefix(self, prefix: str) -> List[str]:
        if prefix is None:
            return []

        node = self.root
        for ch in prefix:
            node = node.children.get(ch)
            if node is None:
                return []

        out: List[str] = []
        stack = [(node, prefix)]
        while stack:
            cur, pref = stack.pop()
            if cur.is_end_of_word:
                out.append(pref)
            for ch, child in cur.children.items():
                stack.append((child, pref + ch))
        return out


class WordCompletor:
    def __init__(self, corpus):
        counter = Counter()
        total_tokens = 0

        for doc in corpus:
            if isinstance(doc, list):
                tokens = [t.lower() for t in doc if isinstance(t, str)]
            elif isinstance(doc, str):
                tokens = doc.lower().split()
            else:
                continue
            counter.update(tokens)
            total_tokens += len(tokens)

        self.freqs = dict(counter)
        self.total_tokens = max(1, total_tokens)
        self.prefix_tree = PrefixTree(list(self.freqs.keys()))

    def get_words_and_probs(self, prefix: str) -> (List[str], List[float]):
        if not isinstance(prefix, str):
            return [], []
        prefix = prefix.lower()

        candidates = self.prefix_tree.search_prefix(prefix)
        candidates = [w for w in candidates if self.freqs.get(w, 0) > 0]

        candidates.sort(key=lambda w: (-self.freqs[w], w))

        words = candidates
        probs = [self.freqs[w] / self.total_tokens for w in candidates]
        return words, probs


class NGramLanguageModel:
    def __init__(self, corpus, n):
        self.n = n
        self.next_counts = defaultdict(Counter)
        self.context_counts = Counter()

        for doc in corpus:
            tokens = (
                doc.split()
                if isinstance(doc, str)
                else [t for t in doc if isinstance(t, str)]
            )
            if self.n == 0:
                for w in tokens:
                    self.next_counts[()].update([w])
                    self.context_counts[()] += 1
            else:
                for i in range(0, len(tokens) - self.n):
                    context = tuple(tokens[i : i + self.n])
                    nxt = tokens[i + self.n]
                    self.next_counts[context].update([nxt])
                    self.context_counts[context] += 1

    def get_next_words_and_probs(self, prefix_list):
        next_words, probs = [], []
        if not isinstance(prefix_list, list):
            return next_words, probs

        context = () if self.n == 0 else tuple(prefix_list[-self.n :])

        counter = self.next_counts.get(context, Counter())
        if not counter:
            return next_words, probs

        total = self.context_counts[context]
        items = sorted(counter.items(), key=lambda x: (-x[1], x[0]))

        next_words = [w for w, _ in items]
        probs = [cnt / total for _, cnt in items]
        return next_words, probs


class TextSuggestion:
    def __init__(self, word_completor, n_gram_model):
        self.word_completor = word_completor
        self.n_gram_model = n_gram_model

    def suggest_text(self, text: Union[str, list], n_words=3, n_texts=1) -> list[list[str]]:
        print(f"Полученный текст: {text}")
        suggestions = []

        tokens = (
            text
            if isinstance(text, list)
            else (text.strip().split() if isinstance(text, str) else [])
        )
        if not tokens:
            print("Ошибка: пустой или некорректный текст")
            return suggestions

        last = tokens[-1]
        cand_words, cand_probs = self.word_completor.get_words_and_probs(last)
        if cand_words:
            best_i = max(range(len(cand_words)), key=lambda i: cand_probs[i])
            completed = cand_words[best_i]
        else:
            completed = last

        print(f"Подсказка: {completed}")
        tokens[-1] = completed
        generated = [completed]
        context = tokens[:]

        target_len = 1 + n_words
        while len(generated) < target_len:
            next_words, next_probs = self.n_gram_model.get_next_words_and_probs(context)
            if not next_words:
                break
            best_next = max(range(len(next_words)), key=lambda i: next_probs[i])
            w = next_words[best_next]
            generated.append(w)
            context.append(w)

        suggestions.append(generated)

        return suggestions


def build_models(corpus: List[List[str]] = None, n: int = 2):
    word_completor = WordCompletor(corpus)
    n_gram_model = NGramLanguageModel(corpus=corpus, n=n)
    text_suggester = TextSuggestion(word_completor, n_gram_model)
    return word_completor, n_gram_model, text_suggester

def suggest(text: str, n_words: int = 3, n: int = 2, topk: int = 1, corpus = None) -> List[str]:
    word_completor, n_gram_model, ts = build_models(corpus=corpus, n=n)
    
    if word_completor is None or n_gram_model is None or ts is None:
        return []
    
    suggestions = ts.suggest_text(text, n_words=n_words, n_texts=min(1, topk))
    return [" ".join(s) for s in suggestions]