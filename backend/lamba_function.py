import json
import boto3
import uuid
from datetime import datetime, timezone  # timestamps

dynamodb = boto3.resource("dynamodb")
# Using the existing Notes table
table = dynamodb.Table("Notes")


def _response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        },
        "body": json.dumps(body),
    }


def _method(event):
    return (
        event.get("requestContext", {})
        .get("http", {})
        .get("method")
    ) or event.get("httpMethod", "")


def _get_user_id(event):
    # Get Cognito user id (sub) from JWT claims
    return (
        event.get("requestContext", {})
        .get("authorizer", {})
        .get("jwt", {})
        .get("claims", {})
        .get("sub")
    )


def lambda_handler(event, context):
    method = _method(event)

    # CORS preflight support
    if method == "OPTIONS":
        return _response(200, {"ok": True})

    qs = event.get("queryStringParameters") or {}

    user_id = _get_user_id(event)
    if not user_id:
        return _response(401, {"message": "Unauthorized"})

    # -------- GET --------
    # GET /notes            -> list my notes
    # GET /notes?id=NOTE_ID -> get one of my notes
    if method == "GET":
        note_id = qs.get("id")

        if note_id:
            resp = table.get_item(Key={"id": note_id})
            item = resp.get("Item")

            # Either doesn't exist OR not owned by this user
            if not item or item.get("owner") != user_id:
                return _response(404, {"message": "Not found"})

            return _response(200, item)

        # List only this user's notes
        # NOTE: "owner" is a reserved word, so we use #o as an alias
        resp = table.scan(
            FilterExpression="#o = :u",
            ExpressionAttributeNames={"#o": "owner"},
            ExpressionAttributeValues={":u": user_id},
        )

        return _response(200, {"items": resp.get("Items", [])})

    # -------- POST --------
    # POST /notes   body: {"text":"hello"}
    if method == "POST":
        raw_body = event.get("body") or "{}"
        body = raw_body if isinstance(raw_body, dict) else json.loads(raw_body)

        note_id = str(uuid.uuid4())

        # ISO 8601 timestamp in UTC, e.g. "2026-02-18T03:00:12Z"
        created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        item = {
            "id": note_id,
            "owner": user_id,
            "text": body.get("text", ""),
            "createdAt": created_at,
        }

        table.put_item(Item=item)
        return _response(200, item)

    # -------- PUT --------
    # PUT /notes?id=NOTE_ID   body: {"text":"updated"}
    if method == "PUT":
        note_id = qs.get("id")
        if not note_id:
            return _response(400, {"message": "Missing required query param: id"})

        raw_body = event.get("body") or "{}"
        body = raw_body if isinstance(raw_body, dict) else json.loads(raw_body)

        if "text" not in body:
            return _response(400, {"message": "Missing required field: text"})

        # Ensure the note exists and belongs to this user
        resp = table.get_item(Key={"id": note_id})
        item = resp.get("Item")

        if not item or item.get("owner") != user_id:
            return _response(404, {"message": "Not found"})

        # New updatedAt timestamp
        updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        table.update_item(
            Key={"id": note_id},
            UpdateExpression="SET #t = :text, #u = :updatedAt",
            ExpressionAttributeNames={
                "#t": "text",
                "#u": "updatedAt",
            },
            ExpressionAttributeValues={
                ":text": body["text"],
                ":updatedAt": updated_at,
            },
        )

        return _response(200, {"updated": True, "id": note_id})

    # -------- DELETE --------
    # DELETE /notes?id=NOTE_ID
    if method == "DELETE":
        note_id = qs.get("id")
        if not note_id:
            return _response(400, {"message": "Missing required query param: id"})

        # Ensure the note exists and belongs to this user
        resp = table.get_item(Key={"id": note_id})
        item = resp.get("Item")

        if not item or item.get("owner") != user_id:
            return _response(404, {"message": "Not found"})

        table.delete_item(Key={"id": note_id})

        return _response(200, {"deleted": True, "id": note_id})

    # Unsupported HTTP method
    return _response(400, {"message": f"Unsupported method: {method}"})