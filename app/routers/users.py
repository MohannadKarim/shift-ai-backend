from fastapi import APIRouter, HTTPException, Depends
from app.dependencies import get_current_user, admin_only
from app.services.firebase import get_db

router = APIRouter()


@router.get("/me")
def get_me(user: dict = Depends(get_current_user)):
    db = get_db()
    doc = db.collection("users").document(user["uid"]).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="User profile not found")
    return {"id": doc.id, **doc.to_dict()}


@router.get("/leaderboard")
def leaderboard(user: dict = Depends(get_current_user)):
    db = get_db()
    docs = db.collection("users").order_by("points", direction="DESCENDING").limit(50).stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]


@router.get("/leaderboard/{department}")
def leaderboard_by_dept(department: str, user: dict = Depends(get_current_user)):
    db = get_db()
    docs = (
        db.collection("users")
        .where("department", "==", department)
        .order_by("points", direction="DESCENDING")
        .limit(50)
        .stream()
    )
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]


@router.get("/")
def list_users(user: dict = Depends(admin_only)):
    db = get_db()
    docs = db.collection("users").stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]


@router.put("/{uid}/role")
def update_role(uid: str, body: dict, user: dict = Depends(admin_only)):
    db = get_db()
    doc = db.collection("users").document(uid).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="User not found")
    role = body.get("role")
    if role not in ["Team Member", "Admin", "Super Admin"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    db.collection("users").document(uid).update({"role": role})
    return {"message": f"Role updated to {role}"}
