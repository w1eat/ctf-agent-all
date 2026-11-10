# Challenge submission workflows

Submission workflows belong to one platform origin and one native challenge ID.
The coordinator inspects the challenge's actual page, saves its observed workflow,
and starts its solver only after that workflow exists. An old platform-wide recipe
does not authorize submission to another challenge. Existing recipes need to be
re-created for each challenge; no automatic migration assumes that the forms match.

Use `save_recipe` with `kind: flag` for a flag field and `{flag}` as its value.
For code, reports, or uploads use `kind: artifact` and named placeholders. Each
selector and action must be observed on the actual page. For example, a code form
with a separate dependency tab may have steps like:

```json
{
  "platform_origin": "https://example.test",
  "challenge_id": "example-code",
  "kind": "artifact",
  "steps": [
    {"action": "navigate", "value": "https://example.test/challenges/{challenge_id}"},
    {"action": "type", "target": "#code", "value": "{code}"},
    {"action": "click", "target": "#requirements-tab"},
    {"action": "type", "target": "#requirements", "value": "{requirements}"},
    {"action": "click", "target": "#submit"}
  ]
}
```

The selectors above are illustrative. The solver calls `submit_artifact` with
`files: {"code": "/challenge/workspace/solve.py"}` and
`values: {"requirements": "curl_cffi"}`. For a file chooser, add a `click`
on the observed chooser immediately followed by an `upload` step with a named
placeholder, and pass that field in `uploads` as a workspace path. Files are
staged temporarily and removed after the browser call.

For chat or other interactive interfaces, save `kind: interactive` and `steps: []`.
The coordinator must handle the interactions and result inspection through browser
tools. This marker does not automatically solve or submit the challenge.

Optional `tracking` describes an observed receipt and a result scoped to that ID:
`id_pattern` must contain exactly one capture group, `url` must be same-origin and
include `{submission_id}`, and `target` must include `{submission_id}`. Configure
observed `success_markers` and `failure_markers`. Polling is bounded by
`timeout_seconds` (0-60) and `interval_seconds` (1-60). Without a unique ID or
unambiguous result, status remains pending or unknown. Use
`check_artifact_submission` to check later. If the result is unknown, inspect the
challenge's records before using `resolve_artifact_submission` with an exact
visible evidence phrase to mark it incorrect or not submitted. This does not mark
the challenge solved. Never blindly retry a submission with an unknown outcome.
