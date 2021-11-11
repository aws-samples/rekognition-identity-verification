# RIV Infrastructure

The folder contains all [AWS Cloud Development Kit](https://docs.aws.amazon.com/cdk/latest/guide/work-with-cdk-python.html) automation for provisioning a [RIV stack](toplogogies.py).  A RIV stack is a self-contained service installation, complete with every required subsystem.

Within each subfolder is a `topology.py` file that defines any exportable symbols.  Typically, consumers should **import** these root constructs (e.g., [RivUserPortal](userportal/topology.py)) versus directly **import** private implementation details (e.g., [RivUserPortalCompareFaces](userportal/functions/definitions.py)).  This approach reduces the risk of future breaking changes.

## What are the root-level subsystems

- [bulkloader](bulkloader).  The RIV bulk importing service. 
- [services](services). Standard AWS supporting components (e.g., backup)
- [storage](storage). Defines all shared data stores.
- [userportal](userportal).  The public interface that endusers interact with
