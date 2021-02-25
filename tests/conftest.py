import pytest

from tests.base import (
    Author,
    Post,
    Comment,
    Keyword,
    User,
    PaymentMethodCreditCard,
    PaymentMethodPaypal,
    fake,
)


def make_author():
    return Author(
        id=fake.random_int(),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        twitter=fake.domain_word(),
    )


def make_post(with_comments=True, with_author=True, with_keywords=True):
    comments = [make_comment() for _ in range(2)] if with_comments else []
    keywords = [make_keyword() for _ in range(3)] if with_keywords else []
    author = make_author() if with_author else None
    return Post(
        id=fake.random_int(),
        title=fake.catch_phrase(),
        author=author,
        author_id=author.id if with_author else None,
        comments=comments,
        keywords=keywords,
    )


def make_comment(with_author=True):
    author = make_author() if with_author else None
    return Comment(id=fake.random_int(), body=fake.bs(), author=author)


def make_keyword():
    return Keyword(keyword=fake.domain_word())


def make_payment_methods():
    return [
        PaymentMethodCreditCard(id=fake.random_int(), last_4="1335"),
        PaymentMethodPaypal(id=fake.random_int(), linked_email="gal@example.com"),
    ]


def make_user():
    return User(
        id=fake.random_int(),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        payment_methods=make_payment_methods(),
    )


@pytest.fixture()
def user():
    return make_user()


@pytest.fixture()
def payment_methods():
    return make_payment_methods()


@pytest.fixture()
def author():
    return make_author()


@pytest.fixture()
def authors():
    return [make_author() for _ in range(3)]


@pytest.fixture()
def comments():
    return [make_comment() for _ in range(3)]


@pytest.fixture()
def post():
    return make_post()


@pytest.fixture()
def post_with_null_comment():
    return make_post(with_comments=False)


@pytest.fixture()
def post_with_null_author():
    return make_post(with_author=False)


@pytest.fixture()
def posts():
    return [make_post() for _ in range(3)]
