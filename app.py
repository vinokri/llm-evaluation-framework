import json
import time
from pathlib import Path
import pandas as pd
import streamlit as st
from src.judge import llm_judge

st.set_page_config(page_title="LLM Evaluation Framework", page_icon="⚖️", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.15rem; padding-bottom: 2.5rem; max-width: 1500px;}
.hero {
  padding: 1.3rem 1.5rem; border:1px solid rgba(49,51,63,.15); border-radius:18px;
  background:linear-gradient(180deg, rgba(250,250,250,.92), rgba(245,245,245,.65));
  margin-bottom:1rem;
}
.kicker {font-size:.78rem; letter-spacing:.1em; text-transform:uppercase; font-weight:750; opacity:.62;}
.sub {opacity:.7; font-size:.98rem;}
.card {padding:1rem 1.05rem;border:1px solid rgba(49,51,63,.14);border-radius:15px;background:rgba(255,255,255,.8);}
.arch {padding:.9rem 1rem;border:1px solid rgba(49,51,63,.16);border-radius:14px;text-align:center;font-weight:700;background:white;}
.muted {opacity:.62;font-size:.88rem;}
.arrow {text-align:center;font-size:1.25rem;opacity:.5;padding:.2rem;}
</style>
""", unsafe_allow_html=True)

tasks = json.loads(Path("data/benchmark_tasks.json").read_text())
pretty_map = {"Model A":"Candidate Model A","Model B":"Candidate Model B","Model C":"Candidate Model C"}
reverse_map = {v:k for k,v in pretty_map.items()}
models = list(pretty_map.values())

with st.sidebar:
    st.markdown("### Benchmark configuration")
    selected_task_ids = st.multiselect(
        "Task suites",
        [f"{t['id']} · {t['category']}" for t in tasks],
        default=[f"{t['id']} · {t['category']}" for t in tasks],
    )
    selected_models = st.multiselect("Candidate models", models, default=models)
    repetitions = st.slider("Repeated judge passes", 1, 5, 2)
    concurrency = st.slider("Evaluation workers", 10, 500, 120, 10)

    st.divider()
    st.markdown("### Evaluation strategy")
    st.markdown("**Deterministic signals + Claude judge**")
    st.caption("Tests / exit status / task checks provide objective signals. Claude scores dimensions that are harder to capture programmatically.")
    st.info("Recorded demo uses synthetic tasks and simulated judge responses. Production pattern: Claude on Amazon Bedrock.")

st.markdown("""
<div class="hero">
  <div class="kicker">LLM Evaluation Framework</div>
  <h1 style="margin-bottom:.3rem;">Evaluate LLM and coding-agent outputs with deterministic checks + LLM-as-a-Judge</h1>
  <div class="sub">Synthetic coding task families · hybrid scoring · traceability · production-scale architecture</div>
