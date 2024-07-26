# Exquisite Exoplanets - API

## Setting up the database

In the `.env` file, add the following: `DATABASE="sqlite:///<db_name>.sqlite"`

## Tech Stack

- Python
- FastAPI
- SQLModel
- python-multipart (for files)

## Endpoints

## User
---

### Create a User

Overview:
Allows for a User to create an account in the game. Account is linked to their Discord ID.

Method:

```
POST /user/{id}     # `id` being the user's Discord ID
```

Responses:

```
// Account details
{
  "id": "212643981593411582"
}
```

| Code | Reason                        |
|------|-------------------------------|
| 200  | Account created successfully. |
| 409  | Account already exists.       |

### Get a User

Overview:
Get the details of a User's account with the user's Discord ID.

Method:

```
GET /user/{id}      # `id` being the user's Discord ID
```

Responses:

```
{
  "user_id": "212643981593411584",
  "experience": {
    "level": 16,
    "experience": 3214
  }
}
```

| Code | Reason                        |
|------|-------------------------------|
| 200  | Account fetched successfully. |
| 404  | Account cannot be found.      |

### Add User Experience

Overview:
Add experience to the User's account.

Method:

```
PATCH /user/{id}/experience/add     # `id` being the user's Discord ID
```

Body:

```
{
    "experience": 300
}
```

Responses:

```
{
  "level_up": true,
  "new_level": 17,
  "new_experience": 3514
}
```

| Code | Reason                         |
|------|--------------------------------|
| 200  | Experience successfully added. |
| 404  | Account cannot be found.       |

### Set User Experience

Overview:
Set the experience of a User.

Method:

```
POST /user/{id}/experience/set     # `id` being the user's Discord ID
```

Body:

```
{
    "experience": 300
}
```

Responses:

```
{
  "level_up": true,
  "new_level": 17,
  "new_experience": 3514
}
```

| Code | Reason                         |
|------|--------------------------------|
| 200  | Experience successfully added. |
| 404  | Account cannot be found.       |

## Company
---

### Create a Company

Overview:
Create a new Company linked to the User. A User can only ever have **one** active company at a time. A Company is
deemed `active` if this is not bankrupt.

A company cannot have the same name as another one, even if it is bankrupt.

Method:

```
POST /company
```

Body:

```
{
    "name": "TheDogShop"
    "owner_id": "111111111111111111"    # # `id` being the user's Discord ID
}
```

Responses:

```
{
  "id": 1,
  "created": "2024-07-26T18:17:03.539Z",
  "name": "TheDogShop",
  "owner_id": "111111111111111111",
  "networth": 0,
  "is_bankrupt": false
}
```

| Code | Reason                        |
|------|-------------------------------|
| 201  | Company created successfully. |
| 409  | Company already exists.       |

### Get a Company

Overview:
Get the details of the current active company bound to a User.

Method:

```
GET /company/{id}       # `id` being the user's Discord ID
```

Responses:

```
{
  "id": 1,
  "created": "2024-07-26T18:17:03.539Z",
  "name": "TheDogShop",
  "owner_id": "111111111111111111",
  "networth": 0,
  "is_bankrupt": false
}
```

| Code | Reason                        |
|------|-------------------------------|
| 200  | Company fetched successfully. |
| 404  | Company not found.            |

### Get Companies

Overview:
Get all the companies that have been registered.

Method:

```
GET /companies
```

Parameters:

| Name      | Type | Detail                                         | Optional | Default |
|-----------|------|------------------------------------------------|----------|---------|
| page      | int  | Get the page.                                  | YES      | 1       |
| limit     | int  | Get the limit (amount of companies on a page). | YES      | 10      |
| ascending | bool | Sort the fetched companies.                    | YES      | false   |

Responses:

```
{
  "page": 1,
  "limit": 10,
  "page_count": 1,
  "entry_count": 3,
  "companies": [
    {
      "name": "theDogShop",
      "owner_id": "111111111111111111",
      "networth": 0,
      "is_bankrupt": true
    },
    {
      "name": "theDogShopSupreme",
      "owner_id": "111111111111111111",
      "networth": 0,
      "is_bankrupt": false
    }
  ]
}
```

| Code | Reason                          |
|------|---------------------------------|
| 200  | Companies fetched successfully. |
| 404  | Companies cannot be found.      |

### Update a Company

Overview:
Update the details of a Company.

Method:

```
PATCH /company/{id}     # `id` being the user's Discord ID
```

Body:

```
{
    "name": "New name here"
}
```

Responses:

| Code | Reason                        |
|------|-------------------------------|
| 200  | Company updated successfully. |
| 404  | Company cannot be found.      |
| 500  | Company cannot be updated.    |

### Delete a Company

Overview:
Delete a company. Marks it as `bankrupt`.

Method:

```
DELETE /company/{id}     # `id` being the user's Discord ID
```

Responses:

| Code | Reason                        |
|------|-------------------------------|
| 200  | Company deleted successfully. |
| 404  | Company cannot be found.      |
| 500  | Company cannot be deleted.    |

### Get Company's Inventory

Overview:
Get all the Items the Company has bought from the Shop.

Method:

```
GET /company/{id}/inventory     # `id` being the user's Discord ID
```

Responses:

```
{
  "company_id": 3,
  "inventory": [
    {
      "item": {
        "item_id": 1,
        "name": "A pot"
      },
      "company_id": 3,
      "stock": 1,
      "total_amount_spent": 1
    }
  ]
}
```

| Code | Reason                                  |
|------|-----------------------------------------|
| 200  | Company inventory fetched successfully. |
| 404  | Company/Inventory cannot be found.      |

### Get Company's Achievements

Overview:
Get all the Achievements a Company has achieved.

Method:

