"""
Core functionality, like applying filters or tokenizing documents.
"""
from collections.abc import Callable, Iterable, Iterator, Sequence
from functools import partial

from its_prep.types import (
    Document,
    Filter,
    Pipeline,
    Property,
    Property_Function,
    Tokens,
)


def apply_filters(docs: Iterable[Document], filters: Pipeline) -> Iterator[Document]:
    """
    Iteratively apply the pipeline's Filter functions on the given documents,
    interpreting the collections of indices returned by the filters as
    tokens to possibly keep.
    Tokens with index not inside a filter's result will be discarded.

    If no filters were given, the documents are returned as-is.
    """

    def apply_all(doc: Document, *filters: Filter) -> Document:
        """
        Apply each filter on the previously filtered document.

        Depending on the implementation of the filter,
        this can result in better performance,
        as the document gets smaller with each application of the filters.
        """
        for fun in filters:
            doc = fun(doc)

        return doc

    for doc in docs:
        yield apply_all(doc, *filters)


def tokenize_documents(
    raw_docs: Iterable[str], tokenize_fun: Callable[[str], Tokens], **kwargs
) -> Iterator[Document]:
    """
    Create Document objects from raw text, using the given tokenizer.

    Any additional keyword arguments are passed onto the tokenization function.
    """
    tokenize_fun = partial(tokenize_fun, **kwargs)
    for raw_doc in raw_docs:
        yield Document.fromtext(raw_doc, tokenize_fun=tokenize_fun)


def selected_properties(
    docs: Iterable[Document], property_fun: Property_Function[Property]
) -> Iterator[tuple[Property, ...]]:
    """
    From the given documents, get the properties for *selected* tokens only.
    """
    for doc in docs:
        props = property_fun(doc)
        yield tuple(
            prop for token, prop in zip(doc, props) if token in doc.selected_tokens
        )
