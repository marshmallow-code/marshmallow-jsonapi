from flask import Flask, url_for, jsonify as J, request

### MODELS ###

class Model:
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

class Comment(Model):
    pass

class Author(Model):
    pass

class Post(Model):
    pass

### MOCK DATABASE ###

comment1 = Comment(id=1, body='First!')
comment2 = Comment(id=2, body='I like XML better!')

author1 = Author(id=1, first_name='Dan', last_name='Gebhardt', twitter='dgeb')

post1 = Post(id=1, title='JSON API paints my bikeshed!',
        author=author1, comments=[comment1, comment2])

db = {
    'comments': [
        comment1,
        comment2
    ],
    'authors': [author1],
    'posts': [post1]
}


### SCHEMAS ###

from marshmallow import validate
from marshmallow_jsonapi import Schema, fields
from marshmallow_jsonapi.flask import HyperlinkRelated

class CommentSchema(Schema):
    id = fields.Str(dump_only=True)
    body = fields.Str()

    class Meta:
        type_ = 'comments'

class AuthorSchema(Schema):
    id = fields.Str(dump_only=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    password = fields.Str(load_only=True, validate=validate.Length(6))
    twitter = fields.Str()

    def get_top_level_links(self, data, many):
        if many:
            self_link = url_for('authors_list', _external=True)
        else:
            self_link = url_for('author_detail', author_id=data['id'], _external=True)
        return {'self': self_link}

    class Meta:
        type_ = 'people'

class PostSchema(Schema):
    id = fields.Str(dump_only=True)
    title = fields.Str()

    author = HyperlinkRelated(
        endpoint='author_detail',
        url_kwargs={'author_id': '<author.id>', '_external': True},
        include_data=True,
        type_='people',
    )

    comments = HyperlinkRelated(
        endpoint='posts_comments',
        url_kwargs={'post_id': '<id>', '_external': True},
        many=True,
        include_data=True,
        type_='comments'
    )

    def get_top_level_links(self, data, many):
        if many:
            self_link = url_for('posts_list', _external=True)
        else:
            self_link = url_for('posts_detail', post_id=data['id'], _external=True)
        return {'self': self_link}

    class Meta:
        type_ = 'posts'


### VIEWS ###

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route('/posts/', methods=['GET'])
def posts_list():
    posts = db['posts']
    data, errs = PostSchema(many=True).dump(posts)
    return J(data)

@app.route('/posts/<int:post_id>')
def posts_detail(post_id):
    post = db['posts'][post_id - 1]
    data, errs = PostSchema().dump(post)
    return J(data)

@app.route('/posts/<int:post_id>/comments/')
def posts_comments(post_id):
    post = db['posts'][post_id - 1]
    comments = post.comments
    data, errs = CommentSchema(many=True).dump(comments)
    return J(data)

@app.route('/authors/')
def authors_list():
    author = db['authors']
    data, errs = AuthorSchema(many=True).dump(author)
    return J(data)

@app.route('/authors/<int:author_id>')
def author_detail(author_id):
    author = db['authors'][author_id - 1]
    data, errs = AuthorSchema().dump(author)
    return J(data)

@app.route('/authors/', methods=['POST'])
def author_create():
    schema = AuthorSchema()
    input_data = request.get_json() or {}
    data, errs = schema.load(input_data)
    if errs:
        return J(errs), 422
    id_ = len(db['authors'])
    author = Author(id=id_, **data)
    db['authors'].append(author)
    result = schema.dump(author)
    return J(result.data)

if __name__ == "__main__":
    app.run()
