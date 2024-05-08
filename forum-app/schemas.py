from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class PlainPostSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str(required=True)
    upvote = fields.Int()
    downvote = fields.Int()
    created_at = fields.Date()


class PlainCommentSchema(Schema):
    id = fields.Int(dump_only=True)
    comment_txt = fields.Str(required=True)
    replied_at = fields.Date(dump_only=True)


class PlainCategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class PlainTagSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class CommentSchema(PlainCommentSchema):
    post_id = fields.Int(load_only=True)
    post = fields.Nested(PlainPostSchema(), dump_only=True)


class PostSchema(PlainPostSchema):
    comments = fields.List(fields.Nested(PlainCommentSchema()), dump_only=True)
    category = fields.Nested(PlainCategorySchema(), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)


class PostUpdateSchema(Schema):
    title = fields.Str()
    description = fields.Str()


class CategorySchema(PlainCategorySchema):
    posts = fields.List(fields.Nested(PlainPostSchema()), dump_only=True)


class TagSchema(PlainTagSchema):
    posts = fields.List(fields.Nested(PlainPostSchema()), dump_only=True)


class TagAndPostSchema(Schema):
    message = fields.Str()
    post = fields.Nested(PostSchema)
    tag = fields.Nested(TagSchema)


class SearchResultSchema(Schema):
    # search query
    query = fields.String(load_only=True)

    id = fields.Integer()
    title = fields.String()
    description = fields.String()


class FilterSchema(Schema):
    tags = fields.String()
    category = fields.String()
    # Add more fields as needed
