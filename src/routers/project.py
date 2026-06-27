from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from src.db.deps import get_db
from src.entities.models import User
from src.entities.schemas import (
    ProjectCreate, ProjectUpdate, ProjectResponse,
    ProjectUserAdd, ProjectUserUpdateRole, ProjectUserResponse,
    BoardColumnCreate, BoardColumnUpdate, BoardColumnResponse,
    TaskResponse, ProjectInvite
)
from src.service.project_service import ProjectService
from src.service.board_service import BoardService
from src.utils.dependencies import get_current_user

router = APIRouter(prefix="/projects", tags=["Projects"])


def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    return ProjectService(db)


@router.post("/", response_model=ProjectResponse)
def create_project(
    data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
):
    project = service.create_project(data=data, created_by=current_user.id)
    if not project:
        raise HTTPException(status_code=400, detail="Could not create project")
    return project


@router.get("/", response_model=list[ProjectResponse])
def list_projects(
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
):
    return service.get_all_projects()


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
):
    project = service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
):
    project = service.update_project(project_id, data)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
):
    deleted = service.delete_project(project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")


# --- Project members ---

@router.get("/{project_id}/users", response_model=list[ProjectUserResponse])
def get_project_users(
    project_id: int,
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
):
    return service.get_project_users(project_id)


@router.post("/{project_id}/users", response_model=ProjectUserResponse)
def add_user(
    project_id: int,
    data: ProjectUserAdd,
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
):
    assoc = service.add_user_to_project(project_id, data)
    if not assoc:
        raise HTTPException(status_code=400, detail="Could not add user to project")
    return assoc


@router.put("/{project_id}/users/{user_id}", response_model=ProjectUserResponse)
def update_user_role(
    project_id: int,
    user_id: int,
    data: ProjectUserUpdateRole,
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
):
    assoc = service.update_user_role(project_id, user_id, data)
    if not assoc:
        raise HTTPException(status_code=404, detail="User not found in project")
    return assoc


@router.delete("/{project_id}/users/{user_id}", status_code=204)
def remove_user(
    project_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
):
    removed = service.remove_user_from_project(project_id, user_id)
    if not removed:
        raise HTTPException(status_code=404, detail="User not found in project")

# --- Board columns ---

def get_board_service(db: Session = Depends(get_db)) -> BoardService:
    return BoardService(db)


@router.get("/{project_id}/columns", response_model=list[BoardColumnResponse])
def get_columns(
    project_id: int,
    current_user: User = Depends(get_current_user),
    service: BoardService = Depends(get_board_service),
):
    return service.get_project_columns(project_id)


@router.post("/{project_id}/columns", response_model=BoardColumnResponse)
def create_column(
    project_id: int,
    data: BoardColumnCreate,
    current_user: User = Depends(get_current_user),
    service: BoardService = Depends(get_board_service),
):
    column = service.create_column(project_id, data)
    if not column:
        raise HTTPException(status_code=400, detail="Could not create column")
    return column


@router.put("/{project_id}/columns/{column_id}", response_model=BoardColumnResponse)
def update_column(
    project_id: int,
    column_id: int,
    data: BoardColumnUpdate,
    current_user: User = Depends(get_current_user),
    service: BoardService = Depends(get_board_service),
):
    column = service.update_column(column_id, data)
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    return column


@router.delete("/{project_id}/columns/{column_id}", status_code=204)
def delete_column(
    project_id: int,
    column_id: int,
    current_user: User = Depends(get_current_user),
    service: BoardService = Depends(get_board_service),
):
    deleted = service.delete_column(column_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Column not found")


@router.get("/{project_id}/columns/{column_id}", response_model=BoardColumnResponse)
def get_column_by_id(
    project_id: int,
    column_id: int,
    current_user: User = Depends(get_current_user),
    service: BoardService = Depends(get_board_service),
):
    column = service.get_column(column_id)
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    return column


@router.get("/{project_id}/columns/{column_id}/tasks", response_model=list[TaskResponse])
def get_column_tasks(
    project_id: int,
    column_id: int,
    current_user: User = Depends(get_current_user),
    service: BoardService = Depends(get_board_service),
):
    return service.get_column_tasks(column_id)

@router.post("/{project_id}/join/{role}")
def join_project(
    project_id: int,
    role: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ProjectService(db)

    service.add_user_to_project(
        project_id,
        ProjectUserAdd(
            user_id=current_user.id,
            role=role
        )
    )

    return {
        "message": "Project joined successfully"
    }

@router.post("/{project_id}/invite")
def invite_user(
    project_id: int,
    data: ProjectInvite,
    db: Session = Depends(get_db)
):
    service = ProjectService(db)

    return service.invite_user(
        project_id,
        data.email
    )