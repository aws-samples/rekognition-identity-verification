# Inventory Created Handler

The **image Bucket** will periodically run an S3 Inventory Report.  When that report writes into the **inventory bucket**, this operations triggers the Inventory Created Handler function.

Next, the function does a light-weight filter while initializing an Amazon S3 Batch Job.  The Batch job performs a fan-out behavior to assess which files qualify for indexing.