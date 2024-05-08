from db import db


# Secondary table for many-to-many relationship between tags and posts
class PostsTags(db.Model):
    __tablename__ = "posts_tags"

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))
    tag_id = db.Column(db.Integer, db.ForeignKey("tags.id"))
