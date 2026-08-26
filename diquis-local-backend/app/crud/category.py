from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from fastapi import HTTPException
from app.models.category import Category, UserCategoryOverride
from app.schemas.category import CategoryCreate, CategoryUpdate
import uuid

def get_categories(db: Session, user_id: str):
    query = db.query(
        Category.id,
        func.coalesce(UserCategoryOverride.custom_name, Category.name).label("name"),
        Category.domain,
        func.coalesce(UserCategoryOverride.custom_icon, Category.icon).label("icon"),
        Category.is_system,
        Category.is_essential_default,
        Category.sort_order
    ).outerjoin(
        UserCategoryOverride, 
        (Category.id == UserCategoryOverride.category_id) & (UserCategoryOverride.user_id == user_id)
    ).filter(
        (Category.is_system == True) | (Category.user_id == user_id)
    ).order_by(Category.sort_order).all()
    
    return query

def create_category(db: Session, user_id: str, category_in: CategoryCreate):
    max_order = db.query(func.max(Category.sort_order)).scalar() or 0
    valid_domains = [
        'grocery', 'transport', 'food_out', 'home', 'health', 
        'entertainment', 'education', 'income', 'savings', 'utilities', 
        'shopping', 'personal_care', 'family', 'other'
    ]
    domain = category_in.domain if category_in.domain in valid_domains else 'other'
    
    db_category = Category(
        user_id=user_id,
        name=category_in.name,
        domain=domain,
        icon=category_in.icon,
        is_system=False,
        is_essential_default=False,
        sort_order=max_order + 1
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def update_category(db: Session, category_id: str, user_id: str, category_in: CategoryUpdate):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada.")

    if db_category.is_system:
        stmt = insert(UserCategoryOverride).values(
            user_id=user_id,
            category_id=category_id,
            custom_name=category_in.name,
            custom_icon=category_in.icon
        )
        
        stmt = stmt.on_conflict_do_update(
            index_elements=['user_id', 'category_id'],
            set_={
                'custom_name': func.coalesce(stmt.excluded.custom_name, UserCategoryOverride.custom_name),
                'custom_icon': func.coalesce(stmt.excluded.custom_icon, UserCategoryOverride.custom_icon),
                'updated_at': func.now()
            }
        )
        db.execute(stmt)
        
    else:
        if str(db_category.user_id) != str(user_id):
            raise HTTPException(status_code=403, detail="No tienes permiso para editar esta categoría.")

        if category_in.name is not None:
            db_category.name = category_in.name
        if category_in.icon is not None:
            db_category.icon = category_in.icon

    db.commit()
    return {"message": "Categoría actualizada exitosamente."}

def delete_category(db: Session, category_id: str, user_id: str):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada.")
    
    if db_category.is_system:
        raise HTTPException(status_code=403, detail="No puedes eliminar una categoría del sistema. Solo puedes editarla o ignorarla.")
    
    if str(db_category.user_id) != str(user_id):
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar esta categoría.")
    
    db.delete(db_category)
    db.commit()
    return {"message": "Categoría eliminada exitosamente."}