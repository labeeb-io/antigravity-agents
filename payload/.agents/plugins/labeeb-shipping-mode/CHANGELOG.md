<div dir="rtl">

## 2026-10-01 — v2.1 Architecture Refinement & Control-Plane Verification

### المستهدف والقرارات
- **توحيد مصدر الحقيقة للوكلاء (Canonical Agents):** اعتماد `.agents/agents/<name>/agent.md` مصدراً وحيداً للوكلاء الستة مع الحفاظ على `subagent: true` و `mainAgent: false` وتطابق كامل للـ System Prompts.
- **إزالة الازدواجية:** أرشفة وكلاء الـ plugin إلى `tasks/release-v0.1/archive/agent-definitions-v2-initial/` وإزالتهم من المسار النشط لمنع الـ drift.
- **المهارات الأصيلة:** اعتماد `.agents/skills/` كمصدر رسمي للمهارات والأوامر السريعة المباشرة، وتوفير `experiment-broker/SKILL.md` محلياً.
- **تقليص مسؤولية الـ Plugin:** حصر دور الـ Plugin في القواعد والسكربتات والخطافات فقط دون حزم وكلاء أو مهارات مكررة.
- **حراسة الـ Hooks الصارمة (Fail-Fast):** استبدال الـ shell wrappers بمسارات نسبية مباشرة (`python3 ./scripts/...`) ومزامنة `hooks.template.json`.
- **تشذيب الأدوات (Tool Pruning):** إزالة `manage_subagents` من أدوات المنسقين للاكتفاء بالإشعارات التلقائية دون polling، وتثبيت Minimal Tool Profiles خالية من الأدوات غير المتوافقة مع الـ runtime.
- **إثبات الجاهزية (Verification & Smoke Tests):**
  - اجتياز 15/15 اختبار وحدة وحراسة في مجلد الـ plugin CWD بنجاح (100% PASS).
  - اجتياز **Smoke Test 1:** بناء وتنفيذ `release-coordinator` دون أخطاء (PASS).
  - اجتياز **Smoke Test 2:** تفويض `discovery-coordinator` لـ `discovery-researcher` واستلام الرد آلياً (PASS).
  - اجتياز **Smoke Test 3:** حل مهارة `experiment-broker` وصياغة عقد التجربة دون أي تعديل ميداني (PASS).
- **ملاحظة حوكمية:** هذا التعديل خاص بهندسة نظام الوكلاء فقط، ولا يمثل دليلاً فنياً على أي معيار إطلاق ولا يغيّر حالة المنتج الفنية.

---

## 2026-10-01 — v2.0 Agent-Native Migration

### الهدف
تحويل طبقة تشغيل Shipping Mode من Legacy Antigravity Workflows وجلسات copy/paste إلى Agent Skills + Custom Subagents + Rules + Hooks، مع بقاء ميثاق المنتج والأدلة الميدانية منفصلين عن آلية التنفيذ.

### مصير كل Workflow قديم

| Workflow القديم | الحالة بعد التحويل | البديل الحالي | ماذا تغير؟ |
|---|---|---|---|
| `.agent/workflows/lead.md` | **MIGRATED** | `/lead` + `/delivery-lead` Skills + `release-coordinator` | لم يعد prompt داخل نفس الجلسة؛ صار coordinator مستقل يقرأ contract/state ويستطيع متابعة العمل تلقائياً. |
| `.agent/workflows/release-cycle.md` | **REPLACED** | `/shipping` + `release-coordinator`، و`/release-cycle` Alias | Lead/Exec/Audit لم تعد مراحل داخل context واحد؛ أصبحت subagents مستقلة ومصالحة مركزية. |
| `.agent/workflows/discovery.md` | **REPLACED/REDESIGNED** | `/discovery` + `discovery-coordinator` + researcher/experiment executor | تحول إلى Runtime-First adaptive discovery؛ أزيل Memory→Wiki→GitNexus→Code كمسار إلزامي؛ أضيف Proof Boundary/Canonical Entrypoint/Experiment Fidelity. |
| `.agent/workflows/exec.md` | **MIGRATED** | `/exec` + `implementation-executor` | worker مستقل لا يبدأ دون Task Contract ولا يملك push/merge/deploy/self-audit. |
| `.agent/workflows/executor.md` | **DEDUPLICATED** | `/executor` Alias لـ`/exec` | الملف القديم كان مكرراً؛ بقي الأمر للتوافق فقط. |
| `.agent/workflows/audit.md` | **MIGRATED** | `/audit` + `release-auditor` | التدقيق صار custom subagent مستقل clean-context. |
| `.agent/workflows/auditor.md` | **DEDUPLICATED** | `/auditor` Alias لـ`/audit` | أزيل wrapper المكرر وبقي الأمر للتوافق. |
| `.agent/workflows/manager-handoff.md` | **REMOVED AS STAGE** | Native `invoke_subagent` أولاً؛ Orchestrator fallback داخلي؛ لا manual relay | لم يعد المؤسس ينقل task packets. Orchestrator بقي capability وليس مرحلة مستقلة. |
| `.agent/workflows/prestart-approval.md` | **DISSOLVED** | Coordinator authority classification + Rules + PreToolUse hook | أزيل الـmandatory archaeology. الصلاحية/المخاطر تُحسم حسب الفعل؛ الأدوات المعرفية JIT. |
| `.agent/workflows/soft-gate.md` | **DISSOLVED** | Task Contract + bounded validation + reconciliation | لا gate مستقل روتيني يضيف latency؛ validation يبقى داخل عقد المهمة. |
| `.agent/workflows/plan-approval.md` | **DISSOLVED** | Founder reserved-decision gate + Task Contract | لا approval يدوي لكل plan؛ التصعيد فقط للقرارات المحفوظة. |

