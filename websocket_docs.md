# WebSocket Endpoint: `/workout_session`

This WebSocket endpoint allows real-time communication for workout sessions.

## Request Parameters:

- `token`: Authentication token of the user.
- `plan_id`: ID of the workout plan in the databse.

## Actions:

The client can send a JSON message with an `action` field to perform various actions:

- `start_session`: Starts a workout session.
  - The server will respond with a JSON message containing:
    - `status`: The status of the request. This will be `session_started` if the request was successful.
    - `exercise`: Information about the current exercise.
    - `breaks`: Information about the breaks between sets and after the exercise is over.

- `finish_set`: Marks the current set as finished.
    - The server will respond with a JSON message containing:
    - `status`: The status of the request. This will be `break_after_set`, `break_after_exercise` or `session_ended`, depending on whether there are more sets/exercises left.

- `modify_sets`: Modifies the total number of sets for the current exercise.
    - `value`: The new number of sets. This should be included in the JSON message sent by the client.
  - The server will respond with a JSON message containing:
    - `status`: The status of the request. This will be `sets_modified` if the request was successful.
    - `sets`: The new total number of sets.

- `modify_break`: Modifies the break duration between sets or exercises.
    - `value`: The new break duration. This should be included in the JSON message sent by the client.
    - `type`: The type of break. This can be either `set` or `exercise` and should be included in the JSON message sent by the client.
    
- The server will respond with a JSON message containing:
    - `status`: The status of the request. This will be `[set/exercise]_break_modified` if the request was successful.
    - `break`: The new break duration.

## Error Handling:

If an error occurs (e.g., invalid token, invalid plan ID, invalid action, etc.), the server will close the WebSocket connection and send a JSON message with the status `Invalid request`.

## Session End:

When the workout session ends, the server will send a JSON message with the status `session_ended` and close the WebSocket connection.