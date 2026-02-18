"""
Standalone report generation router that bypasses all middleware.
This router is mounted separately to avoid authentication middleware issues.
"""

import uuid
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app import models
from app.auth import SECRET_KEY, ALGORITHM, TokenData
from app.database import SessionLocal
from app.permissions import permission_checker

router = APIRouter()


@router.get("/maintenance-executions/{execution_id}/docx")
async def download_execution_report_docx(
    execution_id: uuid.UUID,
    request: Request
):
    """Generate and download a DOCX report for a maintenance execution with AI insights."""
    from app.services.maintenance_report_service import MaintenanceReportService
    
    # Create our own database session
    db = SessionLocal()
    
    try:
        # Extract and validate token
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing authorization header")
        
        token = auth_header.split(" ")[1]
        
        # Try to get session data from Redis (this is a session token, not JWT)
        from app.session_manager import session_manager
        try:
            session_data = session_manager.get_session(token)
            if not session_data:
                raise HTTPException(status_code=401, detail="Invalid or expired session")
            
            current_user = TokenData(
                username=session_data.get("username"),
                user_id=uuid.UUID(session_data.get("user_id")),
                organization_id=uuid.UUID(session_data.get("organization_id")),
                role=session_data.get("role")
            )
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")
        
        # Verify execution exists
        execution = db.query(models.MaintenanceExecution).filter(
            models.MaintenanceExecution.id == execution_id
        ).first()
        
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        # Verify user has access
        machine = db.query(models.Machine).filter(
            models.Machine.id == execution.machine_id
        ).first()
        
        if not machine:
            raise HTTPException(status_code=404, detail="Machine not found")
        
        # Check organization access
        if not permission_checker.is_super_admin(current_user):
            if machine.customer_organization_id != current_user.organization_id:
                raise HTTPException(status_code=403, detail="Access denied")
        
        # Generate report
        report_service = MaintenanceReportService(db)
        buffer = await report_service.generate_docx_report(str(execution_id))
        
        # Generate filename
        protocol_name = execution.protocol.name if execution.protocol else "Custom_Maintenance"
        protocol_name = protocol_name.replace(" ", "_")
        machine_name = machine.name.replace(" ", "_")
        date_str = execution.performed_date.strftime("%Y%m%d") if execution.performed_date else "undated"
        filename = f"Maintenance_Report_{protocol_name}_{machine_name}_{date_str}.docx"
        
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")
    finally:
        db.close()


@router.get("/maintenance-executions/{execution_id}/pdf")
async def download_execution_report_pdf(
    execution_id: uuid.UUID,
    request: Request
):
    """Generate and download a PDF report for a maintenance execution with AI insights."""
    from app.services.maintenance_report_service import MaintenanceReportService
    from app.session_manager import session_manager
    
    # Create our own database session
    db = SessionLocal()
    
    try:
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing authorization header")
        
        token = auth_header.split(" ")[1]
        
        # Debug logging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"PDF Report - Token received: {token[:20]}...")
        logger.info(f"PDF Report - Token length: {len(token)}")
        
        # Try to get session data from Redis (this is a session token, not JWT)
        try:
            session_data = session_manager.get_session(token)
            logger.info(f"PDF Report - Session data: {session_data is not None}")
            if not session_data:
                raise HTTPException(status_code=401, detail="Invalid or expired session")
            
            current_user = TokenData(
                username=session_data.get("username"),
                user_id=uuid.UUID(session_data.get("user_id")),
                organization_id=uuid.UUID(session_data.get("organization_id")),
                role=session_data.get("role")
            )
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")
        
        # Verify execution exists
        execution = db.query(models.MaintenanceExecution).filter(
            models.MaintenanceExecution.id == execution_id
        ).first()
        
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        # Verify user has access
        machine = db.query(models.Machine).filter(
            models.Machine.id == execution.machine_id
        ).first()
        
        if not machine:
            raise HTTPException(status_code=404, detail="Machine not found")
        
        # Check organization access
        if not permission_checker.is_super_admin(current_user):
            if machine.customer_organization_id != current_user.organization_id:
                raise HTTPException(status_code=403, detail="Access denied")
        
        # Generate report
        report_service = MaintenanceReportService(db)
        buffer = await report_service.generate_pdf_report(str(execution_id))
        
        # Generate filename
        protocol_name = execution.protocol.name if execution.protocol else "Custom_Maintenance"
        protocol_name = protocol_name.replace(" ", "_")
        machine_name = machine.name.replace(" ", "_")
        date_str = execution.performed_date.strftime("%Y%m%d") if execution.performed_date else "undated"
        filename = f"Maintenance_Report_{protocol_name}_{machine_name}_{date_str}.pdf"
        
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error(f"PDF Report generation failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")
    finally:
        db.close()
