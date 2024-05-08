from datetime import datetime

from db import db


class PostModel(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String, nullable=True)
    upvote = db.Column(db.Integer, default=0)
    downvote = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)

    comments = db.relationship(
        "CommentModel", back_populates="post", lazy="dynamic", cascade="all, delete"
    )

    category_id = db.Column(
        db.Integer, db.ForeignKey("categories.id"), unique=False, nullable=True
    )

    category = db.relationship("CategoryModel", back_populates="posts")

    tags = db.relationship("TagModel", back_populates="posts", secondary="posts_tags")

