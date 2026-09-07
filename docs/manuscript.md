# From executable repository to manuscript

README.md is the manuscript's canonical narrative. It carries the title,
authorship, abstract, numbered scientific sections, tables, figure captions,
references, and reproducibility appendix. Update it when results change instead
of maintaining a second divergent prose draft. The experiment-design documents
record the methods in greater detail.

| Manuscript component | Repository source |
|---|---|
| Abstract, motivation, hypotheses, methods, interpretation | README.md |
| E1 full protocol | docs/forgiveness_e1.md |
| E2 full protocol | docs/forgiveness_e2.md |
| E3 protocol fixed before execution | docs/forgiveness_e3.md |
| E1 table data | results/forgiveness_e1/summary.md and evaluation.csv |
| E2 table data | results/forgiveness_e2/run_metrics.csv and paired_differences.csv |
| E3 table data and every paired difference | results/forgiveness_e3/run_metrics.csv, paired_differences.csv, summary.md |
| E3 complete populations and raw round-robin measurements | results/forgiveness_e3/populations.json and population_evaluation.csv |
| Figure 1 | figures/e2_paired_effects.pdf (vector), also SVG/PNG |
| Figure generation | experiments/plot_forgiveness_e2.py |
| Figure 2 | figures/e3_paired_effects.pdf (vector), also SVG/PNG |
| Figure 2 generation | experiments/plot_forgiveness_e3.py |
| E3 exact replay and E2 regression evidence | results/forgiveness_e3/verification.json and replay.log |
| Bibliography | references.bib |
| Reproduction details and provenance | results/*/manifest.json, README Appendix A |

When the evidence warrants a manuscript, transfer these existing sections into
an article document and use the existing BibTeX file and vector figure. Markdown
file links become manuscript references or supplementary-material links; tables
retain their captions and denominators. No new typesetting pipeline is needed for
the present experimental step.

This is a conventional research-paper organization, not a claim that arXiv
mandates a particular sequence of headings. Before an eventual submission, follow
[arXiv's format requirements](https://info.arxiv.org/help/policies/format_requirements.html)
and [TeX submission guidance](https://info.arxiv.org/help/submit_tex.html).
The current repository is an exploratory executable artifact, not a submitted or
peer-reviewed article. Submission would be a separate decision.

E3's estimand is mixed-minus-fixed final-population cooperation between distinct
members. Its clone-inclusive training and extra compute must remain explicit in
any transferred methods or discussion. Preserve E1/E2 as earlier evidence and
report E3 as a sequential exploratory follow-up, regardless of the outcome's sign.
