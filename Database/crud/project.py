from Database.crud.base import BaseCRUD
from Database.models import Project

class ProjectCRUD(BaseCRUD):
    pass

project_crud = ProjectCRUD(Project)