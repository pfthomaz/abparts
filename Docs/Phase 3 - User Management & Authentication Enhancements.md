# Phase 3: User Management & Authentication Enhancements 👤🔐

This phase establishes the foundation for secure, role-based access and user self-service. Completing these tasks first will minimize future refactoring and enable safe rollout of all other features.

---

## Task List

### User CRUD & Self-Service

- ✅ **Implement user creation, editing, and deletion in the backend**
  - Endpoints exist for admin user management (create, update, deactivate, delete)
  - Basic validation and error handling for user data (email, password, roles) are present

- ⬜️ **Build frontend UI for Oraseas Admins to manage users**
  - User list view with search/filter
  - User creation/editing form
  - Deactivate/reactivate user actions

- ⬜️ **Add user profile page for self-service**
  - View/update own info (name, email, etc.)
  - Change password form (with validation and feedback)

### Role Assignment & Editing

- ⬜️ **Ensure role assignment and editing is available in both backend and frontend**
  - Backend: endpoints for assigning/removing roles
  - Frontend: UI for admins to set user roles

### Password Reset Flow

- ⬜️ **Implement password reset (forgot password) flow**
  - Backend: endpoint to request password reset (email with token)
  - Backend: endpoint to set new password with valid token
  - Frontend: "Forgot password?" link, reset request form, and new password form

### JWT/Session Expiration & Refresh

- ⬜️ **Ensure JWT/session expiration and refresh logic is robust**
  - Backend: implement token expiration and refresh endpoints if not present
  - Frontend: handle token expiration gracefully (auto-logout, refresh, or prompt user)

### (Optional) User Invitation/Onboarding

- ⬜️ **Implement user invitation and onboarding flow**
  - Backend: endpoint to send invitation email with registration link
  - Frontend: UI for admins to invite users, and for invitees to complete registration

---

## Next Enhancements (Post-MVP)

- 🔒 **Comprehensive validation:** Enforce stricter business rules (e.g., email format, username constraints, role restrictions) in schemas and endpoints.
- 📝 **Audit logging:** Add audit trail for all user CRUD actions.
- 💤 **Soft delete:** Implement user deactivation/reactivation instead of hard delete, if required.
- 🧪 **Automated tests:** Add and expand unit/integration tests for all user management endpoints.
- 📧 **Email integration:** Ensure robust email delivery for password reset and invitations.
- 🛡️ **Granular permissions:** Align user management with future fine-grained permission model.

---

## Dependencies & Notes

- Some tasks (e.g., password reset, invitation) require email sending capability—ensure SMTP or email service is configured.
- Role management should align with the planned permission model (see future phases).
- All new endpoints should have tests and be documented for frontend integration.

---

**Once these tasks are complete, the system will have a robust, secure, and user-friendly foundation for