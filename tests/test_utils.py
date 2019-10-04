import pytest

from marshmallow_jsonapi import fields, utils


def test_get_dump_key():
    field = fields.Integer(dump_to="new_key", data_key="new_key")  # 2.X vs 3.X
    assert utils.get_dump_key(field) == "new_key"


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
