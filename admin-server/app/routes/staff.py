from app.controllers import staff

from . import api_bp


@api_bp.get("/assistants")
def list_assistants():
    return staff.list_staff("assistant")


@api_bp.post("/assistants")
def create_assistant():
    return staff.create_staff("assistant")


@api_bp.get("/assistants/<int:item_id>")
def get_assistant(item_id: int):
    return staff.get_staff("assistant", item_id)


@api_bp.put("/assistants/<int:item_id>")
def update_assistant(item_id: int):
    return staff.update_staff("assistant", item_id)


@api_bp.delete("/assistants/<int:item_id>")
def delete_assistant(item_id: int):
    return staff.delete_staff("assistant", item_id)


@api_bp.get("/customer-services")
def list_customer_services():
    return staff.list_staff("customer_service")


@api_bp.post("/customer-services")
def create_customer_service():
    return staff.create_staff("customer_service")


@api_bp.get("/customer-services/<int:item_id>")
def get_customer_service(item_id: int):
    return staff.get_staff("customer_service", item_id)


@api_bp.put("/customer-services/<int:item_id>")
def update_customer_service(item_id: int):
    return staff.update_staff("customer_service", item_id)


@api_bp.delete("/customer-services/<int:item_id>")
def delete_customer_service(item_id: int):
    return staff.delete_staff("customer_service", item_id)