```
GET /company/{id}/achievements     # `id` being the user's Discord ID
```

Responses:

```
{
  "first_achievement": "Reach Leaderbaord",
  "latest_achievement": "Reach Leaderboard",
  "achievements": [
    {
        "id": 1,
        "name": "Reach Leaderboard",
        "description": "Place on the leaderboard."
    }
  ]
}
```

| Code | Reason                                  |
|------|-----------------------------------------|
| 200  | Company inventory fetched successfully. |
| 404  | Company/Achievements cannot be found.   |

## Shop
---

### Get Shop

Overview:
Get the Items that are currently available in the Shop.

Method:

```
GET /shop
```

| Name        | Type | Detail                                             | Optional | Default |
|-------------|------|----------------------------------------------------|----------|---------|
| page        | int  | Get the page.                                      | YES      | 1       |
| limit       | int  | Get the limit (amount of companies on a page).     | YES      | 10      |
| ascending   | bool | Sort the fetched companies.                        | YES      | false   |
| sort_by     | str  | Sort by the following. `price`, `quantity`, `name` | YES      | `price` |
| is_disabled | bool | Filter by disabled state.                          | YES      | NONE    |

Responses:

```
{
  "page": 1,
  "limit": 10,
  "page_count": 1,
  "entry_count": 2,
  "shop_items": [
    {
      "id": 2,
      "name": "A kettle",
      "price": 10,
      "available_quantity": 100,
      "is_disabled": false
    },
    {
      "id": 1,
      "name": "A pot",
      "price": 1,
      "available_quantity": 99,
      "is_disabled": false
    }
  ]
}
```

| Code | Reason                      |
|------|-----------------------------|
| 200  | Shop fetched successfully.  |
| 404  | Shop Items cannot be found. |

### Get Details on Shop Item

Overview:
Get the details on a certain Item in the Shop.

Method:

```
GET /shop/{id}
```

Responses:

```
{
  "id": 1,
  "name": "A pot",
  "price": 1,
  "available_quantity": 99,
  "is_disabled": false
}
```

| Code | Reason                          |
|------|---------------------------------|
| 200  | Shop Item fetched successfully. |
| 404  | Shop Item cannot be found.      |

### Create Shop Item

Overview:
Create a new Item to be added to the Shop.

Method:

```
POST /shop
```

Body:

```
{
  "name": "A kettle",
  "price": 10,      # price > 0
  "available_quantity": 100`    # quantity > 0
}
```

Responses:

| Code | Reason                          |
|------|---------------------------------|
| 200  | Shop Item created successfully. |
| 400  | Cannot create Shop Item.        |
| 409  | Shop Item already exists.       |

### Update Shop Item

Overview:
Update the details of a Shop Item.

Method:

```
PATCH /shop/{id}
```

Body:

```
{
  "item_id": 1,
  "name": "A guitar.",
  "quantity": 10,       # quantity >= 1
  "price": 10,          # price > 0
  "is_disabled": false
}
```

Responses:

| Code | Reason                          |
|------|---------------------------------|
| 200  | Shop Item updated successfully. |
| 404  | Shop Item cannot be found.      |
| 500  | Unable to update Shop Item.     |

### Purchase Shop Item

Overview:
Allows a Company to purchase the target Item. Purchased item is added to their inventory. If the Item is out of stock,
then it is hidden from the shop.
A Company cannot purchase more than the item quantity. The Company also has to have the required funds to buy the Item.

Method:

```
POST /shop/{id}
```

Body:

```
{
  "company_id": "111111111111111111",
  "item_id": 1,
  "purchase_quantity": 5
}
```

Responses:

| Code | Reason                                                                                     |
|------|--------------------------------------------------------------------------------------------|
| 200  | Shop fetched successfully.                                                                 |
| 400  | Unable to purchase Item. Cannot purchase more than what is available.. Insufficient funds. |
| 403  | Company bankrupt; cannot purchase. No available items to purchase.                         |
| 404  | Shop Items cannot be found.                                                                |

## Achievements
---

### Get Achievement

Overview:
Get the details on the given Achievement.

Method:

```
GET /achievement/{id}
```

Responses:

Eg: 1

```
{
  "id": 1,
  "name": "Reach level 5.",
  "description": "Achievement earned when reaching Level 5.",
  "companies_earned": 1,
  "first_achieved": {
        "name": "theDogShop",
        "owner_id": "111111111111111111",
        "date": "2024-07-26 20:20:52.983463"
    },      # OR none
  "latest_achieved": {
        "name": "theDogShop",
        "owner_id": "111111111111111111",
        "date": "2024-07-26 20:20:52.983463"
    }       # OR none
}
```

Eg 2:

```
{
  "id": 1,
  "name": "Reach level 5.",
  "description": "Achievement earned when reaching Level 5.",
  "companies_earned": 0,
  "first_achieved": null,
  "latest_achieved": null
}
```

| Code | Reason                            |
|------|-----------------------------------|
| 200  | Achievement fetched successfully. |
| 404  | Achievement not found.            |

### Get Achievements

Overview:
Get all the Achievements available to collect.

Method:

```
GET /achievements
```

Responses:

```
{
  "achievements": [
    {
      "id": 1,
      "name": "Reach level 5.",
      "description": "Achievement earned when reaching Level 5.",
      "companies_earned": 0,
      "first_achieved": null,
      "latest_achieved": null
    },
    {
      "id": 2,
      "name": "Reach level 10.",
      "description": "Achievement earned when reaching Level 10.",
      "companies_earned": 0,
      "first_achieved": null,
      "latest_achieved": null
    }
  ]
}
```

| Code | Reason                             |
|------|------------------------------------|
| 200  | Achievements fetched successfully. |
| 404  | Achievements not found.            |
