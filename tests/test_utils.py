import pytest

from marshmallow_jsonapi import utils


@pytest.mark.parametrize(
    "tag,val",
    [
        ("<id>", "id"),
        ("<author.last_name>", "author.last_name"),
        ("<comment.author.first_name>", "comment.author.first_name"),
        ("True", None),
        ("", None),
    ],
)
def test_tpl(tag, val):
    assert utils.tpl(tag) == val
