from db import db

from datetime import datetime


class CommentModel(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)  # auto increment
    comment_txt = db.Column(db.String(), nullable=False)
    replied_at = db.Column(db.DateTime, default=datetime.now)
    # many to one for posts table
    post_id = db.Column(
        db.Integer, db.ForeignKey("posts.id"), unique=False, nullable=False
    )

    post = db.relationship("PostModel", back_populates="comments")