</div>
""", unsafe_allow_html=True)

c1,c2,c3,c4 = st.columns(4)
c1.metric("Task suites", len(selected_task_ids))
c2.metric("Candidate models", len(selected_models))
c3.metric("Judge", "Claude")
c4.metric("Evaluation mode", "Hybrid")

tabs = st.tabs(["Benchmark Run", "Task & Judge Trace", "Scale", "Architecture"])

selected_ids = {x.split(" · ")[0] for x in selected_task_ids}
active_tasks = [t for t in tasks if t["id"] in selected_ids]

with tabs[0]:
    st.markdown("### Coding benchmark run")
    st.caption("Candidate solutions are evaluated first with deterministic task checks, then by Claude for qualitative dimensions.")

    planned = len(active_tasks) * max(len(selected_models),1) * repetitions
    a,b,c,d = st.columns(4)
    a.metric("Benchmark tasks", len(active_tasks))
    b.metric("Planned judge passes", f"{planned:,}")
    c.metric("Worker concurrency", concurrency)
    d.metric("Scoring", "Hybrid")

    if st.button("▶ Start coding benchmark", type="primary", use_container_width=True, disabled=not active_tasks or not selected_models):
        rows = []
        progress = st.progress(0)
        status = st.empty()
        telemetry = st.empty()
        total = len(active_tasks) * len(selected_models)
        done = 0

        for task in active_tasks:
            for pretty in selected_models:
                internal = reverse_map[pretty]
                status.markdown(f"**Running** `{task['id']}` · **{pretty}** → deterministic checks → **Claude judge**")
                result = llm_judge(task, internal, task["candidate_outputs"][internal])
                rows.append({
                    "task_id": task["id"],
                    "category": task["category"],
                    "style": task["style"],
                    "candidate_model": pretty,
                    "prompt": task["prompt"],
                    "candidate_output": task["candidate_outputs"][internal],
                    "reference": task["reference"],
                    **result
                })
                done += 1
                progress.progress(done/total)
                telemetry.markdown(
                    f"""<div class="card"><b>Evaluation telemetry</b><br>
                    Completed: <b>{done}/{total}</b> &nbsp;·&nbsp;
                    Queue depth: <b>{total-done}</b> &nbsp;·&nbsp;
                    Worker pool: <b>{concurrency}</b> &nbsp;·&nbsp;
                    Retry queue: <b>0</b></div>""",
                    unsafe_allow_html=True,
                )
                time.sleep(.08)

        st.session_state["benchmark_results"] = pd.DataFrame(rows)
        status.success("Coding benchmark completed")
        telemetry.empty()

    if "benchmark_results" in st.session_state:
        df = st.session_state["benchmark_results"]
        summary = (
            df.groupby("candidate_model")
            .agg(
                hybrid_score=("overall_score","mean"),
                deterministic_pass=("deterministic_passed","sum"),
                deterministic_total=("deterministic_total","sum"),
                correctness=("correctness","mean"),
                reasoning=("reasoning_quality","mean"),
                minimality=("minimality_safety","mean"),
                instruction_following=("instruction_following","mean"),
                avg_judge_latency_ms=("latency_ms","mean"),
            )
            .reset_index()
        )
        summary["deterministic_pass_rate"] = summary["deterministic_pass"] / summary["deterministic_total"] * 100
        summary = summary.sort_values(["hybrid_score","deterministic_pass_rate"], ascending=False)

        st.markdown("### Model leaderboard")
        st.dataframe(
            summary[[
                "candidate_model","hybrid_score","deterministic_pass_rate","correctness",
                "reasoning","minimality","instruction_following","avg_judge_latency_ms"
            ]].style.format({
                "hybrid_score":"{:.2f}",
                "deterministic_pass_rate":"{:.0f}%",
                "correctness":"{:.2f}",
                "reasoning":"{:.2f}",
                "minimality":"{:.2f}",
                "instruction_following":"{:.2f}",
                "avg_judge_latency_ms":"{:.0f}",
            }),
            use_container_width=True, hide_index=True
        )

        best = summary.iloc[0]
        q1,q2,q3,q4 = st.columns(4)
        q1.metric("Leading model", best["candidate_model"])
        q2.metric("Hybrid score", f"{best['hybrid_score']:.2f}/5")
        q3.metric("Deterministic pass", f"{best['deterministic_pass_rate']:.0f}%")
        q4.metric("Tasks evaluated", len(active_tasks))

        chart = summary.set_index("candidate_model")[["hybrid_score","correctness","reasoning","minimality","instruction_following"]]
        st.bar_chart(chart)

        st.markdown("### Task-level results")
        task_table = df[[
            "task_id","category","candidate_model","overall_score",
            "deterministic_passed","deterministic_total","rationale"
        ]].copy()
        st.dataframe(task_table, use_container_width=True, hide_index=True)

with tabs[1]:
    st.markdown("### Task and Claude judge trace")
    if "v4_results" not in st.session_state:
        st.info("Run the benchmark first.")
    else:
        df = st.session_state["benchmark_results"]
        idx = st.selectbox(
            "Evaluation trace",
            list(range(len(df))),
            format_func=lambda i: f"{df.iloc[i]['task_id']} · {df.iloc[i]['candidate_model']}"
        )
        r = df.iloc[idx]
        task = next(t for t in tasks if t["id"] == r["task_id"])

        l,m = st.columns([1.25,1])
        with l:
            st.markdown(f"#### {r['category']}")
            st.caption(r["style"])
            st.markdown("**Benchmark task**")
            st.code(r["prompt"], language="text")
            st.markdown("**Candidate solution**")
            st.code(r["candidate_output"], language="text")
            st.markdown("**Expected outcome / reference**")
            st.code(r["reference"], language="text")

            st.markdown("**Deterministic checks**")
            checks = task["deterministic_checks"]
            passed = int(r["deterministic_passed"])
            for i, check in enumerate(checks):
                st.write(("✅" if i < passed else "❌") + " " + check)

        with m:
            st.markdown("#### Claude qualitative judgment")
            x1,x2 = st.columns(2)
            x1.metric("Correctness", f"{r['correctness']}/5")
            x2.metric("Reasoning quality", f"{r['reasoning_quality']}/5")
            x3,x4 = st.columns(2)
            x3.metric("Minimality / safety", f"{r['minimality_safety']}/5")
            x4.metric("Instruction following", f"{r['instruction_following']}/5")
            st.metric("Hybrid overall", f"{r['overall_score']}/5")
            st.write(f"**Claude rationale:** {r['rationale']}")
            st.caption("Objective test signals are combined with qualitative LLM judging rather than relying on either alone.")

with tabs[2]:
    st.markdown("### Why coding benchmarks become a scale problem")
    st.caption("Repository tasks, candidate models, judge passes, and repeated runs multiply the evaluation volume.")

    s1,s2,s3,s4 = st.columns(4)
    task_count = s1.number_input("Benchmark tasks", min_value=1, value=20_000, step=1000)
    model_count = s2.number_input("Candidate models", min_value=1, value=8, step=1)
    judge_passes = s3.number_input("Judge passes", min_value=1, value=3, step=1)
    reruns = s4.number_input("Repeated runs", min_value=1, value=2, step=1)
    total_evals = int(task_count * model_count * judge_passes * reruns)
    st.metric("Potential Claude judge evaluations", f"{total_evals:,}")

    p1,p2,p3,p4 = st.columns(4)
    p1.metric("Workers", concurrency)
    p2.metric("Queueing", "Enabled")
    p3.metric("Retries", "Idempotent")
    p4.metric("Traceability", "Per evaluation")

    st.markdown("""
    <div class="card">
    <b>Production controls</b><br><br>
    • Partition benchmark submissions into independent evaluation jobs.<br>
    • Use admission control to stay within model/service capacity.<br>
    • Apply backpressure when queue growth exceeds worker throughput.<br>
    • Keep retries idempotent so failed judge calls do not duplicate scores.<br>
    • Version task definitions, rubrics, and judge configuration for reproducibility.<br>
    • Track latency, token use, queue depth, failure rate, and cost per evaluation.
    </div>
    """, unsafe_allow_html=True)
    st.warning("Scale figures are illustrative and are not customer production measurements.")

with tabs[3]:
    st.markdown("### Production evaluation architecture")
    st.caption("Hybrid evaluation combines objective execution signals with Claude qualitative judgment.")

    # Compact horizontal architecture for a 2-minute walkthrough.
    a1,a2,a3,a4,a5 = st.columns([1,1,1.35,1,1])
    with a1:
        st.markdown('<div class="arch">Coding Tasks<br><span class="muted">Repo · Terminal · Codegen</span></div>', unsafe_allow_html=True)
    with a2:
        st.markdown('<div class="arch">Candidate Models<br><span class="muted">A · B · C</span></div>', unsafe_allow_html=True)
    with a3:
        st.markdown('<div class="arch">Hybrid Evaluation<br><span class="muted">Tests + Claude Judge</span></div>', unsafe_allow_html=True)
    with a4:
        st.markdown('<div class="arch">Score Fusion<br><span class="muted">Objective + qualitative</span></div>', unsafe_allow_html=True)
    with a5:
        st.markdown('<div class="arch">Leaderboard<br><span class="muted">Rank · regressions · slices</span></div>', unsafe_allow_html=True)

    st.markdown(
        '<div style="text-align:center;opacity:.55;font-size:1.1rem;margin:.35rem 0;">'
        'Coding task &nbsp;→&nbsp; model output &nbsp;→&nbsp; deterministic checks + Claude &nbsp;→&nbsp; combined score &nbsp;→&nbsp; analysis'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("#### Inside the hybrid evaluator")
    h1,h2 = st.columns(2)
    with h1:
        st.markdown("""
        <div class="card">
        <b>Deterministic evaluator</b><br><br>
        ✓ Unit / regression tests<br>
        ✓ Build & execution status<br>
        ✓ Exit codes / task checks<br>
        ✓ Environment validation<br><br>
        <span class="muted">Objective signals wherever the task allows them.</span>
        </div>
        """, unsafe_allow_html=True)
    with h2:
        st.markdown("""
        <div class="card">
        <b>Claude · LLM-as-a-Judge</b><br><br>
        ✓ Correctness beyond test coverage<br>
        ✓ Reasoning quality<br>
        ✓ Minimality / safety<br>
        ✓ Instruction following<br><br>
        <span class="muted">Qualitative dimensions that are difficult to encode as tests.</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("#### Production-scale execution layer")
    p1,p2,p3,p4,p5,p6 = st.columns(6)
    for col, title, detail in [
        (p1,"Scheduler","Partition"),
        (p2,"Queue","Backpressure"),
        (p3,"Workers","Fan-out"),
        (p4,"Reliability","Retry + idempotency"),
        (p5,"Observability","Trace + metrics"),
        (p6,"Economics","Tokens + cost"),
    ]:
        with col:
            st.markdown(f'<div class="arch">{title}<br><span class="muted">{detail}</span></div>', unsafe_allow_html=True)

    st.success("Core idea: use deterministic signals where possible, and Claude where judgment is required — then combine both into a reproducible benchmark score.")
