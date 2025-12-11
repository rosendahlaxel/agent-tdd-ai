from fastapi import FastAPI, HTTPException, Response, status
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


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


def reset_state() -> None:
    app.state.items: dict[int, Item] = {}
    app.state.next_id = 1


reset_state()


@app.post("/items", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate) -> Item:
    item_id = app.state.next_id
    app.state.next_id += 1
    stored = Item(id=item_id, name=item.name)
    app.state.items[item_id] = stored
    return stored


@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int) -> Item:
    if item_id not in app.state.items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return app.state.items[item_id]


@app.get("/items", response_model=list[Item])
async def list_items() -> list[Item]:
    return list(app.state.items.values())


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int) -> Response:
    if item_id not in app.state.items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    del app.state.items[item_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: ItemCreate) -> Item:
    if item_id not in app.state.items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    updated = Item(id=item_id, name=item.name)
    app.state.items[item_id] = updated
    return updated
