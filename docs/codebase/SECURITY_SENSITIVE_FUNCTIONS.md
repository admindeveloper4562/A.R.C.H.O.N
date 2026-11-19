# Security-Sensitive Functions

| Qualified name | Location | Security implications |
| --- | --- | --- |
| `test_scaffold.IOSScaffoldTests` | `apps/ios/tests/test_scaffold.py:12` | filesystem access; security or trust-boundary vocabulary |
| `test_scaffold.IOSScaffoldTests.test_ios_app_boundary_is_tracked` | `apps/ios/tests/test_scaffold.py:13` | filesystem access; security or trust-boundary vocabulary |
| `web.server.DashboardHandler` | `apps/web/server.py:20` | security or trust-boundary vocabulary |
| `web.server.DashboardHandler._rewrite_route` | `apps/web/server.py:23` | security or trust-boundary vocabulary |
| `web.server.handler_for` | `apps/web/server.py:50` | security or trust-boundary vocabulary |
| `astra_one.__main__.doctor` | `bootstrap/astra-one/astra_one/__main__.py:21` | external or network access; security or trust-boundary vocabulary |
| `astra_one.__main__.main` | `bootstrap/astra-one/astra_one/__main__.py:42` | filesystem access; security or trust-boundary vocabulary |
| `astra_one.core.git` | `bootstrap/astra-one/astra_one/core.py:77` | command or process execution; security or trust-boundary vocabulary |
| `astra_one.core.validate_source` | `bootstrap/astra-one/astra_one/core.py:84` | filesystem access; security or trust-boundary vocabulary |
| `astra_one.core.Store` | `bootstrap/astra-one/astra_one/core.py:98` | command or process execution; database or query access; filesystem access; security or trust-boundary vocabulary |
| `astra_one.core.Store.__init__` | `bootstrap/astra-one/astra_one/core.py:99` | database or query access; security or trust-boundary vocabulary |
| `astra_one.core.Store.db` | `bootstrap/astra-one/astra_one/core.py:104` | database or query access |
| `astra_one.core.Store.init` | `bootstrap/astra-one/astra_one/core.py:116` | database or query access; security or trust-boundary vocabulary |
| `astra_one.core.Store.config` | `bootstrap/astra-one/astra_one/core.py:132` | database or query access |
| `astra_one.core.Store.set_config` | `bootstrap/astra-one/astra_one/core.py:137` | database or query access |
| `astra_one.core.Store.import_architecture` | `bootstrap/astra-one/astra_one/core.py:141` | filesystem access; security or trust-boundary vocabulary |
| `astra_one.core.Store.approve_architecture` | `bootstrap/astra-one/astra_one/core.py:159` | security or trust-boundary vocabulary |
| `astra_one.core.Store.add_task` | `bootstrap/astra-one/astra_one/core.py:165` | database or query access |
| `astra_one.core.Store.add_plan` | `bootstrap/astra-one/astra_one/core.py:178` | database or query access |
| `astra_one.core.Store.tasks` | `bootstrap/astra-one/astra_one/core.py:200` | database or query access |
| `astra_one.core.Store.claim` | `bootstrap/astra-one/astra_one/core.py:205` | database or query access; security or trust-boundary vocabulary |
| `astra_one.core.Store.start_run` | `bootstrap/astra-one/astra_one/core.py:232` | database or query access; security or trust-boundary vocabulary |
| `astra_one.core.Store.update_status` | `bootstrap/astra-one/astra_one/core.py:236` | database or query access |
| `astra_one.core.Store.event` | `bootstrap/astra-one/astra_one/core.py:242` | database or query access |
| `astra_one.core.Store.unsynced` | `bootstrap/astra-one/astra_one/core.py:246` | database or query access |
| `astra_one.core.Store.synced` | `bootstrap/astra-one/astra_one/core.py:250` | database or query access |
| `astra_one.core.Store.approve_task` | `bootstrap/astra-one/astra_one/core.py:254` | database or query access; security or trust-boundary vocabulary |
| `astra_one.core.Store.recover` | `bootstrap/astra-one/astra_one/core.py:264` | database or query access |
| `astra_one.core.Store.retry` | `bootstrap/astra-one/astra_one/core.py:273` | database or query access |
| `astra_one.core.Store.integration_lock` | `bootstrap/astra-one/astra_one/core.py:281` | filesystem access; security or trust-boundary vocabulary |
| `astra_one.core.Store.integrate` | `bootstrap/astra-one/astra_one/core.py:295` | command or process execution; database or query access; filesystem access; security or trust-boundary vocabulary |
| `astra_one.core.Store.overview` | `bootstrap/astra-one/astra_one/core.py:356` | database or query access; security or trust-boundary vocabulary |
| `astra_one.full_plan._json` | `bootstrap/astra-one/astra_one/full_plan.py:34` | security or trust-boundary vocabulary |
| `astra_one.full_plan.render_task_markdown` | `bootstrap/astra-one/astra_one/full_plan.py:118` | database or query access; security or trust-boundary vocabulary |
| `astra_one.full_plan.load_full_plan` | `bootstrap/astra-one/astra_one/full_plan.py:280` | security or trust-boundary vocabulary |
| `astra_one.linux_cli.diagnose` | `bootstrap/astra-one/astra_one/linux_cli.py:38` | command or process execution; security or trust-boundary vocabulary |
| `astra_one.linux_cli.inspect_repository` | `bootstrap/astra-one/astra_one/linux_cli.py:69` | security or trust-boundary vocabulary |
| `astra_one.linux_cli.parse_requirements` | `bootstrap/astra-one/astra_one/linux_cli.py:109` | filesystem access; security or trust-boundary vocabulary |
| `astra_one.linux_cli._task_requirements` | `bootstrap/astra-one/astra_one/linux_cli.py:185` | database or query access |
| `astra_one.linux_cli.supervise` | `bootstrap/astra-one/astra_one/linux_cli.py:201` | filesystem access; security or trust-boundary vocabulary |
| `astra_one.linux_cli._upgrade_audit_brief` | `bootstrap/astra-one/astra_one/linux_cli.py:259` | security or trust-boundary vocabulary |
| `astra_one.linux_cli.run_upgrade_audit` | `bootstrap/astra-one/astra_one/linux_cli.py:285` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `astra_one.linux_cli.run_master` | `bootstrap/astra-one/astra_one/linux_cli.py:393` | command or process execution; database or query access; filesystem access; security or trust-boundary vocabulary |
| `astra_one.linux_cli.run_master.retry_decision` | `bootstrap/astra-one/astra_one/linux_cli.py:425` | database or query access |
| `astra_one.linux_cli.run_master.maybe_requeue` | `bootstrap/astra-one/astra_one/linux_cli.py:438` | database or query access; security or trust-boundary vocabulary |
| `astra_one.linux_cli.run_recovery` | `bootstrap/astra-one/astra_one/linux_cli.py:562` | command or process execution; database or query access; security or trust-boundary vocabulary |
| `astra_one.linux_cli._single_controller` | `bootstrap/astra-one/astra_one/linux_cli.py:666` | security or trust-boundary vocabulary |
| `astra_one.linux_cli.run_concurrent` | `bootstrap/astra-one/astra_one/linux_cli.py:681` | security or trust-boundary vocabulary |
| `astra_one.linux_cli.process_candidate_queue` | `bootstrap/astra-one/astra_one/linux_cli.py:712` | command or process execution; database or query access; filesystem access; security or trust-boundary vocabulary |
| `astra_one.linux_cli.main` | `bootstrap/astra-one/astra_one/linux_cli.py:849` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `astra_one.linux_runtime.review_finding_codes` | `bootstrap/astra-one/astra_one/linux_runtime.py:207` | database or query access; security or trust-boundary vocabulary |
| `astra_one.linux_runtime.sandbox_status` | `bootstrap/astra-one/astra_one/linux_runtime.py:272` | command or process execution; security or trust-boundary vocabulary |
| `astra_one.linux_runtime._task_allows_ci_workflow` | `bootstrap/astra-one/astra_one/linux_runtime.py:293` | security or trust-boundary vocabulary |
| `astra_one.linux_runtime._task_allows_audit_report` | `bootstrap/astra-one/astra_one/linux_runtime.py:310` | security or trust-boundary vocabulary |
| `astra_one.linux_runtime._check_ci_workflow_actions` | `bootstrap/astra-one/astra_one/linux_runtime.py:327` | command or process execution; security or trust-boundary vocabulary |
| `astra_one.linux_runtime._audit_markdown_paths` | `bootstrap/astra-one/astra_one/linux_runtime.py:356` | security or trust-boundary vocabulary |
| `astra_one.linux_runtime._migration_blob_paths` | `bootstrap/astra-one/astra_one/linux_runtime.py:365` | security or trust-boundary vocabulary |
| `astra_one.linux_runtime._check_markdown_hard_breaks` | `bootstrap/astra-one/astra_one/linux_runtime.py:377` | security or trust-boundary vocabulary |
| `astra_one.linux_runtime._check_diff_whitespace` | `bootstrap/astra-one/astra_one/linux_runtime.py:397` | command or process execution; security or trust-boundary vocabulary |
| `astra_one.linux_runtime._git_common_dir` | `bootstrap/astra-one/astra_one/linux_runtime.py:441` | filesystem access; security or trust-boundary vocabulary |
| `astra_one.linux_runtime._validate_change_entries` | `bootstrap/astra-one/astra_one/linux_runtime.py:447` | security or trust-boundary vocabulary |
| `astra_one.linux_runtime.check_changes` | `bootstrap/astra-one/astra_one/linux_runtime.py:524` | command or process execution; security or trust-boundary vocabulary |
| `astra_one.linux_runtime.check_candidate_changes` | `bootstrap/astra-one/astra_one/linux_runtime.py:555` | command or process execution; security or trust-boundary vocabulary |
| `astra_one.linux_runtime._check_commit_whitespace` | `bootstrap/astra-one/astra_one/linux_runtime.py:600` | command or process execution; security or trust-boundary vocabulary |
| `astra_one.linux_runtime._reference_relative_path` | `bootstrap/astra-one/astra_one/linux_runtime.py:616` | security or trust-boundary vocabulary |
| `astra_one.linux_runtime.pack_scoped_source` | `bootstrap/astra-one/astra_one/linux_runtime.py:629` | filesystem access; security or trust-boundary vocabulary |
| `astra_one.linux_runtime.make_prompt` | `bootstrap/astra-one/astra_one/linux_runtime.py:705` | security or trust-boundary vocabulary |
| `astra_one.linux_runtime.codex_command` | `bootstrap/astra-one/astra_one/linux_runtime.py:794` | security or trust-boundary vocabulary |
| `astra_one.linux_runtime.codex_call` | `bootstrap/astra-one/astra_one/linux_runtime.py:856` | command or process execution; database or query access; security or trust-boundary vocabulary |
| `astra_one.linux_runtime.codex_call.reader` | `bootstrap/astra-one/astra_one/linux_runtime.py:891` | security or trust-boundary vocabulary |
| `astra_one.linux_runtime._docker_context` | `bootstrap/astra-one/astra_one/linux_runtime.py:978` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `astra_one.linux_runtime._write_receipt_artifact` | `bootstrap/astra-one/astra_one/linux_runtime.py:1014` | security or trust-boundary vocabulary |
| `astra_one.linux_runtime._complete_test_receipt` | `bootstrap/astra-one/astra_one/linux_runtime.py:1032` | security or trust-boundary vocabulary |
| `astra_one.linux_runtime.docker_test` | `bootstrap/astra-one/astra_one/linux_runtime.py:1093` | command or process execution; security or trust-boundary vocabulary |
| `astra_one.linux_runtime.independent_qc_report` | `bootstrap/astra-one/astra_one/linux_runtime.py:1162` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `astra_one.linux_runtime.independent_qc` | `bootstrap/astra-one/astra_one/linux_runtime.py:1273` | security or trust-boundary vocabulary |
| `astra_one.linux_runtime.merger_review_result` | `bootstrap/astra-one/astra_one/linux_runtime.py:1295` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `astra_one.linux_runtime.merger_review` | `bootstrap/astra-one/astra_one/linux_runtime.py:1387` | security or trust-boundary vocabulary |
| `astra_one.linux_runtime.worker_failure_code` | `bootstrap/astra-one/astra_one/linux_runtime.py:1435` | command or process execution; database or query access; security or trust-boundary vocabulary |
| `astra_one.linux_runtime.ensure_integration` | `bootstrap/astra-one/astra_one/linux_runtime.py:1467` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `astra_one.linux_runtime.integrate` | `bootstrap/astra-one/astra_one/linux_runtime.py:1497` | command or process execution; database or query access; filesystem access; security or trust-boundary vocabulary |
| `astra_one.linux_runtime.execute_claim` | `bootstrap/astra-one/astra_one/linux_runtime.py:1586` | filesystem access; security or trust-boundary vocabulary |
| `astra_one.linux_sda._ensure_v3_columns` | `bootstrap/astra-one/astra_one/linux_sda.py:365` | database or query access |
| `astra_one.linux_sda._ensure_codex_receipt_columns` | `bootstrap/astra-one/astra_one/linux_sda.py:389` | database or query access |
| `astra_one.linux_sda.file_sha256` | `bootstrap/astra-one/astra_one/linux_sda.py:406` | filesystem access; security or trust-boundary vocabulary |
| `astra_one.linux_sda._checkpoint_value` | `bootstrap/astra-one/astra_one/linux_sda.py:424` | database or query access |
| `astra_one.linux_sda._database_state_digest` | `bootstrap/astra-one/astra_one/linux_sda.py:433` | database or query access |
| `astra_one.linux_sda.git` | `bootstrap/astra-one/astra_one/linux_sda.py:446` | command or process execution; security or trust-boundary vocabulary |
| `astra_one.linux_sda.assert_source` | `bootstrap/astra-one/astra_one/linux_sda.py:453` | filesystem access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.validate_task_type` | `bootstrap/astra-one/astra_one/linux_sda.py:496` | filesystem access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.control_blocked` | `bootstrap/astra-one/astra_one/linux_sda.py:544` | security or trust-boundary vocabulary |
| `astra_one.linux_sda.builder_branch` | `bootstrap/astra-one/astra_one/linux_sda.py:553` | security or trust-boundary vocabulary |
| `astra_one.linux_sda._bounded_evidence` | `bootstrap/astra-one/astra_one/linux_sda.py:564` | security or trust-boundary vocabulary |
| `astra_one.linux_sda.State` | `bootstrap/astra-one/astra_one/linux_sda.py:603` | command or process execution; database or query access; external or network access; filesystem access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State.__init__` | `bootstrap/astra-one/astra_one/linux_sda.py:604` | database or query access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State.db` | `bootstrap/astra-one/astra_one/linux_sda.py:610` | database or query access |
| `astra_one.linux_sda.State.data_version` | `bootstrap/astra-one/astra_one/linux_sda.py:622` | database or query access |
| `astra_one.linux_sda.State.wait_for_data_change` | `bootstrap/astra-one/astra_one/linux_sda.py:627` | database or query access |
| `astra_one.linux_sda.State.master_lock` | `bootstrap/astra-one/astra_one/linux_sda.py:647` | filesystem access |
| `astra_one.linux_sda.State.controller_lock` | `bootstrap/astra-one/astra_one/linux_sda.py:668` | filesystem access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State.ensure_full_plan_schema` | `bootstrap/astra-one/astra_one/linux_sda.py:705` | database or query access |
| `astra_one.linux_sda.State.init` | `bootstrap/astra-one/astra_one/linux_sda.py:762` | database or query access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State.get` | `bootstrap/astra-one/astra_one/linux_sda.py:797` | database or query access |
| `astra_one.linux_sda.State.put` | `bootstrap/astra-one/astra_one/linux_sda.py:802` | database or query access |
| `astra_one.linux_sda.State._checkpoint_snapshot` | `bootstrap/astra-one/astra_one/linux_sda.py:806` | database or query access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State.export_checkpoint` | `bootstrap/astra-one/astra_one/linux_sda.py:845` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State._read_checkpoint` | `bootstrap/astra-one/astra_one/linux_sda.py:910` | database or query access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State.restore_checkpoint` | `bootstrap/astra-one/astra_one/linux_sda.py:949` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State.import_architecture` | `bootstrap/astra-one/astra_one/linux_sda.py:989` | filesystem access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State.add_tasks` | `bootstrap/astra-one/astra_one/linux_sda.py:1015` | database or query access |
| `astra_one.linux_sda.State._refresh_project_queues_db` | `bootstrap/astra-one/astra_one/linux_sda.py:1039` | database or query access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State.import_full_plan` | `bootstrap/astra-one/astra_one/linux_sda.py:1096` | database or query access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State._owner_binding` | `bootstrap/astra-one/astra_one/linux_sda.py:1196` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State.owner_approval_request` | `bootstrap/astra-one/astra_one/linux_sda.py:1272` | database or query access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State._record_base008_owner_children` | `bootstrap/astra-one/astra_one/linux_sda.py:1307` | database or query access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State.approve_owner` | `bootstrap/astra-one/astra_one/linux_sda.py:1345` | command or process execution; database or query access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State.full_plan_status` | `bootstrap/astra-one/astra_one/linux_sda.py:1426` | database or query access |
| `astra_one.linux_sda.State._plan_graph_bindings` | `bootstrap/astra-one/astra_one/linux_sda.py:1483` | database or query access |
| `astra_one.linux_sda.State._plan_file` | `bootstrap/astra-one/astra_one/linux_sda.py:1506` | filesystem access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State._validate_plan_amendment` | `bootstrap/astra-one/astra_one/linux_sda.py:1516` | database or query access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State.validate_plan_amendment` | `bootstrap/astra-one/astra_one/linux_sda.py:1617` | database or query access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State.record_plan_amendment` | `bootstrap/astra-one/astra_one/linux_sda.py:1624` | database or query access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State._validate_tws_scope_amendment` | `bootstrap/astra-one/astra_one/linux_sda.py:1772` | database or query access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State.validate_tws_scope_amendment` | `bootstrap/astra-one/astra_one/linux_sda.py:1925` | database or query access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State.record_tws_scope_amendment` | `bootstrap/astra-one/astra_one/linux_sda.py:1940` | database or query access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State._task_markdown_records` | `bootstrap/astra-one/astra_one/linux_sda.py:2046` | database or query access |
| `astra_one.linux_sda.State.export_task_markdown` | `bootstrap/astra-one/astra_one/linux_sda.py:2081` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State.validate_task_markdown_file` | `bootstrap/astra-one/astra_one/linux_sda.py:2105` | database or query access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State.list_tasks` | `bootstrap/astra-one/astra_one/linux_sda.py:2124` | database or query access |
| `astra_one.linux_sda.State.claim` | `bootstrap/astra-one/astra_one/linux_sda.py:2131` | database or query access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State.builder_claim` | `bootstrap/astra-one/astra_one/linux_sda.py:2240` | filesystem access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State.submit_candidate` | `bootstrap/astra-one/astra_one/linux_sda.py:2273` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State.update_candidate_submission` | `bootstrap/astra-one/astra_one/linux_sda.py:2394` | database or query access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State.claim_recovery_task` | `bootstrap/astra-one/astra_one/linux_sda.py:2417` | database or query access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State.set_task` | `bootstrap/astra-one/astra_one/linux_sda.py:2480` | database or query access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State.record_codex_receipt` | `bootstrap/astra-one/astra_one/linux_sda.py:2611` | database or query access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State.failure_codes` | `bootstrap/astra-one/astra_one/linux_sda.py:2657` | database or query access |
| `astra_one.linux_sda.State.subtask_contract_sha` | `bootstrap/astra-one/astra_one/linux_sda.py:2673` | database or query access |
| `astra_one.linux_sda.State._read_receipt_artifact` | `bootstrap/astra-one/astra_one/linux_sda.py:2686` | filesystem access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State.validate_execution_artifacts` | `bootstrap/astra-one/astra_one/linux_sda.py:2734` | security or trust-boundary vocabulary |
| `astra_one.linux_sda.State.subtask_evidence_ready` | `bootstrap/astra-one/astra_one/linux_sda.py:2789` | database or query access |
| `astra_one.linux_sda.State.record_subtask_evidence` | `bootstrap/astra-one/astra_one/linux_sda.py:2812` | database or query access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State.emit` | `bootstrap/astra-one/astra_one/linux_sda.py:2978` | database or query access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State.sync` | `bootstrap/astra-one/astra_one/linux_sda.py:3005` | database or query access; external or network access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State.recover` | `bootstrap/astra-one/astra_one/linux_sda.py:3029` | database or query access |
| `astra_one.linux_sda.State._write_breakdown_report` | `bootstrap/astra-one/astra_one/linux_sda.py:3038` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State._write_breakdown_report.verify_existing` | `bootstrap/astra-one/astra_one/linux_sda.py:3052` | security or trust-boundary vocabulary |
| `astra_one.linux_sda.State.retry` | `bootstrap/astra-one/astra_one/linux_sda.py:3119` | database or query access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State.reopen_failed` | `bootstrap/astra-one/astra_one/linux_sda.py:3153` | database or query access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State.approve` | `bootstrap/astra-one/astra_one/linux_sda.py:3215` | database or query access; security or trust-boundary vocabulary |
| `astra_one.linux_sda.State.overview` | `bootstrap/astra-one/astra_one/linux_sda.py:3238` | database or query access; security or trust-boundary vocabulary |
| `astra_one.owner_approval.OwnerApprovalError` | `bootstrap/astra-one/astra_one/owner_approval.py:31` | security or trust-boundary vocabulary |
| `astra_one.owner_approval._sha256` | `bootstrap/astra-one/astra_one/owner_approval.py:40` | filesystem access; security or trust-boundary vocabulary |
| `astra_one.owner_approval._secure_file` | `bootstrap/astra-one/astra_one/owner_approval.py:48` | security or trust-boundary vocabulary |
| `astra_one.owner_approval._secure_directory` | `bootstrap/astra-one/astra_one/owner_approval.py:61` | security or trust-boundary vocabulary |
| `astra_one.owner_approval._secure_directory_chain` | `bootstrap/astra-one/astra_one/owner_approval.py:72` | security or trust-boundary vocabulary |
| `astra_one.owner_approval._ensure_private_directory` | `bootstrap/astra-one/astra_one/owner_approval.py:89` | security or trust-boundary vocabulary |
| `astra_one.owner_approval._safe_child` | `bootstrap/astra-one/astra_one/owner_approval.py:101` | filesystem access; security or trust-boundary vocabulary |
| `astra_one.owner_approval._validate_payload` | `bootstrap/astra-one/astra_one/owner_approval.py:115` | security or trust-boundary vocabulary |
| `astra_one.owner_approval._document` | `bootstrap/astra-one/astra_one/owner_approval.py:142` | security or trust-boundary vocabulary |
| `astra_one.owner_approval.prepare_receipt` | `bootstrap/astra-one/astra_one/owner_approval.py:166` | security or trust-boundary vocabulary |
| `astra_one.owner_approval._principal_is_allowed` | `bootstrap/astra-one/astra_one/owner_approval.py:213` | command or process execution; security or trust-boundary vocabulary |
| `astra_one.owner_approval.verify_receipt` | `bootstrap/astra-one/astra_one/owner_approval.py:223` | command or process execution; security or trust-boundary vocabulary |
| `astra_one.owner_approval.main` | `bootstrap/astra-one/astra_one/owner_approval.py:269` | command or process execution; security or trust-boundary vocabulary |
| `astra_one.planner.focused_architecture` | `bootstrap/astra-one/astra_one/planner.py:15` | database or query access |
| `astra_one.planner.propose` | `bootstrap/astra-one/astra_one/planner.py:59` | external or network access; filesystem access; security or trust-boundary vocabulary |
| `astra_one.runner.Progress` | `bootstrap/astra-one/astra_one/runner.py:35` | external or network access; security or trust-boundary vocabulary |
| `astra_one.runner.Progress.__init__` | `bootstrap/astra-one/astra_one/runner.py:36` | security or trust-boundary vocabulary |
| `astra_one.runner.Progress.flush` | `bootstrap/astra-one/astra_one/runner.py:43` | external or network access; security or trust-boundary vocabulary |
| `astra_one.runner.publish_manual_state` | `bootstrap/astra-one/astra_one/runner.py:67` | database or query access; security or trust-boundary vocabulary |
| `astra_one.runner.build_prompt` | `bootstrap/astra-one/astra_one/runner.py:77` | security or trust-boundary vocabulary |
| `astra_one.runner.create_worktree` | `bootstrap/astra-one/astra_one/runner.py:96` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `astra_one.runner.changes_and_qc` | `bootstrap/astra-one/astra_one/runner.py:125` | command or process execution; security or trust-boundary vocabulary |
| `astra_one.runner.execute_claim` | `bootstrap/astra-one/astra_one/runner.py:153` | command or process execution; database or query access; security or trust-boundary vocabulary |
| `astra_one.supervisor.classify_failure` | `bootstrap/astra-one/astra_one/supervisor.py:40` | security or trust-boundary vocabulary |
| `astra_one.supervisor.SupervisorController` | `bootstrap/astra-one/astra_one/supervisor.py:77` | command or process execution; database or query access; filesystem access; security or trust-boundary vocabulary |
| `astra_one.supervisor.SupervisorController._reconcile_recovery_leases_locked` | `bootstrap/astra-one/astra_one/supervisor.py:94` | database or query access; security or trust-boundary vocabulary |
| `astra_one.supervisor.SupervisorController._reconcile_completed_cases_locked` | `bootstrap/astra-one/astra_one/supervisor.py:139` | database or query access; security or trust-boundary vocabulary |
| `astra_one.supervisor.SupervisorController._candidate_patch_is_integrated` | `bootstrap/astra-one/astra_one/supervisor.py:171` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `astra_one.supervisor.SupervisorController.reconcile_recovery_leases` | `bootstrap/astra-one/astra_one/supervisor.py:212` | database or query access |
| `astra_one.supervisor.SupervisorController.triage_failure` | `bootstrap/astra-one/astra_one/supervisor.py:220` | database or query access; security or trust-boundary vocabulary |
| `astra_one.supervisor.SupervisorController.self_doctor` | `bootstrap/astra-one/astra_one/supervisor.py:289` | database or query access |
| `astra_one.supervisor.SupervisorController.mark_external_blocker` | `bootstrap/astra-one/astra_one/supervisor.py:318` | database or query access; security or trust-boundary vocabulary |
| `astra_one.supervisor.SupervisorController.resolve_external` | `bootstrap/astra-one/astra_one/supervisor.py:367` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `astra_one.supervisor.SupervisorController._validate_rel_004_evidence` | `bootstrap/astra-one/astra_one/supervisor.py:529` | filesystem access; security or trust-boundary vocabulary |
| `astra_one.supervisor.SupervisorController._validate_github_free_evidence` | `bootstrap/astra-one/astra_one/supervisor.py:617` | database or query access |
| `astra_one.supervisor.SupervisorController._validate_tws_blender_evidence` | `bootstrap/astra-one/astra_one/supervisor.py:642` | filesystem access; security or trust-boundary vocabulary |
| `astra_one.supervisor.SupervisorController._validate_tws_motion_artist_review` | `bootstrap/astra-one/astra_one/supervisor.py:674` | filesystem access; security or trust-boundary vocabulary |
| `astra_one.supervisor.SupervisorController._validate_cloudflare_deployment_evidence` | `bootstrap/astra-one/astra_one/supervisor.py:727` | security or trust-boundary vocabulary |
| `astra_one.supervisor.SupervisorController._validate_pending_jobs_evidence` | `bootstrap/astra-one/astra_one/supervisor.py:757` | security or trust-boundary vocabulary |
| `astra_one.supervisor.SupervisorController._validate_research_benchmark_evidence` | `bootstrap/astra-one/astra_one/supervisor.py:801` | filesystem access; security or trust-boundary vocabulary |
| `astra_one.supervisor.SupervisorController.claim_recovery` | `bootstrap/astra-one/astra_one/supervisor.py:836` | database or query access; security or trust-boundary vocabulary |
| `astra_one.supervisor.SupervisorController.bind_recovery_candidate` | `bootstrap/astra-one/astra_one/supervisor.py:871` | database or query access; security or trust-boundary vocabulary |
| `astra_one.supervisor.SupervisorController.finish_recovery` | `bootstrap/astra-one/astra_one/supervisor.py:904` | command or process execution; database or query access; security or trust-boundary vocabulary |
| `astra_one.supervisor.SupervisorController.release_unstarted_recovery` | `bootstrap/astra-one/astra_one/supervisor.py:972` | database or query access; security or trust-boundary vocabulary |
| `astra_one.supervisor.SupervisorController.claim_upgrade_audit` | `bootstrap/astra-one/astra_one/supervisor.py:999` | database or query access; security or trust-boundary vocabulary |
| `astra_one.supervisor.SupervisorController.finish_upgrade_audit` | `bootstrap/astra-one/astra_one/supervisor.py:1033` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `astra_one.supervisor.SupervisorController.start_batch` | `bootstrap/astra-one/astra_one/supervisor.py:1081` | database or query access; security or trust-boundary vocabulary |
| `astra_one.supervisor.SupervisorController.batch_status` | `bootstrap/astra-one/astra_one/supervisor.py:1117` | database or query access |
| `astra_one.supervisor.SupervisorController.replenish_batch` | `bootstrap/astra-one/astra_one/supervisor.py:1130` | database or query access; security or trust-boundary vocabulary |
| `astra_one.supervisor.SupervisorController.create_upgrade` | `bootstrap/astra-one/astra_one/supervisor.py:1185` | command or process execution; database or query access; security or trust-boundary vocabulary |
| `astra_one.supervisor.SupervisorController._integration_repository` | `bootstrap/astra-one/astra_one/supervisor.py:1210` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `astra_one.supervisor.SupervisorController._verify_commit` | `bootstrap/astra-one/astra_one/supervisor.py:1224` | command or process execution; security or trust-boundary vocabulary |
| `astra_one.supervisor.SupervisorController._candidate_checkout` | `bootstrap/astra-one/astra_one/supervisor.py:1230` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `astra_one.supervisor.SupervisorController._run_candidate_tests` | `bootstrap/astra-one/astra_one/supervisor.py:1253` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `astra_one.supervisor.SupervisorController._verify_database_backup` | `bootstrap/astra-one/astra_one/supervisor.py:1308` | database or query access; security or trust-boundary vocabulary |
| `astra_one.supervisor.SupervisorController.run_upgrade_check` | `bootstrap/astra-one/astra_one/supervisor.py:1319` | security or trust-boundary vocabulary |
| `astra_one.supervisor.SupervisorController._run_upgrade_check_locked` | `bootstrap/astra-one/astra_one/supervisor.py:1324` | command or process execution; database or query access; security or trust-boundary vocabulary |
| `astra_one.supervisor.SupervisorController.transition_upgrade` | `bootstrap/astra-one/astra_one/supervisor.py:1370` | database or query access; security or trust-boundary vocabulary |
| `astra_one.supervisor.SupervisorController.status` | `bootstrap/astra-one/astra_one/supervisor.py:1417` | database or query access |
| `astra_one.supervisor.SupervisorController.tick` | `bootstrap/astra-one/astra_one/supervisor.py:1433` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `astra_one.test_evidence_cache._sha256_file` | `bootstrap/astra-one/astra_one/test_evidence_cache.py:31` | filesystem access; security or trust-boundary vocabulary |
| `astra_one.test_evidence_cache._git_head` | `bootstrap/astra-one/astra_one/test_evidence_cache.py:39` | command or process execution; security or trust-boundary vocabulary |
| `astra_one.test_evidence_cache._tree_sha` | `bootstrap/astra-one/astra_one/test_evidence_cache.py:48` | filesystem access; security or trust-boundary vocabulary |
| `astra_one.test_evidence_cache._dependency_lock_sha` | `bootstrap/astra-one/astra_one/test_evidence_cache.py:66` | filesystem access; security or trust-boundary vocabulary |
| `astra_one.test_evidence_cache._security_policy_sha` | `bootstrap/astra-one/astra_one/test_evidence_cache.py:83` | security or trust-boundary vocabulary |
| `astra_one.test_evidence_cache._runner_version` | `bootstrap/astra-one/astra_one/test_evidence_cache.py:88` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `astra_one.test_evidence_cache.build_cache_material` | `bootstrap/astra-one/astra_one/test_evidence_cache.py:102` | security or trust-boundary vocabulary |
| `astra_one.test_evidence_cache.EvidenceCache` | `bootstrap/astra-one/astra_one/test_evidence_cache.py:138` | filesystem access; security or trust-boundary vocabulary |
| `astra_one.test_evidence_cache.EvidenceCache.__init__` | `bootstrap/astra-one/astra_one/test_evidence_cache.py:139` | security or trust-boundary vocabulary |
| `astra_one.test_evidence_cache.EvidenceCache.load` | `bootstrap/astra-one/astra_one/test_evidence_cache.py:142` | security or trust-boundary vocabulary |
| `astra_one.test_evidence_cache.EvidenceCache.store` | `bootstrap/astra-one/astra_one/test_evidence_cache.py:158` | filesystem access; security or trust-boundary vocabulary |
| `index.get` | `bootstrap/astra-one/cloudflare/astra-one-monitor/src/index.ts:51` | external or network access; security or trust-boundary vocabulary |
| `index.authorized` | `bootstrap/astra-one/cloudflare/astra-one-monitor/src/index.ts:91` | security or trust-boundary vocabulary |
| `worker.test.call` | `bootstrap/astra-one/cloudflare/astra-one-monitor/tests/worker.test.mjs:38` | security or trust-boundary vocabulary |
| `scripts.verify_manifest._validate_windows_component` | `bootstrap/astra-one/scripts/verify_manifest.py:25` | security or trust-boundary vocabulary |
| `scripts.verify_manifest._safe_relative` | `bootstrap/astra-one/scripts/verify_manifest.py:42` | security or trust-boundary vocabulary |
| `scripts.verify_manifest._safe_path` | `bootstrap/astra-one/scripts/verify_manifest.py:58` | security or trust-boundary vocabulary |
| `scripts.verify_manifest._inventory` | `bootstrap/astra-one/scripts/verify_manifest.py:76` | filesystem access; security or trust-boundary vocabulary |
| `scripts.verify_manifest._verify_manifest` | `bootstrap/astra-one/scripts/verify_manifest.py:115` | filesystem access; security or trust-boundary vocabulary |
| `scripts.verify_manifest.verify_manifest` | `bootstrap/astra-one/scripts/verify_manifest.py:155` | filesystem access; security or trust-boundary vocabulary |
| `scripts.verify_package._run` | `bootstrap/astra-one/scripts/verify_package.py:15` | command or process execution; security or trust-boundary vocabulary |
| `scripts.verify_package._verify_package` | `bootstrap/astra-one/scripts/verify_package.py:22` | security or trust-boundary vocabulary |
| `scripts.verify_package.verify_package` | `bootstrap/astra-one/scripts/verify_package.py:56` | filesystem access; security or trust-boundary vocabulary |
| `test_core.git` | `bootstrap/astra-one/tests/test_core.py:17` | command or process execution; security or trust-boundary vocabulary |
| `test_core.AstraTests` | `bootstrap/astra-one/tests/test_core.py:21` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core.AstraTests.setUp` | `bootstrap/astra-one/tests/test_core.py:22` | filesystem access; security or trust-boundary vocabulary |
| `test_core.AstraTests.architecture` | `bootstrap/astra-one/tests/test_core.py:40` | filesystem access |
| `test_core.AstraTests.test_refuse_dirty_source` | `bootstrap/astra-one/tests/test_core.py:61` | filesystem access |
| `test_core.AstraTests.test_architecture_requires_approval` | `bootstrap/astra-one/tests/test_core.py:66` | filesystem access |
| `test_core.AstraTests.test_wrong_architecture_sha_denied` | `bootstrap/astra-one/tests/test_core.py:73` | filesystem access |
| `test_core.AstraTests.test_task_rejects_unexpected_secret_field` | `bootstrap/astra-one/tests/test_core.py:85` | security or trust-boundary vocabulary |
| `test_core.AstraTests.test_pause_prevents_claim` | `bootstrap/astra-one/tests/test_core.py:115` | security or trust-boundary vocabulary |
| `test_core.AstraTests.test_stop_prevents_claim` | `bootstrap/astra-one/tests/test_core.py:120` | security or trust-boundary vocabulary |
| `test_core.AstraTests.test_architecture_replacement_pauses` | `bootstrap/astra-one/tests/test_core.py:125` | filesystem access; security or trust-boundary vocabulary |
| `test_core.AstraTests.test_qc_rejects_deletion` | `bootstrap/astra-one/tests/test_core.py:179` | filesystem access |
| `test_core.AstraTests.test_qc_rejects_python_syntax` | `bootstrap/astra-one/tests/test_core.py:185` | filesystem access |
| `test_core.AstraTests.test_qc_passes_python_syntax` | `bootstrap/astra-one/tests/test_core.py:191` | filesystem access |
| `test_core.AstraTests.test_reviewed_candidate_integrates_only_to_local_feature` | `bootstrap/astra-one/tests/test_core.py:197` | filesystem access |
| `test_core.AstraTests.test_integration_rejects_unapproved` | `bootstrap/astra-one/tests/test_core.py:218` | security or trust-boundary vocabulary |
| `test_core.AstraTests.test_cloudflare_schema_valid_sqlite` | `bootstrap/astra-one/tests/test_core.py:247` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_event_readiness.EventReadinessTests` | `bootstrap/astra-one/tests/test_event_readiness.py:11` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_event_readiness.EventReadinessTests.setUp` | `bootstrap/astra-one/tests/test_event_readiness.py:12` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_evidence_cache.EvidenceCacheTests` | `bootstrap/astra-one/tests/test_evidence_cache.py:9` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `test_evidence_cache.EvidenceCacheTests.setUp` | `bootstrap/astra-one/tests/test_evidence_cache.py:10` | filesystem access; security or trust-boundary vocabulary |
| `test_evidence_cache.EvidenceCacheTests.material` | `bootstrap/astra-one/tests/test_evidence_cache.py:17` | command or process execution; security or trust-boundary vocabulary |
| `test_evidence_cache.EvidenceCacheTests.test_key_contains_material_inputs_and_changes_with_source` | `bootstrap/astra-one/tests/test_evidence_cache.py:23` | filesystem access |
| `test_evidence_cache.EvidenceCacheTests.test_cache_only_reuses_a_success_and_rejects_stale_key` | `bootstrap/astra-one/tests/test_evidence_cache.py:32` | security or trust-boundary vocabulary |
| `test_full_plan.git_repo` | `bootstrap/astra-one/tests/test_full_plan.py:13` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `test_full_plan.bound_receipts` | `bootstrap/astra-one/tests/test_full_plan.py:42` | security or trust-boundary vocabulary |
| `test_full_plan.FullPlanImportTests` | `bootstrap/astra-one/tests/test_full_plan.py:111` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_full_plan.FullPlanImportTests.setUp` | `bootstrap/astra-one/tests/test_full_plan.py:112` | filesystem access; security or trust-boundary vocabulary |
| `test_full_plan.FullPlanImportTests.test_import_is_idempotent_and_conflicts_are_not_overwritten` | `bootstrap/astra-one/tests/test_full_plan.py:200` | database or query access |
| `test_full_plan.FullPlanImportTests.test_owner_gate_requires_authenticated_release` | `bootstrap/astra-one/tests/test_full_plan.py:222` | security or trust-boundary vocabulary |
| `test_full_plan.FullPlanImportTests.test_approved_owner_gate_is_claimable_but_unapproved_gate_is_not` | `bootstrap/astra-one/tests/test_full_plan.py:229` | database or query access; security or trust-boundary vocabulary |
| `test_full_plan.FullPlanImportTests.test_task_markdown_rejects_payload_or_id_drift` | `bootstrap/astra-one/tests/test_full_plan.py:288` | filesystem access |
| `test_linux_sda.git_repo` | `bootstrap/astra-one/tests/test_linux_sda.py:44` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests` | `bootstrap/astra-one/tests/test_linux_sda.py:78` | command or process execution; database or query access; external or network access; filesystem access; security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.setUp` | `bootstrap/astra-one/tests/test_linux_sda.py:79` | filesystem access; security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests._add_supervisor_policy_files` | `bootstrap/astra-one/tests/test_linux_sda.py:91` | filesystem access; security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_worker_failure_categories_are_bounded` | `bootstrap/astra-one/tests/test_linux_sda.py:105` | database or query access |
| `test_linux_sda.LinuxSDATests.test_supervisor_inspection_is_pinned_and_read_only` | `bootstrap/astra-one/tests/test_linux_sda.py:112` | security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_supervisor_inspection_rejects_missing_or_dirty_source` | `bootstrap/astra-one/tests/test_linux_sda.py:126` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_supervise_prompt_binds_task_acceptance_and_repository_citations` | `bootstrap/astra-one/tests/test_linux_sda.py:164` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_supervise_prompt_binds_task_acceptance_and_repository_citations.fake_codex_call` | `bootstrap/astra-one/tests/test_linux_sda.py:169` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_worker_prompt_renders_task_type_and_scope_contract` | `bootstrap/astra-one/tests/test_linux_sda.py:228` | security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_scoped_reference_pack_is_bounded_and_denies_untrusted_paths` | `bootstrap/astra-one/tests/test_linux_sda.py:238` | filesystem access; security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_task_specific_code_index_guidance_targets_qc_findings` | `bootstrap/astra-one/tests/test_linux_sda.py:291` | security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_source_dirty_refused` | `bootstrap/astra-one/tests/test_linux_sda.py:312` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_architecture_approval_explicit` | `bootstrap/astra-one/tests/test_linux_sda.py:317` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_stop_and_pause_gate` | `bootstrap/astra-one/tests/test_linux_sda.py:331` | filesystem access; security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_lane_pause_does_not_cross_block_the_other_lane` | `bootstrap/astra-one/tests/test_linux_sda.py:354` | filesystem access; security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_normal_and_recovery_lane_runner_overlap_without_second_master` | `bootstrap/astra-one/tests/test_linux_sda.py:363` | security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_normal_and_recovery_lane_runner_overlap_without_second_master.fake_recovery` | `bootstrap/astra-one/tests/test_linux_sda.py:371` | security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_concurrent_runner_initializes_schema_before_lane_threads` | `bootstrap/astra-one/tests/test_linux_sda.py:388` | security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_concurrent_runner_initializes_schema_before_lane_threads.fake_recovery` | `bootstrap/astra-one/tests/test_linux_sda.py:397` | security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_lane_critical_section_waits_for_master_lock_without_inference_locking` | `bootstrap/astra-one/tests/test_linux_sda.py:414` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_second_controller_is_rejected_and_stale_lock_reconciles` | `bootstrap/astra-one/tests/test_linux_sda.py:443` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_retry_claim_clears_stale_attempt_fields_but_keeps_history` | `bootstrap/astra-one/tests/test_linux_sda.py:482` | database or query access |
| `test_linux_sda.LinuxSDATests.test_failed_and_retried_tasks_leave_no_stale_review_or_merge_queue` | `bootstrap/astra-one/tests/test_linux_sda.py:497` | database or query access |
| `test_linux_sda.LinuxSDATests.test_tool_count_is_persisted_on_run_transitions` | `bootstrap/astra-one/tests/test_linux_sda.py:517` | database or query access |
| `test_linux_sda.LinuxSDATests.test_codex_receipt_columns_migrate_additively_from_v4` | `bootstrap/astra-one/tests/test_linux_sda.py:527` | database or query access |
| `test_linux_sda.LinuxSDATests.test_reopen_failed_starts_new_generation_without_erasing_history` | `bootstrap/astra-one/tests/test_linux_sda.py:539` | database or query access |
| `test_linux_sda.LinuxSDATests.test_checkpoint_export_and_restore_preserve_ledger_and_safety_controls` | `bootstrap/astra-one/tests/test_linux_sda.py:557` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_checkpoint_restore_rejects_manifest_or_database_tampering` | `bootstrap/astra-one/tests/test_linux_sda.py:602` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_failure_restart_rollback_controls_prevent_duplicate_effects_and_promotion` | `bootstrap/astra-one/tests/test_linux_sda.py:613` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_progress_sync_publishes_only_bounded_metadata_and_receipt_hashes` | `bootstrap/astra-one/tests/test_linux_sda.py:668` | external or network access |
| `test_linux_sda.LinuxSDATests.test_selector_honors_priority_before_fifo` | `bootstrap/astra-one/tests/test_linux_sda.py:732` | database or query access |
| `test_linux_sda.LinuxSDATests.test_task_rejects_unknown_fields` | `bootstrap/astra-one/tests/test_linux_sda.py:744` | security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_danger_bypass_is_explicit_and_omits_normal_sandbox` | `bootstrap/astra-one/tests/test_linux_sda.py:786` | security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_static_change_accepts_valid_python` | `bootstrap/astra-one/tests/test_linux_sda.py:791` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_static_change_accepts_multiple_files_within_limit` | `bootstrap/astra-one/tests/test_linux_sda.py:796` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_static_change_accepts_javascript_module_files` | `bootstrap/astra-one/tests/test_linux_sda.py:802` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_static_change_accepts_scoped_swift_migration_source` | `bootstrap/astra-one/tests/test_linux_sda.py:807` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_static_change_rejects_generated_artifact_paths` | `bootstrap/astra-one/tests/test_linux_sda.py:832` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_static_change_rejects_paths_outside_task_scope` | `bootstrap/astra-one/tests/test_linux_sda.py:840` | filesystem access; security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_static_change_rejects_scope_prefix_sibling` | `bootstrap/astra-one/tests/test_linux_sda.py:848` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_static_change_accepts_scoped_tool_script` | `bootstrap/astra-one/tests/test_linux_sda.py:857` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_static_change_rejects_secret_bearing_env_profile` | `bootstrap/astra-one/tests/test_linux_sda.py:865` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_static_change_rejects_file_limit_with_specific_code` | `bootstrap/astra-one/tests/test_linux_sda.py:880` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_static_change_parses_staged_and_unstaged_porcelain` | `bootstrap/astra-one/tests/test_linux_sda.py:889` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_static_change_rejects_trailing_whitespace_in_untracked_and_staged_files` | `bootstrap/astra-one/tests/test_linux_sda.py:896` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_static_change_rejects_delete` | `bootstrap/astra-one/tests/test_linux_sda.py:909` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_static_change_rejects_policy` | `bootstrap/astra-one/tests/test_linux_sda.py:921` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_scoped_ci_workflow_repair_can_change_only_workflow_yaml` | `bootstrap/astra-one/tests/test_linux_sda.py:927` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_scoped_ci_workflow_rejects_new_floating_action_ref` | `bootstrap/astra-one/tests/test_linux_sda.py:938` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_scoped_ci_workflow_accepts_immutable_action_ref` | `bootstrap/astra-one/tests/test_linux_sda.py:950` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_ci_workflow_scope_does_not_allow_other_hidden_paths` | `bootstrap/astra-one/tests/test_linux_sda.py:961` | filesystem access; security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_audit_scope_accepts_only_documentation_receipts` | `bootstrap/astra-one/tests/test_linux_sda.py:973` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_committed_audit_markdown_hard_breaks_use_same_bounded_policy` | `bootstrap/astra-one/tests/test_linux_sda.py:980` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_audit_scope_rejects_executable_or_test_changes` | `bootstrap/astra-one/tests/test_linux_sda.py:992` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_design_scope_accepts_only_documentation` | `bootstrap/astra-one/tests/test_linux_sda.py:1000` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_audit_merger_prompt_accepts_explicit_unknowns` | `bootstrap/astra-one/tests/test_linux_sda.py:1018` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_audit_merger_prompt_accepts_explicit_unknowns.fake_merger_call` | `bootstrap/astra-one/tests/test_linux_sda.py:1021` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_design_qc_prompt_does_not_require_downstream_implementation` | `bootstrap/astra-one/tests/test_linux_sda.py:1040` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_design_qc_prompt_does_not_require_downstream_implementation.fake_qc_call` | `bootstrap/astra-one/tests/test_linux_sda.py:1048` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_design_merger_prompt_preserves_documentation_boundary` | `bootstrap/astra-one/tests/test_linux_sda.py:1064` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_design_merger_prompt_preserves_documentation_boundary.fake_merger_call` | `bootstrap/astra-one/tests/test_linux_sda.py:1072` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_merger_retries_once_after_invalid_findings_shape` | `bootstrap/astra-one/tests/test_linux_sda.py:1087` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_merger_retries_once_after_invalid_findings_shape.fake_merger_call` | `bootstrap/astra-one/tests/test_linux_sda.py:1090` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_merger_adjudicates_one_concrete_rejection` | `bootstrap/astra-one/tests/test_linux_sda.py:1108` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_merger_adjudicates_one_concrete_rejection.fake_merger_call` | `bootstrap/astra-one/tests/test_linux_sda.py:1111` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_static_change_rejects_invalid_python` | `bootstrap/astra-one/tests/test_linux_sda.py:1132` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_codex_success_without_file_changes_is_not_a_worker_success` | `bootstrap/astra-one/tests/test_linux_sda.py:1139` | filesystem access; security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_independent_qc_receives_validated_untracked_paths` | `bootstrap/astra-one/tests/test_linux_sda.py:1153` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_independent_qc_receives_validated_untracked_paths.fake_qc_call` | `bootstrap/astra-one/tests/test_linux_sda.py:1160` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_codex_failed_file_change_event_is_reported` | `bootstrap/astra-one/tests/test_linux_sda.py:1175` | filesystem access; security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_crash_after_tool_effect_is_interrupted_without_replay` | `bootstrap/astra-one/tests/test_linux_sda.py:1188` | database or query access; filesystem access |
| `test_linux_sda.LinuxSDATests.test_stop_marker_prevents_master_claims` | `bootstrap/astra-one/tests/test_linux_sda.py:1218` | security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_codex_jsonl_receipt_persists_bounded_metadata` | `bootstrap/astra-one/tests/test_linux_sda.py:1232` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_codex_jsonl_parser_redacts_payloads_and_bounds_lines` | `bootstrap/astra-one/tests/test_linux_sda.py:1266` | database or query access; security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_codex_sandbox_failure_is_reported_before_process_start` | `bootstrap/astra-one/tests/test_linux_sda.py:1296` | command or process execution; security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_docker_qc_stages_linked_worktree_with_private_git_index` | `bootstrap/astra-one/tests/test_linux_sda.py:1303` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_docker_qc_stages_linked_worktree_with_private_git_index.fake_run` | `bootstrap/astra-one/tests/test_linux_sda.py:1314` | command or process execution; security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_merger_safe_serial_integration` | `bootstrap/astra-one/tests/test_linux_sda.py:1356` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_integration_accepts_verified_fast_forward_source_after_transfer` | `bootstrap/astra-one/tests/test_linux_sda.py:1378` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_merger_rejects_non_ancestor_candidate_base_before_apply` | `bootstrap/astra-one/tests/test_linux_sda.py:1391` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_main_builder_handoff_is_idempotent_and_merges_through_qc` | `bootstrap/astra-one/tests/test_linux_sda.py:1434` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_main_builder_handoff_is_idempotent_and_merges_through_qc.fake_docker` | `bootstrap/astra-one/tests/test_linux_sda.py:1488` | security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_main_builder_qualifies_five_independent_candidates_serially` | `bootstrap/astra-one/tests/test_linux_sda.py:1507` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_main_builder_qualifies_five_independent_candidates_serially.fake_docker` | `bootstrap/astra-one/tests/test_linux_sda.py:1545` | security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_candidate_diff_validation_rejects_base_mismatch_and_scope_escape` | `bootstrap/astra-one/tests/test_linux_sda.py:1589` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_project_approval_moves_candidate_to_serial_merge_queue` | `bootstrap/astra-one/tests/test_linux_sda.py:1602` | database or query access |
| `test_linux_sda.LinuxSDATests.test_merger_rejection_fails_task_and_preserves_rebuild_queue` | `bootstrap/astra-one/tests/test_linux_sda.py:1615` | database or query access; filesystem access |
| `test_linux_sda.LinuxSDATests.test_merger_rejects_candidate_trailing_whitespace_before_apply` | `bootstrap/astra-one/tests/test_linux_sda.py:1642` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_architecture_change_invalidates_old_queued_tasks` | `bootstrap/astra-one/tests/test_linux_sda.py:1672` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_full_codex_pipeline_mocked_five_tasks` | `bootstrap/astra-one/tests/test_linux_sda.py:1682` | filesystem access; security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_full_codex_pipeline_mocked_five_tasks.fake_docker_test` | `bootstrap/astra-one/tests/test_linux_sda.py:1700` | security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_repeated_worker_failure_stops_before_retry_ceiling` | `bootstrap/astra-one/tests/test_linux_sda.py:1722` | database or query access; security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_failed_candidate_is_quarantined_and_retry_preserves_error_proof` | `bootstrap/astra-one/tests/test_linux_sda.py:1743` | database or query access; filesystem access |
| `test_linux_sda.LinuxSDATests.test_event_metadata_accepts_new_rebuild_branch_policy` | `bootstrap/astra-one/tests/test_linux_sda.py:1871` | database or query access |
| `test_linux_sda.LinuxSDATests.test_event_metadata_schema` | `bootstrap/astra-one/tests/test_linux_sda.py:1891` | database or query access |
| `test_owner_approval.OwnerApprovalTests` | `bootstrap/astra-one/tests/test_owner_approval.py:16` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `test_owner_approval.OwnerApprovalTests.setUp` | `bootstrap/astra-one/tests/test_owner_approval.py:17` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `test_owner_approval.OwnerApprovalTests.test_signed_receipt_verifies_and_binds_expected_fields` | `bootstrap/astra-one/tests/test_owner_approval.py:62` | security or trust-boundary vocabulary |
| `test_owner_approval.OwnerApprovalTests.test_tampered_receipt_is_rejected` | `bootstrap/astra-one/tests/test_owner_approval.py:71` | filesystem access; security or trust-boundary vocabulary |
| `test_owner_approval.OwnerApprovalTests.test_changed_trusted_signer_file_is_rejected` | `bootstrap/astra-one/tests/test_owner_approval.py:79` | filesystem access; security or trust-boundary vocabulary |
| `test_owner_approval.OwnerApprovalTests.test_receipt_symlink_and_weak_modes_are_rejected` | `bootstrap/astra-one/tests/test_owner_approval.py:85` | filesystem access; security or trust-boundary vocabulary |
| `test_owner_approval_state.OwnerApprovalStateTests` | `bootstrap/astra-one/tests/test_owner_approval_state.py:14` | command or process execution; database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_owner_approval_state.OwnerApprovalStateTests.setUp` | `bootstrap/astra-one/tests/test_owner_approval_state.py:15` | command or process execution; database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_owner_approval_state.OwnerApprovalStateTests.test_master_records_owner_and_three_child_receipts` | `bootstrap/astra-one/tests/test_owner_approval_state.py:91` | command or process execution; database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_owner_approval_state.OwnerApprovalStateTests.test_cli_request_and_approval_commands` | `bootstrap/astra-one/tests/test_owner_approval_state.py:104` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `test_owner_approval_state.OwnerApprovalStateTests.test_missing_owner_receipt_does_not_change_state` | `bootstrap/astra-one/tests/test_owner_approval_state.py:129` | database or query access; security or trust-boundary vocabulary |
| `test_scope_amendment.git_repo` | `bootstrap/astra-one/tests/test_scope_amendment.py:16` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `test_scope_amendment.TwsScopeAmendmentTests` | `bootstrap/astra-one/tests/test_scope_amendment.py:32` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_scope_amendment.TwsScopeAmendmentTests.setUp` | `bootstrap/astra-one/tests/test_scope_amendment.py:33` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_scope_amendment.TwsScopeAmendmentTests.amendment` | `bootstrap/astra-one/tests/test_scope_amendment.py:126` | database or query access; security or trust-boundary vocabulary |
| `test_scope_amendment.TwsScopeAmendmentTests.test_scope_amendment_is_validated_applied_and_idempotent` | `bootstrap/astra-one/tests/test_scope_amendment.py:200` | database or query access; filesystem access |
| `test_supervisor_v3.git_repo` | `bootstrap/astra-one/tests/test_supervisor_v3.py:15` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `test_supervisor_v3.bound_receipts` | `bootstrap/astra-one/tests/test_supervisor_v3.py:79` | security or trust-boundary vocabulary |
| `test_supervisor_v3.SupervisorV3Tests` | `bootstrap/astra-one/tests/test_supervisor_v3.py:116` | command or process execution; database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_supervisor_v3.SupervisorV3Tests.setUp` | `bootstrap/astra-one/tests/test_supervisor_v3.py:117` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `test_supervisor_v3.SupervisorV3Tests.test_failure_taxonomy_and_case_lane_lease_are_durable` | `bootstrap/astra-one/tests/test_supervisor_v3.py:173` | security or trust-boundary vocabulary |
| `test_supervisor_v3.SupervisorV3Tests.test_self_doctor_creates_one_scoped_proposal_across_generations` | `bootstrap/astra-one/tests/test_supervisor_v3.py:199` | database or query access |
| `test_supervisor_v3.SupervisorV3Tests.test_tick_resolves_historical_case_only_after_task_completion` | `bootstrap/astra-one/tests/test_supervisor_v3.py:226` | database or query access |
| `test_supervisor_v3.SupervisorV3Tests.test_tick_releases_lane_when_recovery_finished_before_callback` | `bootstrap/astra-one/tests/test_supervisor_v3.py:244` | database or query access |
| `test_supervisor_v3.SupervisorV3Tests.test_patch_applied_merger_checkpoint_resolves_recovery` | `bootstrap/astra-one/tests/test_supervisor_v3.py:263` | command or process execution; database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_supervisor_v3.SupervisorV3Tests.test_external_blocker_fences_task_without_recovery_generation` | `bootstrap/astra-one/tests/test_supervisor_v3.py:334` | database or query access |
| `test_supervisor_v3.SupervisorV3Tests.test_external_resolution_never_reopens_windows_without_device_evidence` | `bootstrap/astra-one/tests/test_supervisor_v3.py:346` | filesystem access |
| `test_supervisor_v3.SupervisorV3Tests.test_rel004_external_evidence_requires_real_profile_and_sanitized_linux_manifest` | `bootstrap/astra-one/tests/test_supervisor_v3.py:353` | filesystem access |
| `test_supervisor_v3.SupervisorV3Tests.test_research_external_evidence_binds_report_and_limits` | `bootstrap/astra-one/tests/test_supervisor_v3.py:399` | filesystem access |
| `test_supervisor_v3.SupervisorV3Tests.test_cloudflare_deployment_evidence_requires_read_only_health_and_schema` | `bootstrap/astra-one/tests/test_supervisor_v3.py:418` | security or trust-boundary vocabulary |
| `test_supervisor_v3.SupervisorV3Tests.test_pending_jobs_evidence_requires_metadata_only_deployment` | `bootstrap/astra-one/tests/test_supervisor_v3.py:437` | security or trust-boundary vocabulary |
| `test_supervisor_v3.SupervisorV3Tests.test_pending_jobs_resolution_accepts_required_no_secrets_attestation` | `bootstrap/astra-one/tests/test_supervisor_v3.py:465` | filesystem access; security or trust-boundary vocabulary |
| `test_supervisor_v3.SupervisorV3Tests.test_external_blocker_clears_stale_pending_claim_and_survives_refresh` | `bootstrap/astra-one/tests/test_supervisor_v3.py:502` | database or query access |
| `test_supervisor_v3.SupervisorV3Tests.test_reopen_failed_readmits_stale_batch_member_without_erasing_case` | `bootstrap/astra-one/tests/test_supervisor_v3.py:527` | database or query access |
| `test_supervisor_v3.SupervisorV3Tests.test_expired_recovery_lease_is_fenced_after_process_loss` | `bootstrap/astra-one/tests/test_supervisor_v3.py:555` | database or query access |
| `test_supervisor_v3.SupervisorV3Tests.test_resolved_recovery_rejects_empty_unbound_candidate` | `bootstrap/astra-one/tests/test_supervisor_v3.py:590` | database or query access |
| `test_supervisor_v3.SupervisorV3Tests.test_upgrade_candidate_without_tests_is_rejected` | `bootstrap/astra-one/tests/test_supervisor_v3.py:614` | command or process execution; security or trust-boundary vocabulary |
| `test_supervisor_v3.SupervisorV3Tests.test_github_free_plan_amendment_is_sha_bound_and_idempotent` | `bootstrap/astra-one/tests/test_supervisor_v3.py:645` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_supervisor_v3.SupervisorV3Tests.test_mig010_single_builder_amendment_releases_obsolete_blocker` | `bootstrap/astra-one/tests/test_supervisor_v3.py:690` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_supervisor_v3.SupervisorV3Tests.test_rel003_single_builder_amendment_updates_pending_task_idempotently` | `bootstrap/astra-one/tests/test_supervisor_v3.py:752` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_supervisor_v3.SupervisorV3Tests.test_rel016_packaging_amendment_expands_scope_and_releases_quota_blocker` | `bootstrap/astra-one/tests/test_supervisor_v3.py:818` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_supervisor_v3.SupervisorV3Tests.test_linux_platform_amendment_preserves_windows_requirement_and_releases_root` | `bootstrap/astra-one/tests/test_supervisor_v3.py:893` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_supervisor_v3.SupervisorV3Tests.test_tws_motion_review_requires_approved_bound_manifest` | `bootstrap/astra-one/tests/test_supervisor_v3.py:978` | filesystem access; security or trust-boundary vocabulary |
| `cloudflare.dashboard_worker.authorized` | `infra/cloudflare/dashboard_worker.js:36` | security or trust-boundary vocabulary |
| `cloudflare.dashboard_worker.taskId` | `infra/cloudflare/dashboard_worker.js:40` | security or trust-boundary vocabulary |
| `cloudflare.heartbeat_worker.authorized` | `infra/cloudflare/heartbeat_worker.js:27` | security or trust-boundary vocabulary |
| `cloudflare.rate_limit.setting` | `infra/cloudflare/rate_limit.js:4` | security or trust-boundary vocabulary |
| `cloudflare.rate_limit.digest` | `infra/cloudflare/rate_limit.js:9` | security or trust-boundary vocabulary |
| `cloudflare.rate_limit.allowRequest` | `infra/cloudflare/rate_limit.js:14` | security or trust-boundary vocabulary |
| `verify_installation._relative_file` | `infra/verify_installation.py:31` | filesystem access; security or trust-boundary vocabulary |
| `verify_installation.validate_manifest` | `infra/verify_installation.py:55` | security or trust-boundary vocabulary |
| `adapters.legacy_contracts._within` | `migration/adapters/legacy_contracts.py:89` | filesystem access; security or trust-boundary vocabulary |
| `adapters.legacy_contracts.LegacyContractAdapter` | `migration/adapters/legacy_contracts.py:101` | filesystem access; security or trust-boundary vocabulary |
| `adapters.legacy_contracts.LegacyContractAdapter.__init__` | `migration/adapters/legacy_contracts.py:104` | filesystem access; security or trust-boundary vocabulary |
| `adapters.legacy_contracts.LegacyContractAdapter._records` | `migration/adapters/legacy_contracts.py:114` | security or trust-boundary vocabulary |
| `adapters.legacy_contracts.LegacyContractAdapter.snapshot` | `migration/adapters/legacy_contracts.py:157` | security or trust-boundary vocabulary |
| `imported.automation.windows.jarvis_queue_worker.make_worker_id` | `migration/imported/automation/windows/jarvis_queue_worker.py:79` | external or network access |
| `imported.automation.windows.jarvis_queue_worker.CoordinatorClient` | `migration/imported/automation/windows/jarvis_queue_worker.py:264` | external or network access; security or trust-boundary vocabulary |
| `imported.automation.windows.jarvis_queue_worker.CoordinatorClient.request` | `migration/imported/automation/windows/jarvis_queue_worker.py:268` | external or network access; security or trust-boundary vocabulary |
| `imported.automation.windows.jarvis_queue_worker.OllamaClient` | `migration/imported/automation/windows/jarvis_queue_worker.py:390` | external or network access; security or trust-boundary vocabulary |
| `imported.automation.windows.jarvis_queue_worker.OllamaClient.generate` | `migration/imported/automation/windows/jarvis_queue_worker.py:394` | external or network access; security or trust-boundary vocabulary |
| `imported.automation.windows.jarvis_queue_worker.QueueWorker` | `migration/imported/automation/windows/jarvis_queue_worker.py:430` | security or trust-boundary vocabulary |
| `imported.automation.windows.jarvis_queue_worker.QueueWorker.stop` | `migration/imported/automation/windows/jarvis_queue_worker.py:528` | security or trust-boundary vocabulary |
| `imported.automation.windows.jarvis_queue_worker.main` | `migration/imported/automation/windows/jarvis_queue_worker.py:547` | security or trust-boundary vocabulary |
| `imported.backend.colibri.ColibriConfig` | `migration/imported/backend/colibri.py:21` | filesystem access; security or trust-boundary vocabulary |
| `imported.backend.colibri.ColibriConfig.__post_init__` | `migration/imported/backend/colibri.py:30` | security or trust-boundary vocabulary |
| `imported.backend.colibri.ColibriClient` | `migration/imported/backend/colibri.py:59` | external or network access; security or trust-boundary vocabulary |
| `imported.backend.colibri.ColibriClient.models` | `migration/imported/backend/colibri.py:75` | external or network access |
| `imported.backend.colibri.ColibriClient.status` | `migration/imported/backend/colibri.py:82` | external or network access |
| `imported.backend.colibri.ColibriClient.complete` | `migration/imported/backend/colibri.py:106` | external or network access |
| `imported.backend.colibri.ColibriClient.complete_async` | `migration/imported/backend/colibri.py:139` | external or network access; security or trust-boundary vocabulary |
| `imported.backend.colibri.ColibriClient.complete_stream` | `migration/imported/backend/colibri.py:158` | external or network access |
| `imported.backend.colibri.ColibriClient.complete_stream_async` | `migration/imported/backend/colibri.py:199` | external or network access; security or trust-boundary vocabulary |
| `imported.backend.colibri.cli_status` | `migration/imported/backend/colibri.py:242` | command or process execution; security or trust-boundary vocabulary |
| `imported.backend.permissions.FileIdentity` | `migration/imported/backend/permissions.py:24` | filesystem access; security or trust-boundary vocabulary |
| `imported.backend.permissions.FileIdentity.capture` | `migration/imported/backend/permissions.py:32` | security or trust-boundary vocabulary |
| `imported.backend.permissions.FileIdentity.matches` | `migration/imported/backend/permissions.py:39` | filesystem access; security or trust-boundary vocabulary |
| `imported.backend.permissions.FileIdentity.digest` | `migration/imported/backend/permissions.py:51` | security or trust-boundary vocabulary |
| `imported.backend.permissions.ApprovalBroker` | `migration/imported/backend/permissions.py:65` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `imported.backend.permissions.ApprovalBroker._validate_request_id` | `migration/imported/backend/permissions.py:73` | security or trust-boundary vocabulary |
| `imported.backend.permissions.ApprovalBroker.__init__` | `migration/imported/backend/permissions.py:79` | database or query access; security or trust-boundary vocabulary |
| `imported.backend.permissions.ApprovalBroker.propose` | `migration/imported/backend/permissions.py:122` | database or query access; security or trust-boundary vocabulary |
| `imported.backend.permissions.ApprovalBroker._validate_reason` | `migration/imported/backend/permissions.py:145` | security or trust-boundary vocabulary |
| `imported.backend.permissions.ApprovalBroker.propose_directory` | `migration/imported/backend/permissions.py:156` | security or trust-boundary vocabulary |
| `imported.backend.permissions.ApprovalBroker.decide` | `migration/imported/backend/permissions.py:164` | database or query access; security or trust-boundary vocabulary |
| `imported.backend.permissions.ApprovalBroker.authorize_execution` | `migration/imported/backend/permissions.py:184` | database or query access; security or trust-boundary vocabulary |
| `imported.backend.permissions.ApprovalBroker.trash_file` | `migration/imported/backend/permissions.py:203` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `imported.backend.permissions.ApprovalBroker.execute_trash_file` | `migration/imported/backend/permissions.py:284` | security or trust-boundary vocabulary |
| `imported.backend.permissions.ApprovalBroker.verified_file` | `migration/imported/backend/permissions.py:319` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `imported.backend.permissions.ApprovalBroker._checksum_fd` | `migration/imported/backend/permissions.py:364` | filesystem access; security or trust-boundary vocabulary |
| `imported.backend.permissions.ApprovalBroker.trash_manifest` | `migration/imported/backend/permissions.py:380` | database or query access |
| `imported.backend.permissions.ApprovalBroker.propose_restore` | `migration/imported/backend/permissions.py:390` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `imported.backend.permissions.ApprovalBroker.restore_file` | `migration/imported/backend/permissions.py:408` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `imported.backend.permissions.ApprovalBroker.audit` | `migration/imported/backend/permissions.py:469` | database or query access |
| `imported.backend.permissions.ApprovalBroker._audit` | `migration/imported/backend/permissions.py:498` | database or query access; security or trust-boundary vocabulary |
| `imported.backend.router.RouterTelemetry` | `migration/imported/backend/router.py:26` | external or network access |
| `imported.backend.router.RouterTelemetry.snapshot` | `migration/imported/backend/router.py:33` | external or network access |
| `imported.backend.router.ResourceAwareRouter` | `migration/imported/backend/router.py:40` | external or network access |
| `imported.backend.router.ResourceAwareRouter.complete` | `migration/imported/backend/router.py:65` | external or network access |
| `imported.backend.storage.prepare_path` | `migration/imported/backend/storage.py:12` | database or query access; security or trust-boundary vocabulary |
| `imported.backend.storage.connect` | `migration/imported/backend/storage.py:21` | database or query access; security or trust-boundary vocabulary |
| `imported.backend.storage.ensure_schema` | `migration/imported/backend/storage.py:41` | database or query access; security or trust-boundary vocabulary |
| `imported.core.tasks.TaskStore` | `migration/imported/core/tasks.py:31` | database or query access; security or trust-boundary vocabulary |
| `imported.core.tasks.TaskStore.__init__` | `migration/imported/core/tasks.py:32` | security or trust-boundary vocabulary |
| `imported.core.tasks.TaskStore.create` | `migration/imported/core/tasks.py:41` | database or query access; security or trust-boundary vocabulary |
| `imported.core.tasks.TaskStore._event` | `migration/imported/core/tasks.py:56` | database or query access |
| `imported.core.tasks.TaskStore.get` | `migration/imported/core/tasks.py:60` | database or query access; security or trust-boundary vocabulary |
| `imported.core.tasks.TaskStore.transition` | `migration/imported/core/tasks.py:67` | database or query access; security or trust-boundary vocabulary |
| `imported.core.tasks.TaskStore.list` | `migration/imported/core/tasks.py:81` | database or query access; security or trust-boundary vocabulary |
| `imported.core.tasks.TaskStore.events_since` | `migration/imported/core/tasks.py:97` | database or query access; security or trust-boundary vocabulary |
| `imported.core.tasks.TaskStore.events_for` | `migration/imported/core/tasks.py:105` | database or query access; security or trust-boundary vocabulary |
| `imported.core.tasks.TaskStore.cancel` | `migration/imported/core/tasks.py:116` | security or trust-boundary vocabulary |
| `imported.core.tasks.TaskStore.recover_running` | `migration/imported/core/tasks.py:119` | database or query access; security or trust-boundary vocabulary |
| `imported.core.worker.inventory_scan_tool` | `migration/imported/core/worker.py:90` | filesystem access; security or trust-boundary vocabulary |
| `imported.core.worker.validate_inventory_scan` | `migration/imported/core/worker.py:104` | security or trust-boundary vocabulary |
| `imported.guardian.sda_module_integrity.IntegrityError` | `migration/imported/guardian/sda_module_integrity.py:24` | security or trust-boundary vocabulary |
| `imported.guardian.sda_module_integrity._id` | `migration/imported/guardian/sda_module_integrity.py:28` | security or trust-boundary vocabulary |
| `imported.guardian.sda_module_integrity._bool` | `migration/imported/guardian/sda_module_integrity.py:34` | security or trust-boundary vocabulary |
| `imported.guardian.sda_module_integrity.plan` | `migration/imported/guardian/sda_module_integrity.py:40` | security or trust-boundary vocabulary |
| `imported.guardian.sda_module_integrity.main` | `migration/imported/guardian/sda_module_integrity.py:179` | filesystem access; security or trust-boundary vocabulary |
| `imported.guardian.sda_recovery_triage._load_script` | `migration/imported/guardian/sda_recovery_triage.py:32` | security or trust-boundary vocabulary |
| `imported.guardian.sda_recovery_triage.plan` | `migration/imported/guardian/sda_recovery_triage.py:41` | security or trust-boundary vocabulary |
| `imported.guardian.sda_recovery_triage.main` | `migration/imported/guardian/sda_recovery_triage.py:116` | security or trust-boundary vocabulary |
| `imported.runtime.email.SampleEmailProvider` | `migration/imported/runtime/email.py:21` | security or trust-boundary vocabulary |
| `imported.runtime.inventory.mounted_volumes` | `migration/imported/runtime/inventory.py:22` | filesystem access; security or trust-boundary vocabulary |
| `imported.runtime.inventory._is_secret_name` | `migration/imported/runtime/inventory.py:48` | security or trust-boundary vocabulary |
| `imported.runtime.inventory.FileRecord` | `migration/imported/runtime/inventory.py:54` | security or trust-boundary vocabulary |
| `imported.runtime.inventory.is_allowed` | `migration/imported/runtime/inventory.py:62` | security or trust-boundary vocabulary |
| `imported.runtime.inventory.default_roots` | `migration/imported/runtime/inventory.py:76` | filesystem access; security or trust-boundary vocabulary |
| `imported.runtime.inventory.configured_roots` | `migration/imported/runtime/inventory.py:88` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `imported.runtime.inventory._open_git_metadata` | `migration/imported/runtime/inventory.py:104` | filesystem access; security or trust-boundary vocabulary |
| `imported.runtime.inventory._git_branch` | `migration/imported/runtime/inventory.py:125` | filesystem access |
| `imported.runtime.inventory._git_checkpoint` | `migration/imported/runtime/inventory.py:149` | filesystem access |
| `imported.runtime.inventory.discover_projects` | `migration/imported/runtime/inventory.py:186` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `imported.runtime.inventory.add_configured_root` | `migration/imported/runtime/inventory.py:299` | database or query access; security or trust-boundary vocabulary |
| `imported.runtime.inventory.scan` | `migration/imported/runtime/inventory.py:313` | filesystem access; security or trust-boundary vocabulary |
| `imported.runtime.inventory.store` | `migration/imported/runtime/inventory.py:366` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `imported.runtime.inventory.refresh` | `migration/imported/runtime/inventory.py:402` | database or query access; security or trust-boundary vocabulary |
| `imported.runtime.inventory.refresh_status` | `migration/imported/runtime/inventory.py:428` | database or query access; security or trust-boundary vocabulary |
| `imported.runtime.inventory.search` | `migration/imported/runtime/inventory.py:436` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `imported.runtime.inventory.duplicate_groups` | `migration/imported/runtime/inventory.py:483` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `imported.runtime.inventory.verified_duplicate_groups` | `migration/imported/runtime/inventory.py:504` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `imported.runtime.inventory.cleanup_preview` | `migration/imported/runtime/inventory.py:581` | security or trust-boundary vocabulary |
| `imported.runtime.inventory.organization_preview` | `migration/imported/runtime/inventory.py:595` | filesystem access; security or trust-boundary vocabulary |
| `imported.runtime.server._query` | `migration/imported/runtime/server.py:75` | database or query access |
| `imported.runtime.server.init_db` | `migration/imported/runtime/server.py:101` | security or trust-boundary vocabulary |
| `imported.runtime.server.chat_history` | `migration/imported/runtime/server.py:106` | database or query access; security or trust-boundary vocabulary |
| `imported.runtime.server.save_chat_turn` | `migration/imported/runtime/server.py:120` | database or query access; security or trust-boundary vocabulary |
| `imported.runtime.server.voice_summary` | `migration/imported/runtime/server.py:155` | security or trust-boundary vocabulary |
| `imported.runtime.server.calendar_proposals` | `migration/imported/runtime/server.py:191` | database or query access; security or trust-boundary vocabulary |
| `imported.runtime.server.email_drafts` | `migration/imported/runtime/server.py:202` | database or query access; security or trust-boundary vocabulary |
| `imported.runtime.server.email_summary` | `migration/imported/runtime/server.py:210` | security or trust-boundary vocabulary |
| `imported.runtime.server.email_draft_preview` | `migration/imported/runtime/server.py:236` | database or query access; security or trust-boundary vocabulary |
| `imported.runtime.server.probe_colibri` | `migration/imported/runtime/server.py:260` | command or process execution; external or network access; security or trust-boundary vocabulary |
| `imported.runtime.server.page` | `migration/imported/runtime/server.py:265` | database or query access; external or network access; security or trust-boundary vocabulary |
| `imported.runtime.server.App` | `migration/imported/runtime/server.py:355` | database or query access; external or network access; filesystem access; security or trust-boundary vocabulary |
| `imported.runtime.server.App.__init__` | `migration/imported/runtime/server.py:356` | database or query access |
| `imported.runtime.server.App.owner_bootstrapped` | `migration/imported/runtime/server.py:377` | database or query access |
| `imported.runtime.server.App.issue_owner_session` | `migration/imported/runtime/server.py:382` | database or query access; security or trust-boundary vocabulary |
| `imported.runtime.server.App.rotate_session` | `migration/imported/runtime/server.py:393` | security or trust-boundary vocabulary |
| `imported.runtime.server.App.origin_allowed` | `migration/imported/runtime/server.py:416` | external or network access |
| `imported.runtime.server.App.request_origin_allowed` | `migration/imported/runtime/server.py:421` | external or network access; security or trust-boundary vocabulary |
| `imported.runtime.server.App.handle` | `migration/imported/runtime/server.py:435` | database or query access; external or network access; filesystem access; security or trust-boundary vocabulary |
| `imported.runtime.server.App.respond` | `migration/imported/runtime/server.py:1298` | security or trust-boundary vocabulary |
| `imported.runtime.server.App._respond_stream_headers` | `migration/imported/runtime/server.py:1347` | security or trust-boundary vocabulary |
| `imported.runtime.voice._found` | `migration/imported/runtime/voice.py:16` | security or trust-boundary vocabulary |
| `imported.runtime.voice.local_adapters` | `migration/imported/runtime/voice.py:20` | security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.__main__.doctor` | `migration/imported/sda/astra-one-v0.2.0/astra_one/__main__.py:21` | external or network access; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.__main__.main` | `migration/imported/sda/astra-one-v0.2.0/astra_one/__main__.py:42` | filesystem access; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.core.git` | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:77` | command or process execution; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.core.validate_source` | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:84` | filesystem access; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store` | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:98` | command or process execution; database or query access; filesystem access; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.__init__` | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:99` | database or query access; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.db` | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:104` | database or query access |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.init` | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:116` | database or query access; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.config` | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:132` | database or query access |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.set_config` | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:137` | database or query access |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.import_architecture` | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:141` | filesystem access; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.approve_architecture` | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:159` | security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.add_task` | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:165` | database or query access |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.add_plan` | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:178` | database or query access |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.tasks` | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:200` | database or query access |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.claim` | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:205` | database or query access; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.start_run` | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:232` | database or query access; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.update_status` | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:236` | database or query access |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.event` | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:242` | database or query access |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.unsynced` | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:246` | database or query access |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.synced` | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:250` | database or query access |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.approve_task` | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:254` | database or query access; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.recover` | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:264` | database or query access |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.retry` | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:273` | database or query access |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.integration_lock` | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:281` | filesystem access; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.integrate` | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:295` | command or process execution; database or query access; filesystem access; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.overview` | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:356` | database or query access; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_cli.diagnose` | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_cli.py:25` | command or process execution; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_cli.supervise` | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_cli.py:48` | filesystem access; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_cli.run_master` | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_cli.py:95` | command or process execution; database or query access; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_cli.main` | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_cli.py:176` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_runtime.check_changes` | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_runtime.py:26` | command or process execution; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_runtime.codex_command` | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_runtime.py:90` | security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_runtime.codex_call` | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_runtime.py:101` | command or process execution; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_runtime.codex_call.reader` | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_runtime.py:113` | security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_runtime.docker_test` | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_runtime.py:169` | command or process execution; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_runtime.independent_qc` | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_runtime.py:204` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_runtime.merger_review` | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_runtime.py:235` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_runtime.ensure_integration` | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_runtime.py:259` | filesystem access; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_runtime.integrate` | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_runtime.py:276` | command or process execution; database or query access; filesystem access; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_runtime.execute_claim` | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_runtime.py:323` | filesystem access; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.git` | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:71` | command or process execution; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.assert_source` | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:78` | filesystem access; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State` | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:111` | database or query access; external or network access; filesystem access; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State.__init__` | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:112` | database or query access; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State.db` | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:118` | database or query access |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State.master_lock` | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:131` | filesystem access |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State.init` | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:145` | database or query access; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State.get` | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:170` | database or query access |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State.put` | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:175` | database or query access |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State.import_architecture` | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:179` | filesystem access; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State.add_tasks` | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:205` | database or query access |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State.list_tasks` | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:226` | database or query access |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State.claim` | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:230` | database or query access; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State.set_task` | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:253` | database or query access |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State.emit` | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:267` | database or query access |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State.sync` | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:279` | database or query access; external or network access; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State.recover` | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:303` | database or query access |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State.retry` | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:312` | database or query access |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State.approve` | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:319` | database or query access; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State.overview` | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:326` | database or query access; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.planner.focused_architecture` | `migration/imported/sda/astra-one-v0.2.0/astra_one/planner.py:15` | database or query access |
| `imported.sda.astra_one_v0.2.0.astra_one.planner.propose` | `migration/imported/sda/astra-one-v0.2.0/astra_one/planner.py:59` | external or network access; filesystem access; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.runner.Progress` | `migration/imported/sda/astra-one-v0.2.0/astra_one/runner.py:35` | external or network access; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.runner.Progress.__init__` | `migration/imported/sda/astra-one-v0.2.0/astra_one/runner.py:36` | security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.runner.Progress.flush` | `migration/imported/sda/astra-one-v0.2.0/astra_one/runner.py:43` | external or network access; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.runner.publish_manual_state` | `migration/imported/sda/astra-one-v0.2.0/astra_one/runner.py:67` | database or query access; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.runner.build_prompt` | `migration/imported/sda/astra-one-v0.2.0/astra_one/runner.py:77` | security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.runner.create_worktree` | `migration/imported/sda/astra-one-v0.2.0/astra_one/runner.py:96` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.runner.changes_and_qc` | `migration/imported/sda/astra-one-v0.2.0/astra_one/runner.py:125` | command or process execution; security or trust-boundary vocabulary |
| `imported.sda.astra_one_v0.2.0.astra_one.runner.execute_claim` | `migration/imported/sda/astra-one-v0.2.0/astra_one/runner.py:153` | command or process execution; database or query access; security or trust-boundary vocabulary |
| `index.get` | `migration/imported/sda/astra-one-v0.2.0/cloudflare/astra-one-monitor/src/index.ts:51` | external or network access; security or trust-boundary vocabulary |
| `index.authorized` | `migration/imported/sda/astra-one-v0.2.0/cloudflare/astra-one-monitor/src/index.ts:91` | security or trust-boundary vocabulary |
| `worker.test.call` | `migration/imported/sda/astra-one-v0.2.0/cloudflare/astra-one-monitor/tests/worker.test.mjs:38` | security or trust-boundary vocabulary |
| `test_core.git` | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:17` | command or process execution; security or trust-boundary vocabulary |
| `test_core.AstraTests` | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:21` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core.AstraTests.setUp` | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:22` | filesystem access; security or trust-boundary vocabulary |
| `test_core.AstraTests.architecture` | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:40` | filesystem access |
| `test_core.AstraTests.test_refuse_dirty_source` | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:61` | filesystem access |
| `test_core.AstraTests.test_architecture_requires_approval` | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:66` | filesystem access |
| `test_core.AstraTests.test_wrong_architecture_sha_denied` | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:73` | filesystem access |
| `test_core.AstraTests.test_task_rejects_unexpected_secret_field` | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:85` | security or trust-boundary vocabulary |
| `test_core.AstraTests.test_pause_prevents_claim` | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:115` | security or trust-boundary vocabulary |
| `test_core.AstraTests.test_stop_prevents_claim` | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:120` | security or trust-boundary vocabulary |
| `test_core.AstraTests.test_architecture_replacement_pauses` | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:125` | filesystem access; security or trust-boundary vocabulary |
| `test_core.AstraTests.test_qc_rejects_deletion` | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:179` | filesystem access |
| `test_core.AstraTests.test_qc_rejects_python_syntax` | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:185` | filesystem access |
| `test_core.AstraTests.test_qc_passes_python_syntax` | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:191` | filesystem access |
| `test_core.AstraTests.test_reviewed_candidate_integrates_only_to_local_feature` | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:197` | filesystem access |
| `test_core.AstraTests.test_integration_rejects_unapproved` | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:218` | security or trust-boundary vocabulary |
| `test_core.AstraTests.test_cloudflare_schema_valid_sqlite` | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:247` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_linux_sda.git_repo` | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:16` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests` | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:30` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.setUp` | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:31` | filesystem access; security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_source_dirty_refused` | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:43` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_architecture_approval_explicit` | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:48` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_stop_and_pause_gate` | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:62` | filesystem access; security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_task_rejects_unknown_fields` | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:82` | security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_static_change_accepts_valid_python` | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:93` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_static_change_rejects_delete` | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:98` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_static_change_rejects_policy` | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:110` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_static_change_rejects_invalid_python` | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:116` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_merger_safe_serial_integration` | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:142` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_architecture_change_invalidates_old_queued_tasks` | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:164` | filesystem access |
| `test_linux_sda.LinuxSDATests.test_full_codex_pipeline_mocked_five_tasks` | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:174` | filesystem access; security or trust-boundary vocabulary |
| `test_linux_sda.LinuxSDATests.test_event_metadata_schema` | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:202` | database or query access |
| `imported.sda.codex_workhorse_v2.git` | `migration/imported/sda/codex_workhorse_v2.py:51` | command or process execution; security or trust-boundary vocabulary |
| `imported.sda.codex_workhorse_v2.proc_identity` | `migration/imported/sda/codex_workhorse_v2.py:58` | filesystem access; security or trust-boundary vocabulary |
| `imported.sda.codex_workhorse_v2.codex_events` | `migration/imported/sda/codex_workhorse_v2.py:72` | filesystem access; security or trust-boundary vocabulary |
| `imported.sda.codex_workhorse_v2.quota_in_log` | `migration/imported/sda/codex_workhorse_v2.py:125` | filesystem access; security or trust-boundary vocabulary |
| `imported.sda.codex_workhorse_v2.parent_checked` | `migration/imported/sda/codex_workhorse_v2.py:132` | security or trust-boundary vocabulary |
| `imported.sda.codex_workhorse_v2.deleted_sources_logged` | `migration/imported/sda/codex_workhorse_v2.py:139` | security or trust-boundary vocabulary |
| `imported.sda.codex_workhorse_v2.tests_pass` | `migration/imported/sda/codex_workhorse_v2.py:174` | command or process execution; security or trust-boundary vocabulary |
| `imported.sda.codex_workhorse_v2.Master` | `migration/imported/sda/codex_workhorse_v2.py:193` | command or process execution; database or query access; external or network access; filesystem access; security or trust-boundary vocabulary |
| `imported.sda.codex_workhorse_v2.Master.__init__` | `migration/imported/sda/codex_workhorse_v2.py:194` | command or process execution; database or query access; security or trust-boundary vocabulary |
| `imported.sda.codex_workhorse_v2.Master.rows` | `migration/imported/sda/codex_workhorse_v2.py:268` | database or query access; security or trust-boundary vocabulary |
| `imported.sda.codex_workhorse_v2.Master.job` | `migration/imported/sda/codex_workhorse_v2.py:271` | database or query access |
| `imported.sda.codex_workhorse_v2.Master.update` | `migration/imported/sda/codex_workhorse_v2.py:277` | database or query access; security or trust-boundary vocabulary |
| `imported.sda.codex_workhorse_v2.Master.event` | `migration/imported/sda/codex_workhorse_v2.py:285` | database or query access |
| `imported.sda.codex_workhorse_v2.Master.ingest_submissions` | `migration/imported/sda/codex_workhorse_v2.py:291` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `imported.sda.codex_workhorse_v2.Master.archive_submission` | `migration/imported/sda/codex_workhorse_v2.py:343` | database or query access; security or trust-boundary vocabulary |
| `imported.sda.codex_workhorse_v2.Master.ingest` | `migration/imported/sda/codex_workhorse_v2.py:351` | database or query access |
| `imported.sda.codex_workhorse_v2.Master.validate` | `migration/imported/sda/codex_workhorse_v2.py:363` | filesystem access; security or trust-boundary vocabulary |
| `imported.sda.codex_workhorse_v2.Master.pick` | `migration/imported/sda/codex_workhorse_v2.py:384` | database or query access |
| `imported.sda.codex_workhorse_v2.Master.prepare_worker` | `migration/imported/sda/codex_workhorse_v2.py:393` | filesystem access; security or trust-boundary vocabulary |
| `imported.sda.codex_workhorse_v2.Master.prompt` | `migration/imported/sda/codex_workhorse_v2.py:409` | database or query access; security or trust-boundary vocabulary |
| `imported.sda.codex_workhorse_v2.Master.spawn` | `migration/imported/sda/codex_workhorse_v2.py:443` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `imported.sda.codex_workhorse_v2.Master.start_worker` | `migration/imported/sda/codex_workhorse_v2.py:467` | filesystem access; security or trust-boundary vocabulary |
| `imported.sda.codex_workhorse_v2.Master.start_role` | `migration/imported/sda/codex_workhorse_v2.py:473` | database or query access; security or trust-boundary vocabulary |
| `imported.sda.codex_workhorse_v2.Master.saved_usage` | `migration/imported/sda/codex_workhorse_v2.py:489` | database or query access |
| `imported.sda.codex_workhorse_v2.Master.finish_worker` | `migration/imported/sda/codex_workhorse_v2.py:508` | filesystem access; security or trust-boundary vocabulary |
| `imported.sda.codex_workhorse_v2.Master.finish_repairer` | `migration/imported/sda/codex_workhorse_v2.py:533` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `imported.sda.codex_workhorse_v2.Master.setup_merge` | `migration/imported/sda/codex_workhorse_v2.py:578` | filesystem access; security or trust-boundary vocabulary |
| `imported.sda.codex_workhorse_v2.Master.finish_merger` | `migration/imported/sda/codex_workhorse_v2.py:594` | command or process execution; external or network access; filesystem access; security or trust-boundary vocabulary |
| `imported.sda.codex_workhorse_v2.Master.accept_integration` | `migration/imported/sda/codex_workhorse_v2.py:648` | filesystem access; security or trust-boundary vocabulary |
| `imported.sda.codex_workhorse_v2.Master.retire_branch` | `migration/imported/sda/codex_workhorse_v2.py:680` | filesystem access; security or trust-boundary vocabulary |
| `imported.sda.codex_workhorse_v2.Master.rebuild` | `migration/imported/sda/codex_workhorse_v2.py:696` | database or query access; filesystem access |
| `imported.sda.codex_workhorse_v2.Master.checkpoint_push` | `migration/imported/sda/codex_workhorse_v2.py:771` | command or process execution; security or trust-boundary vocabulary |
| `imported.sda.codex_workhorse_v2.Master.reap` | `migration/imported/sda/codex_workhorse_v2.py:804` | database or query access |
| `imported.sda.codex_workhorse_v2.Master.dispatch` | `migration/imported/sda/codex_workhorse_v2.py:816` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `imported.sda.codex_workhorse_v2.Master.pause_quota` | `migration/imported/sda/codex_workhorse_v2.py:847` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `imported.sda.codex_workhorse_v2.Master.archive_marker` | `migration/imported/sda/codex_workhorse_v2.py:876` | security or trust-boundary vocabulary |
| `imported.sda.codex_workhorse_v2.Master.resume_quota` | `migration/imported/sda/codex_workhorse_v2.py:889` | security or trust-boundary vocabulary |
| `imported.sda.codex_workhorse_v2.Master.stop_children` | `migration/imported/sda/codex_workhorse_v2.py:920` | database or query access |
| `imported.sda.codex_workhorse_v2.Master.run` | `migration/imported/sda/codex_workhorse_v2.py:940` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `imported.sda.codex_workhorse_v2.dashboard` | `migration/imported/sda/codex_workhorse_v2.py:993` | database or query access; security or trust-boundary vocabulary |
| `imported.sda.codex_workhorse_v2.cli` | `migration/imported/sda/codex_workhorse_v2.py:1031` | filesystem access; security or trust-boundary vocabulary |
| `imported.sda.workhorse_context.run_git` | `migration/imported/sda/workhorse_context.py:32` | command or process execution; security or trust-boundary vocabulary |
| `imported.sda.workhorse_context.allowed` | `migration/imported/sda/workhorse_context.py:39` | filesystem access; security or trust-boundary vocabulary |
| `imported.sda.workhorse_context.connect` | `migration/imported/sda/workhorse_context.py:77` | database or query access; security or trust-boundary vocabulary |
| `imported.sda.workhorse_context.update_index` | `migration/imported/sda/workhorse_context.py:100` | database or query access; security or trust-boundary vocabulary |
| `imported.sda.workhorse_context.purge` | `migration/imported/sda/workhorse_context.py:133` | database or query access; security or trust-boundary vocabulary |
| `imported.sda.workhorse_context.embed` | `migration/imported/sda/workhorse_context.py:141` | security or trust-boundary vocabulary |
| `imported.sda.workhorse_context.query_words` | `migration/imported/sda/workhorse_context.py:164` | security or trust-boundary vocabulary |
| `imported.sda.workhorse_context.rank` | `migration/imported/sda/workhorse_context.py:171` | database or query access; security or trust-boundary vocabulary |
| `imported.sda.workhorse_context.requirement` | `migration/imported/sda/workhorse_context.py:240` | security or trust-boundary vocabulary |
| `imported.sda.workhorse_context.verified_memory` | `migration/imported/sda/workhorse_context.py:252` | command or process execution; database or query access; security or trust-boundary vocabulary |
| `imported.sda.workhorse_context.record_verified_merge` | `migration/imported/sda/workhorse_context.py:273` | database or query access; security or trust-boundary vocabulary |
| `imported.sda.workhorse_context.packet` | `migration/imported/sda/workhorse_context.py:283` | security or trust-boundary vocabulary |
| `imported.sda.workhorse_context.optimize_prompt` | `migration/imported/sda/workhorse_context.py:325` | database or query access; security or trust-boundary vocabulary |
| `imported.sda.workhorse_context.main` | `migration/imported/sda/workhorse_context.py:345` | security or trust-boundary vocabulary |
| `imported.tws.aurelia3d.build_portable.GLB` | `migration/imported/tws/aurelia3d/build_portable.py:46` | filesystem access; security or trust-boundary vocabulary |
| `imported.tws.aurelia3d.build_portable.GLB.save` | `migration/imported/tws/aurelia3d/build_portable.py:152` | filesystem access; security or trust-boundary vocabulary |
| `imported.tws.aurelia3d.build_portable.build` | `migration/imported/tws/aurelia3d/build_portable.py:273` | filesystem access; security or trust-boundary vocabulary |
| `imported.tws.aurelia3d.build_portable.main` | `migration/imported/tws/aurelia3d/build_portable.py:425` | filesystem access; security or trust-boundary vocabulary |
| `imported.tws.engine.connect` | `migration/imported/tws/engine.py:16` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `imported.tws.engine.connect_readonly` | `migration/imported/tws/engine.py:49` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `imported.tws.engine.initialize` | `migration/imported/tws/engine.py:60` | database or query access |
| `imported.tws.engine.status` | `migration/imported/tws/engine.py:68` | database or query access |
| `imported.tws.engine.companion` | `migration/imported/tws/engine.py:74` | database or query access |
| `imported.tws.engine.quests` | `migration/imported/tws/engine.py:80` | database or query access |
| `imported.tws.engine.accept` | `migration/imported/tws/engine.py:83` | database or query access |
| `imported.tws.engine.submit` | `migration/imported/tws/engine.py:89` | database or query access |
| `imported.tws.engine.complete` | `migration/imported/tws/engine.py:97` | database or query access |
| `imported.tws.engine.next_story` | `migration/imported/tws/engine.py:117` | database or query access |
| `imported.tws.evidence.migrate` | `migration/imported/tws/evidence.py:9` | database or query access |
| `imported.tws.evidence.submit` | `migration/imported/tws/evidence.py:19` | database or query access |
| `imported.tws.evidence.review` | `migration/imported/tws/evidence.py:31` | database or query access |
| `imported.tws.evidence.verified_count` | `migration/imported/tws/evidence.py:40` | database or query access |
| `jarvis_v2.automation.device_registry.AuthenticatedDeviceRegistry` | `src/jarvis_v2/automation/device_registry.py:81` | security or trust-boundary vocabulary |
| `jarvis_v2.automation.device_registry.AuthenticatedDeviceRegistry.authenticate` | `src/jarvis_v2/automation/device_registry.py:132` | security or trust-boundary vocabulary |
| `jarvis_v2.automation.device_registry.AuthenticatedDeviceRegistry.rotate_key` | `src/jarvis_v2/automation/device_registry.py:143` | security or trust-boundary vocabulary |
| `jarvis_v2.automation.queue_api.detect_schema` | `src/jarvis_v2/automation/queue_api.py:113` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.automation.queue_api.CoordinatorQueue` | `src/jarvis_v2/automation/queue_api.py:133` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.automation.queue_api.CoordinatorQueue.__init__` | `src/jarvis_v2/automation/queue_api.py:136` | database or query access |
| `jarvis_v2.automation.queue_api.CoordinatorQueue.open` | `src/jarvis_v2/automation/queue_api.py:154` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.automation.queue_api.CoordinatorQueue.enqueue` | `src/jarvis_v2/automation/queue_api.py:159` | database or query access |
| `jarvis_v2.automation.queue_api.CoordinatorQueue._requeue_expired` | `src/jarvis_v2/automation/queue_api.py:175` | database or query access |
| `jarvis_v2.automation.queue_api.CoordinatorQueue.lease_next` | `src/jarvis_v2/automation/queue_api.py:192` | database or query access |
| `jarvis_v2.automation.queue_api.CoordinatorQueue.release` | `src/jarvis_v2/automation/queue_api.py:219` | database or query access |
| `jarvis_v2.automation.queue_api.CoordinatorQueue.renew` | `src/jarvis_v2/automation/queue_api.py:237` | database or query access |
| `jarvis_v2.automation.queue_api.CoordinatorQueue.complete` | `src/jarvis_v2/automation/queue_api.py:256` | database or query access |
| `jarvis_v2.automation.queue_api.CoordinatorQueue.control_status` | `src/jarvis_v2/automation/queue_api.py:281` | security or trust-boundary vocabulary |
| `jarvis_v2.automation.recovery_drill.RecoveryDrill` | `src/jarvis_v2/automation/recovery_drill.py:15` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.automation.recovery_drill.RecoveryDrill.__init__` | `src/jarvis_v2/automation/recovery_drill.py:18` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.automation.recovery_drill.RecoveryDrill.backup` | `src/jarvis_v2/automation/recovery_drill.py:29` | security or trust-boundary vocabulary |
| `jarvis_v2.automation.recovery_drill.RecoveryDrill.restore` | `src/jarvis_v2/automation/recovery_drill.py:33` | security or trust-boundary vocabulary |
| `jarvis_v2.automation.scheduler.AutomationScheduleStore` | `src/jarvis_v2/automation/scheduler.py:16` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.automation.scheduler.AutomationScheduleStore.__init__` | `src/jarvis_v2/automation/scheduler.py:19` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.authorization.AuthorizationError` | `src/jarvis_v2/backend/authorization.py:23` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.authorization._scope_set` | `src/jarvis_v2/backend/authorization.py:33` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.authorization.OwnerApproval` | `src/jarvis_v2/backend/authorization.py:66` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.authorization.OwnerApproval.for_grant` | `src/jarvis_v2/backend/authorization.py:77` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.authorization.AuthorizationServer` | `src/jarvis_v2/backend/authorization.py:111` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.authorization.AuthorizationServer.grant` | `src/jarvis_v2/backend/authorization.py:132` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.authorization.AuthorizationServer.authorize` | `src/jarvis_v2/backend/authorization.py:166` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.authorization.AuthorizationServer.require` | `src/jarvis_v2/backend/authorization.py:189` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.authorization.AuthorizationServer._check_approval` | `src/jarvis_v2/backend/authorization.py:217` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.backup._path` | `src/jarvis_v2/backend/backup.py:79` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.backup._same_path` | `src/jarvis_v2/backend/backup.py:85` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.backup._sha256` | `src/jarvis_v2/backend/backup.py:89` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.backup._bounded_bytes` | `src/jarvis_v2/backend/backup.py:97` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.backup._sqlite_uri` | `src/jarvis_v2/backend/backup.py:104` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.backup._sidecar` | `src/jarvis_v2/backend/backup.py:108` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.backup._unseal` | `src/jarvis_v2/backend/backup.py:129` | filesystem access |
| `jarvis_v2.backend.backup._exclusive_write` | `src/jarvis_v2/backend/backup.py:139` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.backup.BackupManager` | `src/jarvis_v2/backend/backup.py:155` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.backup.BackupManager.inspect` | `src/jarvis_v2/backend/backup.py:163` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.backup.BackupManager._copy_sqlite` | `src/jarvis_v2/backend/backup.py:213` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.backup.BackupManager.create` | `src/jarvis_v2/backend/backup.py:231` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.backup.BackupManager.restore` | `src/jarvis_v2/backend/backup.py:285` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.cloudflare_jobs.CloudflareJobRecord` | `src/jarvis_v2/backend/cloudflare_jobs.py:40` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.cloudflare_jobs.CloudflareJobRecord.from_payload` | `src/jarvis_v2/backend/cloudflare_jobs.py:57` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.cloudflare_jobs.CloudflareJobAdapter` | `src/jarvis_v2/backend/cloudflare_jobs.py:93` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.cloudflare_jobs.CloudflareJobAdapter.__init__` | `src/jarvis_v2/backend/cloudflare_jobs.py:100` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.cloudflare_jobs.CloudflareJobAdapter._call` | `src/jarvis_v2/backend/cloudflare_jobs.py:166` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.code_index._path` | `src/jarvis_v2/backend/code_index.py:41` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.code_index._language` | `src/jarvis_v2/backend/code_index.py:68` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.code_index._sensitive` | `src/jarvis_v2/backend/code_index.py:75` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.code_index._symbols` | `src/jarvis_v2/backend/code_index.py:79` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.code_index.RepositoryIndex` | `src/jarvis_v2/backend/code_index.py:106` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.code_index.RepositoryIndex.__init__` | `src/jarvis_v2/backend/code_index.py:109` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.code_index.RepositoryIndex.index_file` | `src/jarvis_v2/backend/code_index.py:160` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.code_index.RepositoryIndex.search` | `src/jarvis_v2/backend/code_index.py:225` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.code_index.RepositoryIndex.symbols` | `src/jarvis_v2/backend/code_index.py:248` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.connectors._scopes` | `src/jarvis_v2/backend/connectors.py:36` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.connectors.ConnectorGrant` | `src/jarvis_v2/backend/connectors.py:51` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.connectors.ConnectorBroker` | `src/jarvis_v2/backend/connectors.py:65` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.connectors.ConnectorBroker.grant` | `src/jarvis_v2/backend/connectors.py:77` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.connectors.ConnectorBroker.authorize` | `src/jarvis_v2/backend/connectors.py:116` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.connectors.ConnectorBroker.require` | `src/jarvis_v2/backend/connectors.py:140` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.connectors.ConnectorBroker.grants` | `src/jarvis_v2/backend/connectors.py:180` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.context.estimate_tokens` | `src/jarvis_v2/backend/context.py:22` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.context.ContextPacker` | `src/jarvis_v2/backend/context.py:62` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.context.ContextPacker.pack` | `src/jarvis_v2/backend/context.py:69` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.context.ContextPacker._validate_budget` | `src/jarvis_v2/backend/context.py:139` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.conversation.ConversationStore` | `src/jarvis_v2/backend/conversation.py:80` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.conversation.ConversationStore.__init__` | `src/jarvis_v2/backend/conversation.py:89` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.conversation.ConversationStore.create_conversation` | `src/jarvis_v2/backend/conversation.py:136` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.conversation.ConversationStore.open_conversation` | `src/jarvis_v2/backend/conversation.py:175` | database or query access; filesystem access |
| `jarvis_v2.backend.conversation.ConversationStore.append_turn` | `src/jarvis_v2/backend/conversation.py:191` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.conversation.ConversationStore.get_conversation` | `src/jarvis_v2/backend/conversation.py:265` | database or query access |
| `jarvis_v2.backend.conversation.ConversationStore.list_turns` | `src/jarvis_v2/backend/conversation.py:274` | database or query access |
| `jarvis_v2.backend.conversation.ConversationStore._same_turn` | `src/jarvis_v2/backend/conversation.py:289` | database or query access |
| `jarvis_v2.backend.conversation.ConversationStore._turn` | `src/jarvis_v2/backend/conversation.py:306` | database or query access |
| `jarvis_v2.backend.conversation.ConversationStore._conversation` | `src/jarvis_v2/backend/conversation.py:326` | database or query access |
| `jarvis_v2.backend.effects.EffectJournal` | `src/jarvis_v2/backend/effects.py:52` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.effects.EffectJournal.__init__` | `src/jarvis_v2/backend/effects.py:59` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.effects.EffectJournal.prepare` | `src/jarvis_v2/backend/effects.py:93` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.effects.EffectJournal.reconcile_pending` | `src/jarvis_v2/backend/effects.py:158` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.effects.EffectJournal.get` | `src/jarvis_v2/backend/effects.py:174` | database or query access |
| `jarvis_v2.backend.effects.EffectJournal.pending` | `src/jarvis_v2/backend/effects.py:183` | database or query access |
| `jarvis_v2.backend.effects.EffectJournal._finish` | `src/jarvis_v2/backend/effects.py:192` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.effects.EffectJournal._check_identity` | `src/jarvis_v2/backend/effects.py:236` | database or query access |
| `jarvis_v2.backend.effects.EffectJournal._snapshot` | `src/jarvis_v2/backend/effects.py:252` | database or query access |
| `jarvis_v2.backend.event_bus.DeliveryInProgress` | `src/jarvis_v2/backend/event_bus.py:28` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.event_bus.EventBus` | `src/jarvis_v2/backend/event_bus.py:114` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.event_bus.EventBus.__init__` | `src/jarvis_v2/backend/event_bus.py:117` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.event_bus.EventBus.publish` | `src/jarvis_v2/backend/event_bus.py:131` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.event_bus.EventBus.pending` | `src/jarvis_v2/backend/event_bus.py:213` | database or query access |
| `jarvis_v2.backend.event_bus.EventBus.deliver` | `src/jarvis_v2/backend/event_bus.py:227` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.event_bus.EventBus._event` | `src/jarvis_v2/backend/event_bus.py:323` | database or query access |
| `jarvis_v2.backend.event_bus.EventBus._receipt` | `src/jarvis_v2/backend/event_bus.py:339` | database or query access |
| `jarvis_v2.backend.generation_scheduler.GenerationRequest` | `src/jarvis_v2/backend/generation_scheduler.py:19` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.generation_scheduler.GenerationLease` | `src/jarvis_v2/backend/generation_scheduler.py:30` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.generation_scheduler.GenerationScheduler` | `src/jarvis_v2/backend/generation_scheduler.py:41` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.generation_scheduler.GenerationScheduler.submit` | `src/jarvis_v2/backend/generation_scheduler.py:68` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.generation_scheduler.GenerationScheduler.claim_next` | `src/jarvis_v2/backend/generation_scheduler.py:84` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.handoff._scopes` | `src/jarvis_v2/backend/handoff.py:41` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.handoff.HandoffStore` | `src/jarvis_v2/backend/handoff.py:75` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.handoff.HandoffStore.__init__` | `src/jarvis_v2/backend/handoff.py:78` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.handoff.HandoffStore.handoff` | `src/jarvis_v2/backend/handoff.py:108` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.handoff.HandoffStore.get` | `src/jarvis_v2/backend/handoff.py:175` | database or query access |
| `jarvis_v2.backend.handoff.HandoffStore.list_for_task` | `src/jarvis_v2/backend/handoff.py:184` | database or query access |
| `jarvis_v2.backend.handoff.HandoffStore._snapshot` | `src/jarvis_v2/backend/handoff.py:195` | database or query access |
| `jarvis_v2.backend.linux_service.LinuxServiceProfile` | `src/jarvis_v2/backend/linux_service.py:26` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.linux_service.LinuxServiceProfile.__post_init__` | `src/jarvis_v2/backend/linux_service.py:34` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.linux_service.LinuxServiceProfile.render` | `src/jarvis_v2/backend/linux_service.py:51` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.module_manifest.validate_module_manifest` | `src/jarvis_v2/backend/module_manifest.py:93` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.ollama_profile.OllamaTelemetry` | `src/jarvis_v2/backend/ollama_profile.py:121` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.ollama_profile.OllamaTelemetry.__post_init__` | `src/jarvis_v2/backend/ollama_profile.py:135` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.provider_registry.ProviderRequirements` | `src/jarvis_v2/backend/provider_registry.py:69` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.provider_registry.ProviderRequirements.__post_init__` | `src/jarvis_v2/backend/provider_registry.py:80` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.provider_registry.ProviderRegistry` | `src/jarvis_v2/backend/provider_registry.py:110` | database or query access |
| `jarvis_v2.backend.retrieval.DocumentStore` | `src/jarvis_v2/backend/retrieval.py:42` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.retrieval.DocumentStore.__init__` | `src/jarvis_v2/backend/retrieval.py:45` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.retrieval.DocumentStore.add_document` | `src/jarvis_v2/backend/retrieval.py:88` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.retrieval.DocumentStore.search` | `src/jarvis_v2/backend/retrieval.py:176` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.retrieval.DocumentStore.get` | `src/jarvis_v2/backend/retrieval.py:220` | database or query access |
| `jarvis_v2.backend.retrieval.DocumentStore._snapshot` | `src/jarvis_v2/backend/retrieval.py:230` | database or query access |
| `jarvis_v2.backend.routing.CircuitState` | `src/jarvis_v2/backend/routing.py:26` | filesystem access |
| `jarvis_v2.backend.routing.CircuitBreaker` | `src/jarvis_v2/backend/routing.py:59` | filesystem access |
| `jarvis_v2.backend.scheduler.ReminderScheduler` | `src/jarvis_v2/backend/scheduler.py:140` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.scheduler.ReminderScheduler.__init__` | `src/jarvis_v2/backend/scheduler.py:143` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.scheduler.ReminderScheduler.get` | `src/jarvis_v2/backend/scheduler.py:221` | database or query access |
| `jarvis_v2.backend.scheduler.ReminderScheduler.due_reminders` | `src/jarvis_v2/backend/scheduler.py:229` | database or query access |
| `jarvis_v2.backend.scheduler.ReminderScheduler.acknowledge` | `src/jarvis_v2/backend/scheduler.py:242` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.scheduler.ReminderScheduler.cancel` | `src/jarvis_v2/backend/scheduler.py:282` | database or query access |
| `jarvis_v2.backend.scheduler.ReminderScheduler._insert` | `src/jarvis_v2/backend/scheduler.py:301` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.scheduler.ReminderScheduler._snapshot` | `src/jarvis_v2/backend/scheduler.py:347` | database or query access |
| `jarvis_v2.backend.secrets.SecretBoundaryError` | `src/jarvis_v2/backend/secrets.py:16` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.secrets._name` | `src/jarvis_v2/backend/secrets.py:24` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.secrets._names` | `src/jarvis_v2/backend/secrets.py:30` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.secrets.SecretStore` | `src/jarvis_v2/backend/secrets.py:68` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.secrets.SecretStore.__init__` | `src/jarvis_v2/backend/secrets.py:71` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.secrets.SecretStore.get` | `src/jarvis_v2/backend/secrets.py:97` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.storage.ModuleStore` | `src/jarvis_v2/backend/storage.py:101` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.storage.ModuleStore.__init__` | `src/jarvis_v2/backend/storage.py:104` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.storage.StorageManager` | `src/jarvis_v2/backend/storage.py:117` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.storage.StorageManager.__init__` | `src/jarvis_v2/backend/storage.py:120` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.storage.StorageManager._validate_plan` | `src/jarvis_v2/backend/storage.py:148` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.storage.StorageManager._bootstrap` | `src/jarvis_v2/backend/storage.py:184` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.storage.StorageManager._applied` | `src/jarvis_v2/backend/storage.py:217` | database or query access |
| `jarvis_v2.backend.storage.StorageManager._validate_applied` | `src/jarvis_v2/backend/storage.py:232` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.storage.StorageManager._integrity_check` | `src/jarvis_v2/backend/storage.py:245` | database or query access |
| `jarvis_v2.backend.storage.StorageManager._table_exists` | `src/jarvis_v2/backend/storage.py:250` | database or query access |
| `jarvis_v2.backend.storage.StorageManager._apply_one` | `src/jarvis_v2/backend/storage.py:255` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.storage.StorageManager.rollback` | `src/jarvis_v2/backend/storage.py:305` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.storage.StorageManager.applied_migrations` | `src/jarvis_v2/backend/storage.py:351` | database or query access |
| `jarvis_v2.backend.storage.StorageManager.table_owner` | `src/jarvis_v2/backend/storage.py:358` | database or query access |
| `jarvis_v2.backend.storage.StorageManager._assert_owner` | `src/jarvis_v2/backend/storage.py:366` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.storage.StorageManager.insert` | `src/jarvis_v2/backend/storage.py:377` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.storage.StorageManager.rows` | `src/jarvis_v2/backend/storage.py:397` | database or query access |
| `jarvis_v2.backend.task_capability._paths` | `src/jarvis_v2/backend/task_capability.py:23` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.task_capability.TaskCapabilityManifest` | `src/jarvis_v2/backend/task_capability.py:49` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.task_capability.TaskCapabilityManifest.create` | `src/jarvis_v2/backend/task_capability.py:66` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.task_capability.TaskCapabilityManifest.as_dict` | `src/jarvis_v2/backend/task_capability.py:75` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.task_capability.TaskCapabilityManifest.validate_path` | `src/jarvis_v2/backend/task_capability.py:82` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.backend.task_capability.ValidatedTaskRequest` | `src/jarvis_v2/backend/task_capability.py:107` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.task_capability.validate_task_request` | `src/jarvis_v2/backend/task_capability.py:115` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.windows_agent.LocalAgentJob` | `src/jarvis_v2/backend/windows_agent.py:99` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.windows_agent.LocalAgentJob.__post_init__` | `src/jarvis_v2/backend/windows_agent.py:111` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.windows_agent.WindowsAgentRegistry` | `src/jarvis_v2/backend/windows_agent.py:143` | security or trust-boundary vocabulary |
| `jarvis_v2.backend.windows_agent.WindowsAgentRegistry.route` | `src/jarvis_v2/backend/windows_agent.py:193` | security or trust-boundary vocabulary |
| `jarvis_v2.cli.main` | `src/jarvis_v2/cli.py:13` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.core.budget.ResourceBudgetError` | `src/jarvis_v2/core/budget.py:10` | security or trust-boundary vocabulary |
| `jarvis_v2.core.budget.ResourceBudget` | `src/jarvis_v2/core/budget.py:14` | security or trust-boundary vocabulary |
| `jarvis_v2.core.budget.ResourceBudget.held_slots` | `src/jarvis_v2/core/budget.py:65` | security or trust-boundary vocabulary |
| `jarvis_v2.core.budget.ResourceBudget.claim` | `src/jarvis_v2/core/budget.py:81` | security or trust-boundary vocabulary |
| `jarvis_v2.core.budget.ResourceBudget.finish` | `src/jarvis_v2/core/budget.py:102` | security or trust-boundary vocabulary |
| `jarvis_v2.core.budget.ResourceBudget._validate_owner` | `src/jarvis_v2/core/budget.py:113` | security or trust-boundary vocabulary |
| `jarvis_v2.core.control.CoreControls` | `src/jarvis_v2/core/control.py:22` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.core.control.CoreControls.__init__` | `src/jarvis_v2/core/control.py:25` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.core.control.CoreControls.status` | `src/jarvis_v2/core/control.py:44` | database or query access |
| `jarvis_v2.core.control.CoreControls.stop` | `src/jarvis_v2/core/control.py:55` | security or trust-boundary vocabulary |
| `jarvis_v2.core.control.CoreControls.pause` | `src/jarvis_v2/core/control.py:58` | security or trust-boundary vocabulary |
| `jarvis_v2.core.control.CoreControls._set` | `src/jarvis_v2/core/control.py:64` | database or query access |
| `jarvis_v2.core.dependency.DependencyOrchestrator` | `src/jarvis_v2/core/dependency.py:13` | database or query access |
| `jarvis_v2.core.dependency.DependencyOrchestrator.__init__` | `src/jarvis_v2/core/dependency.py:16` | database or query access |
| `jarvis_v2.core.dependency.DependencyOrchestrator.ready` | `src/jarvis_v2/core/dependency.py:35` | database or query access |
| `jarvis_v2.core.dependency.DependencyOrchestrator.dependent_ids` | `src/jarvis_v2/core/dependency.py:51` | database or query access |
| `jarvis_v2.core.dispatch.DispatchError` | `src/jarvis_v2/core/dispatch.py:19` | security or trust-boundary vocabulary |
| `jarvis_v2.core.dispatch._encode` | `src/jarvis_v2/core/dispatch.py:35` | security or trust-boundary vocabulary |
| `jarvis_v2.core.dispatch.DispatchStore` | `src/jarvis_v2/core/dispatch.py:59` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.core.dispatch.DispatchStore.__init__` | `src/jarvis_v2/core/dispatch.py:62` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.core.dispatch.DispatchStore.create` | `src/jarvis_v2/core/dispatch.py:97` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.core.dispatch.DispatchStore.claim` | `src/jarvis_v2/core/dispatch.py:144` | database or query access |
| `jarvis_v2.core.dispatch.DispatchStore.acknowledge` | `src/jarvis_v2/core/dispatch.py:169` | database or query access |
| `jarvis_v2.core.dispatch.DispatchStore.get` | `src/jarvis_v2/core/dispatch.py:218` | database or query access |
| `jarvis_v2.core.dispatch.DispatchStore._snapshot` | `src/jarvis_v2/core/dispatch.py:225` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.core.event_session.EventSessionInterpreter` | `src/jarvis_v2/core/event_session.py:34` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.core.event_session.EventSessionInterpreter.__init__` | `src/jarvis_v2/core/event_session.py:37` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.core.event_session.EventSessionInterpreter._ensure_schema` | `src/jarvis_v2/core/event_session.py:46` | database or query access |
| `jarvis_v2.core.event_session.EventSessionInterpreter.open_session` | `src/jarvis_v2/core/event_session.py:103` | database or query access; filesystem access |
| `jarvis_v2.core.event_session.EventSessionInterpreter.emit` | `src/jarvis_v2/core/event_session.py:138` | database or query access |
| `jarvis_v2.core.event_session.EventSessionInterpreter.causal_chain` | `src/jarvis_v2/core/event_session.py:209` | database or query access |
| `jarvis_v2.core.event_session.EventSessionInterpreter.replay` | `src/jarvis_v2/core/event_session.py:219` | database or query access |
| `jarvis_v2.core.event_session.EventSessionInterpreter.ack` | `src/jarvis_v2/core/event_session.py:240` | database or query access |
| `jarvis_v2.core.event_session.EventSessionInterpreter.record_failure` | `src/jarvis_v2/core/event_session.py:252` | database or query access |
| `jarvis_v2.core.event_session.EventSessionInterpreter.failure` | `src/jarvis_v2/core/event_session.py:287` | database or query access |
| `jarvis_v2.core.event_session.EventSessionInterpreter._metadata` | `src/jarvis_v2/core/event_session.py:299` | database or query access |
| `jarvis_v2.core.event_session.EventSessionInterpreter._metadata_with_failure` | `src/jarvis_v2/core/event_session.py:311` | database or query access |
| `jarvis_v2.core.event_session.EventSessionInterpreter._failure` | `src/jarvis_v2/core/event_session.py:317` | database or query access |
| `jarvis_v2.core.intent.IntentError` | `src/jarvis_v2/core/intent.py:22` | security or trust-boundary vocabulary |
| `jarvis_v2.core.intent.OwnerIntentRouter` | `src/jarvis_v2/core/intent.py:46` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.core.intent.OwnerIntentRouter.__init__` | `src/jarvis_v2/core/intent.py:49` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.core.intent.OwnerIntentRouter.submit` | `src/jarvis_v2/core/intent.py:81` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.core.intent.OwnerIntentRouter.get` | `src/jarvis_v2/core/intent.py:132` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.core.intent.OwnerIntentRouter._safe_decision` | `src/jarvis_v2/core/intent.py:185` | security or trust-boundary vocabulary |
| `jarvis_v2.core.intent.OwnerIntentRouter._approval_decision` | `src/jarvis_v2/core/intent.py:196` | security or trust-boundary vocabulary |
| `jarvis_v2.core.intent.OwnerIntentRouter._enqueue` | `src/jarvis_v2/core/intent.py:212` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.core.intent.OwnerIntentRouter._store_approval` | `src/jarvis_v2/core/intent.py:232` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.core.intent.OwnerIntentRouter._snapshot` | `src/jarvis_v2/core/intent.py:243` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.core.queue.TaskQueue` | `src/jarvis_v2/core/queue.py:24` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.core.queue.TaskQueue.__init__` | `src/jarvis_v2/core/queue.py:25` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.core.queue.TaskQueue.add` | `src/jarvis_v2/core/queue.py:65` | database or query access |
| `jarvis_v2.core.queue.TaskQueue.block` | `src/jarvis_v2/core/queue.py:74` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.core.queue.TaskQueue.unblock` | `src/jarvis_v2/core/queue.py:98` | database or query access |
| `jarvis_v2.core.queue.TaskQueue.lease_next` | `src/jarvis_v2/core/queue.py:111` | database or query access |
| `jarvis_v2.core.queue.TaskQueue.eligible` | `src/jarvis_v2/core/queue.py:141` | database or query access |
| `jarvis_v2.core.queue.TaskQueue.finish` | `src/jarvis_v2/core/queue.py:159` | database or query access |
| `jarvis_v2.core.queue.TaskQueue.status` | `src/jarvis_v2/core/queue.py:166` | database or query access |
| `jarvis_v2.core.queue.TaskQueue.history` | `src/jarvis_v2/core/queue.py:169` | database or query access |
| `jarvis_v2.core.queue.TaskQueue.replay_events` | `src/jarvis_v2/core/queue.py:182` | database or query access |
| `jarvis_v2.core.queue.TaskQueue.ack_event` | `src/jarvis_v2/core/queue.py:197` | database or query access |
| `jarvis_v2.core.queue.TaskQueue.open_session` | `src/jarvis_v2/core/queue.py:211` | filesystem access |
| `jarvis_v2.core.queue.TaskQueue.dispatch` | `src/jarvis_v2/core/queue.py:232` | security or trust-boundary vocabulary |
| `jarvis_v2.core.queue.TaskQueue.submit_intent` | `src/jarvis_v2/core/queue.py:244` | security or trust-boundary vocabulary |
| `jarvis_v2.core.queue.TaskQueue.stop` | `src/jarvis_v2/core/queue.py:256` | security or trust-boundary vocabulary |
| `jarvis_v2.core.queue.TaskQueue.pause` | `src/jarvis_v2/core/queue.py:259` | security or trust-boundary vocabulary |
| `jarvis_v2.core.registry.ModuleRegistry` | `src/jarvis_v2/core/registry.py:32` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.core.registry.ModuleRegistry.from_config` | `src/jarvis_v2/core/registry.py:58` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.core.registry.ModuleRegistry.authorize` | `src/jarvis_v2/core/registry.py:106` | security or trust-boundary vocabulary |
| `jarvis_v2.core.registry.CoreService` | `src/jarvis_v2/core/registry.py:117` | security or trust-boundary vocabulary |
| `jarvis_v2.core.registry.CoreService.from_config` | `src/jarvis_v2/core/registry.py:123` | security or trust-boundary vocabulary |
| `jarvis_v2.core.registry.CoreService.can` | `src/jarvis_v2/core/registry.py:129` | security or trust-boundary vocabulary |
| `jarvis_v2.core.session.TaskSessionStore` | `src/jarvis_v2/core/session.py:54` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.core.session.TaskSessionStore.__init__` | `src/jarvis_v2/core/session.py:62` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.core.session.TaskSessionStore.open_session` | `src/jarvis_v2/core/session.py:100` | database or query access; filesystem access |
| `jarvis_v2.core.session.TaskSessionStore.restore_session` | `src/jarvis_v2/core/session.py:149` | database or query access |
| `jarvis_v2.core.session.TaskSessionStore.append` | `src/jarvis_v2/core/session.py:169` | database or query access |
| `jarvis_v2.core.session.TaskSessionStore.checkpoint_session` | `src/jarvis_v2/core/session.py:232` | database or query access |
| `jarvis_v2.core.session.TaskSessionStore._snapshot` | `src/jarvis_v2/core/session.py:299` | database or query access |
| `jarvis_v2.core.session.TaskSessionStore._record` | `src/jarvis_v2/core/session.py:324` | database or query access |
| `jarvis_v2.core.timeline.TaskTimeline` | `src/jarvis_v2/core/timeline.py:35` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.core.timeline.TaskTimeline.__init__` | `src/jarvis_v2/core/timeline.py:38` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.core.timeline.TaskTimeline.timeline` | `src/jarvis_v2/core/timeline.py:47` | database or query access |
| `jarvis_v2.core.timeline.TaskTimeline._event` | `src/jarvis_v2/core/timeline.py:155` | database or query access |
| `jarvis_v2.core.timeline.TaskTimeline._record` | `src/jarvis_v2/core/timeline.py:168` | database or query access |
| `jarvis_v2.core.timeline.TaskTimeline._dispatch` | `src/jarvis_v2/core/timeline.py:180` | database or query access |
| `jarvis_v2.finance.advice.FinanceRecommendation` | `src/jarvis_v2/finance/advice.py:15` | security or trust-boundary vocabulary |
| `jarvis_v2.finance.advice.FinanceRecommendation.__post_init__` | `src/jarvis_v2/finance/advice.py:26` | security or trust-boundary vocabulary |
| `jarvis_v2.finance.advice.FinanceNotification` | `src/jarvis_v2/finance/advice.py:66` | security or trust-boundary vocabulary |
| `jarvis_v2.finance.advice.FinanceNotification.__post_init__` | `src/jarvis_v2/finance/advice.py:74` | security or trust-boundary vocabulary |
| `jarvis_v2.finance.advice.FinanceAdviceService` | `src/jarvis_v2/finance/advice.py:99` | security or trust-boundary vocabulary |
| `jarvis_v2.finance.advice.FinanceAdviceService.recommendations` | `src/jarvis_v2/finance/advice.py:108` | security or trust-boundary vocabulary |
| `jarvis_v2.finance.alerts.FinanceAlert` | `src/jarvis_v2/finance/alerts.py:16` | security or trust-boundary vocabulary |
| `jarvis_v2.finance.alerts.FinanceAlert.__post_init__` | `src/jarvis_v2/finance/alerts.py:29` | security or trust-boundary vocabulary |
| `jarvis_v2.finance.alerts.FinanceAlertService` | `src/jarvis_v2/finance/alerts.py:67` | security or trust-boundary vocabulary |
| `jarvis_v2.finance.alerts.FinanceAlertService.detect` | `src/jarvis_v2/finance/alerts.py:75` | security or trust-boundary vocabulary |
| `jarvis_v2.finance.dashboard.FinanceDashboard` | `src/jarvis_v2/finance/dashboard.py:75` | security or trust-boundary vocabulary |
| `jarvis_v2.finance.dashboard.FinanceDashboard.__post_init__` | `src/jarvis_v2/finance/dashboard.py:82` | security or trust-boundary vocabulary |
| `jarvis_v2.finance.dashboard.FinanceDashboardService` | `src/jarvis_v2/finance/dashboard.py:105` | security or trust-boundary vocabulary |
| `jarvis_v2.finance.dashboard.FinanceDashboardService.snapshot` | `src/jarvis_v2/finance/dashboard.py:113` | security or trust-boundary vocabulary |
| `jarvis_v2.finance.ingestion.FinanceStore` | `src/jarvis_v2/finance/ingestion.py:287` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.finance.ingestion.FinanceStore.__init__` | `src/jarvis_v2/finance/ingestion.py:303` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.finance.ingestion.FinanceStore._create_tables` | `src/jarvis_v2/finance/ingestion.py:311` | database or query access |
| `jarvis_v2.finance.ingestion.FinanceStore.sync` | `src/jarvis_v2/finance/ingestion.py:333` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.finance.ingestion.FinanceStore._insert` | `src/jarvis_v2/finance/ingestion.py:393` | database or query access |
| `jarvis_v2.finance.ingestion.FinanceStore._update` | `src/jarvis_v2/finance/ingestion.py:399` | database or query access |
| `jarvis_v2.finance.ingestion.FinanceStore._records` | `src/jarvis_v2/finance/ingestion.py:429` | database or query access |
| `jarvis_v2.finance.ingestion.FinanceStore.accounts` | `src/jarvis_v2/finance/ingestion.py:443` | security or trust-boundary vocabulary |
| `jarvis_v2.finance.ingestion.FinanceStore.categories` | `src/jarvis_v2/finance/ingestion.py:446` | security or trust-boundary vocabulary |
| `jarvis_v2.finance.ingestion.FinanceStore.budgets` | `src/jarvis_v2/finance/ingestion.py:449` | security or trust-boundary vocabulary |
| `jarvis_v2.finance.ingestion.FinanceStore.transactions` | `src/jarvis_v2/finance/ingestion.py:452` | security or trust-boundary vocabulary |
| `jarvis_v2.finance.mira_audit.schema_sha256` | `src/jarvis_v2/finance/mira_audit.py:31` | security or trust-boundary vocabulary |
| `jarvis_v2.finance.mira_audit.MiraAuditSnapshot` | `src/jarvis_v2/finance/mira_audit.py:44` | security or trust-boundary vocabulary |
| `jarvis_v2.finance.mira_audit.MiraAuditSnapshot.validate` | `src/jarvis_v2/finance/mira_audit.py:65` | security or trust-boundary vocabulary |
| `jarvis_v2.finance.mira_connector.MiraExportToken` | `src/jarvis_v2/finance/mira_connector.py:29` | security or trust-boundary vocabulary |
| `jarvis_v2.finance.mira_connector.MiraConnectorTokenBroker` | `src/jarvis_v2/finance/mira_connector.py:38` | security or trust-boundary vocabulary |
| `jarvis_v2.finance.mira_connector.MiraConnectorTokenBroker.authorize` | `src/jarvis_v2/finance/mira_connector.py:61` | security or trust-boundary vocabulary |
| `jarvis_v2.finance.mira_connector.MiraConnectorTokenBroker.audit` | `src/jarvis_v2/finance/mira_connector.py:80` | security or trust-boundary vocabulary |
| `jarvis_v2.finance.paper.PaperFillPolicy` | `src/jarvis_v2/finance/paper.py:23` | filesystem access |
| `jarvis_v2.finance.paper.PaperFillPolicy.__post_init__` | `src/jarvis_v2/finance/paper.py:34` | filesystem access |
| `jarvis_v2.finance.paper.PaperAccount` | `src/jarvis_v2/finance/paper.py:58` | security or trust-boundary vocabulary |
| `jarvis_v2.finance.paper.PaperAccount.__post_init__` | `src/jarvis_v2/finance/paper.py:65` | security or trust-boundary vocabulary |
| `jarvis_v2.finance.paper.PaperLedger` | `src/jarvis_v2/finance/paper.py:167` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.finance.paper.PaperLedger.__init__` | `src/jarvis_v2/finance/paper.py:170` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.finance.paper.PaperLedger.open_account` | `src/jarvis_v2/finance/paper.py:214` | database or query access; filesystem access |
| `jarvis_v2.finance.paper.PaperLedger.place_order` | `src/jarvis_v2/finance/paper.py:230` | database or query access |
| `jarvis_v2.finance.paper.PaperLedger.fill_order` | `src/jarvis_v2/finance/paper.py:248` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.finance.paper.PaperLedger.account` | `src/jarvis_v2/finance/paper.py:314` | database or query access |
| `jarvis_v2.finance.paper.PaperLedger.orders` | `src/jarvis_v2/finance/paper.py:321` | database or query access |
| `jarvis_v2.finance.paper.PaperLedger.positions` | `src/jarvis_v2/finance/paper.py:325` | database or query access |
| `jarvis_v2.finance.paper.PaperLedger._account` | `src/jarvis_v2/finance/paper.py:330` | database or query access |
| `jarvis_v2.finance.paper.PaperLedger._order` | `src/jarvis_v2/finance/paper.py:334` | database or query access |
| `jarvis_v2.finance.paper.PaperLedger._position` | `src/jarvis_v2/finance/paper.py:342` | database or query access |
| `jarvis_v2.finance.performance.PaperPerformanceService` | `src/jarvis_v2/finance/performance.py:104` | filesystem access |
| `jarvis_v2.finance.performance.PaperPerformanceService.evaluate` | `src/jarvis_v2/finance/performance.py:108` | filesystem access |
| `jarvis_v2.finance.planning.FinanceForecast` | `src/jarvis_v2/finance/planning.py:50` | security or trust-boundary vocabulary |
| `jarvis_v2.finance.planning.FinanceForecast.__post_init__` | `src/jarvis_v2/finance/planning.py:60` | security or trust-boundary vocabulary |
| `jarvis_v2.finance.reconciliation.FinanceReconciliationStore` | `src/jarvis_v2/finance/reconciliation.py:142` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.finance.reconciliation.FinanceReconciliationStore.__init__` | `src/jarvis_v2/finance/reconciliation.py:145` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.finance.reconciliation.FinanceReconciliationStore.sync` | `src/jarvis_v2/finance/reconciliation.py:179` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.finance.reconciliation.FinanceReconciliationStore.operations` | `src/jarvis_v2/finance/reconciliation.py:228` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.finance.reconciliation.FinanceReconciliationStore.reconcile` | `src/jarvis_v2/finance/reconciliation.py:251` | filesystem access |
| `jarvis_v2.finance.reconciliation.FinanceReconciliationStore._insert` | `src/jarvis_v2/finance/reconciliation.py:283` | database or query access |
| `jarvis_v2.finance.reconciliation.FinanceReconciliationStore._update` | `src/jarvis_v2/finance/reconciliation.py:296` | database or query access |
| `jarvis_v2.finance.reports.FinanceReportService` | `src/jarvis_v2/finance/reports.py:67` | security or trust-boundary vocabulary |
| `jarvis_v2.finance.reports.FinanceReportService.report` | `src/jarvis_v2/finance/reports.py:75` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.controller.GuardianControllerError` | `src/jarvis_v2/guardian/controller.py:19` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.controller.TrustedControllerManager` | `src/jarvis_v2/guardian/controller.py:26` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.guardian.controller.TrustedControllerManager.__init__` | `src/jarvis_v2/guardian/controller.py:35` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.guardian.controller.TrustedControllerManager.verify` | `src/jarvis_v2/guardian/controller.py:60` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.controller.TrustedControllerManager.restart` | `src/jarvis_v2/guardian/controller.py:103` | command or process execution; security or trust-boundary vocabulary |
| `jarvis_v2.guardian.controller.TrustedControllerManager._active_markers` | `src/jarvis_v2/guardian/controller.py:119` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.controller.TrustedControllerManager._validate_command` | `src/jarvis_v2/guardian/controller.py:128` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.controller.TrustedControllerManager._spawn` | `src/jarvis_v2/guardian/controller.py:139` | command or process execution; security or trust-boundary vocabulary |
| `jarvis_v2.guardian.controller._sha256` | `src/jarvis_v2/guardian/controller.py:154` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.guardian.controller.main` | `src/jarvis_v2/guardian/controller.py:162` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.cutover.CutoverError` | `src/jarvis_v2/guardian/cutover.py:19` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.cutover.CutoverDecision` | `src/jarvis_v2/guardian/cutover.py:24` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.cutover.CutoverDecision.as_dict` | `src/jarvis_v2/guardian/cutover.py:36` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.cutover.CutoverCoordinator` | `src/jarvis_v2/guardian/cutover.py:42` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.guardian.cutover.CutoverCoordinator.__init__` | `src/jarvis_v2/guardian/cutover.py:45` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.guardian.cutover.CutoverCoordinator.prepare` | `src/jarvis_v2/guardian/cutover.py:66` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.cutover.CutoverCoordinator.cutover` | `src/jarvis_v2/guardian/cutover.py:109` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.cutover.CutoverCoordinator.failback` | `src/jarvis_v2/guardian/cutover.py:131` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.cutover.CutoverCoordinator._active_controls` | `src/jarvis_v2/guardian/cutover.py:168` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.cutover._value` | `src/jarvis_v2/guardian/cutover.py:174` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.failure.FailureClassificationError` | `src/jarvis_v2/guardian/failure.py:16` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.failure.FailureAssessment` | `src/jarvis_v2/guardian/failure.py:21` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.failure.FailureAssessment.as_dict` | `src/jarvis_v2/guardian/failure.py:34` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.failure.FailureClassifier` | `src/jarvis_v2/guardian/failure.py:45` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.failure.FailureClassifier.classify` | `src/jarvis_v2/guardian/failure.py:48` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.failure._identifier` | `src/jarvis_v2/guardian/failure.py:99` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.failure._observation` | `src/jarvis_v2/guardian/failure.py:105` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.failure._dependencies` | `src/jarvis_v2/guardian/failure.py:115` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.failure._references` | `src/jarvis_v2/guardian/failure.py:126` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.fencing.WriterFenceError` | `src/jarvis_v2/guardian/fencing.py:16` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.fencing.WriterLease` | `src/jarvis_v2/guardian/fencing.py:21` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.fencing.WriterLease.as_dict` | `src/jarvis_v2/guardian/fencing.py:29` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.fencing.WriterFence` | `src/jarvis_v2/guardian/fencing.py:33` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.fencing.WriterFence.__init__` | `src/jarvis_v2/guardian/fencing.py:41` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.fencing.WriterFence.acquire` | `src/jarvis_v2/guardian/fencing.py:47` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.fencing.WriterFence.renew` | `src/jarvis_v2/guardian/fencing.py:61` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.fencing.WriterFence.handoff` | `src/jarvis_v2/guardian/fencing.py:72` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.fencing.WriterFence.release` | `src/jarvis_v2/guardian/fencing.py:90` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.fencing.WriterFence.assert_current` | `src/jarvis_v2/guardian/fencing.py:95` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.fencing.WriterFence.snapshot` | `src/jarvis_v2/guardian/fencing.py:100` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.fencing.WriterFence._require` | `src/jarvis_v2/guardian/fencing.py:111` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.fencing.WriterFence._expire` | `src/jarvis_v2/guardian/fencing.py:119` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.fencing.WriterFence._now` | `src/jarvis_v2/guardian/fencing.py:123` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.fencing._identifier` | `src/jarvis_v2/guardian/fencing.py:130` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.fencing._ttl` | `src/jarvis_v2/guardian/fencing.py:136` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.health.GuardianHealthError` | `src/jarvis_v2/guardian/health.py:15` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.health.ProbeResult` | `src/jarvis_v2/guardian/health.py:20` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.health.ProbeResult.__post_init__` | `src/jarvis_v2/guardian/health.py:27` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.health.ProbeResult.as_dict` | `src/jarvis_v2/guardian/health.py:40` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.health.HealthEvidence` | `src/jarvis_v2/guardian/health.py:45` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.health.HealthEvidence.as_dict` | `src/jarvis_v2/guardian/health.py:59` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.health.GuardianHealthEvaluator` | `src/jarvis_v2/guardian/health.py:70` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.health.GuardianHealthEvaluator.assess` | `src/jarvis_v2/guardian/health.py:73` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.health.GuardianHealthEvaluator._evidence` | `src/jarvis_v2/guardian/health.py:185` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.health._valid_identifier` | `src/jarvis_v2/guardian/health.py:189` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.health._identifier` | `src/jarvis_v2/guardian/health.py:193` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.health._identifiers` | `src/jarvis_v2/guardian/health.py:199` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.health._dependency_result` | `src/jarvis_v2/guardian/health.py:215` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.incidents.IncidentTrackerError` | `src/jarvis_v2/guardian/incidents.py:18` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.incidents.IncidentRecord` | `src/jarvis_v2/guardian/incidents.py:23` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.incidents.IncidentRecord.as_dict` | `src/jarvis_v2/guardian/incidents.py:35` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.incidents.IncidentNotice` | `src/jarvis_v2/guardian/incidents.py:42` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.incidents.IncidentNotice.as_dict` | `src/jarvis_v2/guardian/incidents.py:49` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.incidents.IncidentTracker` | `src/jarvis_v2/guardian/incidents.py:57` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.incidents.IncidentTracker.__init__` | `src/jarvis_v2/guardian/incidents.py:60` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.incidents.IncidentTracker.records` | `src/jarvis_v2/guardian/incidents.py:78` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.incidents.IncidentTracker.record` | `src/jarvis_v2/guardian/incidents.py:82` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.incidents.IncidentTracker.acknowledge` | `src/jarvis_v2/guardian/incidents.py:125` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.incidents._fingerprint` | `src/jarvis_v2/guardian/incidents.py:146` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.integrity.IntegrityScanError` | `src/jarvis_v2/guardian/integrity.py:16` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.integrity.IntegrityReport` | `src/jarvis_v2/guardian/integrity.py:21` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.integrity.IntegrityReport.as_dict` | `src/jarvis_v2/guardian/integrity.py:33` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.integrity.IntegrityScanner` | `src/jarvis_v2/guardian/integrity.py:42` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.guardian.integrity.IntegrityScanner.__init__` | `src/jarvis_v2/guardian/integrity.py:49` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.integrity.IntegrityScanner.scan` | `src/jarvis_v2/guardian/integrity.py:62` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.integrity._version` | `src/jarvis_v2/guardian/integrity.py:99` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.integrity._identifiers` | `src/jarvis_v2/guardian/integrity.py:109` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.integrity._versions` | `src/jarvis_v2/guardian/integrity.py:123` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.integrity._queues` | `src/jarvis_v2/guardian/integrity.py:133` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.integrity._hashes` | `src/jarvis_v2/guardian/integrity.py:145` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.integrity._mapping_findings` | `src/jarvis_v2/guardian/integrity.py:157` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.integrity._hash_findings` | `src/jarvis_v2/guardian/integrity.py:173` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.isolation.IsolationError` | `src/jarvis_v2/guardian/isolation.py:19` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.isolation.EffectRecord` | `src/jarvis_v2/guardian/isolation.py:24` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.isolation.EffectRecord.as_dict` | `src/jarvis_v2/guardian/isolation.py:31` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.isolation.IsolationSnapshot` | `src/jarvis_v2/guardian/isolation.py:36` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.isolation.IsolationSnapshot.in_flight` | `src/jarvis_v2/guardian/isolation.py:46` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.isolation.IsolationSnapshot.unresolved` | `src/jarvis_v2/guardian/isolation.py:52` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.isolation.IsolationSnapshot.accepts_effects` | `src/jarvis_v2/guardian/isolation.py:60` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.isolation.IsolationSnapshot.as_dict` | `src/jarvis_v2/guardian/isolation.py:63` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.isolation._ComponentState` | `src/jarvis_v2/guardian/isolation.py:77` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.isolation._ComponentState.__post_init__` | `src/jarvis_v2/guardian/isolation.py:83` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.isolation.IsolationController` | `src/jarvis_v2/guardian/isolation.py:88` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.isolation.IsolationController.__init__` | `src/jarvis_v2/guardian/isolation.py:96` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.isolation.IsolationController.register` | `src/jarvis_v2/guardian/isolation.py:109` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.isolation.IsolationController.snapshot` | `src/jarvis_v2/guardian/isolation.py:120` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.isolation.IsolationController.can_accept_effect` | `src/jarvis_v2/guardian/isolation.py:131` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.isolation.IsolationController.begin_effect` | `src/jarvis_v2/guardian/isolation.py:134` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.isolation.IsolationController.complete_effect` | `src/jarvis_v2/guardian/isolation.py:150` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.isolation.IsolationController.reconcile_effect` | `src/jarvis_v2/guardian/isolation.py:170` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.isolation.IsolationController.reconcile` | `src/jarvis_v2/guardian/isolation.py:198` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.isolation.IsolationController.drain` | `src/jarvis_v2/guardian/isolation.py:226` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.isolation.IsolationController.quiesce` | `src/jarvis_v2/guardian/isolation.py:239` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.isolation.IsolationController.isolate` | `src/jarvis_v2/guardian/isolation.py:254` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.isolation.IsolationController.resume` | `src/jarvis_v2/guardian/isolation.py:272` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.isolation.IsolationController._component` | `src/jarvis_v2/guardian/isolation.py:289` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.isolation.IsolationController._check_generation` | `src/jarvis_v2/guardian/isolation.py:296` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.isolation._identifier` | `src/jarvis_v2/guardian/isolation.py:301` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.isolation._reason` | `src/jarvis_v2/guardian/isolation.py:307` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.isolation._evidence_ref` | `src/jarvis_v2/guardian/isolation.py:318` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.isolation._effect_status` | `src/jarvis_v2/guardian/isolation.py:324` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.model.GuardianModelError` | `src/jarvis_v2/guardian/model.py:15` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.model.GuardianModelHealth` | `src/jarvis_v2/guardian/model.py:20` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.model.GuardianModelHealth.as_dict` | `src/jarvis_v2/guardian/model.py:30` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.model._model` | `src/jarvis_v2/guardian/model.py:34` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.model.LocalGuardianModel` | `src/jarvis_v2/guardian/model.py:40` | command or process execution; security or trust-boundary vocabulary |
| `jarvis_v2.guardian.model.LocalGuardianModel.__init__` | `src/jarvis_v2/guardian/model.py:43` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.model.LocalGuardianModel.probe` | `src/jarvis_v2/guardian/model.py:56` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.model.LocalGuardianModel._health` | `src/jarvis_v2/guardian/model.py:66` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.model.LocalGuardianModel._run` | `src/jarvis_v2/guardian/model.py:76` | command or process execution; security or trust-boundary vocabulary |
| `jarvis_v2.guardian.priority.SlotPriority` | `src/jarvis_v2/guardian/priority.py:7` | external or network access; security or trust-boundary vocabulary |
| `jarvis_v2.guardian.priority.SlotPriority.__init__` | `src/jarvis_v2/guardian/priority.py:17` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.priority.SlotPriority.slots` | `src/jarvis_v2/guardian/priority.py:30` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.priority.SlotPriority.held_slots` | `src/jarvis_v2/guardian/priority.py:34` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.priority.SlotPriority.available_slots` | `src/jarvis_v2/guardian/priority.py:39` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.priority.SlotPriority.guardian_request` | `src/jarvis_v2/guardian/priority.py:42` | external or network access; security or trust-boundary vocabulary |
| `jarvis_v2.guardian.priority.SlotPriority.claim` | `src/jarvis_v2/guardian/priority.py:56` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.priority.SlotPriority.start` | `src/jarvis_v2/guardian/priority.py:95` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.priority.SlotPriority.finish` | `src/jarvis_v2/guardian/priority.py:99` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.priority.SlotPriority._normalize_slots` | `src/jarvis_v2/guardian/priority.py:115` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.priority.SlotPriority._sync_compatibility_state` | `src/jarvis_v2/guardian/priority.py:131` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.recovery.RecoveryError` | `src/jarvis_v2/guardian/recovery.py:14` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.recovery.GuardianRecoveryController` | `src/jarvis_v2/guardian/recovery.py:18` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.guardian.recovery.GuardianRecoveryController.__init__` | `src/jarvis_v2/guardian/recovery.py:21` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.guardian.recovery.GuardianRecoveryController.boot` | `src/jarvis_v2/guardian/recovery.py:36` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.recovery.GuardianRecoveryController._controls` | `src/jarvis_v2/guardian/recovery.py:95` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.recovery.GuardianRecoveryController._safe_mode` | `src/jarvis_v2/guardian/recovery.py:101` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.release.inspect` | `src/jarvis_v2/guardian/release.py:13` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.guardian.release.inspect_canary` | `src/jarvis_v2/guardian/release.py:41` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.guardian.restart.RestartBudgetError` | `src/jarvis_v2/guardian/restart.py:19` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.restart.RestartAttempt` | `src/jarvis_v2/guardian/restart.py:24` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.restart.RestartAttempt.as_dict` | `src/jarvis_v2/guardian/restart.py:35` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.restart.RestartDecision` | `src/jarvis_v2/guardian/restart.py:40` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.restart.RestartDecision.as_dict` | `src/jarvis_v2/guardian/restart.py:53` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.restart.RestartBudget` | `src/jarvis_v2/guardian/restart.py:57` | external or network access; security or trust-boundary vocabulary |
| `jarvis_v2.guardian.restart.RestartBudget.__init__` | `src/jarvis_v2/guardian/restart.py:66` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.restart.RestartBudget.generation` | `src/jarvis_v2/guardian/restart.py:97` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.restart.RestartBudget.history` | `src/jarvis_v2/guardian/restart.py:101` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.restart.RestartBudget.snapshot` | `src/jarvis_v2/guardian/restart.py:104` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.restart.RestartBudget.request` | `src/jarvis_v2/guardian/restart.py:120` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.restart.RestartBudget.record_outcome` | `src/jarvis_v2/guardian/restart.py:155` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.restart.RestartBudget.resolve_unknown` | `src/jarvis_v2/guardian/restart.py:187` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.restart.RestartBudget.new_generation` | `src/jarvis_v2/guardian/restart.py:220` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.restart.RestartBudget._state` | `src/jarvis_v2/guardian/restart.py:232` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.restart.RestartBudget._decision` | `src/jarvis_v2/guardian/restart.py:247` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.restart.RestartBudget._history_index` | `src/jarvis_v2/guardian/restart.py:260` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.restart.RestartBudget._append` | `src/jarvis_v2/guardian/restart.py:267` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.restart.RestartBudget._now` | `src/jarvis_v2/guardian/restart.py:270` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.restart._identifier` | `src/jarvis_v2/guardian/restart.py:282` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.restart._reason` | `src/jarvis_v2/guardian/restart.py:288` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.restart._evidence_ref` | `src/jarvis_v2/guardian/restart.py:299` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.rollback.RollbackError` | `src/jarvis_v2/guardian/rollback.py:24` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.rollback.RollbackPlan` | `src/jarvis_v2/guardian/rollback.py:29` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.rollback.RollbackPlan.as_dict` | `src/jarvis_v2/guardian/rollback.py:43` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.rollback.select_last_known_good` | `src/jarvis_v2/guardian/rollback.py:49` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.guardian.rollback.restore_last_known_good` | `src/jarvis_v2/guardian/rollback.py:121` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.guardian.rollback._status` | `src/jarvis_v2/guardian/rollback.py:172` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.rollback._relative` | `src/jarvis_v2/guardian/rollback.py:178` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.guardian.rollback._safe_file` | `src/jarvis_v2/guardian/rollback.py:187` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.rollback._regular` | `src/jarvis_v2/guardian/rollback.py:201` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.rollback._root` | `src/jarvis_v2/guardian/rollback.py:207` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.rollback._digest` | `src/jarvis_v2/guardian/rollback.py:213` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.guardian.rollback._checkpoint_digest` | `src/jarvis_v2/guardian/rollback.py:221` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.rollback._fsync_directory` | `src/jarvis_v2/guardian/rollback.py:228` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.guardian.standby.StandbyError` | `src/jarvis_v2/guardian/standby.py:16` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.standby.StandbyLauncher` | `src/jarvis_v2/guardian/standby.py:20` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.standby.StandbyLauncher.__init__` | `src/jarvis_v2/guardian/standby.py:27` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.standby.StandbyLauncher.inspect` | `src/jarvis_v2/guardian/standby.py:52` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.standby.StandbyLauncher.start` | `src/jarvis_v2/guardian/standby.py:87` | security or trust-boundary vocabulary |
| `jarvis_v2.guardian.standby._value` | `src/jarvis_v2/guardian/standby.py:114` | security or trust-boundary vocabulary |
| `jarvis_v2.health._systemd_state` | `src/jarvis_v2/health.py:17` | command or process execution; security or trust-boundary vocabulary |
| `jarvis_v2.health._git_head` | `src/jarvis_v2/health.py:29` | command or process execution; security or trust-boundary vocabulary |
| `jarvis_v2.health._root_blockers` | `src/jarvis_v2/health.py:42` | database or query access |
| `jarvis_v2.health._native_health` | `src/jarvis_v2/health.py:73` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.health.collect_health` | `src/jarvis_v2/health.py:140` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.monitor._safe` | `src/jarvis_v2/monitor.py:35` | security or trust-boundary vocabulary |
| `jarvis_v2.monitor._connect` | `src/jarvis_v2/monitor.py:46` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.monitor._columns` | `src/jarvis_v2/monitor.py:58` | database or query access |
| `jarvis_v2.monitor._detect` | `src/jarvis_v2/monitor.py:64` | database or query access |
| `jarvis_v2.monitor._fetch_astra` | `src/jarvis_v2/monitor.py:104` | database or query access |
| `jarvis_v2.monitor._fetch_atlas` | `src/jarvis_v2/monitor.py:181` | database or query access |
| `jarvis_v2.monitor.snapshot` | `src/jarvis_v2/monitor.py:208` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.monitor.render` | `src/jarvis_v2/monitor.py:243` | security or trust-boundary vocabulary |
| `jarvis_v2.monitor._choose_db` | `src/jarvis_v2/monitor.py:312` | security or trust-boundary vocabulary |
| `jarvis_v2.monitor.main` | `src/jarvis_v2/monitor.py:328` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.monitor_supervision._cols` | `src/jarvis_v2/monitor_supervision.py:49` | database or query access |
| `jarvis_v2.monitor_supervision._group` | `src/jarvis_v2/monitor_supervision.py:63` | database or query access |
| `jarvis_v2.monitor_supervision.collect` | `src/jarvis_v2/monitor_supervision.py:90` | database or query access |
| `jarvis_v2.monitor_supervision.render_lines` | `src/jarvis_v2/monitor_supervision.py:247` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.native_controller._absolute` | `src/jarvis_v2/native_controller.py:36` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.native_controller._child` | `src/jarvis_v2/native_controller.py:43` | security or trust-boundary vocabulary |
| `jarvis_v2.native_controller._directory` | `src/jarvis_v2/native_controller.py:52` | security or trust-boundary vocabulary |
| `jarvis_v2.native_controller.NativeController` | `src/jarvis_v2/native_controller.py:75` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.native_controller.NativeController.__init__` | `src/jarvis_v2/native_controller.py:78` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.native_controller.NativeController._acquire_lock` | `src/jarvis_v2/native_controller.py:119` | filesystem access |
| `jarvis_v2.native_controller.NativeController.run_forever` | `src/jarvis_v2/native_controller.py:200` | security or trust-boundary vocabulary |
| `jarvis_v2.native_controller._default_state` | `src/jarvis_v2/native_controller.py:219` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.native_controller.main` | `src/jarvis_v2/native_controller.py:223` | security or trust-boundary vocabulary |
| `jarvis_v2.research.analysis.MediaAnalysisEvidence` | `src/jarvis_v2/research/analysis.py:43` | security or trust-boundary vocabulary |
| `jarvis_v2.research.analysis.MediaAnalysisEvidence.__post_init__` | `src/jarvis_v2/research/analysis.py:56` | security or trust-boundary vocabulary |
| `jarvis_v2.research.analysis.MediaAnalysisStore` | `src/jarvis_v2/research/analysis.py:104` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.research.analysis.MediaAnalysisStore.__init__` | `src/jarvis_v2/research/analysis.py:107` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.research.analysis.MediaAnalysisStore.save` | `src/jarvis_v2/research/analysis.py:135` | database or query access |
| `jarvis_v2.research.analysis.MediaAnalysisStore.latest` | `src/jarvis_v2/research/analysis.py:149` | database or query access |
| `jarvis_v2.research.analysis.MediaAnalysisStore._evidence` | `src/jarvis_v2/research/analysis.py:167` | security or trust-boundary vocabulary |
| `jarvis_v2.research.analysis.MediaAnalysisService` | `src/jarvis_v2/research/analysis.py:192` | security or trust-boundary vocabulary |
| `jarvis_v2.research.analysis.MediaAnalysisService._save` | `src/jarvis_v2/research/analysis.py:232` | security or trust-boundary vocabulary |
| `jarvis_v2.research.comparison.ComparisonError` | `src/jarvis_v2/research/comparison.py:15` | security or trust-boundary vocabulary |
| `jarvis_v2.research.comparison.SourceClaim` | `src/jarvis_v2/research/comparison.py:45` | security or trust-boundary vocabulary |
| `jarvis_v2.research.github._safe_path` | `src/jarvis_v2/research/github.py:54` | security or trust-boundary vocabulary |
| `jarvis_v2.research.github.RepositoryPolicy` | `src/jarvis_v2/research/github.py:65` | security or trust-boundary vocabulary |
| `jarvis_v2.research.github.RepositoryPolicy.__post_init__` | `src/jarvis_v2/research/github.py:74` | security or trust-boundary vocabulary |
| `jarvis_v2.research.github.RepositoryPolicy.repository` | `src/jarvis_v2/research/github.py:90` | security or trust-boundary vocabulary |
| `jarvis_v2.research.github.RepositoryPolicy.allows_path` | `src/jarvis_v2/research/github.py:93` | security or trust-boundary vocabulary |
| `jarvis_v2.research.github.SourceFile` | `src/jarvis_v2/research/github.py:98` | security or trust-boundary vocabulary |
| `jarvis_v2.research.github.SourceFile.__post_init__` | `src/jarvis_v2/research/github.py:104` | security or trust-boundary vocabulary |
| `jarvis_v2.research.github.SourceFile.as_dict` | `src/jarvis_v2/research/github.py:112` | security or trust-boundary vocabulary |
| `jarvis_v2.research.github.GitHubSourceAdapter` | `src/jarvis_v2/research/github.py:234` | security or trust-boundary vocabulary |
| `jarvis_v2.research.github.GitHubSourceAdapter.inspect_commit` | `src/jarvis_v2/research/github.py:306` | security or trust-boundary vocabulary |
| `jarvis_v2.research.github.GitHubSourceAdapter._repository_uri` | `src/jarvis_v2/research/github.py:353` | security or trust-boundary vocabulary |
| `jarvis_v2.research.github.GitHubSourceAdapter._files` | `src/jarvis_v2/research/github.py:370` | security or trust-boundary vocabulary |
| `jarvis_v2.research.handbook.HandbookEditProposalV1` | `src/jarvis_v2/research/handbook.py:96` | security or trust-boundary vocabulary |
| `jarvis_v2.research.handbook.HandbookEditProposalV1.__post_init__` | `src/jarvis_v2/research/handbook.py:115` | security or trust-boundary vocabulary |
| `jarvis_v2.research.handbook.HandbookOwnerApproval` | `src/jarvis_v2/research/handbook.py:220` | security or trust-boundary vocabulary |
| `jarvis_v2.research.handbook.HandbookOwnerApproval.__post_init__` | `src/jarvis_v2/research/handbook.py:229` | security or trust-boundary vocabulary |
| `jarvis_v2.research.handbook._proposer_allowed` | `src/jarvis_v2/research/handbook.py:282` | security or trust-boundary vocabulary |
| `jarvis_v2.research.handbook.HandbookProposalWorkflow` | `src/jarvis_v2/research/handbook.py:292` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.research.handbook.HandbookProposalWorkflow.review` | `src/jarvis_v2/research/handbook.py:332` | security or trust-boundary vocabulary |
| `jarvis_v2.research.handbook.HandbookProposalWorkflow.owner_approve` | `src/jarvis_v2/research/handbook.py:352` | security or trust-boundary vocabulary |
| `jarvis_v2.research.handbook.HandbookProposalWorkflow.queue_for_merge` | `src/jarvis_v2/research/handbook.py:365` | security or trust-boundary vocabulary |
| `jarvis_v2.research.instagram.instagram_reel_id_from_url` | `src/jarvis_v2/research/instagram.py:43` | security or trust-boundary vocabulary |
| `jarvis_v2.research.instagram.InstagramReelStore` | `src/jarvis_v2/research/instagram.py:126` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.research.instagram.InstagramReelStore.__init__` | `src/jarvis_v2/research/instagram.py:129` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.research.instagram.InstagramReelStore.save` | `src/jarvis_v2/research/instagram.py:158` | database or query access |
| `jarvis_v2.research.instagram.InstagramReelStore.latest` | `src/jarvis_v2/research/instagram.py:174` | database or query access |
| `jarvis_v2.research.instagram.InstagramReelService` | `src/jarvis_v2/research/instagram.py:225` | external or network access |
| `jarvis_v2.research.instagram.InstagramReelService.fetch` | `src/jarvis_v2/research/instagram.py:243` | external or network access |
| `jarvis_v2.research.media_rag.MediaRAGStore` | `src/jarvis_v2/research/media_rag.py:332` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.research.media_rag.MediaRAGStore.__init__` | `src/jarvis_v2/research/media_rag.py:335` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.research.media_rag.MediaRAGStore.save_chunks` | `src/jarvis_v2/research/media_rag.py:359` | database or query access |
| `jarvis_v2.research.media_rag.MediaRAGStore.save_summary` | `src/jarvis_v2/research/media_rag.py:369` | database or query access |
| `jarvis_v2.research.media_rag.MediaRAGStore.chunks_for` | `src/jarvis_v2/research/media_rag.py:377` | database or query access |
| `jarvis_v2.research.media_rag.MediaRAGStore.summary` | `src/jarvis_v2/research/media_rag.py:384` | database or query access |
| `jarvis_v2.research.subscriptions.Subscription` | `src/jarvis_v2/research/subscriptions.py:56` | security or trust-boundary vocabulary |
| `jarvis_v2.research.subscriptions.Subscription.__post_init__` | `src/jarvis_v2/research/subscriptions.py:69` | security or trust-boundary vocabulary |
| `jarvis_v2.research.subscriptions.SubscriptionStore` | `src/jarvis_v2/research/subscriptions.py:123` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.research.subscriptions.SubscriptionStore.__init__` | `src/jarvis_v2/research/subscriptions.py:126` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.research.subscriptions.SubscriptionStore.save` | `src/jarvis_v2/research/subscriptions.py:164` | database or query access |
| `jarvis_v2.research.subscriptions.SubscriptionStore.get` | `src/jarvis_v2/research/subscriptions.py:209` | database or query access |
| `jarvis_v2.research.subscriptions.SubscriptionStore.due` | `src/jarvis_v2/research/subscriptions.py:218` | database or query access |
| `jarvis_v2.research.subscriptions.SubscriptionStore.record_refresh` | `src/jarvis_v2/research/subscriptions.py:231` | database or query access |
| `jarvis_v2.research.subscriptions.SubscriptionStore.disable` | `src/jarvis_v2/research/subscriptions.py:248` | database or query access |
| `jarvis_v2.research.subscriptions.SubscriptionStore._row` | `src/jarvis_v2/research/subscriptions.py:258` | database or query access |
| `jarvis_v2.research.web.SourcePolicy` | `src/jarvis_v2/research/web.py:63` | security or trust-boundary vocabulary |
| `jarvis_v2.research.web.SourcePolicy.__post_init__` | `src/jarvis_v2/research/web.py:70` | security or trust-boundary vocabulary |
| `jarvis_v2.research.web.SourcePolicy.allows` | `src/jarvis_v2/research/web.py:77` | security or trust-boundary vocabulary |
| `jarvis_v2.research.web.WebDiscoveryService` | `src/jarvis_v2/research/web.py:226` | external or network access |
| `jarvis_v2.research.web.WebDiscoveryService.fetch` | `src/jarvis_v2/research/web.py:302` | external or network access |
| `jarvis_v2.research.youtube.video_id_from_url` | `src/jarvis_v2/research/youtube.py:43` | security or trust-boundary vocabulary |
| `jarvis_v2.research.youtube.VideoResearchStore` | `src/jarvis_v2/research/youtube.py:196` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.research.youtube.VideoResearchStore.__init__` | `src/jarvis_v2/research/youtube.py:199` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.research.youtube.VideoResearchStore.save` | `src/jarvis_v2/research/youtube.py:228` | database or query access |
| `jarvis_v2.research.youtube.VideoResearchStore.latest` | `src/jarvis_v2/research/youtube.py:244` | database or query access |
| `jarvis_v2.research.youtube.YouTubeResearchService` | `src/jarvis_v2/research/youtube.py:270` | external or network access |
| `jarvis_v2.research.youtube.YouTubeResearchService.fetch` | `src/jarvis_v2/research/youtube.py:288` | external or network access |
| `jarvis_v2.runtime.browser.BrowserProfile` | `src/jarvis_v2/runtime/browser.py:85` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.browser.BrowserProfile.model_context` | `src/jarvis_v2/runtime/browser.py:95` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.browser.BrowserActionReceipt` | `src/jarvis_v2/runtime/browser.py:125` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.browser.BrowserActionReceipt.model_context` | `src/jarvis_v2/runtime/browser.py:136` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.browser.BrowserAdapter` | `src/jarvis_v2/runtime/browser.py:148` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.browser.BrowserProfileService` | `src/jarvis_v2/runtime/browser.py:284` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.runtime.browser.BrowserProfileService.__init__` | `src/jarvis_v2/runtime/browser.py:287` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.runtime.browser.BrowserProfileService.create_profile` | `src/jarvis_v2/runtime/browser.py:348` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.runtime.browser.BrowserProfileService.begin_login` | `src/jarvis_v2/runtime/browser.py:380` | database or query access |
| `jarvis_v2.runtime.browser.BrowserProfileService.complete_login` | `src/jarvis_v2/runtime/browser.py:408` | database or query access |
| `jarvis_v2.runtime.browser.BrowserProfileService.revoke_profile` | `src/jarvis_v2/runtime/browser.py:438` | database or query access |
| `jarvis_v2.runtime.browser.BrowserProfileService.authorize_action` | `src/jarvis_v2/runtime/browser.py:449` | database or query access |
| `jarvis_v2.runtime.browser.BrowserProfileService.get_profile` | `src/jarvis_v2/runtime/browser.py:496` | database or query access |
| `jarvis_v2.runtime.browser.BrowserProfileService.adapter_context` | `src/jarvis_v2/runtime/browser.py:505` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.browser.BrowserProfileService._profile` | `src/jarvis_v2/runtime/browser.py:526` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.runtime.browser.BrowserProfileService._handoff` | `src/jarvis_v2/runtime/browser.py:540` | database or query access |
| `jarvis_v2.runtime.browser.BrowserProfileService._receipt` | `src/jarvis_v2/runtime/browser.py:546` | database or query access |
| `jarvis_v2.runtime.calendar.CalendarAuthorizationError` | `src/jarvis_v2/runtime/calendar.py:26` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.calendar.CalendarService` | `src/jarvis_v2/runtime/calendar.py:117` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.runtime.calendar.CalendarService.__init__` | `src/jarvis_v2/runtime/calendar.py:120` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.calendar.CalendarService.update_event` | `src/jarvis_v2/runtime/calendar.py:173` | database or query access |
| `jarvis_v2.runtime.calendar.CalendarService._require` | `src/jarvis_v2/runtime/calendar.py:194` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.chat.ChatService` | `src/jarvis_v2/runtime/chat.py:29` | filesystem access |
| `jarvis_v2.runtime.chat.ChatService.stream` | `src/jarvis_v2/runtime/chat.py:37` | filesystem access |
| `jarvis_v2.runtime.email.EmailAuthorizationError` | `src/jarvis_v2/runtime/email.py:31` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.email.EmailService` | `src/jarvis_v2/runtime/email.py:158` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.email.EmailService.__init__` | `src/jarvis_v2/runtime/email.py:161` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.email.EmailService.send` | `src/jarvis_v2/runtime/email.py:219` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.email.EmailService._require` | `src/jarvis_v2/runtime/email.py:243` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.file_actions.FileIdentity` | `src/jarvis_v2/runtime/file_actions.py:40` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.file_actions.FileIdentity.digest` | `src/jarvis_v2/runtime/file_actions.py:47` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.file_actions.FileActionRequest` | `src/jarvis_v2/runtime/file_actions.py:53` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.file_actions.FileActionService` | `src/jarvis_v2/runtime/file_actions.py:73` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.runtime.file_actions.FileActionService.__init__` | `src/jarvis_v2/runtime/file_actions.py:76` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.runtime.file_actions.FileActionService.preview` | `src/jarvis_v2/runtime/file_actions.py:156` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.file_actions.FileActionService.propose_trash` | `src/jarvis_v2/runtime/file_actions.py:169` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.file_actions.FileActionService.propose_directory` | `src/jarvis_v2/runtime/file_actions.py:174` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.file_actions.FileActionService.decide` | `src/jarvis_v2/runtime/file_actions.py:178` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.runtime.file_actions.FileActionService.trash_file` | `src/jarvis_v2/runtime/file_actions.py:197` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.runtime.file_actions.FileActionService.propose_restore` | `src/jarvis_v2/runtime/file_actions.py:248` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.runtime.file_actions.FileActionService.restore_file` | `src/jarvis_v2/runtime/file_actions.py:265` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.runtime.file_actions.FileActionService.trash_manifest` | `src/jarvis_v2/runtime/file_actions.py:318` | database or query access |
| `jarvis_v2.runtime.file_actions.FileActionService.audit` | `src/jarvis_v2/runtime/file_actions.py:323` | database or query access |
| `jarvis_v2.runtime.file_actions.FileActionService._insert_request` | `src/jarvis_v2/runtime/file_actions.py:332` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.runtime.file_actions.FileActionService._authorized` | `src/jarvis_v2/runtime/file_actions.py:347` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.runtime.file_actions.FileActionService._row` | `src/jarvis_v2/runtime/file_actions.py:355` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.runtime.file_actions.FileActionService._request_from_row` | `src/jarvis_v2/runtime/file_actions.py:362` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.runtime.file_actions.FileActionService._identity` | `src/jarvis_v2/runtime/file_actions.py:370` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.runtime.file_actions.FileActionService._request_id` | `src/jarvis_v2/runtime/file_actions.py:374` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.file_actions.FileActionService._reason` | `src/jarvis_v2/runtime/file_actions.py:380` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.file_actions.FileActionService._capture_allowed_file` | `src/jarvis_v2/runtime/file_actions.py:387` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.file_actions.FileActionService._validate_restore_target` | `src/jarvis_v2/runtime/file_actions.py:404` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.file_actions.FileActionService._assert_identity` | `src/jarvis_v2/runtime/file_actions.py:416` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.file_actions.FileActionService._normalize_roots` | `src/jarvis_v2/runtime/file_actions.py:434` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.file_actions.FileActionService._inside` | `src/jarvis_v2/runtime/file_actions.py:449` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.file_actions.FileActionService._is_protected` | `src/jarvis_v2/runtime/file_actions.py:456` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.file_actions.FileActionService._open_directory` | `src/jarvis_v2/runtime/file_actions.py:463` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.runtime.file_actions.FileActionService._checksum_at` | `src/jarvis_v2/runtime/file_actions.py:467` | filesystem access |
| `jarvis_v2.runtime.file_actions.FileActionService._checksum_path` | `src/jarvis_v2/runtime/file_actions.py:478` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.file_actions.FileActionService._restore_move` | `src/jarvis_v2/runtime/file_actions.py:501` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.file_actions.FileActionService._audit_db` | `src/jarvis_v2/runtime/file_actions.py:513` | database or query access |
| `jarvis_v2.runtime.file_actions.FileActionService._append_log` | `src/jarvis_v2/runtime/file_actions.py:520` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.runtime.offline.OfflineChatService` | `src/jarvis_v2/runtime/offline.py:23` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.offline.OfflineChatService.stream` | `src/jarvis_v2/runtime/offline.py:59` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.qualification.HostAcceptanceRecord` | `src/jarvis_v2/runtime/qualification.py:37` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.qualification.HostAcceptanceRecord.__post_init__` | `src/jarvis_v2/runtime/qualification.py:47` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.reminders.ReminderService` | `src/jarvis_v2/runtime/reminders.py:102` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.runtime.reminders.ReminderService.__init__` | `src/jarvis_v2/runtime/reminders.py:105` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.runtime.reminders.ReminderService.preferences` | `src/jarvis_v2/runtime/reminders.py:147` | database or query access |
| `jarvis_v2.runtime.reminders.ReminderService.set_preferences` | `src/jarvis_v2/runtime/reminders.py:166` | database or query access |
| `jarvis_v2.runtime.security.OwnerSession` | `src/jarvis_v2/runtime/security.py:44` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.security._authority` | `src/jarvis_v2/runtime/security.py:67` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.security._origin` | `src/jarvis_v2/runtime/security.py:83` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.security.RuntimeSecurity` | `src/jarvis_v2/runtime/security.py:103` | external or network access; security or trust-boundary vocabulary |
| `jarvis_v2.runtime.security.RuntimeSecurity.__init__` | `src/jarvis_v2/runtime/security.py:111` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.service.RuntimeService` | `src/jarvis_v2/runtime/service.py:44` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.service.RuntimeService.handle` | `src/jarvis_v2/runtime/service.py:67` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.service.RuntimeService.rotate_owner_session` | `src/jarvis_v2/runtime/service.py:121` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.service.RuntimeService._create_task` | `src/jarvis_v2/runtime/service.py:146` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.service.RuntimeService._authorized` | `src/jarvis_v2/runtime/service.py:224` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.service.RuntimeService._request_identity` | `src/jarvis_v2/runtime/service.py:241` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.speech.SpeechService` | `src/jarvis_v2/runtime/speech.py:25` | security or trust-boundary vocabulary |
| `jarvis_v2.runtime.speech.SpeechService._stop_adapter` | `src/jarvis_v2/runtime/speech.py:128` | security or trust-boundary vocabulary |
| `jarvis_v2.system_inventory._command` | `src/jarvis_v2/system_inventory.py:40` | command or process execution; security or trust-boundary vocabulary |
| `jarvis_v2.system_inventory._command_summary` | `src/jarvis_v2/system_inventory.py:54` | security or trust-boundary vocabulary |
| `jarvis_v2.system_inventory._optional_command_summary` | `src/jarvis_v2/system_inventory.py:64` | security or trust-boundary vocabulary |
| `jarvis_v2.system_inventory._metadata` | `src/jarvis_v2/system_inventory.py:74` | security or trust-boundary vocabulary |
| `jarvis_v2.system_inventory.scan_filesystem` | `src/jarvis_v2/system_inventory.py:87` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.system_inventory._software` | `src/jarvis_v2/system_inventory.py:173` | security or trust-boundary vocabulary |
| `jarvis_v2.system_inventory.collect_inventory` | `src/jarvis_v2/system_inventory.py:207` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.system_inventory.compare_inventories` | `src/jarvis_v2/system_inventory.py:249` | security or trust-boundary vocabulary |
| `jarvis_v2.system_inventory.write_inventory` | `src/jarvis_v2/system_inventory.py:274` | filesystem access; security or trust-boundary vocabulary |
| `jarvis_v2.tws.__init__.QuestStore` | `src/jarvis_v2/tws/__init__.py:287` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.tws.__init__.QuestStore.__init__` | `src/jarvis_v2/tws/__init__.py:290` | security or trust-boundary vocabulary |
| `jarvis_v2.tws.__init__.QuestStore.schema_version` | `src/jarvis_v2/tws/__init__.py:305` | database or query access |
| `jarvis_v2.tws.__init__.QuestStore._one` | `src/jarvis_v2/tws/__init__.py:317` | database or query access |
| `jarvis_v2.tws.__init__.QuestStore.add_wing` | `src/jarvis_v2/tws/__init__.py:321` | database or query access |
| `jarvis_v2.tws.__init__.QuestStore.create_quest` | `src/jarvis_v2/tws/__init__.py:338` | database or query access |
| `jarvis_v2.tws.__init__.QuestStore.import_tasks_as_quests` | `src/jarvis_v2/tws/__init__.py:375` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.tws.__init__.QuestStore.task_quest_proposals` | `src/jarvis_v2/tws/__init__.py:506` | database or query access |
| `jarvis_v2.tws.__init__.QuestStore.transition_quest` | `src/jarvis_v2/tws/__init__.py:518` | database or query access |
| `jarvis_v2.tws.__init__.QuestStore.catalog` | `src/jarvis_v2/tws/__init__.py:543` | database or query access |
| `jarvis_v2.tws.__init__.QuestStore.append_proof` | `src/jarvis_v2/tws/__init__.py:568` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.tws.__init__.QuestStore.review_proof` | `src/jarvis_v2/tws/__init__.py:603` | database or query access |
| `jarvis_v2.tws.__init__.QuestStore.define_realm` | `src/jarvis_v2/tws/__init__.py:623` | database or query access |
| `jarvis_v2.tws.__init__.QuestStore.xp_total` | `src/jarvis_v2/tws/__init__.py:661` | database or query access |
| `jarvis_v2.tws.__init__.QuestStore.award_xp` | `src/jarvis_v2/tws/__init__.py:668` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.tws.__init__.QuestStore.unlock_realm` | `src/jarvis_v2/tws/__init__.py:729` | database or query access |
| `jarvis_v2.tws.__init__.QuestStore.record_achievement` | `src/jarvis_v2/tws/__init__.py:758` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.tws.__init__.QuestStore.achievements` | `src/jarvis_v2/tws/__init__.py:833` | database or query access |
| `jarvis_v2.tws.__init__.QuestStore.cultivation_progress` | `src/jarvis_v2/tws/__init__.py:854` | database or query access |
| `jarvis_v2.tws.__init__.QuestStore.adapt_skill` | `src/jarvis_v2/tws/__init__.py:876` | database or query access |
| `jarvis_v2.tws.__init__.QuestStore.set_aurelia_state` | `src/jarvis_v2/tws/__init__.py:945` | database or query access |
| `jarvis_v2.tws.__init__.QuestStore.record_aurelia_turn` | `src/jarvis_v2/tws/__init__.py:985` | database or query access |
| `jarvis_v2.tws.__init__.QuestStore.aurelia_state` | `src/jarvis_v2/tws/__init__.py:1038` | database or query access |
| `jarvis_v2.tws.__init__.QuestStore.aurelia_turns` | `src/jarvis_v2/tws/__init__.py:1044` | database or query access |
| `jarvis_v2.tws.__init__.QuestStore.set_preferences` | `src/jarvis_v2/tws/__init__.py:1055` | database or query access |
| `jarvis_v2.tws.__init__.QuestStore.preferences` | `src/jarvis_v2/tws/__init__.py:1099` | database or query access |
| `jarvis_v2.tws.__init__.QuestStore.set_onboarding` | `src/jarvis_v2/tws/__init__.py:1105` | database or query access |
| `jarvis_v2.tws.__init__.QuestStore.wings` | `src/jarvis_v2/tws/__init__.py:1129` | database or query access |
| `jarvis_v2.tws.__init__.QuestStore.sanctuary_snapshot` | `src/jarvis_v2/tws/__init__.py:1139` | database or query access |
| `jarvis_v2.tws.__init__.QuestStore.wing` | `src/jarvis_v2/tws/__init__.py:1171` | database or query access |
| `jarvis_v2.tws.__init__.QuestStore.quest` | `src/jarvis_v2/tws/__init__.py:1174` | database or query access |
| `jarvis_v2.tws.__init__.QuestStore.proofs` | `src/jarvis_v2/tws/__init__.py:1177` | database or query access |
| `jarvis_v2.tws.aurelia_model.validate_visual_qa_manifest` | `src/jarvis_v2/tws/aurelia_model.py:208` | security or trust-boundary vocabulary |
| `jarvis_v2.wic.__init__._url` | `src/jarvis_v2/wic/__init__.py:82` | security or trust-boundary vocabulary |
| `jarvis_v2.wic.__init__.normalize_url` | `src/jarvis_v2/wic/__init__.py:122` | security or trust-boundary vocabulary |
| `jarvis_v2.wic.__init__.SourceStore` | `src/jarvis_v2/wic/__init__.py:264` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.wic.__init__.SourceStore.__init__` | `src/jarvis_v2/wic/__init__.py:267` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.wic.__init__.SourceStore.save` | `src/jarvis_v2/wic/__init__.py:307` | database or query access |
| `jarvis_v2.wic.__init__.SourceStore.observations` | `src/jarvis_v2/wic/__init__.py:330` | database or query access |
| `jarvis_v2.wic.__init__.SourceStore.latest` | `src/jarvis_v2/wic/__init__.py:350` | database or query access |
| `jarvis_v2.wic.__init__.SourceStore.record_health` | `src/jarvis_v2/wic/__init__.py:363` | database or query access |
| `jarvis_v2.wic.__init__.SourceStore.health` | `src/jarvis_v2/wic/__init__.py:397` | database or query access |
| `jarvis_v2.wic.__init__.StoryClusterStore` | `src/jarvis_v2/wic/__init__.py:472` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.wic.__init__.StoryClusterStore.__init__` | `src/jarvis_v2/wic/__init__.py:475` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.wic.__init__.StoryClusterStore.add` | `src/jarvis_v2/wic/__init__.py:508` | database or query access |
| `jarvis_v2.wic.__init__.StoryClusterStore.get` | `src/jarvis_v2/wic/__init__.py:546` | database or query access |
| `jarvis_v2.wic.__init__.StoryClusterStore.clusters` | `src/jarvis_v2/wic/__init__.py:568` | database or query access |
| `jarvis_v2.wic.__init__.ClaimLedger` | `src/jarvis_v2/wic/__init__.py:693` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.wic.__init__.ClaimLedger.__init__` | `src/jarvis_v2/wic/__init__.py:696` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.wic.__init__.ClaimLedger.get` | `src/jarvis_v2/wic/__init__.py:802` | database or query access |
| `jarvis_v2.wic.__init__.ClaimLedger.history` | `src/jarvis_v2/wic/__init__.py:812` | database or query access |
| `jarvis_v2.wic.__init__.ClaimLedger._insert_new` | `src/jarvis_v2/wic/__init__.py:823` | database or query access |
| `jarvis_v2.wic.__init__.ClaimLedger._append` | `src/jarvis_v2/wic/__init__.py:841` | database or query access |
| `jarvis_v2.wic.__init__.CategoryStore` | `src/jarvis_v2/wic/__init__.py:921` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.wic.__init__.CategoryStore.__init__` | `src/jarvis_v2/wic/__init__.py:924` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.wic.__init__.CategoryStore.get` | `src/jarvis_v2/wic/__init__.py:974` | database or query access |
| `jarvis_v2.wic.__init__.CategoryStore.search` | `src/jarvis_v2/wic/__init__.py:987` | database or query access |
| `jarvis_v2.wic.__init__.CategoryStore.history` | `src/jarvis_v2/wic/__init__.py:1001` | database or query access |
| `jarvis_v2.wic.__init__.CategoryStore._insert_new` | `src/jarvis_v2/wic/__init__.py:1012` | database or query access |
| `jarvis_v2.wic.__init__.CategoryStore._append` | `src/jarvis_v2/wic/__init__.py:1030` | database or query access |
| `jarvis_v2.wic.__init__.SummaryStore` | `src/jarvis_v2/wic/__init__.py:1203` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.wic.__init__.SummaryStore.__init__` | `src/jarvis_v2/wic/__init__.py:1206` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.wic.__init__.SummaryStore.save` | `src/jarvis_v2/wic/__init__.py:1226` | database or query access |
| `jarvis_v2.wic.__init__.SummaryStore.get` | `src/jarvis_v2/wic/__init__.py:1242` | database or query access |
| `jarvis_v2.wic.__init__.WatchlistPreferences` | `src/jarvis_v2/wic/__init__.py:1273` | security or trust-boundary vocabulary |
| `jarvis_v2.wic.__init__.WatchlistPreferences.__post_init__` | `src/jarvis_v2/wic/__init__.py:1283` | security or trust-boundary vocabulary |
| `jarvis_v2.wic.__init__.WatchlistPreferences.from_dict` | `src/jarvis_v2/wic/__init__.py:1306` | security or trust-boundary vocabulary |
| `jarvis_v2.wic.__init__.WatchlistStore` | `src/jarvis_v2/wic/__init__.py:1325` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.wic.__init__.WatchlistStore.__init__` | `src/jarvis_v2/wic/__init__.py:1328` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.wic.__init__.WatchlistStore.save` | `src/jarvis_v2/wic/__init__.py:1356` | database or query access |
| `jarvis_v2.wic.__init__.WatchlistStore.history` | `src/jarvis_v2/wic/__init__.py:1390` | database or query access |
| `jarvis_v2.wic.__init__.WatchlistStore._get` | `src/jarvis_v2/wic/__init__.py:1400` | database or query access |
| `jarvis_v2.wic.__init__.WatchlistStore._assert_owner` | `src/jarvis_v2/wic/__init__.py:1410` | security or trust-boundary vocabulary |
| `jarvis_v2.wic.__init__.AlertPolicy` | `src/jarvis_v2/wic/__init__.py:1430` | security or trust-boundary vocabulary |
| `jarvis_v2.wic.__init__.AlertPolicy.__post_init__` | `src/jarvis_v2/wic/__init__.py:1442` | security or trust-boundary vocabulary |
| `jarvis_v2.wic.__init__.AlertPolicy.from_dict` | `src/jarvis_v2/wic/__init__.py:1476` | security or trust-boundary vocabulary |
| `jarvis_v2.wic.__init__.AlertStore` | `src/jarvis_v2/wic/__init__.py:1530` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.wic.__init__.AlertStore.__init__` | `src/jarvis_v2/wic/__init__.py:1533` | database or query access; security or trust-boundary vocabulary |
| `jarvis_v2.wic.__init__.AlertStore.save_policy` | `src/jarvis_v2/wic/__init__.py:1564` | database or query access |
| `jarvis_v2.wic.__init__.AlertStore.get_policy` | `src/jarvis_v2/wic/__init__.py:1583` | database or query access |
| `jarvis_v2.wic.__init__.AlertStore.evaluate` | `src/jarvis_v2/wic/__init__.py:1597` | database or query access |
| `jarvis_v2.wic.__init__.AlertStore.history` | `src/jarvis_v2/wic/__init__.py:1647` | database or query access |
| `jarvis_v2.wic.__init__.AlertStore._assert_owner` | `src/jarvis_v2/wic/__init__.py:1660` | security or trust-boundary vocabulary |
| `test_acceptance_evidence.AcceptanceEvidenceTests` | `tests/test_acceptance_evidence.py:21` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_acceptance_evidence.AcceptanceEvidenceTests.setUp` | `tests/test_acceptance_evidence.py:22` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_acceptance_evidence.AcceptanceEvidenceTests.seed_history` | `tests/test_acceptance_evidence.py:30` | database or query access |
| `test_acceptance_evidence.AcceptanceEvidenceTests.test_history_limit_boundary_and_invalid_types` | `tests/test_acceptance_evidence.py:55` | database or query access |
| `test_acceptance_evidence.AcceptanceEvidenceTests.test_explicit_module_local_permissions_and_typed_compatibility` | `tests/test_acceptance_evidence.py:163` | security or trust-boundary vocabulary |
| `test_acceptance_evidence.AcceptanceEvidenceTests.test_gate_and_milestone_evidence_fields_are_complete` | `tests/test_acceptance_evidence.py:206` | security or trust-boundary vocabulary |
| `test_aegis_slots.AegisSlotTests` | `tests/test_aegis_slots.py:8` | security or trust-boundary vocabulary |
| `test_aegis_slots.AegisSlotTests.test_in_flight_work_is_not_preempted` | `tests/test_aegis_slots.py:9` | security or trust-boundary vocabulary |
| `test_aegis_slots.AegisSlotTests.test_overlapping_lower_priority_request_remains_fenced` | `tests/test_aegis_slots.py:20` | security or trust-boundary vocabulary |
| `test_aegis_slots.AegisSlotTests.test_guardian_blocks_lower_priority_until_next_compatible_slot` | `tests/test_aegis_slots.py:29` | security or trust-boundary vocabulary |
| `test_aegis_slots.AegisSlotTests.test_guardian_uses_stable_configured_slot_order` | `tests/test_aegis_slots.py:37` | security or trust-boundary vocabulary |
| `test_aegis_slots.AegisSlotTests.test_request_sequence_is_idempotent_and_release_is_strict` | `tests/test_aegis_slots.py:42` | security or trust-boundary vocabulary |
| `test_aegis_slots.AegisSlotTests.test_bounded_sequences_do_not_leak_or_starve_guardian` | `tests/test_aegis_slots.py:63` | security or trust-boundary vocabulary |
| `test_astra_watchdog.load_watchdog` | `tests/test_astra_watchdog.py:9` | filesystem access; security or trust-boundary vocabulary |
| `test_astra_watchdog.WatchdogTests` | `tests/test_astra_watchdog.py:18` | command or process execution; database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_astra_watchdog.WatchdogTests.test_rollback_is_fenced_and_durable_pending_without_pointer` | `tests/test_astra_watchdog.py:19` | command or process execution; database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_astra_watchdog.WatchdogTests.test_activation_fast_forwards_and_records_verified_receipt` | `tests/test_astra_watchdog.py:54` | command or process execution; database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_astra_watchdog.WatchdogTests.test_activation_refuses_control_marker_without_moving_head` | `tests/test_astra_watchdog.py:106` | command or process execution; database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_atlas_core_events.AtlasCoreEventHistoryTests` | `tests/test_atlas_core_events.py:8` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_atlas_core_events.AtlasCoreEventHistoryTests.test_history_is_ordered_bounded_and_excludes_private_values` | `tests/test_atlas_core_events.py:9` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_atlas_core_events.AtlasCoreEventHistoryTests.test_history_for_unknown_task_is_empty` | `tests/test_atlas_core_events.py:30` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_atlas_core_events.AtlasCoreEventHistoryTests.test_duplicate_completion_is_rejected` | `tests/test_atlas_core_events.py:36` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_automation_dispatcher.ReconnectDispatcherTests` | `tests/test_automation_dispatcher.py:22` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_automation_dispatcher.ReconnectDispatcherTests.setUp` | `tests/test_automation_dispatcher.py:23` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_automation_leases.CoordinatorLeaseTests` | `tests/test_automation_leases.py:8` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_automation_leases.CoordinatorLeaseTests.test_renewal_extends_a_live_lease_and_completion_is_idempotent` | `tests/test_automation_leases.py:12` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_automation_leases.CoordinatorLeaseTests.test_expired_lease_is_requeued_and_old_owner_cannot_complete` | `tests/test_automation_leases.py:21` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_automation_leases.CoordinatorLeaseTests.test_stale_or_invalid_renewals_do_not_change_the_queue` | `tests/test_automation_leases.py:31` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_automation_queue_api.CoordinatorQueueTests` | `tests/test_automation_queue_api.py:15` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_automation_queue_api.CoordinatorQueueTests.test_versioned_envelope_round_trip_and_unknown_fields_are_rejected` | `tests/test_automation_queue_api.py:16` | security or trust-boundary vocabulary |
| `test_automation_queue_api.CoordinatorQueueTests.test_existing_task_queue_reopens_without_migration_or_data_loss` | `tests/test_automation_queue_api.py:25` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_automation_queue_api.CoordinatorQueueTests.test_lease_completion_and_duplicate_enqueue_preserve_state` | `tests/test_automation_queue_api.py:36` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_automation_queue_api.CoordinatorQueueTests.test_reopen_requeues_expired_lease_and_duplicate_receipt_is_idempotent` | `tests/test_automation_queue_api.py:47` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_automation_recovery_drill.RecoveryDrillTests` | `tests/test_automation_recovery_drill.py:9` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_automation_recovery_drill.RecoveryDrillTests.test_restored_completed_event_is_not_applied_twice` | `tests/test_automation_recovery_drill.py:10` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_automation_recovery_drill.RecoveryDrillTests.test_replay_after_restore_keeps_effect_idempotent` | `tests/test_automation_recovery_drill.py:43` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_automation_recovery_drill.RecoveryDrillTests.test_replay_limit_is_bounded` | `tests/test_automation_recovery_drill.py:73` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_automation_scheduler.AutomationScheduleTests` | `tests/test_automation_scheduler.py:13` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_automation_scheduler.AutomationScheduleTests.test_schedule_survives_offline_reopen_and_uses_utc` | `tests/test_automation_scheduler.py:14` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_automation_scheduler.AutomationScheduleTests.test_dst_transition_and_replay_use_backend_contract` | `tests/test_automation_scheduler.py:29` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_automation_scheduler.AutomationScheduleTests.test_once_schedule_is_idempotent_and_conflicts_fail` | `tests/test_automation_scheduler.py:43` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_acceptance.BackendAcceptanceTests` | `tests/test_backend_acceptance.py:33` | command or process execution; database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_acceptance.BackendAcceptanceTests.test_scoped_authorization_and_context_reject_cross_scope_data` | `tests/test_backend_acceptance.py:34` | security or trust-boundary vocabulary |
| `test_backend_acceptance.BackendAcceptanceTests.test_linux_authenticated_inference_roundtrip_preserves_context_and_audit` | `tests/test_backend_acceptance.py:107` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_acceptance.BackendAcceptanceTests.test_backup_restore_preserves_owned_backend_state` | `tests/test_backend_acceptance.py:150` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_acceptance.BackendAcceptanceTests.test_create_only_migration_records_provenance_without_touching_source` | `tests/test_backend_acceptance.py:183` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `test_backend_authorization.BackendAuthorizationTests` | `tests/test_backend_authorization.py:12` | security or trust-boundary vocabulary |
| `test_backend_authorization.BackendAuthorizationTests.test_cross_module_grant_requires_exact_owner_approval` | `tests/test_backend_authorization.py:31` | security or trust-boundary vocabulary |
| `test_backend_authorization.BackendAuthorizationTests.test_approval_and_identity_conflicts_fail_closed` | `tests/test_backend_authorization.py:40` | security or trust-boundary vocabulary |
| `test_backend_backup.BackendBackupTests` | `tests/test_backend_backup.py:23` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_backup.BackendBackupTests.make_database` | `tests/test_backend_backup.py:24` | database or query access; security or trust-boundary vocabulary |
| `test_backend_backup.BackendBackupTests.test_backup_and_restore_preserve_schema_data_and_wal_state` | `tests/test_backend_backup.py:33` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_backup.BackendBackupTests.test_destination_is_never_overwritten_and_source_is_not_mutated` | `tests/test_backend_backup.py:62` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_backup.BackendBackupTests.test_explicit_cipher_round_trip_and_digest_fence` | `tests/test_backend_backup.py:76` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_backup.BackendBackupTests.test_wal_sidecar_mismatch_fails_closed` | `tests/test_backend_backup.py:94` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_cloudflare_jobs.CloudflareJobAdapterTests` | `tests/test_backend_cloudflare_jobs.py:9` | external or network access; security or trust-boundary vocabulary |
| `test_backend_cloudflare_jobs.CloudflareJobAdapterTests.setUp` | `tests/test_backend_cloudflare_jobs.py:10` | external or network access; security or trust-boundary vocabulary |
| `test_backend_cloudflare_jobs.CloudflareJobAdapterTests.setUp.transport` | `tests/test_backend_cloudflare_jobs.py:14` | external or network access; security or trust-boundary vocabulary |
| `test_backend_cloudflare_jobs.CloudflareJobAdapterTests.test_create_claim_complete_uses_durable_metadata_and_https_only` | `tests/test_backend_cloudflare_jobs.py:40` | external or network access; security or trust-boundary vocabulary |
| `test_backend_cloudflare_jobs.CloudflareJobAdapterTests.test_invalid_url_and_token_fail_closed_without_network` | `tests/test_backend_cloudflare_jobs.py:52` | security or trust-boundary vocabulary |
| `test_backend_cloudflare_jobs.CloudflareJobAdapterTests.test_response_and_transport_failures_do_not_expose_secret` | `tests/test_backend_cloudflare_jobs.py:60` | security or trust-boundary vocabulary |
| `test_backend_code_index.BackendCodeIndexTests` | `tests/test_backend_code_index.py:12` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_code_index.BackendCodeIndexTests.test_python_symbols_imports_tests_and_provenance_are_searchable` | `tests/test_backend_code_index.py:13` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_code_index.BackendCodeIndexTests.test_sensitive_sources_are_excluded_without_becoming_searchable` | `tests/test_backend_code_index.py:29` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_code_index.BackendCodeIndexTests.test_reindex_replaces_old_blob_and_preserves_source_binding` | `tests/test_backend_code_index.py:42` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_code_index.BackendCodeIndexTests.test_invalid_provenance_and_python_fail_without_partial_index` | `tests/test_backend_code_index.py:51` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_connectors.BackendConnectorTests` | `tests/test_backend_connectors.py:10` | security or trust-boundary vocabulary |
| `test_backend_connectors.BackendConnectorTests.test_each_connector_is_independently_revocable` | `tests/test_backend_connectors.py:11` | security or trust-boundary vocabulary |
| `test_backend_connectors.BackendConnectorTests.test_connector_revoke_does_not_cross_identities_or_connectors` | `tests/test_backend_connectors.py:27` | security or trust-boundary vocabulary |
| `test_backend_connectors.BackendConnectorTests.test_invalid_scope_connector_and_credential_value_fail_closed` | `tests/test_backend_connectors.py:37` | security or trust-boundary vocabulary |
| `test_backend_connectors.BackendConnectorTests.test_idempotent_grant_and_unknown_revoke` | `tests/test_backend_connectors.py:48` | security or trust-boundary vocabulary |
| `test_backend_context.BackendContextTests` | `tests/test_backend_context.py:6` | security or trust-boundary vocabulary |
| `test_backend_context.BackendContextTests.test_protected_sections_survive_history_reduction` | `tests/test_backend_context.py:7` | security or trust-boundary vocabulary |
| `test_backend_context.BackendContextTests.test_protected_content_fails_closed_when_budget_is_too_small` | `tests/test_backend_context.py:24` | security or trust-boundary vocabulary |
| `test_backend_context.BackendContextTests.test_packet_digest_is_deterministic_and_empty_history_is_valid` | `tests/test_backend_context.py:28` | security or trust-boundary vocabulary |
| `test_backend_context.BackendContextTests.test_oversized_context_rejects_repeatedly_without_a_retry_loop` | `tests/test_backend_context.py:44` | security or trust-boundary vocabulary |
| `test_backend_conversation.BackendConversationTests` | `tests/test_backend_conversation.py:11` | command or process execution; database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_conversation.BackendConversationTests.test_backend_exports_are_safe_when_core_is_imported_first` | `tests/test_backend_conversation.py:12` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `test_backend_conversation.BackendConversationTests.test_turns_are_durable_ordered_and_provider_neutral` | `tests/test_backend_conversation.py:24` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_conversation.BackendConversationTests.test_turn_replay_is_idempotent_and_conflicts_are_rejected` | `tests/test_backend_conversation.py:55` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_conversation.BackendConversationTests.test_invalid_and_unbounded_values_are_rejected_without_partial_turn` | `tests/test_backend_conversation.py:85` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_conversation.BackendConversationTests.test_explicit_conversation_creation_is_idempotent_but_metadata_is_bound` | `tests/test_backend_conversation.py:97` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_effects.BackendEffectJournalTests` | `tests/test_backend_effects.py:8` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_effects.BackendEffectJournalTests.test_completed_effect_is_not_executed_again_after_restart` | `tests/test_backend_effects.py:9` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_effects.BackendEffectJournalTests.test_unfinished_effect_requires_reconciliation_before_retry` | `tests/test_backend_effects.py:27` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_effects.BackendEffectJournalTests.test_effect_identity_and_result_replays_are_bound` | `tests/test_backend_effects.py:47` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_effects.BackendEffectJournalTests.test_invalid_effects_do_not_create_records` | `tests/test_backend_effects.py:66` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_event_bus.BackendEventBusTests` | `tests/test_backend_event_bus.py:8` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_event_bus.BackendEventBusTests.test_publish_is_durable_and_idempotent` | `tests/test_backend_event_bus.py:9` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_event_bus.BackendEventBusTests.test_conflicting_idempotency_payload_is_rejected` | `tests/test_backend_event_bus.py:26` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_event_bus.BackendEventBusTests.test_successful_effect_receipt_prevents_duplicate_effect` | `tests/test_backend_event_bus.py:33` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_event_bus.BackendEventBusTests.test_failed_effect_is_retryable_then_completes` | `tests/test_backend_event_bus.py:49` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_event_bus.BackendEventBusTests.test_invalid_envelopes_are_rejected_before_outbox_write` | `tests/test_backend_event_bus.py:66` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_generation_scheduler.GenerationSchedulerTests` | `tests/test_backend_generation_scheduler.py:10` | security or trust-boundary vocabulary |
| `test_backend_generation_scheduler.GenerationSchedulerTests.test_guardian_reservation_and_finish_are_fenced` | `tests/test_backend_generation_scheduler.py:23` | security or trust-boundary vocabulary |
| `test_backend_handoff.BackendHandoffTests` | `tests/test_backend_handoff.py:8` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_handoff.BackendHandoffTests.test_handoff_preserves_task_permissions_effects_and_context_after_restart` | `tests/test_backend_handoff.py:9` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_handoff.BackendHandoffTests.test_handoff_replay_is_idempotent_and_conflicts_fail_closed` | `tests/test_backend_handoff.py:30` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_handoff.BackendHandoffTests.test_handoff_rejects_invalid_or_unbounded_inputs_without_a_record` | `tests/test_backend_handoff.py:44` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_manifest.manifest` | `tests/test_backend_manifest.py:11` | security or trust-boundary vocabulary |
| `test_backend_ollama_profile.OllamaProfileTests` | `tests/test_backend_ollama_profile.py:13` | security or trust-boundary vocabulary |
| `test_backend_ollama_profile.OllamaProfileTests.test_measured_linux_probe_is_redacted_and_bound_to_profile` | `tests/test_backend_ollama_profile.py:24` | security or trust-boundary vocabulary |
| `test_backend_protocol_adapters.BackendProtocolAdapterTests` | `tests/test_backend_protocol_adapters.py:25` | security or trust-boundary vocabulary |
| `test_backend_protocol_adapters.BackendProtocolAdapterTests.test_chat_adapter_encodes_and_decodes_tool_arguments` | `tests/test_backend_protocol_adapters.py:41` | security or trust-boundary vocabulary |
| `test_backend_provider_registry.capability` | `tests/test_backend_provider_registry.py:11` | security or trust-boundary vocabulary |
| `test_backend_provider_registry.BackendProviderRegistryTests` | `tests/test_backend_provider_registry.py:25` | security or trust-boundary vocabulary |
| `test_backend_provider_registry.BackendProviderRegistryTests.test_compatible_request_is_selected` | `tests/test_backend_provider_registry.py:29` | security or trust-boundary vocabulary |
| `test_backend_provider_registry.BackendProviderRegistryTests.test_each_dispatch_requirement_blocks_incompatible_provider` | `tests/test_backend_provider_registry.py:41` | security or trust-boundary vocabulary |
| `test_backend_retrieval.BackendRetrievalTests` | `tests/test_backend_retrieval.py:8` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_retrieval.BackendRetrievalTests.test_search_returns_scope_source_timestamp_and_citation` | `tests/test_backend_retrieval.py:9` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_retrieval.BackendRetrievalTests.test_source_filter_and_replay_are_deterministic` | `tests/test_backend_retrieval.py:31` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_retrieval.BackendRetrievalTests.test_invalid_queries_and_unbounded_documents_are_rejected` | `tests/test_backend_retrieval.py:45` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_retrieval.BackendRetrievalTests.test_optional_reranker_preserves_search_result_shape` | `tests/test_backend_retrieval.py:59` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_scheduler.BackendSchedulerTests` | `tests/test_backend_scheduler.py:13` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_scheduler.BackendSchedulerTests.test_one_shot_survives_reopen_and_uses_utc` | `tests/test_backend_scheduler.py:14` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_scheduler.BackendSchedulerTests.test_daily_wall_time_survives_fall_dst_transition` | `tests/test_backend_scheduler.py:27` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_scheduler.BackendSchedulerTests.test_spring_gap_moves_forward_and_replay_is_idempotent` | `tests/test_backend_scheduler.py:42` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_scheduler.BackendSchedulerTests.test_invalid_timezone_and_message_are_rejected` | `tests/test_backend_scheduler.py:61` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_storage.migration` | `tests/test_backend_storage.py:13` | database or query access |
| `test_backend_storage.BackendStorageTests` | `tests/test_backend_storage.py:27` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_storage.BackendStorageTests.test_default_migration_is_idempotent_and_backend_owns_rows` | `tests/test_backend_storage.py:28` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_storage.BackendStorageTests.test_module_ownership_fences_cross_module_writes` | `tests/test_backend_storage.py:47` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_storage.BackendStorageTests.test_failed_migration_rolls_back_table_and_ledger` | `tests/test_backend_storage.py:61` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_storage.BackendStorageTests.test_rollback_removes_owned_table_and_preserves_integrity` | `tests/test_backend_storage.py:73` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_storage.BackendStorageTests.test_changed_definition_and_invalid_plan_fail_closed` | `tests/test_backend_storage.py:85` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_backend_task_capability.TaskCapabilityTests` | `tests/test_backend_task_capability.py:12` | filesystem access; security or trust-boundary vocabulary |
| `test_backend_task_capability.TaskCapabilityTests.test_manifest_allows_only_granted_operation_and_path` | `tests/test_backend_task_capability.py:13` | filesystem access; security or trust-boundary vocabulary |
| `test_backend_task_capability.TaskCapabilityTests.test_disallowed_operation_and_path_fail_closed` | `tests/test_backend_task_capability.py:22` | filesystem access; security or trust-boundary vocabulary |
| `test_backend_task_capability.TaskCapabilityTests.test_relative_and_symlink_escape_paths_are_rejected` | `tests/test_backend_task_capability.py:33` | filesystem access; security or trust-boundary vocabulary |
| `test_backend_task_capability.TaskCapabilityTests.test_sensitive_paths_are_rejected_even_inside_an_allowed_root` | `tests/test_backend_task_capability.py:47` | filesystem access; security or trust-boundary vocabulary |
| `test_batch_cycle.BatchCycleFailurePropagationTests` | `tests/test_batch_cycle.py:13` | command or process execution; database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_batch_cycle.BatchCycleFailurePropagationTests.run_fixture` | `tests/test_batch_cycle.py:14` | command or process execution; database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_ci_workflow.CIWorkflowTests` | `tests/test_ci_workflow.py:18` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `test_ci_workflow.CIWorkflowTests.test_report_rejects_raw_payloads_and_extra_fields` | `tests/test_ci_workflow.py:66` | security or trust-boundary vocabulary |
| `test_ci_workflow.CIWorkflowTests.test_report_rejects_escape_and_symlink_without_writing` | `tests/test_ci_workflow.py:81` | filesystem access; security or trust-boundary vocabulary |
| `test_ci_workflow.CIWorkflowTests.test_cli_writes_complete_bounded_receipt` | `tests/test_ci_workflow.py:96` | filesystem access; security or trust-boundary vocabulary |
| `test_ci_workflow.CIWorkflowTests.test_public_check_and_report_clis` | `tests/test_ci_workflow.py:137` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `test_ci_workflow.CIWorkflowTests.test_secret_and_workflow_boundaries_reject_common_unsafe_inputs` | `tests/test_ci_workflow.py:179` | security or trust-boundary vocabulary |
| `test_cloudflare_dashboard.call` | `tests/test_cloudflare_dashboard.mjs:32` | security or trust-boundary vocabulary |
| `test_cloudflare_heartbeat.call` | `tests/test_cloudflare_heartbeat.mjs:36` | security or trust-boundary vocabulary |
| `test_core_budget.CoreBudgetTests` | `tests/test_core_budget.py:6` | security or trust-boundary vocabulary |
| `test_core_budget.CoreBudgetTests.test_guardian_reservation_blocks_lower_priority_without_preemption` | `tests/test_core_budget.py:16` | security or trust-boundary vocabulary |
| `test_core_budget.CoreBudgetTests.test_guardian_lock_preserves_disjoint_budget_capacity` | `tests/test_core_budget.py:25` | security or trust-boundary vocabulary |
| `test_core_budget.CoreBudgetTests.test_guardian_reservation_is_not_starved_by_repeated_safe_work` | `tests/test_core_budget.py:42` | security or trust-boundary vocabulary |
| `test_core_controls.CoreControlTests` | `tests/test_core_controls.py:9` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_controls.CoreControlTests.test_stop_blocks_dispatch_and_survives_restart` | `tests/test_core_controls.py:10` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_controls.CoreControlTests.test_pause_and_resume_preserve_pending_approval` | `tests/test_core_controls.py:27` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_controls.CoreControlTests.test_control_reason_is_bounded` | `tests/test_core_controls.py:59` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_dependencies.CoreDependencyTests` | `tests/test_core_dependencies.py:9` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_dependencies.CoreDependencyTests.test_pending_dependency_does_not_block_ready_work_and_resumes_after_result` | `tests/test_core_dependencies.py:10` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_dependencies.CoreDependencyTests.test_missing_and_cyclic_dependencies_are_not_claimed` | `tests/test_core_dependencies.py:21` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_dependencies.CoreDependencyTests.test_dependency_declarations_are_validated_and_dependents_are_discoverable` | `tests/test_core_dependencies.py:31` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_dispatch.CoreDispatchTests` | `tests/test_core_dispatch.py:9` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_dispatch.CoreDispatchTests.test_dispatch_contains_scope_acceptance_and_correlation_and_reconstructs` | `tests/test_core_dispatch.py:10` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_dispatch.CoreDispatchTests.test_one_claim_and_one_ack_are_fenced_and_idempotent` | `tests/test_core_dispatch.py:35` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_dispatch.CoreDispatchTests.test_dispatch_payload_conflicts_and_unbounded_values_are_rejected` | `tests/test_core_dispatch.py:60` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_event_guard.CoreEventGuardTests` | `tests/test_core_event_guard.py:12` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_event_guard.CoreEventGuardTests.test_duplicate_event_id_is_idempotent_and_storm_is_bounded` | `tests/test_core_event_guard.py:13` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_event_guard.CoreEventGuardTests.test_repeated_failures_quarantine_and_redact_diagnostics` | `tests/test_core_event_guard.py:32` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_event_sessions.CoreEventSessionTests` | `tests/test_core_event_sessions.py:9` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_event_sessions.CoreEventSessionTests.test_event_session_is_separate_and_reconstructs_causal_chain` | `tests/test_core_event_sessions.py:10` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_event_sessions.CoreEventSessionTests.test_event_replay_ack_is_durable_and_event_ids_are_idempotent` | `tests/test_core_event_sessions.py:33` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_event_sessions.CoreEventSessionTests.test_event_session_rejects_unbounded_detail_and_invalid_replay_limit` | `tests/test_core_event_sessions.py:49` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_fault_injection.CoreFaultInjectionTests` | `tests/test_core_fault_injection.py:9` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_fault_injection.CoreFaultInjectionTests.test_committed_completion_survives_reopen_without_phantom_replay` | `tests/test_core_fault_injection.py:10` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_fault_injection.CoreFaultInjectionTests.test_priority_fifo_is_stable_after_a_failed_claim` | `tests/test_core_fault_injection.py:27` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_fault_injection.CoreFaultInjectionTests.test_dispatch_claim_is_isolated_and_wrong_executor_cannot_ack` | `tests/test_core_fault_injection.py:39` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_intents.intent` | `tests/test_core_intents.py:9` | security or trust-boundary vocabulary |
| `test_core_intents.CoreIntentTests` | `tests/test_core_intents.py:24` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_intents.CoreIntentTests.test_safe_owner_intent_is_idempotently_enqueued` | `tests/test_core_intents.py:25` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_intents.CoreIntentTests.test_ambiguous_or_sensitive_intent_waits_for_exact_explicit_approval` | `tests/test_core_intents.py:35` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_intents.CoreIntentTests.test_rejected_sensitive_intent_is_recorded_without_a_task` | `tests/test_core_intents.py:50` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_intents.CoreIntentTests.test_intent_conflicts_and_invalid_contracts_are_rejected` | `tests/test_core_intents.py:61` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_priority.CorePriorityTests` | `tests/test_core_priority.py:8` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_priority.CorePriorityTests.test_priority_fifo_and_blocked_work` | `tests/test_core_priority.py:9` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_priority.CorePriorityTests.test_leased_block_requires_current_lease_and_can_reenter_fifo` | `tests/test_core_priority.py:25` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_queue_replay.CoreQueueReplayTests` | `tests/test_core_queue_replay.py:8` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_queue_replay.CoreQueueReplayTests.test_events_survive_restart_and_are_replayed_once_after_ack` | `tests/test_core_queue_replay.py:9` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_queue_replay.CoreQueueReplayTests.test_replay_is_consumer_scoped_and_bounded` | `tests/test_core_queue_replay.py:33` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_registry.CoreRegistryTests` | `tests/test_core_registry.py:12` | filesystem access; security or trust-boundary vocabulary |
| `test_core_registry.CoreRegistryTests.test_config_registers_ten_stable_modules_without_business` | `tests/test_core_registry.py:13` | security or trust-boundary vocabulary |
| `test_core_registry.CoreRegistryTests.test_invalid_identity_scope_and_business_config_are_rejected` | `tests/test_core_registry.py:33` | filesystem access; security or trust-boundary vocabulary |
| `test_core_sessions.CoreSessionTests` | `tests/test_core_sessions.py:9` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_sessions.CoreSessionTests.test_parent_session_reconstructs_decisions_handoffs_and_receipts_after_restart` | `tests/test_core_sessions.py:10` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_sessions.CoreSessionTests.test_receipt_and_checkpoint_replays_are_idempotent_and_conflicts_are_rejected` | `tests/test_core_sessions.py:44` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_sessions.CoreSessionTests.test_store_reuses_an_existing_connection_and_bounds_inputs` | `tests/test_core_sessions.py:59` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_timeline.CoreTimelineTests` | `tests/test_core_timeline.py:9` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_timeline.CoreTimelineTests.test_timeline_joins_sources_states_and_hashed_outcomes` | `tests/test_core_timeline.py:10` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_core_timeline.CoreTimelineTests.test_progress_is_bounded_and_query_is_read_only` | `tests/test_core_timeline.py:45` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_acceptance.FinanceAcceptanceTests` | `tests/test_finance_acceptance.py:21` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_acceptance.FinanceAcceptanceTests.test_revocation_stops_sync_and_fixture_budget_report_remain_stable` | `tests/test_finance_acceptance.py:22` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_advice.FinanceAdviceTests` | `tests/test_finance_advice.py:19` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_advice.FinanceAdviceTests.store` | `tests/test_finance_advice.py:20` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_advice.FinanceAdviceTests.test_without_consent_advice_is_bounded_and_requires_consent` | `tests/test_finance_advice.py:33` | database or query access |
| `test_finance_alerts.FinanceAlertTests` | `tests/test_finance_alerts.py:19` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_alerts.FinanceAlertTests.test_recurring_alert_is_explainable_source_linked_and_suppressible` | `tests/test_finance_alerts.py:20` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_alerts.FinanceAlertTests.test_unusual_alert_uses_a_bounded_explainable_threshold` | `tests/test_finance_alerts.py:39` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_alerts.FinanceAlertTests.test_scope_isolation_and_invalid_multiplier_are_enforced` | `tests/test_finance_alerts.py:55` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_dashboard.FinanceDashboardTests` | `tests/test_finance_dashboard.py:19` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_dashboard.FinanceDashboardTests.test_estimated_balances_are_scoped_labeled_and_timestamped` | `tests/test_finance_dashboard.py:20` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_dashboard.FinanceDashboardTests.test_reconciled_balance_overrides_estimate_without_leaking_scope` | `tests/test_finance_dashboard.py:34` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_dashboard.FinanceDashboardTests.test_authoritative_balance_must_match_a_known_account_and_status` | `tests/test_finance_dashboard.py:47` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_ingestion.FinanceIngestionTests` | `tests/test_finance_ingestion.py:31` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_ingestion.FinanceIngestionTests.test_sync_preserves_original_ids_timestamps_and_integer_satang` | `tests/test_finance_ingestion.py:32` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_ingestion.FinanceIngestionTests.test_replaying_identical_snapshot_is_idempotent` | `tests/test_finance_ingestion.py:41` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_ingestion.FinanceIngestionTests.test_newer_source_revision_updates_one_row_without_duplication` | `tests/test_finance_ingestion.py:48` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_ingestion.FinanceIngestionTests.test_scope_isolation_is_required_for_reads` | `tests/test_finance_ingestion.py:56` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_ingestion.FinanceIngestionTests.test_source_mappings_are_normalized_without_losing_original_ids` | `tests/test_finance_ingestion.py:61` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_ingestion.FinanceIngestionTests.test_conflicting_revision_rolls_back_the_whole_snapshot` | `tests/test_finance_ingestion.py:81` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_mira_audit.MiraAuditTests` | `tests/test_finance_mira_audit.py:10` | security or trust-boundary vocabulary |
| `test_finance_mira_audit.MiraAuditTests.test_secret_values_are_not_part_of_evidence` | `tests/test_finance_mira_audit.py:58` | security or trust-boundary vocabulary |
| `test_finance_mira_connector.MiraConnectorTokenTests` | `tests/test_finance_mira_connector.py:9` | security or trust-boundary vocabulary |
| `test_finance_mira_connector.MiraConnectorTokenTests.test_issue_is_short_lived_scoped_and_identity_bound` | `tests/test_finance_mira_connector.py:10` | security or trust-boundary vocabulary |
| `test_finance_mira_connector.MiraConnectorTokenTests.test_revoke_is_immediate_and_audit_is_redacted` | `tests/test_finance_mira_connector.py:19` | security or trust-boundary vocabulary |
| `test_finance_mira_connector.MiraConnectorTokenTests.test_token_registration_is_idempotent_but_conflicts_fail` | `tests/test_finance_mira_connector.py:31` | security or trust-boundary vocabulary |
| `test_finance_paper.FinancePaperTests` | `tests/test_finance_paper.py:21` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_paper.FinancePaperTests.test_paper_cash_and_positions_are_separate_from_finance_store` | `tests/test_finance_paper.py:22` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_paper.FinancePaperTests.test_duplicate_order_is_idempotent_and_insufficient_cash_fails` | `tests/test_finance_paper.py:38` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_paper.FinancePaperTests.test_sell_cannot_create_a_position_or_touch_real_accounts` | `tests/test_finance_paper.py:49` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_paper.FinancePaperTests.test_fill_policy_records_spread_slippage_and_fee` | `tests/test_finance_paper.py:56` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_paper.FinancePaperTests.test_market_hours_and_liquidity_reject_invalid_fills` | `tests/test_finance_paper.py:67` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_planning.FinancePlanningTests` | `tests/test_finance_planning.py:20` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_planning.FinancePlanningTests.test_forecast_is_uncertain_and_uses_historical_net` | `tests/test_finance_planning.py:21` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_planning.FinancePlanningTests.test_goal_progress_does_not_double_debit_transaction_totals` | `tests/test_finance_planning.py:36` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_reconciliation.FinanceReconciliationTests` | `tests/test_finance_reconciliation.py:17` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_reconciliation.FinanceReconciliationTests.test_transfer_is_applied_once_and_has_zero_net_effect` | `tests/test_finance_reconciliation.py:18` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_reconciliation.FinanceReconciliationTests.test_savings_has_transfer_semantics_and_adjustment_is_applied_once` | `tests/test_finance_reconciliation.py:27` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_reconciliation.FinanceReconciliationTests.test_newer_revision_replaces_effect_without_creating_a_second_operation` | `tests/test_finance_reconciliation.py:37` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_reconciliation.FinanceReconciliationTests.test_scope_isolation_and_mapping_input_are_enforced` | `tests/test_finance_reconciliation.py:44` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_reconciliation.FinanceReconciliationTests.test_invalid_transfer_and_stale_conflict_fail_closed` | `tests/test_finance_reconciliation.py:52` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_reports.FinanceReportTests` | `tests/test_finance_reports.py:19` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_reports.FinanceReportTests.test_summary_totals_breakdowns_and_trend_match_fixture_ledger` | `tests/test_finance_reports.py:20` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_reports.FinanceReportTests.test_period_filter_and_person_scope_are_applied_before_aggregation` | `tests/test_finance_reports.py:39` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_finance_reports.FinanceReportTests.test_reversed_period_and_bad_date_fail_closed` | `tests/test_finance_reports.py:48` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_foundation.FoundationTests` | `tests/test_foundation.py:10` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_foundation.FoundationTests.test_fifo_same_priority` | `tests/test_foundation.py:11` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_foundation.FoundationTests.test_priority` | `tests/test_foundation.py:19` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_foundation.FoundationTests.test_lease_receipt` | `tests/test_foundation.py:26` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_foundation.FoundationTests.test_guardian_waits_for_active` | `tests/test_foundation.py:36` | security or trust-boundary vocabulary |
| `test_foundation.FoundationTests.test_guardian_waiting_blocks_background_claim` | `tests/test_foundation.py:46` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_foundation.FoundationTests.test_release_example_blocked` | `tests/test_foundation.py:54` | filesystem access; security or trust-boundary vocabulary |
| `test_git_policy.PolicyTests` | `tests/test_git_policy.py:3` | database or query access; security or trust-boundary vocabulary |
| `test_git_policy.PolicyTests.test_good_branch` | `tests/test_git_policy.py:4` | security or trust-boundary vocabulary |
| `test_git_policy.PolicyTests.test_good_commit` | `tests/test_git_policy.py:10` | security or trust-boundary vocabulary |
| `test_git_policy.PolicyTests.test_bad_commit` | `tests/test_git_policy.py:13` | database or query access |
| `test_guardian_controller.GuardianControllerTests` | `tests/test_guardian_controller.py:9` | filesystem access; security or trust-boundary vocabulary |
| `test_guardian_controller.GuardianControllerTests._manager` | `tests/test_guardian_controller.py:10` | security or trust-boundary vocabulary |
| `test_guardian_controller.GuardianControllerTests.test_verified_artifact_is_the_only_launchable_controller` | `tests/test_guardian_controller.py:24` | filesystem access; security or trust-boundary vocabulary |
| `test_guardian_controller.GuardianControllerTests.test_digest_change_and_symlink_fail_closed` | `tests/test_guardian_controller.py:39` | filesystem access; security or trust-boundary vocabulary |
| `test_guardian_controller.GuardianControllerTests.test_control_markers_are_honored_before_artifact_execution` | `tests/test_guardian_controller.py:53` | filesystem access; security or trust-boundary vocabulary |
| `test_guardian_controller.GuardianControllerTests.test_command_must_be_direct_and_artifact_must_be_private_to_group` | `tests/test_guardian_controller.py:64` | filesystem access; security or trust-boundary vocabulary |
| `test_guardian_cutover.GuardianCutoverTests` | `tests/test_guardian_cutover.py:10` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_guardian_cutover.GuardianCutoverTests.setUp` | `tests/test_guardian_cutover.py:11` | database or query access; security or trust-boundary vocabulary |
| `test_guardian_cutover.GuardianCutoverTests._readiness` | `tests/test_guardian_cutover.py:22` | database or query access; security or trust-boundary vocabulary |
| `test_guardian_cutover.GuardianCutoverTests.test_ready_cutover_fences_old_writer_and_keeps_one_authority` | `tests/test_guardian_cutover.py:35` | security or trust-boundary vocabulary |
| `test_guardian_cutover.GuardianCutoverTests.test_unverified_sync_degrades_without_handoff` | `tests/test_guardian_cutover.py:48` | security or trust-boundary vocabulary |
| `test_guardian_cutover.GuardianCutoverTests.test_capacity_and_schema_mismatch_do_not_fabricate_readiness` | `tests/test_guardian_cutover.py:63` | database or query access; security or trust-boundary vocabulary |
| `test_guardian_cutover.GuardianCutoverTests.test_failback_requires_failed_health_and_fences_bad_standby` | `tests/test_guardian_cutover.py:72` | security or trust-boundary vocabulary |
| `test_guardian_cutover.GuardianCutoverTests.test_control_marker_blocks_cutover` | `tests/test_guardian_cutover.py:90` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_guardian_fault_injection.GuardianFaultInjectionTests` | `tests/test_guardian_fault_injection.py:16` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_guardian_fault_injection.GuardianFaultInjectionTests._controller` | `tests/test_guardian_fault_injection.py:17` | security or trust-boundary vocabulary |
| `test_guardian_fault_injection.GuardianFaultInjectionTests.test_p0_controls_survive_recovery_denial` | `tests/test_guardian_fault_injection.py:29` | filesystem access; security or trust-boundary vocabulary |
| `test_guardian_fault_injection.GuardianFaultInjectionTests.test_p1_crash_loop_is_bounded_and_history_is_retained` | `tests/test_guardian_fault_injection.py:47` | filesystem access; security or trust-boundary vocabulary |
| `test_guardian_fault_injection.GuardianFaultInjectionTests.test_p2_stale_writer_cannot_survive_cutover` | `tests/test_guardian_fault_injection.py:73` | database or query access; security or trust-boundary vocabulary |
| `test_guardian_fault_injection.GuardianFaultInjectionTests.test_p3_bad_canary_restores_artifact_without_state_loss` | `tests/test_guardian_fault_injection.py:102` | filesystem access; security or trust-boundary vocabulary |
| `test_guardian_fault_injection.GuardianFaultInjectionTests.test_unverified_cutover_degrades_without_changing_authority` | `tests/test_guardian_fault_injection.py:151` | database or query access; security or trust-boundary vocabulary |
| `test_guardian_fencing.GuardianFencingTests` | `tests/test_guardian_fencing.py:6` | security or trust-boundary vocabulary |
| `test_guardian_fencing.GuardianFencingTests.setUp` | `tests/test_guardian_fencing.py:7` | security or trust-boundary vocabulary |
| `test_guardian_fencing.GuardianFencingTests.test_only_one_writer_and_stale_lease_is_rejected_after_handoff` | `tests/test_guardian_fencing.py:11` | security or trust-boundary vocabulary |
| `test_guardian_fencing.GuardianFencingTests.test_expiry_allows_new_generation_but_old_lease_cannot_return` | `tests/test_guardian_fencing.py:22` | security or trust-boundary vocabulary |
| `test_guardian_fencing.GuardianFencingTests.test_renew_and_release_require_current_lease` | `tests/test_guardian_fencing.py:30` | security or trust-boundary vocabulary |
| `test_guardian_fencing.GuardianFencingTests.test_invalid_ttl_and_owner_fail_closed` | `tests/test_guardian_fencing.py:39` | security or trust-boundary vocabulary |
| `test_guardian_model.GuardianModelTests` | `tests/test_guardian_model.py:9` | security or trust-boundary vocabulary |
| `test_guardian_model.GuardianModelTests.test_local_model_and_inference_are_probed_without_retaining_output` | `tests/test_guardian_model.py:10` | security or trust-boundary vocabulary |
| `test_guardian_model.GuardianModelTests.test_local_model_and_inference_are_probed_without_retaining_output.runner` | `tests/test_guardian_model.py:13` | security or trust-boundary vocabulary |
| `test_guardian_model.GuardianModelTests.test_missing_model_does_not_fallback_and_stop_remains_available` | `tests/test_guardian_model.py:27` | security or trust-boundary vocabulary |
| `test_guardian_model.GuardianModelTests.test_inference_failure_is_distinct_from_model_presence` | `tests/test_guardian_model.py:37` | security or trust-boundary vocabulary |
| `test_guardian_model.GuardianModelTests.test_inference_failure_is_distinct_from_model_presence.runner` | `tests/test_guardian_model.py:38` | security or trust-boundary vocabulary |
| `test_guardian_recovery.GuardianRecoveryTests` | `tests/test_guardian_recovery.py:11` | filesystem access; security or trust-boundary vocabulary |
| `test_guardian_recovery.GuardianRecoveryTests._controller` | `tests/test_guardian_recovery.py:12` | security or trust-boundary vocabulary |
| `test_guardian_recovery.GuardianRecoveryTests.test_one_verified_boot_attempt_starts_controller` | `tests/test_guardian_recovery.py:24` | filesystem access; security or trust-boundary vocabulary |
| `test_guardian_recovery.GuardianRecoveryTests.test_crash_loop_enters_safe_mode_at_bounded_attempt_limit` | `tests/test_guardian_recovery.py:39` | filesystem access; security or trust-boundary vocabulary |
| `test_guardian_recovery.GuardianRecoveryTests.test_crash_loop_enters_safe_mode_at_bounded_attempt_limit.crash` | `tests/test_guardian_recovery.py:43` | security or trust-boundary vocabulary |
| `test_guardian_recovery.GuardianRecoveryTests.test_stop_quota_and_approval_are_preserved` | `tests/test_guardian_recovery.py:64` | filesystem access; security or trust-boundary vocabulary |
| `test_guardian_recovery.GuardianRecoveryTests.test_invalid_request_fails_closed` | `tests/test_guardian_recovery.py:86` | filesystem access; security or trust-boundary vocabulary |
| `test_guardian_release.GuardianReleaseTests` | `tests/test_guardian_release.py:10` | filesystem access; security or trust-boundary vocabulary |
| `test_guardian_release.GuardianReleaseTests._manifest` | `tests/test_guardian_release.py:11` | filesystem access; security or trust-boundary vocabulary |
| `test_guardian_release.GuardianReleaseTests.test_only_evidence_bound_candidate_with_closed_route_is_eligible` | `tests/test_guardian_release.py:43` | filesystem access; security or trust-boundary vocabulary |
| `test_guardian_release.GuardianReleaseTests.test_missing_qc_evidence_is_not_accepted` | `tests/test_guardian_release.py:49` | filesystem access; security or trust-boundary vocabulary |
| `test_guardian_release.GuardianReleaseTests.test_open_or_extended_route_gate_is_rejected` | `tests/test_guardian_release.py:59` | filesystem access; security or trust-boundary vocabulary |
| `test_guardian_release.GuardianReleaseTests.test_artifact_change_invalidates_canary` | `tests/test_guardian_release.py:69` | filesystem access; security or trust-boundary vocabulary |
| `test_guardian_rollback.GuardianRollbackTests` | `tests/test_guardian_rollback.py:14` | filesystem access; security or trust-boundary vocabulary |
| `test_guardian_rollback.GuardianRollbackTests._manifest` | `tests/test_guardian_rollback.py:15` | filesystem access; security or trust-boundary vocabulary |
| `test_guardian_rollback.GuardianRollbackTests.test_failed_canary_restores_last_known_good_and_preserves_state` | `tests/test_guardian_rollback.py:62` | filesystem access; security or trust-boundary vocabulary |
| `test_guardian_rollback.GuardianRollbackTests.test_healthy_canary_cannot_trigger_rollback` | `tests/test_guardian_rollback.py:78` | filesystem access; security or trust-boundary vocabulary |
| `test_guardian_rollback.GuardianRollbackTests.test_tampered_last_known_good_is_rejected` | `tests/test_guardian_rollback.py:83` | filesystem access; security or trust-boundary vocabulary |
| `test_guardian_rollback.GuardianRollbackTests.test_unsafe_path_and_target_mismatch_are_rejected` | `tests/test_guardian_rollback.py:91` | filesystem access; security or trust-boundary vocabulary |
| `test_guardian_standby.GuardianStandbyTests` | `tests/test_guardian_standby.py:9` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_guardian_standby.GuardianStandbyTests._launcher` | `tests/test_guardian_standby.py:10` | database or query access; security or trust-boundary vocabulary |
| `test_guardian_standby.GuardianStandbyTests.test_matching_schema_and_explicit_capacity_start_is_isolated` | `tests/test_guardian_standby.py:23` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_guardian_standby.GuardianStandbyTests.test_matching_schema_and_explicit_capacity_start_is_isolated.runner` | `tests/test_guardian_standby.py:26` | security or trust-boundary vocabulary |
| `test_guardian_standby.GuardianStandbyTests.test_capacity_is_not_assumed_or_probed` | `tests/test_guardian_standby.py:43` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_guardian_standby.GuardianStandbyTests.test_schema_and_state_mismatch_do_not_start` | `tests/test_guardian_standby.py:57` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_guardian_standby.GuardianStandbyTests.test_active_control_marker_blocks_start` | `tests/test_guardian_standby.py:69` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_health.HealthTests` | `tests/test_health.py:14` | command or process execution; database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_health.HealthTests.test_health_reads_without_creating_or_mutating_database` | `tests/test_health.py:15` | command or process execution; database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_health.HealthTests.test_health_rejects_missing_canonical_database` | `tests/test_health.py:50` | filesystem access; security or trust-boundary vocabulary |
| `test_health.HealthTests.test_health_reads_fresh_native_runtime_without_historical_ledger` | `tests/test_health.py:55` | command or process execution; database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_health.HealthTests.test_cli_health_returns_structured_state` | `tests/test_health.py:76` | command or process execution; security or trust-boundary vocabulary |
| `test_importer.ImporterTests` | `tests/test_importer.py:8` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `test_importer.ImporterTests.test_fixture_import_dry_run_then_apply` | `tests/test_importer.py:9` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `test_importer.ImporterTests.test_unsafe_target` | `tests/test_importer.py:29` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `test_mig_015_acceptance.Mig015AcceptanceTests` | `tests/test_mig_015_acceptance.py:16` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_mig_015_acceptance.Mig015AcceptanceTests.test_identity_manifest_and_operator_docs_use_approved_roles` | `tests/test_mig_015_acceptance.py:17` | security or trust-boundary vocabulary |
| `test_mig_015_acceptance.Mig015AcceptanceTests.test_native_snapshot_is_read_only_and_does_not_invoke_runner` | `tests/test_mig_015_acceptance.py:30` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_mig_016_identity.Mig016IdentityTests` | `tests/test_mig_016_identity.py:17` | command or process execution; database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_mig_016_identity.Mig016IdentityTests.test_receipts_add_atlas_identity_without_rewriting_records` | `tests/test_mig_016_identity.py:27` | command or process execution; database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_migration_compatibility.MigrationCompatibilityTests` | `tests/test_migration_compatibility.py:16` | filesystem access; security or trust-boundary vocabulary |
| `test_migration_compatibility.MigrationCompatibilityTests.test_snapshot_contains_no_legacy_source_content` | `tests/test_migration_compatibility.py:26` | security or trust-boundary vocabulary |
| `test_migration_compatibility.MigrationCompatibilityTests.test_tampered_staged_blob_fails_closed` | `tests/test_migration_compatibility.py:32` | filesystem access; security or trust-boundary vocabulary |
| `test_migration_compatibility.MigrationCompatibilityTests.test_incomplete_contract_fails_closed` | `tests/test_migration_compatibility.py:41` | filesystem access; security or trust-boundary vocabulary |
| `test_migration_guardrails.MigrationGuardrailTests` | `tests/test_migration_guardrails.py:10` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `test_migration_guardrails.MigrationGuardrailTests.setUp` | `tests/test_migration_guardrails.py:11` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `test_migration_guardrails.MigrationGuardrailTests.setUp.git` | `tests/test_migration_guardrails.py:18` | command or process execution; security or trust-boundary vocabulary |
| `test_migration_guardrails.MigrationGuardrailTests.test_case_only_collisions_fail_before_writing` | `tests/test_migration_guardrails.py:64` | filesystem access |
| `test_monitor.MonitorTests` | `tests/test_monitor.py:37` | command or process execution; database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_monitor.MonitorTests._astra` | `tests/test_monitor.py:38` | database or query access; security or trust-boundary vocabulary |
| `test_monitor.MonitorTests.test_missing_database_never_created` | `tests/test_monitor.py:64` | filesystem access; security or trust-boundary vocabulary |
| `test_monitor.MonitorTests.test_astra_status_worker_slot_progress_and_controls` | `tests/test_monitor.py:71` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_monitor.MonitorTests.test_old_run_events_do_not_fabricate_current_worker_slot` | `tests/test_monitor.py:96` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_monitor.MonitorTests.test_astra_runtime_version_comes_from_read_only_settings` | `tests/test_monitor.py:111` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_monitor.MonitorTests.test_no_raw_spec_in_json_and_no_objectives` | `tests/test_monitor.py:121` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_monitor.MonitorTests.test_wal_updates_seen_without_writes` | `tests/test_monitor.py:134` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_monitor.MonitorTests.test_native_atlas_queue_and_auto_detection` | `tests/test_monitor.py:148` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_monitor.MonitorTests.test_unrecognized_db_refused` | `tests/test_monitor.py:168` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_monitor.MonitorTests.test_cli_one_snapshot_prints_json_and_is_not_runner` | `tests/test_monitor.py:175` | command or process execution; database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_monitor.MonitorTests.test_terminal_escape_sanitized` | `tests/test_monitor.py:188` | security or trust-boundary vocabulary |
| `test_monitor.MonitorTests.test_auto_prefers_native_atlas_and_explicit_astra_stays_legacy` | `tests/test_monitor.py:199` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_monitor_supervision.SupervisorTelemetryTests` | `tests/test_monitor_supervision.py:28` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_monitor_supervision.SupervisorTelemetryTests._fixture` | `tests/test_monitor_supervision.py:29` | database or query access; security or trust-boundary vocabulary |
| `test_monitor_supervision.SupervisorTelemetryTests.test_legacy_astra_db_gracefully_reports_missing_lanes` | `tests/test_monitor_supervision.py:108` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_monitor_supervision.SupervisorTelemetryTests.test_new_lanes_queues_failures_and_upgrade_without_private_data` | `tests/test_monitor_supervision.py:124` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_monitor_supervision.SupervisorTelemetryTests.test_unknown_event_and_failure_values_are_redacted` | `tests/test_monitor_supervision.py:152` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_native_controller.NativeControllerTests` | `tests/test_native_controller.py:8` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_native_controller.NativeControllerTests.test_empty_native_cycle_is_a_safe_idle_without_an_executor` | `tests/test_native_controller.py:9` | filesystem access; security or trust-boundary vocabulary |
| `test_native_controller.NativeControllerTests.test_process_lock_fences_a_second_native_controller_and_releases_on_close` | `tests/test_native_controller.py:16` | filesystem access; security or trust-boundary vocabulary |
| `test_native_controller.NativeControllerTests.test_controls_stop_admission_before_a_task_is_claimed` | `tests/test_native_controller.py:27` | filesystem access; security or trust-boundary vocabulary |
| `test_native_controller.NativeControllerTests.test_executor_completion_and_failure_are_digest_only_and_durable` | `tests/test_native_controller.py:39` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_native_controller.NativeControllerTests.test_executor_exception_is_recorded_as_failed_without_raw_error` | `tests/test_native_controller.py:61` | filesystem access; security or trust-boundary vocabulary |
| `test_native_controller.NativeControllerTests.test_native_user_unit_points_only_to_the_native_controller` | `tests/test_native_controller.py:76` | filesystem access; security or trust-boundary vocabulary |
| `test_packaging_policy.PackagingPolicyTests` | `tests/test_packaging_policy.py:33` | filesystem access; security or trust-boundary vocabulary |
| `test_packaging_policy.PackagingPolicyTests.make_package` | `tests/test_packaging_policy.py:34` | filesystem access; security or trust-boundary vocabulary |
| `test_packaging_policy.PackagingPolicyTests.write_manifest` | `tests/test_packaging_policy.py:39` | filesystem access; security or trust-boundary vocabulary |
| `test_packaging_policy.PackagingPolicyTests.test_actual_case_collision_is_rejected` | `tests/test_packaging_policy.py:50` | filesystem access |
| `test_packaging_policy.PackagingPolicyTests.test_actual_generated_directory_is_rejected` | `tests/test_packaging_policy.py:57` | filesystem access |
| `test_packaging_policy.PackagingPolicyTests.test_actual_case_colliding_directories_are_rejected` | `tests/test_packaging_policy.py:65` | filesystem access |
| `test_packaging_policy.PackagingPolicyTests.test_unlisted_file_is_rejected` | `tests/test_packaging_policy.py:73` | filesystem access |
| `test_packaging_policy.PackagingPolicyTests.test_symlink_is_rejected_without_following_it` | `tests/test_packaging_policy.py:80` | filesystem access |
| `test_packaging_policy.PackagingPolicyTests.test_preexisting_build_output_is_preserved` | `tests/test_packaging_policy.py:93` | filesystem access |
| `test_packaging_policy.PackagingPolicyTests.test_generated_manifest_entries_and_wrangle_directories_are_rejected` | `tests/test_packaging_policy.py:103` | filesystem access |
| `test_packaging_policy.PackagingPolicyTests.test_package_tools_do_not_forward_inherited_environment` | `tests/test_packaging_policy.py:131` | security or trust-boundary vocabulary |
| `test_packaging_policy.PackagingPolicyTests.test_package_tools_do_not_forward_inherited_environment.fake_run` | `tests/test_packaging_policy.py:136` | security or trust-boundary vocabulary |
| `test_rel003_core_sda_delegation.Rel003CoreSdaDelegationTests` | `tests/test_rel003_core_sda_delegation.py:17` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_rel003_core_sda_delegation.Rel003CoreSdaDelegationTests.setUp` | `tests/test_rel003_core_sda_delegation.py:18` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_rel003_core_sda_delegation.Rel003CoreSdaDelegationTests.request` | `tests/test_rel003_core_sda_delegation.py:40` | security or trust-boundary vocabulary |
| `test_rel003_core_sda_delegation.Rel003CoreSdaDelegationTests._delegate` | `tests/test_rel003_core_sda_delegation.py:49` | security or trust-boundary vocabulary |
| `test_rel003_core_sda_delegation.Rel003CoreSdaDelegationTests.test_restart_preserves_result_and_delivery_is_idempotent` | `tests/test_rel003_core_sda_delegation.py:118` | security or trust-boundary vocabulary |
| `test_rel003_core_sda_delegation.Rel003CoreSdaDelegationTests.test_scope_claim_and_completion_idempotency_fail_closed` | `tests/test_rel003_core_sda_delegation.py:141` | security or trust-boundary vocabulary |
| `test_rel004_cross_device.Rel004CrossDeviceTests` | `tests/test_rel004_cross_device.py:19` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_rel004_cross_device.Rel004CrossDeviceTests.test_context_handoff_and_tool_effects_reconstruct_without_replay` | `tests/test_rel004_cross_device.py:20` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_rel006_guardian_priority.GuardianPriorityQualificationTests` | `tests/test_rel006_guardian_priority.py:8` | security or trust-boundary vocabulary |
| `test_rel006_guardian_priority.GuardianPriorityQualificationTests.test_guardian_uses_next_slot_without_preempting_active_inference` | `tests/test_rel006_guardian_priority.py:11` | security or trust-boundary vocabulary |
| `test_rel013_recovery_drills.Rel013RecoveryDrillTests` | `tests/test_rel013_recovery_drills.py:19` | command or process execution; database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_rel013_recovery_drills.Rel013RecoveryDrillTests._git` | `tests/test_rel013_recovery_drills.py:20` | command or process execution; security or trust-boundary vocabulary |
| `test_rel013_recovery_drills.Rel013RecoveryDrillTests._legacy_source` | `tests/test_rel013_recovery_drills.py:28` | filesystem access; security or trust-boundary vocabulary |
| `test_rel013_recovery_drills.Rel013RecoveryDrillTests._destination` | `tests/test_rel013_recovery_drills.py:42` | filesystem access; security or trust-boundary vocabulary |
| `test_rel013_recovery_drills.Rel013RecoveryDrillTests._release_manifest` | `tests/test_rel013_recovery_drills.py:53` | filesystem access; security or trust-boundary vocabulary |
| `test_rel013_recovery_drills.Rel013RecoveryDrillTests.test_pinned_migration_dry_run_apply_and_verified_rollback` | `tests/test_rel013_recovery_drills.py:99` | filesystem access; security or trust-boundary vocabulary |
| `test_rel013_recovery_drills.Rel013RecoveryDrillTests.test_recovery_backup_replay_and_corruption_are_bounded` | `tests/test_rel013_recovery_drills.py:138` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_rel013_recovery_drills.Rel013RecoveryDrillTests.test_provider_outage_crash_and_stop_controls_fence_restart` | `tests/test_rel013_recovery_drills.py:181` | filesystem access; security or trust-boundary vocabulary |
| `test_rel013_recovery_drills.Rel013RecoveryDrillTests.test_unsafe_migration_and_rollback_inputs_fail_before_writes` | `tests/test_rel013_recovery_drills.py:225` | filesystem access; security or trust-boundary vocabulary |
| `test_rel017_installation.Rel017InstallationTests` | `tests/test_rel017_installation.py:16` | command or process execution; filesystem access; security or trust-boundary vocabulary |
| `test_rel017_installation.Rel017InstallationTests.test_manifest_artifacts_are_real_regular_files` | `tests/test_rel017_installation.py:28` | filesystem access; security or trust-boundary vocabulary |
| `test_rel017_installation.Rel017InstallationTests.test_windows_script_has_no_embedded_credentials_or_remote_queue` | `tests/test_rel017_installation.py:47` | security or trust-boundary vocabulary |
| `test_rel017_installation.Rel017InstallationTests.test_verifier_cli_is_read_only_and_green` | `tests/test_rel017_installation.py:61` | command or process execution; security or trust-boundary vocabulary |
| `test_rel_cross_module_contracts.ReleaseCrossModuleContractTests` | `tests/test_rel_cross_module_contracts.py:14` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_rel_cross_module_contracts.ReleaseCrossModuleContractTests.test_every_configured_module_has_a_valid_identity_and_permission_fixture` | `tests/test_rel_cross_module_contracts.py:20` | security or trust-boundary vocabulary |
| `test_rel_cross_module_contracts.ReleaseCrossModuleContractTests.test_each_module_can_publish_and_deliver_the_versioned_event_fixture` | `tests/test_rel_cross_module_contracts.py:44` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_research_analysis.ResearchAnalysisTests` | `tests/test_research_analysis.py:12` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_research_analysis.ResearchAnalysisTests.store` | `tests/test_research_analysis.py:13` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_research_github.ResearchGitHubTests` | `tests/test_research_github.py:16` | security or trust-boundary vocabulary |
| `test_research_github.ResearchGitHubTests.test_pinned_commit_requires_allowlisted_license_and_preserves_pin` | `tests/test_research_github.py:28` | security or trust-boundary vocabulary |
| `test_research_github.ResearchGitHubTests.test_pinned_commit_requires_allowlisted_license_and_preserves_pin.inspect` | `tests/test_research_github.py:29` | security or trust-boundary vocabulary |
| `test_research_github.ResearchGitHubTests.test_path_allowlist_and_pinned_sha_are_enforced` | `tests/test_research_github.py:80` | security or trust-boundary vocabulary |
| `test_research_github.ResearchGitHubTests.test_path_allowlist_and_pinned_sha_are_enforced.unsafe` | `tests/test_research_github.py:81` | security or trust-boundary vocabulary |
| `test_research_github.ResearchGitHubTests.test_policy_rejects_empty_license_allowlist` | `tests/test_research_github.py:131` | security or trust-boundary vocabulary |
| `test_research_handbook.ResearchHandbookTests` | `tests/test_research_handbook.py:18` | security or trust-boundary vocabulary |
| `test_research_handbook.ResearchHandbookTests.test_research_tip_round_trip_requires_review_and_merger` | `tests/test_research_handbook.py:49` | security or trust-boundary vocabulary |
| `test_research_handbook.ResearchHandbookTests.test_constitution_requires_distinct_owner_receipt` | `tests/test_research_handbook.py:91` | security or trust-boundary vocabulary |
| `test_research_instagram.ResearchInstagramTests` | `tests/test_research_instagram.py:13` | database or query access; external or network access; filesystem access; security or trust-boundary vocabulary |
| `test_research_instagram.ResearchInstagramTests.store` | `tests/test_research_instagram.py:14` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_research_instagram.ResearchInstagramTests.test_public_metadata_caption_audio_and_source_links_persist` | `tests/test_research_instagram.py:17` | external or network access |
| `test_research_instagram.ResearchInstagramTests.test_private_content_is_blocked_without_audio_access` | `tests/test_research_instagram.py:35` | external or network access |
| `test_research_instagram.ResearchInstagramTests.test_login_required_content_is_blocked_transparently` | `tests/test_research_instagram.py:50` | external or network access |
| `test_research_instagram.ResearchInstagramTests.test_audio_unavailable_is_partial_with_persisted_reason` | `tests/test_research_instagram.py:61` | external or network access |
| `test_research_instagram.ResearchInstagramTests.test_invalid_url_is_blocked_before_provider_calls` | `tests/test_research_instagram.py:73` | external or network access |
| `test_research_instagram.ResearchInstagramTests.test_invalid_audio_offsets_are_failed_and_persisted` | `tests/test_research_instagram.py:86` | external or network access |
| `test_research_media_rag.ResearchMediaRAGTests` | `tests/test_research_media_rag.py:30` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_research_media_rag.ResearchMediaRAGTests.test_cross_video_summary_is_sorted_extractive_and_persistent` | `tests/test_research_media_rag.py:45` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_research_safety.ResearchSafetyTests` | `tests/test_research_safety.py:25` | database or query access; external or network access; filesystem access; security or trust-boundary vocabulary |
| `test_research_safety.ResearchSafetyTests.test_instruction_like_web_content_stays_data_and_scope_is_allowlisted` | `tests/test_research_safety.py:26` | external or network access; security or trust-boundary vocabulary |
| `test_research_safety.ResearchSafetyTests.test_instruction_like_web_content_stays_data_and_scope_is_allowlisted.fetch` | `tests/test_research_safety.py:30` | external or network access |
| `test_research_safety.ResearchSafetyTests.test_private_media_requires_explicit_access_and_does_not_call_audio` | `tests/test_research_safety.py:53` | database or query access; external or network access; filesystem access; security or trust-boundary vocabulary |
| `test_research_safety.ResearchSafetyTests.test_video_observations_are_immutable_and_replayed_without_overwrite` | `tests/test_research_safety.py:85` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_research_subscriptions.ResearchSubscriptionTests` | `tests/test_research_subscriptions.py:14` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_research_subscriptions.ResearchSubscriptionTests.service` | `tests/test_research_subscriptions.py:15` | security or trust-boundary vocabulary |
| `test_research_subscriptions.ResearchSubscriptionTests.test_follow_is_stable_and_enforces_provider_terms` | `tests/test_research_subscriptions.py:18` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_research_subscriptions.ResearchSubscriptionTests.test_only_due_subscriptions_refresh_and_next_cadence_is_recorded` | `tests/test_research_subscriptions.py:33` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_research_subscriptions.ResearchSubscriptionTests.test_provider_failure_is_bounded_and_does_not_leak_exception_text` | `tests/test_research_subscriptions.py:50` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_research_subscriptions.ResearchSubscriptionTests.test_disabled_subscription_is_not_refreshed_after_restart` | `tests/test_research_subscriptions.py:65` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_research_web.ResearchWebTests` | `tests/test_research_web.py:15` | external or network access |
| `test_research_web.ResearchWebTests.test_fetch_is_bounded_and_hashes_content` | `tests/test_research_web.py:38` | external or network access |
| `test_research_web.ResearchWebTests.test_fetch_is_bounded_and_hashes_content.fetch` | `tests/test_research_web.py:39` | external or network access |
| `test_research_web.ResearchWebTests.test_unallowlisted_source_is_blocked_before_transport` | `tests/test_research_web.py:51` | external or network access |
| `test_research_web.ResearchWebTests.test_unallowlisted_source_is_blocked_before_transport.fetch` | `tests/test_research_web.py:54` | external or network access |
| `test_research_web.ResearchWebTests.test_provider_failures_are_explicit_and_redacted` | `tests/test_research_web.py:75` | external or network access |
| `test_research_web.ResearchWebTests.test_invalid_content_and_requests_fail_closed` | `tests/test_research_web.py:87` | external or network access |
| `test_research_youtube.ResearchYouTubeTests` | `tests/test_research_youtube.py:17` | database or query access; external or network access; filesystem access; security or trust-boundary vocabulary |
| `test_research_youtube.ResearchYouTubeTests.store` | `tests/test_research_youtube.py:18` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_research_youtube.ResearchYouTubeTests.test_metadata_offsets_source_links_and_record_persist` | `tests/test_research_youtube.py:21` | external or network access |
| `test_research_youtube.ResearchYouTubeTests.test_transcript_failure_reason_is_persisted` | `tests/test_research_youtube.py:44` | external or network access |
| `test_research_youtube.ResearchYouTubeTests.test_invalid_url_is_blocked_before_provider_calls` | `tests/test_research_youtube.py:59` | external or network access |
| `test_research_youtube.ResearchYouTubeTests.test_invalid_offsets_are_failed_and_persisted` | `tests/test_research_youtube.py:72` | external or network access |
| `test_research_youtube.ResearchYouTubeTests.test_missing_metadata_transport_is_persisted` | `tests/test_research_youtube.py:85` | external or network access |
| `test_runtime_browser.BrowserProfileServiceTests` | `tests/test_runtime_browser.py:9` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_runtime_browser.BrowserProfileServiceTests.make_service` | `tests/test_runtime_browser.py:10` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_runtime_browser.BrowserProfileServiceTests.test_profile_and_human_handoff_persist_without_raw_session_value` | `tests/test_runtime_browser.py:18` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_runtime_browser_tools.BrowserToolServiceTests` | `tests/test_runtime_browser_tools.py:32` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_runtime_browser_tools.BrowserToolServiceTests.setUp` | `tests/test_runtime_browser_tools.py:33` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_runtime_browser_tools.BrowserToolServiceTests.test_form_rejects_sensitive_fields_and_allows_bounded_typed_fields` | `tests/test_runtime_browser_tools.py:65` | security or trust-boundary vocabulary |
| `test_runtime_calendar.RuntimeCalendarTests` | `tests/test_runtime_calendar.py:38` | security or trust-boundary vocabulary |
| `test_runtime_calendar.RuntimeCalendarTests.test_read_and_writes_use_separate_scopes_and_confirmation` | `tests/test_runtime_calendar.py:39` | security or trust-boundary vocabulary |
| `test_runtime_calendar.RuntimeCalendarTests.test_timezone_is_aware_and_normalized_to_utc` | `tests/test_runtime_calendar.py:55` | security or trust-boundary vocabulary |
| `test_runtime_calendar.RuntimeCalendarTests.test_read_rejects_bad_ranges_and_adapter_results` | `tests/test_runtime_calendar.py:73` | security or trust-boundary vocabulary |
| `test_runtime_calendar.RuntimeCalendarTests.test_read_and_write_scopes_are_independently_required` | `tests/test_runtime_calendar.py:101` | security or trust-boundary vocabulary |
| `test_runtime_chat.RuntimeChatTests` | `tests/test_runtime_chat.py:15` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_runtime_chat.RuntimeChatTests.test_completed_stream_persists_only_after_done` | `tests/test_runtime_chat.py:16` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_runtime_chat.RuntimeChatTests.test_cancellation_does_not_persist_a_successful_turn` | `tests/test_runtime_chat.py:37` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_runtime_chat.RuntimeChatTests.test_provider_failures_are_precise_and_not_persisted` | `tests/test_runtime_chat.py:56` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_runtime_chat.RuntimeChatTests.test_invalid_delta_and_empty_response_are_not_successes` | `tests/test_runtime_chat.py:75` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_runtime_chat.RuntimeChatTests.test_invalid_delta_and_empty_response_are_not_successes.run` | `tests/test_runtime_chat.py:76` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_runtime_dashboard.RuntimeDashboardTests` | `tests/test_runtime_dashboard.py:10` | security or trust-boundary vocabulary |
| `test_runtime_dashboard.RuntimeDashboardTests.get` | `tests/test_runtime_dashboard.py:24` | security or trust-boundary vocabulary |
| `test_runtime_dashboard_service.RuntimeDashboardServiceTests` | `tests/test_runtime_dashboard_service.py:11` | database or query access |
| `test_runtime_dashboard_service.RuntimeDashboardServiceTests.test_snapshot_preserves_source_timestamps_and_failures` | `tests/test_runtime_dashboard_service.py:12` | database or query access |
| `test_runtime_email.RuntimeEmailTests` | `tests/test_runtime_email.py:38` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_runtime_email.RuntimeEmailTests.test_scopes_and_owner_approval_gate_operations` | `tests/test_runtime_email.py:39` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_runtime_email.RuntimeEmailTests.test_send_receipt_is_idempotent_after_reopen` | `tests/test_runtime_email.py:55` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_runtime_email.RuntimeEmailTests.test_timeout_is_fenced_and_receipt_survives_reconciliation` | `tests/test_runtime_email.py:67` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_runtime_email.RuntimeEmailTests.test_effect_journal_does_not_store_message_body` | `tests/test_runtime_email.py:82` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_runtime_file_actions.FileActionServiceTests` | `tests/test_runtime_file_actions.py:8` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_runtime_file_actions.FileActionServiceTests.setUp` | `tests/test_runtime_file_actions.py:9` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_runtime_file_actions.FileActionServiceTests.test_preview_requires_one_file_and_directory_approval_is_forbidden` | `tests/test_runtime_file_actions.py:27` | filesystem access; security or trust-boundary vocabulary |
| `test_runtime_file_actions.FileActionServiceTests.test_each_file_requires_approval_and_trash_is_recoverable` | `tests/test_runtime_file_actions.py:37` | filesystem access; security or trust-boundary vocabulary |
| `test_runtime_file_actions.FileActionServiceTests.test_identity_change_and_protected_or_outside_paths_fail_closed` | `tests/test_runtime_file_actions.py:61` | filesystem access; security or trust-boundary vocabulary |
| `test_runtime_file_actions.FileActionServiceTests.test_audit_is_redacted_and_no_direct_delete_operation_exists` | `tests/test_runtime_file_actions.py:78` | filesystem access; security or trust-boundary vocabulary |
| `test_runtime_offline.RuntimeOfflineTests` | `tests/test_runtime_offline.py:10` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_runtime_offline.RuntimeOfflineTests._service` | `tests/test_runtime_offline.py:11` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_runtime_reminders.RuntimeReminderTests` | `tests/test_runtime_reminders.py:16` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_runtime_reminders.RuntimeReminderTests.test_schedule_and_preferences_survive_restart` | `tests/test_runtime_reminders.py:17` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_runtime_reminders.RuntimeReminderTests.test_daily_schedule_and_disabled_notifications_are_safe` | `tests/test_runtime_reminders.py:34` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_runtime_security.RuntimeSecurityTests` | `tests/test_runtime_security.py:15` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_runtime_security.RuntimeSecurityTests.setUp` | `tests/test_runtime_security.py:16` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_runtime_security.RuntimeSecurityTests.request` | `tests/test_runtime_security.py:40` | security or trust-boundary vocabulary |
| `test_runtime_security.RuntimeSecurityTests.test_owner_session_requires_matching_identity_and_csrf_for_mutations` | `tests/test_runtime_security.py:51` | security or trust-boundary vocabulary |
| `test_runtime_security.RuntimeSecurityTests.test_rotation_invalidates_old_session_and_responses_are_hardened` | `tests/test_runtime_security.py:82` | security or trust-boundary vocabulary |
| `test_runtime_service.RuntimeServiceTests` | `tests/test_runtime_service.py:16` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_runtime_service.RuntimeServiceTests.setUp` | `tests/test_runtime_service.py:17` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_runtime_service.RuntimeServiceTests.request` | `tests/test_runtime_service.py:38` | security or trust-boundary vocabulary |
| `test_runtime_service.RuntimeServiceTests.test_authenticated_health_and_scope_denial` | `tests/test_runtime_service.py:47` | security or trust-boundary vocabulary |
| `test_runtime_service.RuntimeServiceTests.test_task_handoff_claim_ack_and_event_stream` | `tests/test_runtime_service.py:61` | security or trust-boundary vocabulary |
| `test_runtime_service.RuntimeServiceTests.test_duplicate_handoff_is_idempotent_and_foreign_scope_is_rejected` | `tests/test_runtime_service.py:104` | security or trust-boundary vocabulary |
| `test_runtime_service.RuntimeServiceTests.test_invalid_target_and_ack_claim_are_fail_closed` | `tests/test_runtime_service.py:124` | security or trust-boundary vocabulary |
| `test_runtime_speech._Adapter` | `tests/test_runtime_speech.py:10` | security or trust-boundary vocabulary |
| `test_runtime_speech._Adapter.stop` | `tests/test_runtime_speech.py:20` | security or trust-boundary vocabulary |
| `test_runtime_speech.RuntimeSpeechTests` | `tests/test_runtime_speech.py:24` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_runtime_speech.RuntimeSpeechTests.test_interruption_stops_adapter_without_persisting_speech` | `tests/test_runtime_speech.py:33` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_sda_003_profiles.SDA003ProfileTests` | `tests/test_sda_003_profiles.py:17` | filesystem access; security or trust-boundary vocabulary |
| `test_sda_003_profiles.SDA003ProfileTests.setUp` | `tests/test_sda_003_profiles.py:18` | filesystem access; security or trust-boundary vocabulary |
| `test_sda_003_profiles.SDA003ProfileTests.fake_run` | `tests/test_sda_003_profiles.py:32` | security or trust-boundary vocabulary |
| `test_sda_003_profiles.SDA003ProfileTests.fake_run.run` | `tests/test_sda_003_profiles.py:33` | security or trust-boundary vocabulary |
| `test_sda_003_profiles.SDA003ProfileTests.test_profile_commands_are_read_only_and_preserve_each_requested_alias` | `tests/test_sda_003_profiles.py:79` | filesystem access; security or trust-boundary vocabulary |
| `test_sda_003_profiles.SDA003ProfileTests.test_unavailable_alias_stops_without_fallback_or_later_roles` | `tests/test_sda_003_profiles.py:97` | security or trust-boundary vocabulary |
| `test_sda_003_profiles.SDA003ProfileTests.test_controls_and_authentication_stop_before_model_calls` | `tests/test_sda_003_profiles.py:107` | filesystem access; security or trust-boundary vocabulary |
| `test_sda_003_profiles.SDA003ProfileTests.test_controls_and_authentication_stop_before_model_calls.denied_login` | `tests/test_sda_003_profiles.py:119` | security or trust-boundary vocabulary |
| `test_sda_003_profiles.SDA003ProfileTests.test_model_failure_reasons_propagate_without_fallback` | `tests/test_sda_003_profiles.py:132` | security or trust-boundary vocabulary |
| `test_system_inventory.SystemInventoryTests` | `tests/test_system_inventory.py:9` | filesystem access; security or trust-boundary vocabulary |
| `test_system_inventory.SystemInventoryTests.test_scan_is_metadata_only_bounded_and_does_not_follow_symlinks` | `tests/test_system_inventory.py:10` | filesystem access; security or trust-boundary vocabulary |
| `test_system_inventory.SystemInventoryTests.test_digest_and_comparison_ignore_collection_time` | `tests/test_system_inventory.py:23` | security or trust-boundary vocabulary |
| `test_system_inventory.SystemInventoryTests.test_inventory_reports_model_and_acceleration_capability_slots` | `tests/test_system_inventory.py:31` | filesystem access; security or trust-boundary vocabulary |
| `test_system_inventory.SystemInventoryTests.test_inventory_cli_writes_private_output_and_returns_summary` | `tests/test_system_inventory.py:42` | filesystem access; security or trust-boundary vocabulary |
| `test_tws_cultivation.TWSCultivationTests` | `tests/test_tws_cultivation.py:8` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_tws_cultivation.TWSCultivationTests.test_progression_requires_independent_proof_acceptance` | `tests/test_tws_cultivation.py:30` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_tws_cultivation.TWSCultivationTests.test_achievement_and_adaptation_are_idempotent_and_fair` | `tests/test_tws_cultivation.py:42` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_tws_dialogue.TWSDialogueTests` | `tests/test_tws_dialogue.py:8` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_tws_dialogue.TWSDialogueTests.test_dialogue_state_and_turns_are_idempotent_without_reward_side_effects` | `tests/test_tws_dialogue.py:20` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_tws_dialogue.TWSDialogueTests.test_dialogue_inputs_are_bounded_and_mood_is_allowlisted` | `tests/test_tws_dialogue.py:47` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_tws_lifecycle.TWSLifecycleTests` | `tests/test_tws_lifecycle.py:8` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_tws_lifecycle.TWSLifecycleTests.test_catalog_metadata_and_lifecycle` | `tests/test_tws_lifecycle.py:9` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_tws_lifecycle.TWSLifecycleTests.test_invalid_transition_and_missing_proof_fail_closed` | `tests/test_tws_lifecycle.py:28` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_tws_preferences.TWSPreferenceTests` | `tests/test_tws_preferences.py:8` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_tws_preferences.TWSPreferenceTests.test_onboarding_and_presentation_choices_are_independent` | `tests/test_tws_preferences.py:9` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_tws_preferences.TWSPreferenceTests.test_invalid_preferences_and_onboarding_states_fail_closed` | `tests/test_tws_preferences.py:27` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_tws_rewards.TWSRewardTests` | `tests/test_tws_rewards.py:8` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_tws_rewards.TWSRewardTests.test_review_gate_and_reward_retry_are_idempotent` | `tests/test_tws_rewards.py:18` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_tws_rewards.TWSRewardTests.test_rejected_proof_and_invalid_scope_cannot_be_rewarded` | `tests/test_tws_rewards.py:34` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_tws_rewards.TWSRewardTests.test_realm_prerequisites_and_xp_thresholds_are_enforced` | `tests/test_tws_rewards.py:45` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_tws_sanctuary.TWSSanctuaryTests` | `tests/test_tws_sanctuary.py:8` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_tws_sanctuary.TWSSanctuaryTests.test_sanctuary_snapshot_reads_current_wing_and_quest_ledger` | `tests/test_tws_sanctuary.py:9` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_tws_storage.TWSStorageTests` | `tests/test_tws_storage.py:9` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_tws_storage.TWSStorageTests.test_versioned_upgrade_preserves_wings_and_proofs` | `tests/test_tws_storage.py:10` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_tws_storage.TWSStorageTests.test_retries_are_idempotent_and_duplicate_proofs_are_rejected` | `tests/test_tws_storage.py:37` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_tws_storage.TWSStorageTests.test_rejects_unknown_references_and_invalid_evidence` | `tests/test_tws_storage.py:50` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_tws_task_import.TWSTaskImportTests` | `tests/test_tws_task_import.py:9` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_tws_task_import.TWSTaskImportTests.test_import_is_consent_bound_idempotent_and_draft_only` | `tests/test_tws_task_import.py:22` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_tws_task_import.TWSTaskImportTests.test_import_rejects_missing_consent_or_same_task_mutation` | `tests/test_tws_task_import.py:39` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_tws_task_import.TWSTaskImportTests.test_import_accepts_only_known_cross_module_sources` | `tests/test_tws_task_import.py:52` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_tws_visual_qa.manifest` | `tests/test_tws_visual_qa.py:6` | security or trust-boundary vocabulary |
| `test_wic_alerts.WICAlertTests` | `tests/test_wic_alerts.py:16` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_wic_alerts.WICAlertTests.policy` | `tests/test_wic_alerts.py:17` | security or trust-boundary vocabulary |
| `test_wic_alerts.WICAlertTests.test_material_change_is_queued_once_and_persists` | `tests/test_wic_alerts.py:28` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_wic_alerts.WICAlertTests.test_non_material_change_does_not_create_alert` | `tests/test_wic_alerts.py:46` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_wic_alerts.WICAlertTests.test_quiet_hours_and_cadence_suppress_without_delivery` | `tests/test_wic_alerts.py:57` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_wic_alerts.WICAlertTests.test_owner_scope_and_disabled_policy_fail_closed` | `tests/test_wic_alerts.py:81` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_wic_categories.WICCategoryTests` | `tests/test_wic_categories.py:12` | database or query access; security or trust-boundary vocabulary |
| `test_wic_categories.WICCategoryTests.test_assignments_are_searchable` | `tests/test_wic_categories.py:13` | database or query access |
| `test_wic_categories.WICCategoryTests.test_correction_replaces_current_search_and_preserves_history` | `tests/test_wic_categories.py:21` | database or query access |
| `test_wic_categories.WICCategoryTests.test_invalid_category_and_duplicate_assignment_fail_closed` | `tests/test_wic_categories.py:31` | database or query access |
| `test_wic_categories.WICCategoryTests.test_history_survives_reopen` | `tests/test_wic_categories.py:40` | database or query access; security or trust-boundary vocabulary |
| `test_wic_clusters.WICClusterTests` | `tests/test_wic_clusters.py:21` | database or query access; security or trust-boundary vocabulary |
| `test_wic_clusters.WICClusterTests.test_same_incident_keeps_both_sources_in_one_cluster` | `tests/test_wic_clusters.py:28` | database or query access |
| `test_wic_clusters.WICClusterTests.test_cluster_membership_survives_reopen_and_replay` | `tests/test_wic_clusters.py:41` | database or query access; security or trust-boundary vocabulary |
| `test_wic_clusters.WICClusterTests.test_different_urls_require_explicit_incident_key` | `tests/test_wic_clusters.py:53` | database or query access |
| `test_wic_clusters.WICClusterTests.test_one_observation_cannot_be_assigned_to_two_incidents` | `tests/test_wic_clusters.py:61` | database or query access |
| `test_wic_sources.WICSourceTests` | `tests/test_wic_sources.py:19` | database or query access; security or trust-boundary vocabulary |
| `test_wic_sources.WICSourceTests.test_ingestion_retains_authorized_urls_and_separate_timestamps` | `tests/test_wic_sources.py:26` | database or query access |
| `test_wic_sources.WICSourceTests.test_observations_survive_store_reopen` | `tests/test_wic_sources.py:52` | database or query access; security or trust-boundary vocabulary |
| `test_wic_sources.WICSourceTests.test_replay_is_idempotent` | `tests/test_wic_sources.py:64` | database or query access |
| `test_wic_sources.WICSourceTests.test_foreign_items_are_rejected_without_persistence` | `tests/test_wic_sources.py:75` | database or query access |
| `test_wic_sources.WICSourceTests.test_unallowlisted_feed_is_blocked_before_transport` | `tests/test_wic_sources.py:86` | database or query access |
| `test_wic_sources.WICSourceTests.test_provider_failure_is_bounded` | `tests/test_wic_sources.py:97` | database or query access |
| `test_wic_sources.WICSourceTests.test_health_becomes_stale_after_successful_snapshot_age` | `tests/test_wic_sources.py:107` | database or query access |
| `test_wic_sources.WICSourceTests.test_provider_outage_preserves_last_success_and_marks_outage` | `tests/test_wic_sources.py:124` | database or query access |
| `test_wic_sources.WICSourceTests.test_unknown_health_has_no_false_timestamp` | `tests/test_wic_sources.py:142` | database or query access |
| `test_wic_sources.WICSourceTests.test_invalid_dates_are_rejected_and_valid_items_remain` | `tests/test_wic_sources.py:151` | database or query access |
| `test_wic_sources.WICSourceTests.test_non_public_policy_and_bad_observation_fail_closed` | `tests/test_wic_sources.py:163` | database or query access |
| `test_wic_summaries.WICSummariesTests` | `tests/test_wic_summaries.py:11` | database or query access; security or trust-boundary vocabulary |
| `test_wic_summaries.WICSummariesTests.test_summary_store_is_idempotent_and_survives_reopen` | `tests/test_wic_summaries.py:41` | database or query access; security or trust-boundary vocabulary |
| `test_wic_verification.WICVerificationTests` | `tests/test_wic_verification.py:29` | database or query access; security or trust-boundary vocabulary |
| `test_wic_verification.WICVerificationTests.cluster` | `tests/test_wic_verification.py:30` | security or trust-boundary vocabulary |
| `test_wic_verification.WICVerificationTests.test_uncertain_claim_cannot_be_verified` | `tests/test_wic_verification.py:36` | database or query access; security or trust-boundary vocabulary |
| `test_wic_verification.WICVerificationTests.test_corroboration_is_required_before_verification` | `tests/test_wic_verification.py:46` | database or query access; security or trust-boundary vocabulary |
| `test_wic_verification.WICVerificationTests.test_retraction_is_visible_and_blocks_verification` | `tests/test_wic_verification.py:58` | database or query access; security or trust-boundary vocabulary |
| `test_wic_verification.WICVerificationTests.test_correction_preserves_retraction_history` | `tests/test_wic_verification.py:72` | database or query access; security or trust-boundary vocabulary |
| `test_wic_verification.WICVerificationTests.test_claim_history_survives_reopen` | `tests/test_wic_verification.py:91` | database or query access; security or trust-boundary vocabulary |
| `test_wic_watchlists.WICWatchlistTests` | `tests/test_wic_watchlists.py:11` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_wic_watchlists.WICWatchlistTests.test_owner_can_save_and_reopen_preferences` | `tests/test_wic_watchlists.py:12` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_wic_watchlists.WICWatchlistTests.test_preferences_are_owner_scoped` | `tests/test_wic_watchlists.py:27` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_wic_watchlists.WICWatchlistTests.test_unchanged_save_is_idempotent_and_changes_are_revisioned` | `tests/test_wic_watchlists.py:35` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `test_wic_watchlists.WICWatchlistTests.test_invalid_duplicate_preferences_fail_closed` | `tests/test_wic_watchlists.py:49` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `astra_watchdog._regular` | `tools/astra_watchdog.py:34` | security or trust-boundary vocabulary |
| `astra_watchdog._read_settings` | `tools/astra_watchdog.py:41` | database or query access |
| `astra_watchdog._git_commit_exists` | `tools/astra_watchdog.py:45` | command or process execution; security or trust-boundary vocabulary |
| `astra_watchdog._git_head` | `tools/astra_watchdog.py:54` | command or process execution; security or trust-boundary vocabulary |
| `astra_watchdog._git_clean` | `tools/astra_watchdog.py:62` | command or process execution; security or trust-boundary vocabulary |
| `astra_watchdog._git_fast_forward` | `tools/astra_watchdog.py:72` | command or process execution; security or trust-boundary vocabulary |
| `astra_watchdog._git_restore` | `tools/astra_watchdog.py:82` | command or process execution; security or trust-boundary vocabulary |
| `astra_watchdog._activation_journal` | `tools/astra_watchdog.py:94` | security or trust-boundary vocabulary |
| `astra_watchdog._write_journal` | `tools/astra_watchdog.py:100` | filesystem access; security or trust-boundary vocabulary |
| `astra_watchdog._read_journal` | `tools/astra_watchdog.py:109` | security or trust-boundary vocabulary |
| `astra_watchdog._open_readonly` | `tools/astra_watchdog.py:131` | database or query access; security or trust-boundary vocabulary |
| `astra_watchdog._verified_backup` | `tools/astra_watchdog.py:138` | database or query access; security or trust-boundary vocabulary |
| `astra_watchdog.check` | `tools/astra_watchdog.py:150` | command or process execution; database or query access; filesystem access; security or trust-boundary vocabulary |
| `astra_watchdog._activation_ready` | `tools/astra_watchdog.py:192` | database or query access |
| `astra_watchdog._require_no_controls` | `tools/astra_watchdog.py:224` | security or trust-boundary vocabulary |
| `astra_watchdog.activate` | `tools/astra_watchdog.py:230` | command or process execution; database or query access; filesystem access; security or trust-boundary vocabulary |
| `astra_watchdog.rollback` | `tools/astra_watchdog.py:394` | command or process execution; database or query access; filesystem access; security or trust-boundary vocabulary |
| `astra_watchdog.main` | `tools/astra_watchdog.py:483` | command or process execution; database or query access; security or trust-boundary vocabulary |
| `build_final_audit.git` | `tools/build_final_audit.py:79` | command or process execution; security or trust-boundary vocabulary |
| `build_final_audit.read_text` | `tools/build_final_audit.py:92` | security or trust-boundary vocabulary |
| `build_final_audit.relative` | `tools/build_final_audit.py:96` | security or trust-boundary vocabulary |
| `build_final_audit.excluded` | `tools/build_final_audit.py:100` | security or trust-boundary vocabulary |
| `build_final_audit.iter_files` | `tools/build_final_audit.py:109` | filesystem access; security or trust-boundary vocabulary |
| `build_final_audit.module_name` | `tools/build_final_audit.py:120` | filesystem access; security or trust-boundary vocabulary |
| `build_final_audit.security_reasons` | `tools/build_final_audit.py:160` | command or process execution; database or query access; external or network access; filesystem access; security or trust-boundary vocabulary |
| `build_final_audit.maintenance_status` | `tools/build_final_audit.py:175` | security or trust-boundary vocabulary |
| `build_final_audit.recommendation` | `tools/build_final_audit.py:185` | security or trust-boundary vocabulary |
| `build_final_audit.make_record` | `tools/build_final_audit.py:196` | security or trust-boundary vocabulary |
| `build_final_audit.parse_python` | `tools/build_final_audit.py:242` | security or trust-boundary vocabulary |
| `build_final_audit.parse_python.visit` | `tools/build_final_audit.py:258` | security or trust-boundary vocabulary |
| `build_final_audit.parse_other` | `tools/build_final_audit.py:341` | security or trust-boundary vocabulary |
| `build_final_audit.parse_code` | `tools/build_final_audit.py:388` | security or trust-boundary vocabulary |
| `build_final_audit.resolve_relations` | `tools/build_final_audit.py:423` | security or trust-boundary vocabulary |
| `build_final_audit.build_markdown` | `tools/build_final_audit.py:545` | security or trust-boundary vocabulary |
| `build_final_audit.index_files` | `tools/build_final_audit.py:590` | security or trust-boundary vocabulary |
| `build_final_audit.write_json` | `tools/build_final_audit.py:633` | filesystem access; security or trust-boundary vocabulary |
| `build_final_audit.main` | `tools/build_final_audit.py:637` | database or query access; filesystem access; security or trust-boundary vocabulary |
| `ci_checks._quiet_run` | `tools/ci_checks.py:48` | command or process execution; security or trust-boundary vocabulary |
| `ci_checks._build_local_wheel` | `tools/ci_checks.py:66` | filesystem access; security or trust-boundary vocabulary |
| `ci_checks.dependency_scan` | `tools/ci_checks.py:127` | filesystem access; security or trust-boundary vocabulary |
| `ci_checks._workspace_files` | `tools/ci_checks.py:220` | filesystem access; security or trust-boundary vocabulary |
| `ci_checks._read_workspace_file` | `tools/ci_checks.py:242` | filesystem access; security or trust-boundary vocabulary |
| `ci_checks.secret_scan` | `tools/ci_checks.py:277` | command or process execution; security or trust-boundary vocabulary |
| `ci_checks._workflow_files` | `tools/ci_checks.py:357` | filesystem access; security or trust-boundary vocabulary |
| `ci_checks.security_scan` | `tools/ci_checks.py:361` | security or trust-boundary vocabulary |
| `ci_report._safe_target` | `tools/ci_report.py:114` | filesystem access; security or trust-boundary vocabulary |
| `ci_report._open_directory` | `tools/ci_report.py:138` | filesystem access; security or trust-boundary vocabulary |
| `ci_report._write_report` | `tools/ci_report.py:157` | filesystem access; security or trust-boundary vocabulary |
| `ci_report.write_report` | `tools/ci_report.py:194` | filesystem access; security or trust-boundary vocabulary |
| `ci_report.main` | `tools/ci_report.py:212` | filesystem access; security or trust-boundary vocabulary |
| `import_legacy.git` | `tools/import_legacy.py:9` | command or process execution; security or trust-boundary vocabulary |
| `import_legacy.safe_relative` | `tools/import_legacy.py:13` | filesystem access; security or trust-boundary vocabulary |
| `import_legacy._casefold_parts` | `tools/import_legacy.py:21` | security or trust-boundary vocabulary |
| `import_legacy._check_existing_path` | `tools/import_legacy.py:24` | security or trust-boundary vocabulary |
| `import_legacy.prepare_manifest` | `tools/import_legacy.py:51` | filesystem access; security or trust-boundary vocabulary |
| `import_legacy.main` | `tools/import_legacy.py:109` | filesystem access; security or trust-boundary vocabulary |
| `verify_codex_profiles._control` | `tools/verify_codex_profiles.py:33` | security or trust-boundary vocabulary |
| `verify_codex_profiles._bounded_run` | `tools/verify_codex_profiles.py:37` | command or process execution; security or trust-boundary vocabulary |
| `verify_codex_profiles._profile_command` | `tools/verify_codex_profiles.py:165` | filesystem access; security or trust-boundary vocabulary |
| `verify_codex_profiles.verify_profiles` | `tools/verify_codex_profiles.py:190` | filesystem access; security or trust-boundary vocabulary |
| `verify_codex_profiles.main` | `tools/verify_codex_profiles.py:268` | security or trust-boundary vocabulary |
| `verify_foundation.safe_import_target` | `tools/verify_foundation.py:23` | security or trust-boundary vocabulary |
| `verify_foundation.verify_foundation` | `tools/verify_foundation.py:37` | filesystem access; security or trust-boundary vocabulary |
