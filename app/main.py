from typing import Literal

from fastapi import FastAPI, HTTPException, Query, Response, status
from pydantic import BaseModel, field_validator
from pydantic_core import PydanticCustomError

app = FastAPI()


class ItemCreate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def name_min_length(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 3:
            raise PydanticCustomError("name_too_short", "Name must be at least 3 characters long")
        return value


class Item(ItemCreate):
    id: int


class Event(BaseModel):
    id: int
    type: Literal["reset", "item_created", "item_updated", "item_deleted"]
    item_id: int | None = None
    name: str | None = None


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


def reset_items(*, keep_events: bool) -> None:
    app.state.items: dict[int, Item] = {}
    app.state.next_id = 1
    if not keep_events:
        app.state.events = []
        app.state.next_event_id = 1


def reset_state() -> None:
    reset_items(keep_events=False)


reset_state()


def _append_event(
    *,
    type_: Literal["reset", "item_created", "item_updated", "item_deleted"],
    item_id: int | None = None,
    name: str | None = None,
) -> int:
    event_id = app.state.next_event_id
    app.state.next_event_id += 1
    app.state.events.append(Event(id=event_id, type=type_, item_id=item_id, name=name))
    return event_id


def _items_at_event(at_event_id: int | None) -> dict[int, Item]:
    if at_event_id is None:
        return app.state.items

    items: dict[int, Item] = {}
    for event in app.state.events:
        if event.id > at_event_id:
            break

        match event.type:
            case "reset":
                items = {}
            case "item_created" | "item_updated":
                if event.item_id is not None and event.name is not None:
                    items[event.item_id] = Item(id=event.item_id, name=event.name)
            case "item_deleted":
                if event.item_id is not None:
                    items.pop(event.item_id, None)

    return items


@app.get("/events", response_model=list[Event])
async def list_events(
    since: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=1, le=1000),
) -> list[Event]:
    events = app.state.events
    if since is not None:
        events = [e for e in events if e.id > since]
    if limit is not None:
        events = events[:limit]
    return events


@app.get("/items/{item_id}/history", response_model=list[Event])
async def item_history(
    item_id: int,
    include_resets: bool = True,
    limit: int | None = Query(default=None, ge=1, le=1000),
) -> list[Event]:
    events = [
        e
        for e in app.state.events
        if (e.item_id == item_id) or (include_resets and e.type == "reset")
    ]
    if limit is not None:
        events = events[-limit:]
    return events


@app.post("/items", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate) -> Item:
    if any(stored.name == item.name for stored in app.state.items.values()):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Name already exists")

    item_id = app.state.next_id
    app.state.next_id += 1
    stored = Item(id=item_id, name=item.name)
    app.state.items[item_id] = stored
    _append_event(type_="item_created", item_id=item_id, name=stored.name)
    return stored


@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int, at: int | None = Query(default=None, ge=0)) -> Item:
    items = _items_at_event(at)
    if item_id not in items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return items[item_id]


@app.get("/items", response_model=list[Item])
async def list_items(at: int | None = Query(default=None, ge=0)) -> list[Item]:
    items = _items_at_event(at)
    return list(items.values())


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int) -> Response:
    if item_id in app.state.items:
        del app.state.items[item_id]
        _append_event(type_="item_deleted", item_id=item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: ItemCreate, response: Response) -> Item:
    for existing_id, stored in app.state.items.items():
        if existing_id != item_id and stored.name == item.name:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Name already exists")

    response.status_code = status.HTTP_200_OK
    if item_id not in app.state.items:
        response.status_code = status.HTTP_201_CREATED
        app.state.next_id = max(app.state.next_id, item_id + 1)

    updated = Item(id=item_id, name=item.name)
    app.state.items[item_id] = updated
    _append_event(type_="item_updated", item_id=item_id, name=updated.name)
    return updated


@app.post("/reset", status_code=status.HTTP_204_NO_CONTENT)
async def reset() -> Response:
    reset_items(keep_events=True)
    _append_event(type_="reset")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
