# Bulk Loader Throttled Indexer

This function reads from an SQS Queue and indexes the messages into the **UserPortal** gateway.

Afterward, it will update the **ImportHistoryTable** DynamoDB Table, avoiding reprocessing the data.
