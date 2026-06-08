from database.crud.base import BaseCRUD
from database.models import Project

class ProjectCRUD(BaseCRUD):
    pass

project_crud = ProjectCRUD(Project)