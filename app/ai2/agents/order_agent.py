@tool
async def track_order(
    user_id:int,
    order_id:int
):

    order=await demo_order_service.get_order(
        user_id=user_id,
        order_id=order_id
    )

    if not order:

        return {
            "success":False,
            "message":"Order not found"
        }

    return {
        "success":True,
        "product":order["product"],
        "status":order["status"],
        "tracking":order["tracking"],
        "delivery":order["delivery_date"],
        "courier":order["courier"]
    }