### Rule القديم

| القديم | الجديد |
|---|---|
| `.agent/rules/release_governance.md` | `rules/shipping-invariants.md` + `rules/evidence-invariants.md` |

الفرق: الـRule القديمة كانت تمزج routing والأدوار وMemory/GitNexus والـWorkflows في سياق دائم. القواعد الجديدة تحفظ invariants فقط وتستخدم `trigger: model_decision` وفق صيغة Antigravity الحديثة.

### Hooks/Scripts

| القديم | الحالة | البديل |
|---|---|---|
| `guard-governance-files.sh` | Replaced | `shipping_guard.py` actor-aware permissions |
| `inject-release-state.sh` | Removed | كان فارغاً؛ coordinator يقرأ state عند الحاجة |
| `auto-lint-check.sh` | Removed | كان no-op؛ validation أصبح جزءاً من Task Contract |
| `smart-delegate.sh` | Removed | Native subagents / Orchestrator fallback داخل coordinator |
| `pre-flight-check.sh` | Migrated/Simplified | plugin `scripts/preflight.sh` كفحص معلوماتي قبل implementation |
| root `.agent/hooks.json` shipping hooks | Replaced | plugin `hooks.json`: safety + discovery drift + discovery stop gate |

### تغييرات الحوكمة

- Founder Gate لم يعد موجوداً لكل Finding روتيني.
- `Finding -> Release Coordinator Delegation Check -> Bounded Task` إذا كان داخل الميثاق والمخاطر المفوضة.
- تبقى للمؤسس حصراً: تغيير الميثاق/القيمة، المخاطر الجوهرية والمال، المعمارية الكبرى، والـGo/No-Go النهائي.
- WIP=1 و`Merged != DONE` بقيا دون تغيير.
- Release Criterion PASS ما زال يحتاج تدقيقاً مستقلاً بالدليل المطلوب.

### الوثائق العربية

- `01_RELEASE_CONTRACT.md`: لم يُغيّر مضمونه.
- `00_RELEASE_CONTROL.md`: تحديث طبقة الوكلاء وروابط التشغيل دون تغيير النتائج الفنية.
- `02_OPERATING_MANUAL.md`: إعادة صياغة التشغيل ليصبح Agent-Native ويحافظ على Evidence-Driven Experimentation.
- `03_DELEGATION_RECORD.md`: توضيح التفويض التلقائي للوكلاء والفصل بين routine work والقرارات المحفوظة.
- `04_ROLE_PROMPTS.md`: تحول من prompts للنسخ إلى Agent Role Registry.
- `sprints/sprint_S01.md`: تمت مصالحة WIP مع قرار 1 أكتوبر المسجل في Release Control؛ Migration نفسها لا تعتبر دليلاً فنياً.

### ملفات تاريخية مؤرشفة
الـShipping Manual الأصلي وخطط الـagent system القديمة محفوظة تحت `archive/legacy-agent-system/` للرجوع التاريخي فقط، وتُزال نسخها القديمة من جذر `tasks/release-v0.1/` عند cutover إذا كانت مطابقة للـbaseline المرفوع.

### التحقق قبل التسليم

تم تنفيذ تحقق محلي على نسخة workspace مطابقة للملفات المرفوعة:

- `11/11` اختبارات hooks/guards ناجحة.
- Full clean migration: `PASS`.
- Post-install verification: `PASS`.
- Legacy workflows/rule/scripts لم تعد نشطة بعد cutover.
- الوثائق التصميمية القديمة نُقلت من جذر Release إلى `archive/legacy-agent-system/`.
- `01_RELEASE_CONTRACT.md` بقي مطابقاً byte-for-byte للنسخة المرفوعة.
- Existing `reports/` evidence لا تتم الكتابة فوقه أثناء Migration.
- Rollback test أعاد الـREADME والـWorkflows الأصلية وأزال plugin/docs المولدة.
- Baseline-drift test يوقف التثبيت **قبل أي تغيير** إذا تغير ملف حي منذ بناء الحزمة.

</div>
