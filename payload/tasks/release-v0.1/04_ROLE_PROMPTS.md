<div dir="rtl">

# لبيب — سجل أدوار الوكلاء وعقود التكليف (Agent Role Registry)
**تاريخ التحديث:** 1 أكتوبر 2026 | **المرجع:** [02_OPERATING_MANUAL.md](./02_OPERATING_MANUAL.md)

> [!IMPORTANT]
> هذه الوثيقة لم تعد تحتوي Prompts للنسخ واللصق بين الجلسات. الأدوار أصبحت **Custom Agents + Agent Skills** داخل Plugin `labeeb-shipping-mode`. الغاية من هذا السجل هي معرفة من يملك كل قرار وحدود صلاحياته.

---

## 1. Release Coordinator

- **Agent:** `release-coordinator`
- **Slash entrypoints:** `/shipping`, `/lead`, `/delivery-lead`, `/release-cycle` (توافق خلفي)
- **المسؤولية:** إدارة دورة Shipping Mode كاملة، اختيار proof target، WIP=1، تشغيل بقية الوكلاء، المصالحة، تحديث الحالة.
- **يسمح له:** تحديث Release Control والسبرينت والتقارير؛ تفويض discovery/implementation/audit؛ targeted correction؛ إغلاق المهام الروتينية بعد PASS مستقل.
- **يمنع عليه:** كتابة product code بنفسه؛ تغيير الميثاق/التفويض/المعمارية دون قرار محفوظ.

---

## 2. Discovery Coordinator

- **Agent:** `discovery-coordinator`
- **Skill:** `/discovery`
- **المسؤولية:** سؤال واحد Runtime-First، proof boundaries، canonical entrypoint، experiment fidelity، Finding Card.
- **صلاحية التغيير:** Read-only. إذا احتاج mutation يستخدم Experiment Broker وexecutor منفصل.
- **ممنوع:** broad architecture archaeology كبديل عن runtime، إصلاح الكود، توسيع Finding إلى Task بنفسه.

### مساعدو Discovery
- `discovery-researcher`: سؤال read-only ضيق فقط.
- `discovery-experiment-executor`: تجربة Local محددة فقط؛ لا كود/migrations/deploy/git.

---

## 3. Implementation Executor

- **Agent:** `implementation-executor`
- **Skills:** `/exec`, `/executor`
- **المدخل الإلزامي:** `task_contract` مثبت ومقيد.
- **المسؤولية:** أصغر تعديل يعالج الفشل المرصود + validation محلي.
- **ممنوع:** اختيار المهمة، توسيع scope، governance edits، push/merge/deploy، self-audit.
- **Workspace:** `branch` مفضل للتعديلات المستقلة؛ `inherit` عندما يعتمد الإثبات على Docker/runtime المحلي الحالي.

---

## 4. Independent Release Auditor

- **Agent:** `release-auditor`
- **Skills:** `/audit`, `/auditor`
- **المسؤولية:** إعادة original proof path مستقلاً وإصدار `PASS | FAIL | BLOCKED | UNKNOWN`.
- **ممنوع:** تعديل product code أو إصلاح ما يراه أثناء التدقيق.
- **مخرجاته:** تقرير تحت `tasks/release-v0.1/reports/` + دليل قابل للمصالحة.

---

## 5. Orchestrator

لم يعد `/manager-handoff` مرحلة منفصلة.

ترتيب التفويض:
1. Native Antigravity `invoke_subagent`.
2. Orchestrator CLI عند غياب native subagents، أو طلب نموذج خارجي بعينه، أو حاجة مستقلة مادية.
3. لا manual copy/paste للمؤسس.

المعالجة الافتراضية عند fallback:
- `claude-code`: read-only research / independent audit إذا كان متاحاً.
- `codex`: bounded implementation إذا كان متاحاً.
- يجب التحقق من runtime/model الحاليين عبر Orchestrator بدلاً من افتراض وجودهما.

---

## 6. مصفوفة السلطة

| القرار | المالك |
|---|---|
| ما proof target التالي؟ | Release Coordinator |
| هل الـruntime يعمل فعلياً؟ | Discovery/Auditor حسب المرحلة |
| كيف ننفذ Task Contract؟ | Implementation Executor ضمن الحدود |
| هل الإصلاح اجتاز proof path؟ | Independent Auditor |
| هل يتحول Finding روتيني إلى Task؟ | Release Coordinator |
| تغيير scope/قيمة/معمارية كبرى/مخاطر جوهرية | المؤسس |
| Go/No-Go العام | المؤسس |

</div>
