(Langgraph) mdsweatt@Michaels-MacBook-Pro req_dev_musical_spork % python main.py examples/phase0_simple_spec.txt --subsystem "Authenication" --domain generic 
✓ LangSmith tracing enabled

╭─────────────────────────────────────╮
│ Requirements Decomposition System   │
│ AI-Powered Requirements Engineering │
╰─────────────────────────────────────╯

                     Workflow Configuration                      
 Specification Document          examples/phase0_simple_spec.txt 
 Target Subsystem                Authenication                   
 Quality Threshold               0.80                            
 Max Iterations                  3                               
 Pre-Decomposition Review        No                              

Checkpoint ID: 20251209_141951_authenication

Cost tracking active (budget: $5.00)

Initializing workflow...
Executing Requirements Decomposition Workflow

Starting workflow execution...


[1/5] Extracting Requirements...
  ✓ Extracted 5 requirements (1.6s)

[2/5] Analyzing System Context...
  ✓ Generated decomposition strategy (23.1s)

[3/5] Decomposing Requirements...
  ✓ Decomposed 3 requirements (48.5s)

[4/5] Validating Quality...
  ✓ Quality score: 0.85 (PASSED) (27.4s)

[5/5] Generating Documentation...

Generating Documentation...

Output directory: outputs/run_20251209_142132_authenication

→ Generating requirements specification...
  ✓ Requirements document: outputs/run_20251209_142132_authenication/requirements.md
→ Generating traceability matrix...
  ✓ Traceability matrix: outputs/run_20251209_142132_authenication/traceability.csv
→ Generating quality assessment report...
  ✓ Quality report: outputs/run_20251209_142132_authenication/quality_report.md

✓ Documentation Generation Complete

Requirements Specification: outputs/run_20251209_142132_authenication/requirements.md
Traceability Matrix: outputs/run_20251209_142132_authenication/traceability.csv
Quality Report: outputs/run_20251209_142132_authenication/quality_report.md

================================================================================

  ✓ Documentation complete (0.0s)

Workflow execution complete
Fetching cost data from LangSmith...
✓ Retrieved 29003 tokens from LangSmith
✓ Costs calculated from LangSmith traces (precise)

================================================================================
✓ Workflow Complete
================================================================================

                                 Results Summary                                  
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Metric                                   ┃ Value                               ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Extracted Requirements                   │ 5                                   │
│ Decomposed Requirements                  │ 3                                   │
│ Quality Score                            │ 0.85 (✅ PASSED)                    │
│ Refinement Iterations                    │ 0                                   │
│ Human Review Required                    │ No                                  │
│ Total Cost                               │ $0.0357 (LangSmith)                 │
└──────────────────────────────────────────┴─────────────────────────────────────┘

                              Performance, Cost & Energy Breakdown                               
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Node                 ┃     Time (s) ┃     % Time ┃     Cost ($) ┃    Energy (Wh) ┃   % Energy ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ Decompose            │         48.5 │      48.2% │       $0.004 │         0.0035 │      22.1% │
│ Validate             │         27.4 │      27.3% │       $0.006 │         0.0036 │      23.3% │
│ Analyze              │         23.1 │      23.0% │       $0.026 │         0.0054 │      34.4% │
│ Extract              │          1.6 │       1.5% │       $0.000 │         0.0032 │      20.2% │
│ Document             │          0.0 │       0.0% │       $0.000 │         0.0000 │       0.0% │
│ TOTAL                │        100.7 │     100.0% │       $0.036 │      0.0157 Wh │     100.0% │
└──────────────────────┴──────────────┴────────────┴──────────────┴────────────────┴────────────┘

💡 Energy Context:
   • Equivalent to ~0.0 minutes of LED TV usage (50W average)
   • Equivalent to ~0.1 meters driven by electric car (0.25 kWh/km)

✓ Costs/Energy calculated from LangSmith traces (precise)

Generated Documents:
  📄 Requirements: outputs/run_20251209_142132_authenication/requirements.md
  📊 Traceability: outputs/run_20251209_142132_authenication/traceability.csv
  📈 Quality Report: outputs/run_20251209_142132_authenication/quality_report.md
  📋 Run Info: outputs/run_20251209_142132_authenication/README.txt

✓ Decomposition complete!
