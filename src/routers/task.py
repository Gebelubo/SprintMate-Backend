from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from src.service.board_service import BoardService
from src.entities.schemas import TaskMoveRequest, UserResponse
from src.service.attachment_service import AttachmentService
from src.service.comment_service import CommentService
from src.service.project_service import ProjectService
from src.db.deps import get_db
from src.entities.schemas import (
    AttachmentCreate,
    AttachmentCreate,
    AttachmentResponse,
    CommentCreate,
    CommentResponse,
    CommentUpdate,
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    UserTaskResponse
)
from src.service.task_service import TaskService
from src.utils.dependencies import get_current_user
from src.entities.models import User


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)

comment_router = APIRouter(
    prefix="/comments",
    tags=["Comments"]
)

attachment_router = APIRouter(
    prefix="/attachments",
    tags=["Attachments"]
)

def get_task_service(
    db: Session = Depends(get_db)
) -> TaskService:
    return TaskService(db)

def get_project_service(
    db: Session = Depends(get_db)
) -> ProjectService:
    return ProjectService(db)

def get_comment_service(
    db: Session = Depends(get_db)
):
    return CommentService(db)

def get_attachment_service(
    db: Session = Depends(get_db)
):
    return AttachmentService(db)


@router.post("/", response_model=TaskResponse)
def create_task(
    data: TaskCreate,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    task= service.create_task(
        data=data,
        created_by=current_user.id
    )
    return task


@router.get("/", response_model=list[TaskResponse])
def list_tasks(
    service: TaskService = Depends(get_task_service)
):
    return service.get_all_tasks()


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    service: TaskService = Depends(get_task_service)
):
    task = service.get_task(task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task


@router.put(
    "/{task_id}",
    response_model=TaskResponse
)
def update_task(
    task_id: int,
    data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
    project_service: ProjectService = Depends(get_project_service),
):
    task = service.get_task(task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    if data.points is not None or data.estimate is not None:
        if not project_service.is_project_leader(task.project_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Only the project leader can set the task estimate/points",
            )

    updated_task = service.update_task(task_id, data)

    if not updated_task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return updated_task


@router.delete(
    "/{task_id}",
    status_code=204
)
def delete_task(
    task_id: int,
    service: TaskService = Depends(get_task_service)
):
    deleted = service.delete_task(task_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )
    
@router.get(
    "/{task_id}/comments",
    response_model=list[CommentResponse]
)
def list_comments(
    task_id: int,
    service: CommentService = Depends(
        get_comment_service
    )
):
    return service.get_task_comments(task_id)


@router.post(
    "/{task_id}/comments",
    response_model=CommentResponse
)
def create_comment(
    task_id: int,
    data: CommentCreate,
    current_user: User = Depends(
        get_current_user
    ),
    service: CommentService = Depends(
        get_comment_service
    )
):
    return service.create_comment(
        task_id=task_id,
        user_id=current_user.id,
        data=data
    )

@comment_router.get(
    "/{comment_id}",
    response_model=CommentResponse
)
def get_comment(
    comment_id: int,
    service: CommentService = Depends(
        get_comment_service
    )
):
    comment = service.get_comment(comment_id)

    if not comment:
        raise HTTPException(
            404,
            "Comment not found"
        )

    return comment


@comment_router.patch(
    "/{comment_id}",
    response_model=CommentResponse
)
def update_comment(
    comment_id: int,
    data: CommentUpdate,
    service: CommentService = Depends(
        get_comment_service
    )
):
    comment = service.update_comment(
        comment_id,
        data
    )

    if not comment:
        raise HTTPException(
            404,
            "Comment not found"
        )

    return comment


@comment_router.delete(
    "/{comment_id}",
    status_code=204
)
def delete_comment(
    comment_id: int,
    service: CommentService = Depends(
        get_comment_service
    )
):
    deleted = service.delete_comment(
        comment_id
    )

    if not deleted:
        raise HTTPException(
            404,
            "Comment not found"
        )
    
@router.get(
    "/{task_id}/attachments",
    response_model=list[AttachmentResponse]
)
def list_attachments(
    task_id: int,
    service: AttachmentService = Depends(
        get_attachment_service
    )
):
    return service.get_task_attachments(
        task_id
    )


@router.post(
    "/{task_id}/attachments",
    response_model=AttachmentResponse
)
def create_attachment(
    task_id: int,
    data: AttachmentCreate,
    service: AttachmentService = Depends(
        get_attachment_service
    )
):
    return service.create_attachment(
        task_id,
        data
    )

@attachment_router.get(
    "/{attachment_id}",
    response_model=AttachmentResponse
)
def get_attachment(
    attachment_id: int,
    service: AttachmentService = Depends(
        get_attachment_service
    )
):
    attachment = service.get_attachment(
        attachment_id
    )

    if not attachment:
        raise HTTPException(
            404,
            "Attachment not found"
        )

    return attachment


@attachment_router.delete(
    "/{attachment_id}",
    status_code=204
)
def delete_attachment(
    attachment_id: int,
    service: AttachmentService = Depends(
        get_attachment_service
    )
):
    deleted = service.delete_attachment(
        attachment_id
    )

    if not deleted:
        raise HTTPException(
            404,
            "Attachment not found"
        )

# --- Board move ---

def get_board_service(db: Session = Depends(get_db)) -> BoardService:
    return BoardService(db)


@router.patch("/{task_id}/move", response_model=TaskResponse)
def move_task(
    task_id: int,
    data: TaskMoveRequest,
    current_user: User = Depends(get_current_user),
    board_service: BoardService = Depends(get_board_service),
):
    task = board_service.move_task(task_id, data.column_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task or column not found")
    return task

@router.post("/{task_id}/users/{user_id}/assign", response_model=UserTaskResponse)
def assign_user_to_task(
    item_id: int,
    user_id: int,
    service: TaskService = Depends(get_task_service)
):
    try:
        user_task = service.assign_user_to_task(item_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=409, detail="User is already assigned to this task.")
    if not user_task:
        raise HTTPException(status_code=404, detail="Task or user not found")
    return user_task

@router.get("/{task_id}/assigned-user", response_model=UserResponse)
def get_assigned_user(
    task_id: int,
    service: TaskService = Depends(get_task_service)
):
    user = service.get_assigned_user(task_id)
    if not user:
        raise HTTPException(status_code=404, detail="Task not found or no user assigned")
    return user