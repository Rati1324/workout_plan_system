import redis 
from fastapi import WebSocket
from ..main import get_workout_plans_db
r = redis.Redis(host='redis_service', port=6379, decode_responses=True)

# r.flushall()
@app.websocket("/workout_session")
async def websocket_endpoint(websocket: WebSocket, token: str):
    await websocket.accept()
    db = SessionLocal()
    user = None
    try:
        user = get_current_user(db, token=token)
    except HTTPException:
        await websocket.send_text("Invalid token")
        await websocket.close()
        return None

    await websocket.send_text("Connected successfully")
    user_workout_plans = get_workout_plans_db(db, user.id)

    def finish_set():
        cur_set = int(r.get("cur_set"))
        r.set("break", r.get("break_between_sets"))
        r.set("cur_set", cur_set + 1)
        r.set("status", "break_after_set")

    def finish_exercise(exercises):
        cur_exercise_index = int(r.get("cur_exercise_index")) + 1
        r.set("break", r.get("break_after_exercise"))
        r.set("cur_exercise_index", cur_exercise_index)
        r.set("cur_exercise_name", exercises[cur_exercise_index]["name"])
        r.set("cur_set", 1)
        r.set("total_sets", exercises[cur_exercise_index]["sets"])
        r.set("status", "break_after_exercise")

    while 1:
        request = await websocket.receive_text()

        json_request = json.loads(request)
        action = json_request["action"]

        if "plan_id" in json_request:
            cur_plan = [plan for plan in user_workout_plans if plan["id"] == json_request["plan_id"]][0]

        if action == "start_session":
            cur_exercise = cur_plan["exercises"][0]
            total_exercises = len(cur_plan["exercises"])

            r.set("total_exercises", total_exercises)
            r.set("cur_exercise_index", 0)
            r.set("cur_exercise_name", cur_exercise["name"])
            r.set("break_after_exercise", cur_exercise["break_after_exercise"])

            r.set("total_sets", cur_exercise["sets"])
            r.set("cur_set", 1)
            r.set("break_between_sets", cur_exercise["break_between_sets"])

            r.set("status", "started")

            cur_exercise = cur_plan["exercises"][int(r.get("cur_exercise_index"))]
            await websocket.send_text(json.dumps({"status": "session_started", "cur_exercise": cur_exercise}))

        elif action == "finish_set":
            cur_set = r.get("cur_set")
            total_sets = r.get("total_sets")

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
                await websocket.send_text(json.dumps({"status": "started"}))

            else:
                cur_exercise = cur_plan["exercises"][int(r.get("cur_exercise_index"))]
                cur_set = r.get("cur_set")
                await websocket.send_text(json.dumps({"status": "set_started", "cur_exercise": cur_exercise, "cur_set": cur_set}))


        if r.get("status") == "session_ended":
            break
        # await websocket.send_text(json.dumps(r.get("status")))
            


