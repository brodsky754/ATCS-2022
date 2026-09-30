"""
The file that holds the schema/classes
that will be used to create objects
and connect to data tables.
"""

import hashlib
import hmac
import secrets

from sqlalchemy import ForeignKey, Column, INTEGER, TEXT, DATETIME
from sqlalchemy.orm import relationship
from database import Base

# Password storage format: "pbkdf2_sha256$<iterations>$<hex salt>$<hex digest>".
# Rows written before hashing existed hold the raw password; verify_password()
# still accepts those so existing accounts keep working, and Twitter.login()
# re-hashes them on the next successful login.
_HASH_NAME = "pbkdf2_sha256"
_ITERATIONS = 600_000  # OWASP recommendation for PBKDF2-HMAC-SHA256


def hash_password(password):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"),
                                 salt.encode("utf-8"), _ITERATIONS)
    return "$".join([_HASH_NAME, str(_ITERATIONS), salt, digest.hex()])


def is_hashed(stored):
    return stored.startswith(_HASH_NAME + "$")


def verify_password(stored, password):
    if not is_hashed(stored):
        # Legacy plaintext row: constant-time compare against the raw value.
        return hmac.compare_digest(stored.encode("utf-8"), password.encode("utf-8"))
    try:
        _, iterations, salt, digest_hex = stored.split("$", 3)
        iterations = int(iterations)
    except ValueError:
        return False
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"),
                                    salt.encode("utf-8"), iterations)
    return hmac.compare_digest(candidate.hex(), digest_hex)

class User(Base):
    __tablename__ = "users"

    # Columns
    username = Column("username", TEXT, primary_key=True)
    password = Column("password", TEXT, nullable=False)

    following = relationship("User", 
                             secondary="followers",
                             primaryjoin="User.username==Follower.follower_id",
                             secondaryjoin="User.username==Follower.following_id")
    
    followers = relationship("User", 
                             secondary="followers",
                             primaryjoin="User.username==Follower.following_id",
                             secondaryjoin="User.username==Follower.follower_id",
                             overlaps="following")
    
    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def set_password(self, password):
        self.password = hash_password(password)

    def check_password(self, password):
        return verify_password(self.password, password)

    def needs_rehash(self):
        return not is_hashed(self.password)
    
    def __repr__(self):
        return "@" + self.username


class Follower(Base):
    __tablename__ = "followers"

    # Columns
    id = Column("id", INTEGER, primary_key=True)
    follower_id = Column('follower_id', TEXT, ForeignKey('users.username'))
    following_id = Column('following_id', TEXT, ForeignKey('users.username'))

    def __init__(self, follower_id, following_id):
        self.follower_id = follower_id
        self.following_id = following_id

class Tweet(Base):
    # TODO: Complete the class
    __tablename__ = "tweets"

    id = Column("id", INTEGER, primary_key = True)
    content = Column("content", TEXT)
    timestamp = Column("timestamp", TEXT)
    username = Column("username", TEXT)
    tags = relationship("Tag", secondary = "tweet_tags", back_populates = "tweets")
    
    

    def __init__(self, content, timestamp, username):
        self.content = content
        self.timestamp = timestamp
        self.username = username

    def __repr__(self):
        list_tags = ""
        for t in self.tags:
            list_tags = list_tags + t.content
        return "@" + self.username + "\n" + self.content  + "\n" + list_tags + "\n" + self.timestamp 
        
class Tag(Base):
    # TODO: Complete the class
    __tablename__ = "tags"

    id = Column("id", INTEGER, primary_key = True)
    content = Column("content", TEXT, nullable = False)
    tweets = relationship("Tweet", secondary = "tweet_tags", back_populates = "tags")

    def __init__(self, content):
        self.content = content

    def __repr__(self):
        return "#" + self.content
    

class TweetTag(Base):
    # TODO: Complete the class
    __tablename__ = "tweet_tags"

    id = Column("id", INTEGER, primary_key = True)
    tweet_id = Column("tweet_id", INTEGER, ForeignKey('tweets.id'))
    tag_id = Column("tag_id", INTEGER, ForeignKey('tags.id'))

    def __init__(self, tweet_id, tag_id):
        self.tweet_id = tweet_id
        self.tag_id = tag_id

