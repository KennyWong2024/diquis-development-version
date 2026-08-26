from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.api.dependencies import get_db_with_rls, get_current_user
from app.schemas.category import CategoryResponse, CategoryCreate, CategoryUpdate
from app.crud import category as crud_category

router = APIRouter()

@router.get("/", response_model=List[CategoryResponse])
def read_categories(
    db: Session = Depends(get_db_with_rls),
    current_user_id: str = Depends(get_current_user)
):
    """Lista todas las categorías, aplicando las preferencias visuales del usuario."""
    return crud_category.get_categories(db=db, user_id=current_user_id)

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category_in: CategoryCreate, 
    db: Session = Depends(get_db_with_rls),
    current_user_id: str = Depends(get_current_user)
):
    """Crea una nueva categoría personalizada para el usuario."""
    return crud_category.create_category(db=db, user_id=current_user_id, category_in=category_in)

@router.put("/{category_id}")
def update_category(
    category_id: str, 
    category_in: CategoryUpdate, 
    db: Session = Depends(get_db_with_rls),
    current_user_id: str = Depends(get_current_user)
):
    """
    Edita una categoría. 
    Si es de sistema, guarda las personalizaciones en la tabla satélite.
    Si es propia, la actualiza directamente.
    """
    return crud_category.update_category(
        db=db, category_id=category_id, user_id=current_user_id, category_in=category_in
    )

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: str, 
    db: Session = Depends(get_db_with_rls),
    current_user_id: str = Depends(get_current_user)
):
    """
    Elimina una categoría personalizada.
    Falla intencionalmente si se intenta borrar una de sistema o de otro usuario.
    """
    crud_category.delete_category(db=db, category_id=category_id, user_id=current_user_id)