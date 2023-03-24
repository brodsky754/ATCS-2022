"""
The file that holds the schema/classes
that will be used to create objects
and connect to data tables.
"""

from sqlalchemy import ForeignKey, Column, INTEGER, TEXT, DATETIME
from sqlalchemy.orm import relationship
from database import Base

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


class Follower(Base):
    __tablename__ = "followers"

    # Columns
    id = Column("id", INTEGER, primary_key=True)
    follower_id = Column('follower_id', TEXT, ForeignKey('users.username'))
    following_id = Column('following_id', TEXT, ForeignKey('users.username'))

class Tweet(Base):
    __tablename__ = "tweet"
    # TODO: Complete the class
    id = Column("id", INTEGER, primary_key=True)
    content = Column('content',TEXT)
    timestamp = Column('timestamp', DATETIME)
    username = Column('username', TEXT, ForeignKey('users.username'))
    pass

class Tag(Base):
    __tablename__ = "tag"
    # TODO: Complete the class
    id = Column("id", INTEGER, primary_key=True)
    content = Column('content',TEXT)
    pass

class TweetTag(Base):
    __tablename__ = "tweettag"
    # TODO: Complete the class
    id = Column("id", INTEGER, primary_key=True)
    tweet_id = Column('tweet_id',TEXT, ForeignKey('tweets.id'))
    tag_id = Column('tag_id',TEXT, ForeignKey('tags.id'))
    pass
