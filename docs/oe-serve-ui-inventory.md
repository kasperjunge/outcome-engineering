# oe serve UI inventory

Scope: `uv run oe serve examples/ui-evaluation-product-graph --host 127.0.0.1 --port 18878 --no-open`, tested with `playwright-cli` against the sanitized comprehensive graph fixture.

## Production-like local data

- Fixture: `examples/ui-evaluation-product-graph`
- Scale: 40 graph nodes, 42 edges
- Node kinds: `icp`, `outcome`, `opportunity`, `solution`, `assumption-test`, `prd`
- Edge kinds: 33 structural edges, 9 ICP reference edges
- Content coverage: vision, strategy, four ICPs, three outcomes, nested opportunities, solutions, PRDs, assumption tests, status variation, long markdown bodies, ICP references
- Role coverage: local graph operator with filesystem write access; there is no authentication, authorization, or remote team role in the local-only UI

## Routes and API

| Route | User-facing purpose | Acceptance criteria | Risk-based edge cases |
| --- | --- | --- | --- |
| `GET /` | Load graph editor | HTML loads, fetches `/api/graph`, renders overview, exposes header controls | Missing graph data, mobile viewport, browser favicon request |
| `GET /favicon.ico` | Browser chrome request | Returns empty success response without console 404 | Repeated first-load console noise |
| `GET /api/graph` | Load graph payload | Returns root, vision, strategy, schema, nodes, edges | Large graph, distinct structural/ICP edges, missing optional status |
| `POST /api/nodes` | Create a graph node | Creates legal node, returns id and validation issues | Missing fields, duplicate slug, illegal parent kind |
| `PUT /api/nodes/{id}` | Save marker edits | Persists marker content, reports validation issues without losing edit context | Invalid ICP reference, missing content, unknown id |
| `DELETE /api/nodes/{id}` | Delete node | Deletes leaf nodes; requires cascade confirmation for nodes with children | Unknown id, parent with children, cancelled confirmation |

## Controls and states

| Feature | Controls and inputs | Acceptance criteria | Risk-based edge cases |
| --- | --- | --- | --- |
| Overview graph | ICP nodes, outcome nodes, legend, Fit | Shows strategic nodes and ICP edges; Overview button is disabled while already in overview | Empty graph, hidden kind filters, fit after resize |
| Focus graph | Outcome click, breadcrumb, collapse toggles | Opens selected outcome subtree; toggles are attached to their nodes; breadcrumb returns to overview | Deep tree, collapsed branch, hidden child kind |
| Detail panel | Node click, ICP chips, markdown renderer | Shows kind, status, id, ICP references, actions, markdown body | Long markdown, code fences, missing ICP target |
| Vision/Strategy panels | Vision button, Strategy button | Shows root prose documents without changing graph mode | Missing document text |
| Create form | `+ Outcome`, `+ ICP`, `+ <child kind>`, title input, Create, Cancel | Slug preview updates; Create adds legal node and selects it | Empty title, duplicate title, illegal placement |
| Edit form | Edit, marker textarea, Save, Cancel | Valid save returns to read panel; invalid save displays issues and keeps Save enabled for correction | Validation-breaking edit, network/API error, repeated save |
| Delete flow | Delete, browser confirm | Leaf delete removes node; child delete prompts cascade; dismiss leaves graph unchanged | Cascade deletion, cancelled dialog |
| Layout | Desktop flex layout, mobile stacked layout | Desktop keeps side panel; narrow screens avoid horizontal overflow | 390px viewport, long header controls |

## Bug log

| ID | Status | Reproduction evidence | Cause | Fix |
| --- | --- | --- | --- | --- |
| UI-001 | Fixed | In focus mode on Team Alignment, `playwright-cli` returned seven `.toggle` elements all with `transform=\"translate(0,35)\"` | Toggle groups were appended at local coordinates instead of graph coordinates | Toggle transform now includes node `x` and `y`; rerun returned seven unique transforms |
| UI-002 | Fixed | After saving an invalid ICP reference, the detail panel showed validation issues and `Save` stayed disabled | Save button was disabled before request and never re-enabled when validation issues came back in a 200 response | Invalid saves now clear old issues, report new issues, and re-enable Save |
| UI-003 | Fixed | Initial browser load logged `Failed to load resource: ... /favicon.ico 404` | Server did not handle browser favicon request | `/favicon.ico` now returns `204 No Content`; latest console log has 0 errors and 0 warnings |
| UI-004 | Fixed | Starting `oe serve` on occupied ports printed a Python traceback | CLI did not catch bind failures | `serve` command catches `OSError` and prints `Could not bind host:port: ...` |
| UI-005 | Fixed | At 390px viewport, detail panel computed width was `400px` and body overflowed horizontally | Fixed side-panel width applied on mobile | Mobile media query stacks graph/detail and sets detail width to `100%`; rerun showed `bodyScrollWidth === innerWidth === 390` |

## Clean-pass evidence

- `uv run oe validate examples/ui-evaluation-product-graph`: `OK`
- `uv run pytest`: 38 passed
- Playwright overview load: 7 overview nodes, 7 overview edges
- Playwright focus rerun: Team Alignment rendered 18 nodes, 19 edges, 7 unique toggle transforms
- Playwright invalid edit rerun: validation issue displayed, Save remained enabled, valid correction returned to read panel
- Playwright responsive rerun: 390px viewport had no horizontal overflow and stacked layout
- Playwright console rerun: 0 errors, 0 warnings
