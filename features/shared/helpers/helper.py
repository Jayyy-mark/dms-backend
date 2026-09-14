
from rest_framework.response import Response
from rest_framework import status
from features.logs.models import AuditLog

def removeNoneValue(data : dict)->dict:
    return {
        k:v for k,v in data.items() if v is not None
    }

def toApiResponse(data=None, message="")->Response:
    return Response({
        "data" : data,
        "message" : message
    },status=status.HTTP_201_CREATED)

def generateId(model,field, prefix)->str:
    last_id = model.objects.order_by(f"-{field}").values_list(field, flat=True).first()
    if last_id:
        number = int(last_id.split("-")[1]) + 1
        return f"{prefix}-{number:03d}"
    else:
        number = 1
    return f"{prefix}-{number:03d}"

def log_action(user, action, model_name, object_id=None, description=""):
    AuditLog.objects.create(
        user=user,
        action=action,
        model_name=model_name,
        object_id=object_id,
        description=description
    )