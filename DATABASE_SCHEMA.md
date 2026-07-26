# Database Schema

## channels

id

name

username

enabled

category

created_at

---

## posts

id

channel

hash

title

content

published

created_at

---

## queue

id

post_id

status

retry_count

last_try

---

## logs

id

level

message

created_at

---

## settings

key

value

---

## cache

key

value

expires
