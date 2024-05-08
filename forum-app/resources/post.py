from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_

from flask import jsonify

from flask_jwt_extended import jwt_required, get_jwt_identity

from db import db
from models import PostModel, VoteModel
from schemas import PostSchema, PostUpdateSchema, FilterSchema, SearchResultSchema

blp = Blueprint("Posts", __name__, url_prefix="/api", description="Operations on posts")


@blp.route("/post/<int:post_id>")
class Post(MethodView):
    @blp.response(200, PostSchema)
    def get(self, post_id):
        try:
            post = PostModel.query.get_or_404(post_id)
        except KeyError:
            abort(404, message="Post not found!")
        return post

    @jwt_required()
    def delete(self, post_id):
        post = PostModel.query.get_or_404(post_id)
        db.session.delete(post)
        db.session.commit()
        return {'message': 'Post deleted successfully'}, 200

    @blp.arguments(PostUpdateSchema)
    @blp.response(200, PostSchema)  # response decorator always should be placed deeper
    def put(self, post_data, post_id):
        post = PostModel.query.get(post_id)
        if post:
            post.title = post_data['title']
            post.description = post_data['description']
        else:
            post = PostModel(id=post_id, **post_data)
        db.session.add(post)
        db.session.commit()
        return post


@blp.route('/post')
class PostList(MethodView):
    @blp.response(200, PostSchema(many=True))
    def get(self):
        return PostModel.query.all()

    @jwt_required()
    @blp.arguments(PostSchema)
    @blp.response(201, PostSchema)
    def post(self, post_data):
        post = PostModel(**post_data)
        try:
            db.session.add(post)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message='An error occurred while inserting the post')
        return post


@blp.route('/post/<int:post_id>/upvote')
class Upvote(MethodView):
    @jwt_required()
    @blp.response(201, PostSchema)
    def post(self, post_id):
        """Upvote a post"""
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({'message': 'Need to login to vote.'}), 400

        vote = VoteModel.query.filter_by(post_id=post_id, user_id=user_id, vote_type='upvote').first()
        post = PostModel.query.get_or_404(post_id)

        if vote:
            # post.upvote -= 1
            # db.session.delete(vote)
            # db.session.commit()
            return jsonify({'message': 'You have already upvoted this post'}), 400

        post.upvote += 1
        db.session.add(VoteModel(post_id=post_id, user_id=user_id, vote_type='upvote'))
        db.session.commit()
        return post


@blp.route('/post/<int:post_id>/downvote')
class Downvote(MethodView):
    @jwt_required()
    @blp.response(201, PostSchema)
    def post(self, post_id):
        """Downvote a post"""
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({'message': 'Need to login to vote.'}), 200

        vote = VoteModel.query.filter_by(post_id=post_id, user_id=user_id, vote_type='downvote').first()
        if vote:
            return jsonify({'message': 'You have already downvoted this post'}), 400

        post = PostModel.query.get_or_404(post_id)
        post.downvote += 1
        db.session.add(VoteModel(post_id=post_id, user_id=user_id, vote_type='downvote'))
        db.session.commit()
        return post


@blp.route("/filter")
class FilterEndpoint(MethodView):
    @blp.arguments(FilterSchema, location="query")
    @blp.response(200, PostSchema(many=True))
    def get(self, filter_data):
        # Build the filter criteria based on the provided query parameters
        filter_criteria = []
        if filter_data.get('tags'):
            filter_criteria.append(PostModel.tags.any(name=filter_data['tags']))
        if filter_data.get('category'):
            filter_criteria.append(PostModel.category.has(name=filter_data['category']))

        if not filter_criteria:
            abort(400, message="No filter criteria provided.")

        # Combine filter criteria with OR
        query = PostModel.query.filter(or_(*filter_criteria)).all()

        if not query:
            abort(404, message="No results found.")

        return query


@blp.route("/search")
class SearchEndpoint(MethodView):
    @blp.arguments(SearchResultSchema, location="query")
    @blp.response(200, SearchResultSchema(many=True))
    def get(self, search_data):
        # print("Search data:", search_data)
        # Extract the search query from the search_data dictionary
        if not search_data:
            abort(400, message="No search query provided.")
        else:
            search_query = search_data.get("query")
            results = PostModel.query.filter(or_(PostModel.title.ilike(f"%{search_query}%"),
                                                 PostModel.description.ilike(f"%{search_query}%"))).all()
            return results


