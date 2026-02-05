# User Creation Error Handling Fix

## Issue

When trying to create a user with an email that already exists in the database, the system returned:
- **Frontend**: "Internal Server Error"
- **Backend**: 500 error with full stack trace

This was confusing for users who didn't know why the user creation failed.

## Root Cause

The backend CRUD function `create_user()` didn't handle database `IntegrityError` exceptions when duplicate emails or usernames were inserted. The error bubbled up as a 500 Internal Server Error instead of a user-friendly 400 Bad Request.

## Solution Implemented

### 1. Updated CRUD Function (`backend/app/crud/users.py`)

Added proper error handling for duplicate email/username:

```python
def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    from sqlalchemy.exc import IntegrityError
    
    # ... create user object ...
    
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        # Re-raise with more specific error message
        if "users_email_key" in str(e.orig):
            raise ValueError(f"A user with email '{user.email}' already exists")
        elif "users_username_key" in str(e.orig):
            raise ValueError(f"A user with username '{user.username}' already exists")
        else:
            raise ValueError(f"Failed to create user: {str(e)}")
```

### 2. Updated Router Endpoint (`backend/app/routers/users.py`)

Added try-catch to handle ValueError and return proper HTTP status:

```python
@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(...):
    organization = crud.organizations.get_organization(db, user.organization_id)
    _check_create_user_permissions(user, organization, current_user)
    
    try:
        db_user = crud.users.create_user(db=db, user=user)
        if not db_user:
            raise HTTPException(status_code=400, detail="Failed to create user")
        return db_user
    except ValueError as e:
        # Handle duplicate email/username errors with user-friendly message
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
```

## Result

Now when a user tries to create an account with an existing email:

**Before:**
- Status: 500 Internal Server Error
- Message: "Internal Server Error"

**After:**
- Status: 400 Bad Request
- Message: "A user with email 'h.akturk@ilknak.com' already exists"

## Testing

Try creating a user with an existing email:
1. Go to Users page
2. Click "Add User"
3. Enter email that already exists (e.g., h.akturk@ilknak.com)
4. Submit form
5. Should see clear error message: "A user with email 'h.akturk@ilknak.com' already exists"

## Deployment

Changes applied to production:
- Updated `backend/app/crud/users.py`
- Updated `backend/app/routers/users.py`
- Restarted API container: `docker compose -f docker-compose.prod.yml restart api`

## Status

✅ **FIXED** - User creation now shows clear error messages for duplicate emails/usernames
