from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker, Session
from sqlalchemy import create_engine
import numpy as np

Base = declarative_base()


class Issue(Base):
    __tablename__ = "issue"
    id = Column(Integer, primary_key=True)
    github_id = Column(Integer)
    title = Column(String)
    boby = Column(String)
    repo_name = Column(String)
    embedding = Column(LargeBinary)
    # cluster_id = Column("cluster_id", Integer, ForeignKey("cluster.id"))


class Cluster(Base):
    __tablename__ = "cluster"
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer)
    issue_id = Column(Integer)
    # issues = relationship("Issue", backref=backref("issue"))


def get_issue_by_repo(session: Session, repo_name: str):
    return session.query(Issue).filter_by(repo_name=repo_name).all()


def create_new_issue(session: Session, github_id: int, title: str, body: str,
                 embedding: np.ndarray, repo_name: str):
    issue = Issue()
    issue.title = title
    issue.boby = body
    issue.github_id = github_id
    issue.embedding = embedding.tobytes()
    issue.repo_name = repo_name
    session.add(issue)
    session.commit()


def create_new_cluster(session: Session, issue_id: int, group_id: int) -> Cluster:
    new_cluster = Cluster()
    new_cluster.issue_id = issue_id
    new_cluster.group_id = group_id
    session.add(new_cluster)
    session.commit()
    return new_cluster


def setup_db() -> Session:
    """Main entry point of program"""
    # Connect to the database using SQLAlchemy
    engine = create_engine(f"sqlite:///models.db")
    Session = sessionmaker()
    Session.configure(bind=engine)
    return Session()
