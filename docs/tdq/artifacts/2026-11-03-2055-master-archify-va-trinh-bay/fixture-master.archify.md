# Master local fixture {#master-fixture}

@meta locale=en

Local fixture with one overview and one flow card. No external data.

## Overview {#overview-panel}

@diagram architecture id=overview source=fixture-overview.json title="Overview"

## Flow detail {#flow-panel}

@diagram workflow id=flow source=fixture-flow.json title="Flow"

@steps id=flow-card
| open-flow | Read flow | Opens detail diagram. | flow | read |
