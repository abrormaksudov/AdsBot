from sqlalchemy import Column, BigInteger, String, TIMESTAMP, func, Integer

from tgbot.services.db_base import Base


class User(Base):
    __tablename__ = "users"
    user_id = Column(BigInteger, primary_key=True)
    first_name = Column(String(length=100), nullable=False)
    last_name = Column(String(length=100), nullable=True)
    username = Column(String(length=100), nullable=True, unique=True)
    role = Column(String(length=100), default='user')
    posted_today = Column(Integer, default=0)
    post_limit = Column(Integer, nullable=True)
    max_active = Column(Integer, nullable=True)
    restricted_till = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True),
                        default=func.now(),
                        onupdate=func.now(),
                        server_default=func.now())

    __mapper_args__ = {"eager_defaults": True}

    def __repr__(self):
        return f'User (ID: {self.user_id} - {self.first_name})'
