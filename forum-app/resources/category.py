from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from models import CategoryModel, PostModel
from db import db
from schemas import CategorySchema, PostSchema

blp = Blueprint('Categories', __name__, url_prefix="/api", description='Operations on category')


@blp.route("/category")
class CategoryList(MethodView):
    @blp.response(200, CategorySchema(many=True))
    def get(self):
        return CategoryModel.query.all()

    @blp.arguments(CategorySchema)
    @blp.response(201, CategorySchema)
    def post(self, category_data):
        if CategoryModel.query.filter(CategoryModel.name == category_data["name"]).first():
            abort(400, message="A category with that name already exists.")

        category = CategoryModel(**category_data)
        try:
            db.session.add(category)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(
                500,
                message=str(e),
            )
        return category


@blp.route("/category/<int:category_id>")
class Category(MethodView):
    @blp.response(200, CategorySchema)
    def get(self, category_id):
        try:
            category = CategoryModel.query.get_or_404(category_id)
        except KeyError:
            abort(404, message="Category not found!")
        return category

    def delete(self, category_id):
        category = CategoryModel.query.get_or_404(category_id)
        db.session.delete(category)
        db.session.commit()
        return {"message": "Category deleted successfully."}, 200


@blp.route("/category/<int:category_id>/post")
class CategoryPost(MethodView):
    @blp.response(200, PostSchema(many=True))
    def get(self, category_id):
        category = CategoryModel.query.get_or_404(category_id)
        return category.posts


@blp.route("/category/<int:category_id>/post/<int:post_id>")
class LinkCategoryToPost(MethodView):
    @blp.response(201, CategorySchema)
    def post(self, category_id, post_id):
        category = CategoryModel.query.get_or_404(category_id)
        post = PostModel.query.get_or_404(post_id)

        # Check if the post already belongs to a category
        if post.category_id:
            abort(400, message="Post already belongs to a category.")

        # Assign the category to the post
        post.category = category

        try:
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while linking post to the category.")

        return category

    @blp.response(200, CategorySchema)
    def delete(self, category_id, post_id):
        category = CategoryModel.query.get_or_404(category_id)
        post = PostModel.query.get_or_404(post_id)

        # Check if the post belongs to the specified category
        if post.category_id != category.id:
            abort(404, message="Post does not belong to the specified category.")

        # Remove the category from the post
        post.category = None

        try:
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while deleting the link.")

        return category


