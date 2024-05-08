from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from models import TagModel, PostModel
from db import db
from schemas import TagSchema, TagAndPostSchema

blp = Blueprint('Tags', __name__, url_prefix="/api", description='Operations on tags')


@blp.route("/tag")
class TagList(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self):
        return TagModel.query.all()

    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, tag_data):
        tag = TagModel(**tag_data)
        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(
                500,
                message=str(e),
            )
        return tag


@blp.route("/tag/<int:tag_id>")
class Tag(MethodView):
    @blp.response(200, TagSchema)
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag

    @blp.response(
        202,
        description="Deletes a tag if no post is tagged with it.",
        example={"message": "Tag deleted."},
    )
    @blp.alt_response(404, description="Tag not found.")
    @blp.alt_response(
        400,
        description="Returned if the tag is assigned to one or more posts. In this case, the tag is not deleted.",
    )
    def delete(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)

        if not tag.posts:
            db.session.delete(tag)
            db.session.commit()
            return {"message": "Tag deleted."}
        abort(
            400,
            message="Could not delete tag. Make sure tag is not associated with any posts, then try again.",
        )


@blp.route("/post/<int:post_id>/tag/<int:tag_id>")
class LinkTagsToPost(MethodView):
    @blp.response(201, TagSchema)
    def post(self, post_id, tag_id):
        post = PostModel.query.get_or_404(post_id)
        tag = TagModel.query.get_or_404(tag_id)
        post.tags.append(tag)

        try:
            db.session.add(post)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the tag.")

        return tag

    @blp.response(200, TagAndPostSchema)
    def delete(self, post_id, tag_id):
        post = PostModel.query.get_or_404(post_id)
        tag = TagModel.query.get_or_404(tag_id)

        post.tags.remove(tag)

        try:
            db.session.add(post)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the tag.")

        return {"message": "Item removed from tag", "post": post, "tag": tag}

