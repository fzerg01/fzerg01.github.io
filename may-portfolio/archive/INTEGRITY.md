# May archive integrity and Actions validation

## Workflow review

| Workflow | Trigger and permissions | Source binding and failure behavior |
| --- | --- | --- |
| may-portfolio-archive | Manual dispatch; matching pushes on main only. contents: read, actions: read. | Builds and validates 31 successful works before upload. Exposes actual immutable artifact ID, archive and integrity-metadata SHA-256, and producer attempt as job outputs. Failed captures prevent upload and both consumers. |
| split-may-archive | workflow_call only; read permissions. | Downloads explicit artifact ID within caller run, verifies repository/run/attempt/commit/ref, ZIP and per-file hashes, manifest paths and required nonempty files before extraction or splitting. Produces all parts with checksums; byte-compares reassembly. |
| publish-may-static-archive | workflow_call only; read permissions. | Uses identical source verification and pinned source checkout. Generates a review artifact, with source metadata and output checksums. No commit, push, or contents: write. |

## Reruns and trust boundary

Artifact names include run ID and attempt; overwrite is disabled. A full rerun creates a fresh artifact. A downstream-only rerun keeps the successful producer's ID and attempt through needs outputs. Verification permits an earlier producer attempt within the same run, but rejects future attempts, different runs, repository, ref or commit. If GitHub does not preserve those outputs in a particular rerun mode, the consumer must fail rather than selecting another artifact.

Hashes bind bytes to producer job outputs; they are not an independent signature or proof that a captured page contains the intended article. Trusted repository workflow code can produce different content. Third-party actions currently retain existing major-version tags and should be SHA-pinned separately if required by repository policy. Browser captures and Ghostscript parse external content, but jobs now have no repository write permission or persisted checkout credentials.

Only the builder is independently dispatchable. To split/publish an archive, dispatch the builder; historical fixed-ID archives are intentionally not accepted. Static review bundles require explicit human review and a normal reviewed repository change to deploy. The source run does not publish automatically.

## Local validation completed

Python compilation and workflow YAML parsing passed. A synthetic 31-work ZIP passed sealing and verification. Downstream rerun with an earlier producer attempt passed. Wrong run, future attempt and modified ZIP were rejected. These checks do not execute Playwright, Ghostscript or GitHub Actions.

## Required live Actions checks

1. Dispatch the builder on this branch after all files are committed. Confirm workflow_call validation, token permissions and artifact ID download support in repository Actions policy.
2. Confirm all 31 external captures succeed with actual PDF/MHTML/thumbnail content; capture errors and HTTP failures must stop consumers.
3. Confirm artifact transport, retention, available disk, upload limits, run timeouts and all variable-count parts work for the real archive.
4. Download parts, verify SHA256SUMS, concatenate in lexical order and verify reconstructed ZIP against archive-integrity.json.
5. Inspect generated static pages, PDFs and links; check Ghostscript runtime and file sizes. Validate review SHA256SUMS after download.
6. Rerun failed consumers only, then rerun all jobs; confirm original producer binding in the former and fresh attempt binding in the latter.
7. Exercise missing/deleted artifact and tampered metadata/member/manifest, duplicate/path-traversal ZIP fixtures in a test run; consumers must fail and upload no derived bundle.
8. Confirm main has no content changes or pushes from any archive job. A successful workflow is a review result, not deployment approval.
