from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from flask_jwt_extended import jwt_required

from schemas import CommentSchema

from db import db

from models import CommentModel, PostModel

blp = Blueprint("Comments", __name__, url_prefix="/api", description="Operations on comments")


@blp.route("/post/<int:post_id>/comment")
class CommentsInPost(MethodView):
    @blp.response(200, CommentSchema(many=True))
    def get(self, post_id):
        post = PostModel.query.get_or_404(post_id)
        return post.comments.all()

    @jwt_required()
    @blp.arguments(CommentSchema)
    @blp.response(201, CommentSchema)
    def post(self, comment_data, post_id):
        print(post_id)
        comment = CommentModel(**comment_data, post_id=post_id)
        print(comment)
        try:
            db.session.add(comment)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message='An error occurred while inserting the comment.')
        return comment


@blp.route("/comment/<int:comment_id>")
class Comment(MethodView):
    @blp.response(200, CommentSchema)
    def get(self, comment_id):
        comment = CommentModel.query.get_or_404(comment_id)
        return comment

    def delete(self, comment_id):
        comment = CommentModel.query.get_or_404(comment_id)
        db.session.delete(comment)
        db.session.commit()
        return {'message': 'Comment deleted successfully.'}, 200

