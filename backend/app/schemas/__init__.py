# backend/app/schemas/__init__.py

from .organization import *
from .user import *
from .part import *
from .warehouse import *
from .inventory import *
from .supplier_order import *
from .customer_order import *
from .part_usage import *
from .machine import *
from .stock_adjustment import *
from .stocktake import *
from .transaction import *
from .predictive_maintenance import *
from .part_order import *
from .token import *
from .session import *
from .invitation import *
from .dashboard import *
from .inventory_workflow import *
from .maintenance_protocol import *

# Rebuild maintenance protocol schemas with forward references
from .maintenance_protocol import (
    ProtocolChecklistItemResponse,
    MaintenanceProtocolResponse,
    MaintenanceExecutionCreate,
    MaintenanceExecutionResponse,
    MaintenanceChecklistCompletionResponse,
    MaintenanceReminderResponse
)

# Rebuild models to resolve forward references
ProtocolChecklistItemResponse.model_rebuild()
MaintenanceProtocolResponse.model_rebuild()
MaintenanceExecutionCreate.model_rebuild()
MaintenanceExecutionResponse.model_rebuild()
MaintenanceChecklistCompletionResponse.model_rebuild()
MaintenanceReminderResponse.model_rebuild()