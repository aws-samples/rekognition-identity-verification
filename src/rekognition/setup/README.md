# Setup Rekognition Utility

This utility configures any Amazon Rekognition objects required for your environment.

## How do I run this app

The script requires three enviroment variables.  A later update should convert this to the click framework.

```sh
export RIV_STACK_NAME=Prod
export REGION=ca-central-1
export TOTAL_COLLECTIONS=2
./app.py
```

## How do I determine TOTAL_COLLECTIONS

The **TOTAL_COLLECTIONS** value defines the number of _AWS Rekognition Collections_ that the system will leverage.  AWS Customers __cannot change this value later, without significant effort__.  The RIV team strongly encourages over allocation, since there are **no cost** associated with having too many collections.

Typically, customers should follow the formula `ceil( count(max_users) / 10M ) +1` total partitions.  For instance, 27M maximum users requires 4 partitions.

## What challenges exist with multiple partitions

Users within the RIV system provide the tuple `(userid, password)`; where **password** is a `utf8(base64(image))` bytearray of themselves.

The registration system will persist the user metadata within the `partition_id = hash(userid) % TOTAL_COLLECTIONS`.  This design means that a specific photo (password) is unique within its **associated partition, not globally unique**.  For instance, a customer might be able to register themselves as `(fred1234, flintstone.png)` and `(barney4567, flintstone.png)`.

Customers can avoid this behavior by setting `TOTAL_COLLECTIONS=1`, which limits the **max_users** to about 20M total.  For many scenarios this is completely acceptable.  However, nation-wide brands will find this prohibitively restrictive.

Instead, the RIV team recommends adding controls around the `user_id` selection.  This situation could include scanning a drivers license and setting the `user_id` equal to their `state id` or `government id`.
