from fastapi import APIRouter, HTTPException, Depends
from app.dependencies import get_current_user, super_admin_only
from app.services.firebase import set_user_role, get_db
from datetime import datetime, timezone

router = APIRouter()


@router.post("/verify")
def verify(user: dict = Depends(get_current_user)):
    db = get_db()
    doc = db.collection("users").document(user["uid"]).get()
    role = "Team Member"
    if doc.exists:
        role = doc.to_dict().get("role", "Team Member")
    return {
        "uid": user.get("uid"),
        "email": user.get("email"),
        "role": role,
    }


@router.post("/set-role")
def assign_role(body: dict, user: dict = Depends(super_admin_only)):
    uid = body.get("uid")
    role = body.get("role")
    if not uid or not role:
        raise HTTPException(status_code=400, detail="uid and role are required")
    if role not in ["Team Member", "Admin", "Super Admin"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    try:
        set_user_role(uid, role)
        return {"message": f"Role '{role}' assigned to {uid}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
