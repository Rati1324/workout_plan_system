import redis, json, asyncio
from .services import get_workout_plans_db
from fastapi import APIRouter, HTTPException, WebSocket
from .config import SessionLocal
from .utils import get_current_user

r = redis.Redis(host='redis_service', port=6379, decode_responses=True)

router = APIRouter()

def finish_set():
    cur_set = int(r.get("cur_set"))
    r.set("break", r.get("break_between_sets"))
    r.set("cur_set", cur_set + 1)
    r.set("status", "break_after_set")

def finish_exercise(exercises):
    cur_exercise_index = int(r.get("cur_exercise_index")) + 1
    r.set("break", r.get("break_between_exercise"))
    r.set("cur_exercise_index", cur_exercise_index)
    r.set("cur_exercise_name", exercises[cur_exercise_index]["name"])
    r.set("cur_set", 1)
    r.set("total_sets", exercises[cur_exercise_index]["sets"])
    r.set("status", "break_between_exercise")

# r.flushall()
@router.websocket("/workout_session")
async def websocket_endpoint(websocket: WebSocket, token: str, plan_id):
    await websocket.accept()
    db = SessionLocal()
    user = None
    try:
        user = get_current_user(db, token=token)
        plan_id = int(plan_id)
        cur_plan = await get_workout_plans_db(db, user.id, name=None, plan_id=plan_id)
        cur_plan = cur_plan[0]
    except HTTPException:
        await websocket.send_text("Invalid request")
        await websocket.close()

    await websocket.send_text("Connected successfully")
    while 1:
        request = await websocket.receive_text()

        json_request = json.loads(request)
        action = json_request["action"]

        if action == "start_session":
            cur_exercise = cur_plan["exercises"][0]
            total_exercises = len(cur_plan["exercises"])

            r.set("total_exercises", total_exercises)
            r.set("cur_exercise_index", 0)
            r.set("cur_exercise_name", cur_exercise["name"])
            r.set("break_between_exercise", cur_exercise["break_after_exercise"])

            r.set("total_sets", int(cur_exercise["sets"]))
            r.set("cur_set", 1)
            r.set("break_between_sets", cur_exercise["break_between_sets"])

            r.set("status", "started")

            cur_exercise = cur_plan["exercises"][int(r.get("cur_exercise_index"))]
            await websocket.send_text(json.dumps({"status": "session_started", "cur_exercise": cur_exercise}))

        elif action == "finish_set":
            cur_set = int(r.get("cur_set"))
            total_sets = int(r.get("total_sets"))

            cur_exercise_index = int(r.get("cur_exercise_index"))
            total_exercises = int(r.get("total_exercises"))
            if cur_set == total_sets:
                if (cur_exercise_index + 1) == total_exercises:
                    await websocket.send_text(json.dumps({"status": "session_ended"}))
                    await websocket.close(code=1000, reason="session_ended")
                else:
                    finish_exercise(cur_plan["exercises"])
            else:
                finish_set()

            status = r.get("status")
            await websocket.send_text(json.dumps({"status": status}))

            await asyncio.sleep(int(r.get("break")))

            if r.get("status") == "break_after_set":
                await websocket.send_text(json.dumps({"status": "started", "sets_left": total_sets - cur_set}))
            else:
                cur_exercise = cur_plan["exercises"][int(r.get("cur_exercise_index"))]
                cur_set = r.get("cur_set")
                await websocket.send_text(json.dumps({"status": "set_started", "cur_exercise": cur_exercise, "cur_set": cur_set}))

        elif action == "modify_sets":
            cur_set = int(r.get("cur_set"))
            try:
                new_total_sets = int(json_request["value"])
                if new_total_sets < 0 or new_total_sets < cur_set:
                    raise ValueError
            except ValueError:
                await websocket.send_text(json.dumps({"status": "Invalid value for total sets"}))
                continue

            r.set("status", "modify_set")
            r.set("total_sets", new_total_sets)
            await websocket.send_text(json.dumps({"status": "sets_modified", "total_sets": new_total_sets}))

        elif action == "modify_break":
            try:
                new_break = int(json_request["value"])
                if new_break < 0:
                    raise ValueError

            except ValueError:
                await websocket.send_text(json.dumps({"status": "Invalid value for break between sets"}))
                continue

            break_type = json_request["type"]

            r.set(f"break_between_{break_type}", new_break)
            status = f"{break_type}_break_modified"
            await websocket.send_text(json.dumps({"status": status, "new_duration": new_break}))
        
        if r.get("status") == "session_ended":
            break

