# Layer 2 Step 5b Diagnostic — Census 2021 subset

## Probe results

```json
{
  "header_row": 6,
  "data_start_row": 8,
  "income": {
    "file": "Income Database.xlsx",
    "sheet": "Table 1",
    "n_cols": 93,
    "matches": []
  },
  "empl": {
    "file": "Education and employment database.xlsx",
    "sheet": "Table 1",
    "n_cols": 93,
    "matches": [
      {
        "col": 52,
        "header": "in the labour force (no.) | 10658459 | 11471295",
        "samples": [
          10658459.0,
          11471295.0,
          12695853.0,
          3334854.0,
          3605885.0,
          3874012.0,
          2675477.0,
          2929597.0,
          3330560.0,
          2171075.0
        ]
      },
      {
        "col": 54,
        "header": "participation rate (%) | 61.4 | 60.3",
        "samples": [
          61.4,
          60.3,
          61.1,
          59.7,
          59.2,
          58.7,
          61.4,
          60.5,
          62.4,
          62.8
        ]
      },
      {
        "col": 55,
        "header": "not in the labour force (%) | 33 | 33.1",
        "samples": [
          33.0,
          33.1,
          33.1,
          34.6,
          34.3,
          35.5,
          33.3,
          33.2,
          32.2,
          31.2
        ]
      }
    ]
  },
  "null_markers": [
    "-",
    "..",
    "np",
    "n.a.",
    "na",
    "NA",
    "NP",
    ""
  ],
  "notes": [
    "Apply will pick the BEST matching column per workbook.",
    "Selection rule: header-text match + sample-value range check.",
    "  Income: expect weekly $ values 500-3000 typically.",
    "  Female LFP: expect % values 30-80 typically.",
    "Decision 50: validate by sample value range, not header alone."
  ]
}
```
