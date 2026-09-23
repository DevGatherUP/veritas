from app.services.embedder import embed, embed_many


def test_embed_returns_vector():
    result = embed("fever and headache were reported in patients")
    assert isinstance(result, list)
    assert len(result) == 384
    assert all(isinstance(v, float) for v in result)


def test_embed_many_returns_list_of_vectors():
    texts = ["fever was reported", "the drug was approved in 2019"]
    result = embed_many(texts)
    assert len(result) == 2
    assert all(len(v) == 384 for v in result)
