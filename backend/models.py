from datetime import datetime

import itsdangerous
from flask import current_app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from backend import db


class User(db.Model, UserMixin):
    """
    A database model class to store information about users.
    ...
    Attributes
    ----------
    id : int
        ID of the user object
    name : str
        Name of the user
    email : str
        Email of the user
    password : str
        (Hashed) Password of the user
    access_level : int
        Flag indicating the permission level of the user
    Methods
    -------
    get_auth_token(expires_seconds=86400)
        Generates a new authentication token for the user
    verify_auth_token(token)
        Verifies the provided authentication token for the user
    get_reset_token(expires_seconds=1800)
        Generates a new password reset token for the user
    verify_reset_token(token)
        Verifies the provided password reset token for the user
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(127), nullable=False)
    email = db.Column(db.String(63), unique=True, nullable=False)
    password = db.Column(db.String(63), unique=False, nullable=False)
    access_level = db.Column(db.Integer, nullable=False, default=0)
    slack_session = db.Column(db.String(127), nullable=True)

    def __init__(self, name: str, email: str, password: str, access_level: int = 0):
        """
        Parameters
        ----------
        name : str
            Name of the user
        email : str
            Email of the user
        password : str
            (Hashed) Password of the user
        access_level : int
            Flag indicating the permission level of the user
        """
        self.name = name
        self.email = email
        self.password = password
        self.access_level = access_level

    def get_auth_token(self, expires_seconds: int = 3600) -> str:
        """
        Generates a new authentication token for the user.
        Parameters
        ----------
        expires_seconds : int, optional
            Number of seconds after which the token expires (default is 86400)
        Returns
        -------
        str
            The serialized authentication token to be returned to the user
        """
        s = Serializer(current_app.config['SECRET_KEY'], expires_seconds)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token: str):
        """
        Verifies the authentication token for the user.
        Parameters
        ----------
        token : str
            Serialized authentication token provided to verify the user's identity
        Returns
        -------
        User
            The User object corresponding to the provided authentication token
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except itsdangerous.BadSignature:
            return None
        return User.query.get(user_id)

    def get_reset_token(self, expires_seconds: int = 1800) -> str:
        """
        Generates a new password reset token for the user.
        Parameters
        ----------
        expires_seconds : int, optional
            Number of seconds after which the token expires (default is 86400)
        Returns
        -------
        str
            The serialized password reset token to be returned to the user
        """
        s = Serializer(current_app.config['SECRET_KEY'], expires_seconds)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token: str):
        """
        Verifies the password reset token for the user.
        Parameters
        ----------
        token : str
            Serialized password reset token provided to verify the user's identity
        Returns
        -------
        User
            The User object corresponding to the provided password reset token
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except itsdangerous.BadSignature:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User ID {self.id}"


class Query(db.Model):
    """
    A database model class to store information about queries.

    ...

    Attributes
    ----------
    id : int
        ID of the class
    entry_o : str
        Origin location entry from user
    entry_d : str
        Destination Location entry from user
    user_id : str
        User ID of the query creator, as stored in User table
    fd      : float
        Threshold distance before a recommendation is made for a stopover
    """

    id = db.Column(db.Integer, primary_key=True)
    entry_o = db.Column(db.String(127), nullable=False)
    entry_d = db.Column(db.String(127), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    fd = db.Column(db.Float, nullable=False)

    def __init__(self, entry_o: str, entry_d: str, user_id: int, fd: float = 50):
        """
        Parameters
        ----------
        entry_o : str
            Origin location entry from user
        entry_d : str
            Destination Location entry from user
        user_id : str
            User ID of the query creator, as stored in User table
        """
        self.entry_o = entry_o
        self.entry_d = entry_d
        self.user_id = user_id
        self.fd = fd


class Tag(db.Model):
    """
    A database model class to store information about tags.

    ...

    Attributes
    ----------
    id : int
        ID of the class
    keyword : str
        Keyword indicating user preference
    user_id : int
        User ID of the query creator, as stored in User table
    """

    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(127), nullable=False)
    query_id = db.Column(db.Integer, db.ForeignKey('query.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, keyword: str, query_id: int, user_id: int):
        """
        Parameters
        ----------
        keyword : str
            Keyword indicating user preference
        query_id : int
            Query ID of the query creator, as stored in User table
        user_id : int
            User ID of the query creator, as stored in User table
        """
        self.keyword = keyword
        self.query_id = query_id
        self.user_id = user_id


class Location(db.Model):
    """
    A database model class to store information about locations.

    ...

    Attributes
    ----------
    id : int
        ID of the class
    keyword : str
        Keyword indicating user sponsor location
    lat : float
        Latitude of sponsor location
    lng : float
        Longitude of sponsor location
    user_id : int
        User ID of the query creator, as stored in User table
    is_sp : bool
        Flag to denote whether or not is this a sponsor location
    query_id : int
        Query ID of the query creator, as stored in Query table
    """

    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(127), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_sp = db.Column(db.Boolean, nullable=False)
    query_id = db.Column(db.Integer, db.ForeignKey('query.id'), nullable=True)

    def __init__(self, keyword: str, lat: float, lng: float, user_id: int, query_id: int = -1, is_sp: bool = False):
        """
        Parameters
        ----------
        keyword : str
            Keyword indicating user sponsor location
        lat : float
            Latitude of sponsor location
        lng : float
            Longitude of sponsor location
        user_id : int
            User ID of the query creator, as stored in User table
        is_sp : bool
            Flag to denote whether or not is this a sponsor location
        query_id : int
            Query ID of the query creator, as stored in Query table
        """
        self.keyword = keyword
        self.lat = lat
        self.lng = lng
        self.user_id = user_id
        self.is_sp = is_sp
        if query_id != -1:
            self.query_id = query_id
