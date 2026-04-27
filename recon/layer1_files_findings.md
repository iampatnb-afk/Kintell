# Phase 2.5 Layer 1 — Raw File Inventory (abs_data\)
_Generated: 2026-04-26T14:34:44_

## File listing
  - Economic and Industry Database.csv                                              2,679 bytes
  - Education and employment database.xlsx                                     14,325,582 bytes
  - Family and Community Database.xlsx                                         15,629,450 bytes
  - Income Database.xlsx                                                       12,656,810 bytes
  - NCVER_ECEC_Completions_2019-2024.xlsx                                          15,276 bytes
  - NQAITS Quarterly Data Splits (Q3 2013 - Q4 2025).xlsx                     138,797,876 bytes
  - NQS Data Q4 2025.XLSX                                                      10,692,453 bytes
  - POA_2021_AUST.xlsx                                                         18,584,662 bytes
  - Population and People Database.xlsx                                        28,291,536 bytes
  - SA2_2021_AUST.xlsx                                                            250,022 bytes
  - SALM Smoothed SA2 Datafiles (ASGS 2021) - December quarter 2025.xlsx        2,362,447 bytes
  - meshblock-correspondence-file-asgs-edn3.xlsx                               14,590,449 bytes
  - module2b_catchment.py                                                          29,674 bytes
  - postcode_to_sa2_concordance.csv                                                51,442 bytes

## NQAITS Quarterly Data Splits — schema reconnaissance
`abs_data\NQAITS Quarterly Data Splits (Q3 2013 - Q4 2025).xlsx`  (138,797,876 bytes)
sheet count: 53
sheets (verbatim names):
  - Contents
  - Data Descriptions
  - Explanatory Notes
  - Q42025data
  - Q32025data
  - Q22025data
  - Q12025data
  - Q42024data
  - Q32024data
  - Q22024data
  - Q12024data
  - Q42023data
  - Q32023data
  - Q22023data
  - Q12023data
  - Q42022data
  - Q32022data
  - Q22022data
  - Q12022data
  - Q42021data
  - Q32021data
  - Q22021data
  - Q12021data
  - Q42020data
  - Q32020data
  - Q22020data
  - Q12020data
  - Q42019data
  - Q32019data
  - Q22019data
  - Q12019data
  - Q42018data
  - Q32018data
  - Q22018data
  - Q12018data
  - Q42017data
  - Q32017data
  - Q22017data
  - Q12017data
  - Q42016data
  - Q32016data
  - Q22016data
  - Q12016data
  - Q42015data
  - Q32015data
  - Q22015data
  - Q12015data
  - Q42014data
  - Q32014data
  - Q22014data
  - Q12014data
  - Q42013data
  - Q32013data

### Schema dump — first / middle / last sheet
Picked: ['Contents', 'Q12020data', 'Q32013data']

#### `Contents`  cols=14
    0. None
    1. None
    2. None
    3. Australian Children's Education and Care Quality Authority
    4. None
    5. None
    6. None
    7. None
    8. None
    9. None
   10. None
   11. None
   12. None
   13. None
sample row: [None, None, None, None, None, None, None, None, None, None, None, None, None, None]

#### `Q12020data`  cols=32
    0. Service ID
    1. Service Name
    2. Provider ID
    3. Provider Name
    4. Provider Management Type
    5. Managing Jurisdiction
    6. Service Type
    7. ApprovalDate
    8. SEIFA
    9. ARIA
   10. Maximum total places
   11. NQS Version
   12. Final Report Sent Date
   13. Overall Rating
   14. Quality Area 1
   15. Quality Area 2
   16. Quality Area 3
   17. Quality Area 4
   18. Quality Area 5
   19. Quality Area 6
   20. Quality Area 7
   21. Service sub-type (ordered counting method)
   22. Long Day Care
   23. PreschoolKindergarten Stand Alone
   24. PreschoolKindergarten Part of a School
   25. OSHC BeforeSchool
   26. OSHC After School
   27. OSHC Vacation Care
   28. Nature Care Other
   29. Postcode
   30. Latitude
   31. Longitude
sample row: ['SE-00009638', 'Aeon Academy', 'PR-40017687', 'AEON ARTS LTD.', 'Private not for profit other organisations', 'ACT', 'Centre-Based Care', datetime.datetime(2012, 1, 1, 0, 0), '10', 'Major Cities of Australia', 99, 'NQS (2012)', datetime.datetime(2015, 9, 11, 0, 0), 'Meeting NQS', 'Exceeding NQS', 'Meeting NQS', 'Exceeding NQS', 'Meeting NQS', 'Exceeding NQS', 'Meeting NQS', 'Meeting NQS', 'OSHC', 'No', 'No', 'No', 'No', 'Yes', 'Yes', 'No', '2600', -35.307, 149.10591]

#### `Q32013data`  cols=32
    0. Service ID
    1. Service Name
    2. Provider ID
    3. Provider Name
    4. Provider Management Type
    5. Managing Jurisdiction 
    6. Service Type
    7. Approval Date
    8. SEIFA
    9. ARIA+
   10. Maximum total places
   11. NQS Version
   12. Final Report Sent Date
   13. Overall Rating
   14. Quality Area 1
   15. Quality Area 2
   16. Quality Area 3
   17. Quality Area 4
   18. Quality Area 5
   19. Quality Area 6
   20. Quality Area 7
   21. Service sub-type (ordered counting method)
   22. Long Day Care
   23. PreschoolKindergarten Stand Alone
   24. PreschoolKindergarten Part of a School
   25. OSHC BeforeSchool
   26. OSHC After School
   27. OSHC Vacation Care
   28. Nature Care Other
   29. Postcode
   30. Latitude
   31. Longitude
sample row: ['SE-00000167', 'Bundamba Child Care Centre', 'PR-00000001', 'Bundamba Child Care Centre Inc', 'Private not for profit community managed', 'QLD', 'Centre-Based Care', datetime.datetime(2011, 4, 28, 0, 0), 3, 'Major Cities of Australia', 32, 'NQS (2012)', datetime.datetime(2012, 11, 22, 0, 0), 'Working Towards NQS', 'Working Towards NQS', 'Meeting NQS', 'Working Towards NQS', 'Meeting NQS', 'Working Towards NQS', 'Meeting NQS', 'Meeting NQS', 'LDC', 'Yes', 'No', 'No', 'No', 'No', 'No', 'No', '4304', -27.60583, 152.80618]

### Column stability across sampled sheets
COMMON across sampled: 0

UNIQUE to `Contents`: 1
  - Australian Children's Education and Care Quality Authority
UNIQUE to `Q12020data`: 32
  - ARIA
  - ApprovalDate
  - Final Report Sent Date
  - Latitude
  - Long Day Care
  - Longitude
  - Managing Jurisdiction
  - Maximum total places
  - NQS Version
  - Nature Care Other
  - OSHC After School
  - OSHC BeforeSchool
  - OSHC Vacation Care
  - Overall Rating
  - Postcode
  - PreschoolKindergarten Part of a School
  - PreschoolKindergarten Stand Alone
  - Provider ID
  - Provider Management Type
  - Provider Name
  - Quality Area 1
  - Quality Area 2
  - Quality Area 3
  - Quality Area 4
  - Quality Area 5
  - Quality Area 6
  - Quality Area 7
  - SEIFA
  - Service ID
  - Service Name
  - Service Type
  - Service sub-type (ordered counting method)
UNIQUE to `Q32013data`: 32
  - ARIA+
  - Approval Date
  - Final Report Sent Date
  - Latitude
  - Long Day Care
  - Longitude
  - Managing Jurisdiction 
  - Maximum total places
  - NQS Version
  - Nature Care Other
  - OSHC After School
  - OSHC BeforeSchool
  - OSHC Vacation Care
  - Overall Rating
  - Postcode
  - PreschoolKindergarten Part of a School
  - PreschoolKindergarten Stand Alone
  - Provider ID
  - Provider Management Type
  - Provider Name
  - Quality Area 1
  - Quality Area 2
  - Quality Area 3
  - Quality Area 4
  - Quality Area 5
  - Quality Area 6
  - Quality Area 7
  - SEIFA
  - Service ID
  - Service Name
  - Service Type
  - Service sub-type (ordered counting method)

### Service Approval column presence
  Contents: []
  Q12020data: []
  Q32013data: []

## SALM Smoothed SA2
`abs_data\SALM Smoothed SA2 Datafiles (ASGS 2021) - December quarter 2025.xlsx`  (2,362,447 bytes)
sheet count: 3
  - Smoothed SA2 unemployment rate
  - Smoothed SA2 unemployment
  - Smoothed SA2 labour force

### sheet: `Smoothed SA2 unemployment rate`
  row 0: ['Smoothed Unemployment Rate (%)', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
  row 1: ['Note: Cells containing a dash (-) indicate that data are unavailable. Estimates are unavailable either because the SA2 labour force estimate did not meet the minimum size or because there is a break in the series caused by the shift from the 2011 to the 2016 ASGS or the 2016 to 2021 ASGS. For more information, see the SALM Methodology page on the Department of Employment and Workplace Relations (DEWR) website and the 2016 or 2021 ASGS changeover user guides (also available from the DEWR website).', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
  row 2: [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
  row 3: ['Statistical Area Level 2 (SA2) (2021 ASGS)', 'SA2 Code (2021 ASGS)', datetime.datetime(2010, 12, 1, 0, 0), datetime.datetime(2011, 3, 1, 0, 0), datetime.datetime(2011, 6, 1, 0, 0), datetime.datetime(2011, 9, 1, 0, 0), datetime.datetime(2011, 12, 1, 0, 0), datetime.datetime(2012, 3, 1, 0, 0), datetime.datetime(2012, 6, 1, 0, 0), datetime.datetime(2012, 9, 1, 0, 0), datetime.datetime(2012, 12, 1, 0, 0), datetime.datetime(2013, 3, 1, 0, 0), datetime.datetime(2013, 6, 1, 0, 0), datetime.datetime(2013, 9, 1, 0, 0), datetime.datetime(2013, 12, 1, 0, 0), datetime.datetime(2014, 3, 1, 0, 0), datetime.datetime(2014, 6, 1, 0, 0), datetime.datetime(2014, 9, 1, 0, 0), datetime.datetime(2014, 12, 1, 0, 0), datetime.datetime(2015, 3, 1, 0, 0), datetime.datetime(2015, 6, 1, 0, 0), datetime.datetime(2015, 9, 1, 0, 0), datetime.datetime(2015, 12, 1, 0, 0), datetime.datetime(2016, 3, 1, 0, 0), datetime.datetime(2016, 6, 1, 0, 0), datetime.datetime(2016, 9, 1, 0, 0), datetime.datetime(2016, 12, 1, 0, 0), datetime.datetime(2017, 3, 1, 0, 0), datetime.datetime(2017, 6, 1, 0, 0), datetime.datetime(2017, 9, 1, 0, 0), datetime.datetime(2017, 12, 1, 0, 0), datetime.datetime(2018, 3, 1, 0, 0), datetime.datetime(2018, 6, 1, 0, 0), datetime.datetime(2018, 9, 1, 0, 0), datetime.datetime(2018, 12, 1, 0, 0), datetime.datetime(2019, 3, 1, 0, 0), datetime.datetime(2019, 6, 1, 0, 0), datetime.datetime(2019, 9, 1, 0, 0), datetime.datetime(2019, 12, 1, 0, 0), datetime.datetime(2020, 3, 1, 0, 0), datetime.datetime(2020, 6, 1, 0, 0), datetime.datetime(2020, 9, 1, 0, 0), datetime.datetime(2020, 12, 1, 0, 0), datetime.datetime(2021, 3, 1, 0, 0), datetime.datetime(2021, 6, 1, 0, 0), datetime.datetime(2021, 9, 1, 0, 0), datetime.datetime(2021, 12, 1, 0, 0), datetime.datetime(2022, 3, 1, 0, 0), datetime.datetime(2022, 6, 1, 0, 0), datetime.datetime(2022, 9, 1, 0, 0), datetime.datetime(2022, 12, 1, 0, 0), datetime.datetime(2023, 3, 1, 0, 0), datetime.datetime(2023, 6, 1, 0, 0), datetime.datetime(2023, 9, 1, 0, 0), datetime.datetime(2023, 12, 1, 0, 0), datetime.datetime(2024, 3, 1, 0, 0), datetime.datetime(2024, 6, 1, 0, 0), datetime.datetime(2024, 9, 1, 0, 0), datetime.datetime(2024, 12, 1, 0, 0), datetime.datetime(2025, 3, 1, 0, 0), datetime.datetime(2025, 6, 1, 0, 0), datetime.datetime(2025, 9, 1, 0, 0), datetime.datetime(2025, 12, 1, 0, 0)]
  row 4: ['Braidwood', 101021007, 3, 2.3, 2.1, 2.1, 2.3, 2.5, 2.7, 2.8, 2.7, 3.2, 3.4, 3.3, 3.8, 5.3, 5.9, 6, 5.5, 4.1, 3.2, 3.3, 3.5, 3.6, 3.6, 3.3, 3.3, 3.5, 3.5, 3.9, 4, 3.6, 3.8, 3.8, 3.7, 3.5, 3.3, 3.2, 2.9, 2.8, 3.2, 3.2, 3.6, 3.9, 4.2, 4.6, 5, 5.2, 4.7, 3.9, 3.6, 2.6, 2.3, 2.3, 1.9, 2.1, 2.2, 2.7, 3.2, 3.3, 3.5, 2.9, 2.5]
  row 5: ['Karabar', 101021008, 2.5, 1.8, 1.6, 1.5, 1.7, 1.7, 1.8, 2.1, 2, 2.5, 2.8, 2.8, 3.1, 4.1, 4.6, 4.6, 4.3, 3.4, 2.8, 2.9, 3.1, 3.2, 3.3, 3.3, 3.5, 4, 4.1, 4.5, 4.4, 4, 4.2, 4.4, 4.7, 4.4, 4, 3.8, 3.5, 3.7, 4.1, 3.9, 4.3, 4.5, 5, 5.5, 5.8, 6, 5.1, 4.3, 4, 3, 2.8, 2.9, 2.3, 2.4, 2.2, 2.6, 2.9, 3.2, 3.4, 2.9, 2.8]

### sheet: `Smoothed SA2 unemployment`
  row 0: ['Smoothed Unemployment', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
  row 1: ['Note: Cells containing a dash (-) indicate that data are unavailable. Estimates are unavailable either because the SA2 labour force estimate did not meet the minimum size or because there is a break in the series caused by the shift from the 2011 to the 2016 ASGS or the 2016 to 2021 ASGS. For more information, see the SALM Methodology page on the Department of Employment and Workplace Relations (DEWR) website and the 2016 or 2021 ASGS changeover user guides (also available from the DEWR website).', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
  row 2: [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
  row 3: ['Statistical Area Level 2 (SA2) (2021 ASGS)', 'SA2 Code (2021 ASGS)', datetime.datetime(2010, 12, 1, 0, 0), datetime.datetime(2011, 3, 1, 0, 0), datetime.datetime(2011, 6, 1, 0, 0), datetime.datetime(2011, 9, 1, 0, 0), datetime.datetime(2011, 12, 1, 0, 0), datetime.datetime(2012, 3, 1, 0, 0), datetime.datetime(2012, 6, 1, 0, 0), datetime.datetime(2012, 9, 1, 0, 0), datetime.datetime(2012, 12, 1, 0, 0), datetime.datetime(2013, 3, 1, 0, 0), datetime.datetime(2013, 6, 1, 0, 0), datetime.datetime(2013, 9, 1, 0, 0), datetime.datetime(2013, 12, 1, 0, 0), datetime.datetime(2014, 3, 1, 0, 0), datetime.datetime(2014, 6, 1, 0, 0), datetime.datetime(2014, 9, 1, 0, 0), datetime.datetime(2014, 12, 1, 0, 0), datetime.datetime(2015, 3, 1, 0, 0), datetime.datetime(2015, 6, 1, 0, 0), datetime.datetime(2015, 9, 1, 0, 0), datetime.datetime(2015, 12, 1, 0, 0), datetime.datetime(2016, 3, 1, 0, 0), datetime.datetime(2016, 6, 1, 0, 0), datetime.datetime(2016, 9, 1, 0, 0), datetime.datetime(2016, 12, 1, 0, 0), datetime.datetime(2017, 3, 1, 0, 0), datetime.datetime(2017, 6, 1, 0, 0), datetime.datetime(2017, 9, 1, 0, 0), datetime.datetime(2017, 12, 1, 0, 0), datetime.datetime(2018, 3, 1, 0, 0), datetime.datetime(2018, 6, 1, 0, 0), datetime.datetime(2018, 9, 1, 0, 0), datetime.datetime(2018, 12, 1, 0, 0), datetime.datetime(2019, 3, 1, 0, 0), datetime.datetime(2019, 6, 1, 0, 0), datetime.datetime(2019, 9, 1, 0, 0), datetime.datetime(2019, 12, 1, 0, 0), datetime.datetime(2020, 3, 1, 0, 0), datetime.datetime(2020, 6, 1, 0, 0), datetime.datetime(2020, 9, 1, 0, 0), datetime.datetime(2020, 12, 1, 0, 0), datetime.datetime(2021, 3, 1, 0, 0), datetime.datetime(2021, 6, 1, 0, 0), datetime.datetime(2021, 9, 1, 0, 0), datetime.datetime(2021, 12, 1, 0, 0), datetime.datetime(2022, 3, 1, 0, 0), datetime.datetime(2022, 6, 1, 0, 0), datetime.datetime(2022, 9, 1, 0, 0), datetime.datetime(2022, 12, 1, 0, 0), datetime.datetime(2023, 3, 1, 0, 0), datetime.datetime(2023, 6, 1, 0, 0), datetime.datetime(2023, 9, 1, 0, 0), datetime.datetime(2023, 12, 1, 0, 0), datetime.datetime(2024, 3, 1, 0, 0), datetime.datetime(2024, 6, 1, 0, 0), datetime.datetime(2024, 9, 1, 0, 0), datetime.datetime(2024, 12, 1, 0, 0), datetime.datetime(2025, 3, 1, 0, 0), datetime.datetime(2025, 6, 1, 0, 0), datetime.datetime(2025, 9, 1, 0, 0), datetime.datetime(2025, 12, 1, 0, 0)]
  row 4: ['Braidwood', 101021007, 53, 42, 38, 39, 44, 47, 51, 55, 53, 62, 65, 61, 69, 95, 107, 110, 102, 77, 61, 63, 67, 69, 70, 64, 63, 65, 66, 76, 80, 75, 78, 78, 77, 74, 70, 70, 65, 64, 73, 72, 78, 85, 90, 97, 106, 112, 101, 86, 78, 58, 50, 52, 44, 50, 53, 67, 77, 80, 82, 68, 57]
  row 5: ['Karabar', 101021008, 132, 99, 88, 83, 91, 96, 100, 113, 111, 137, 149, 142, 152, 196, 217, 222, 210, 165, 135, 139, 148, 152, 159, 155, 162, 179, 182, 205, 206, 192, 202, 209, 218, 206, 192, 187, 172, 183, 204, 191, 205, 211, 229, 250, 265, 273, 233, 199, 185, 137, 128, 133, 109, 116, 111, 132, 146, 159, 165, 140, 131]

### sheet: `Smoothed SA2 labour force`
  row 0: ['Smoothed Labour Force', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
  row 1: ['Note: Cells containing a dash (-) indicate that data are unavailable. Estimates are unavailable either because the SA2 labour force estimate did not meet the minimum size or because there is a break in the series caused by the shift from the 2011 to the 2016 ASGS or the 2016 to 2021 ASGS. For more information, see the SALM Methodology page on the Department of Employment and Workplace Relations (DEWR) website and the 2016 or 2021 ASGS changeover user guides (also available from the DEWR website).', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
  row 2: [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
  row 3: ['Statistical Area Level 2 (SA2) (2021 ASGS)', 'SA2 Code (2021 ASGS)', datetime.datetime(2010, 12, 1, 0, 0), datetime.datetime(2011, 3, 1, 0, 0), datetime.datetime(2011, 6, 1, 0, 0), datetime.datetime(2011, 9, 1, 0, 0), datetime.datetime(2011, 12, 1, 0, 0), datetime.datetime(2012, 3, 1, 0, 0), datetime.datetime(2012, 6, 1, 0, 0), datetime.datetime(2012, 9, 1, 0, 0), datetime.datetime(2012, 12, 1, 0, 0), datetime.datetime(2013, 3, 1, 0, 0), datetime.datetime(2013, 6, 1, 0, 0), datetime.datetime(2013, 9, 1, 0, 0), datetime.datetime(2013, 12, 1, 0, 0), datetime.datetime(2014, 3, 1, 0, 0), datetime.datetime(2014, 6, 1, 0, 0), datetime.datetime(2014, 9, 1, 0, 0), datetime.datetime(2014, 12, 1, 0, 0), datetime.datetime(2015, 3, 1, 0, 0), datetime.datetime(2015, 6, 1, 0, 0), datetime.datetime(2015, 9, 1, 0, 0), datetime.datetime(2015, 12, 1, 0, 0), datetime.datetime(2016, 3, 1, 0, 0), datetime.datetime(2016, 6, 1, 0, 0), datetime.datetime(2016, 9, 1, 0, 0), datetime.datetime(2016, 12, 1, 0, 0), datetime.datetime(2017, 3, 1, 0, 0), datetime.datetime(2017, 6, 1, 0, 0), datetime.datetime(2017, 9, 1, 0, 0), datetime.datetime(2017, 12, 1, 0, 0), datetime.datetime(2018, 3, 1, 0, 0), datetime.datetime(2018, 6, 1, 0, 0), datetime.datetime(2018, 9, 1, 0, 0), datetime.datetime(2018, 12, 1, 0, 0), datetime.datetime(2019, 3, 1, 0, 0), datetime.datetime(2019, 6, 1, 0, 0), datetime.datetime(2019, 9, 1, 0, 0), datetime.datetime(2019, 12, 1, 0, 0), datetime.datetime(2020, 3, 1, 0, 0), datetime.datetime(2020, 6, 1, 0, 0), datetime.datetime(2020, 9, 1, 0, 0), datetime.datetime(2020, 12, 1, 0, 0), datetime.datetime(2021, 3, 1, 0, 0), datetime.datetime(2021, 6, 1, 0, 0), datetime.datetime(2021, 9, 1, 0, 0), datetime.datetime(2021, 12, 1, 0, 0), datetime.datetime(2022, 3, 1, 0, 0), datetime.datetime(2022, 6, 1, 0, 0), datetime.datetime(2022, 9, 1, 0, 0), datetime.datetime(2022, 12, 1, 0, 0), datetime.datetime(2023, 3, 1, 0, 0), datetime.datetime(2023, 6, 1, 0, 0), datetime.datetime(2023, 9, 1, 0, 0), datetime.datetime(2023, 12, 1, 0, 0), datetime.datetime(2024, 3, 1, 0, 0), datetime.datetime(2024, 6, 1, 0, 0), datetime.datetime(2024, 9, 1, 0, 0), datetime.datetime(2024, 12, 1, 0, 0), datetime.datetime(2025, 3, 1, 0, 0), datetime.datetime(2025, 6, 1, 0, 0), datetime.datetime(2025, 9, 1, 0, 0), datetime.datetime(2025, 12, 1, 0, 0)]
  row 4: ['Braidwood', 101021007, 1761, 1806, 1832, 1859, 1885, 1899, 1917, 1931, 1941, 1944, 1925, 1876, 1830, 1807, 1805, 1832, 1871, 1898, 1901, 1929, 1934, 1941, 1962, 1951, 1916, 1884, 1885, 1927, 2011, 2069, 2078, 2059, 2065, 2086, 2125, 2210, 2229, 2248, 2261, 2228, 2196, 2159, 2143, 2126, 2136, 2146, 2172, 2182, 2196, 2197, 2201, 2232, 2300, 2383, 2427, 2455, 2426, 2398, 2363, 2326, 2318]
  row 5: ['Karabar', 101021008, 5249, 5363, 5425, 5475, 5513, 5501, 5489, 5468, 5439, 5395, 5292, 5108, 4931, 4822, 4767, 4798, 4860, 4884, 4848, 4874, 4843, 4819, 4832, 4768, 4645, 4528, 4493, 4553, 4711, 4809, 4788, 4705, 4682, 4693, 4747, 4907, 4919, 4932, 4938, 4845, 4754, 4656, 4602, 4545, 4550, 4559, 4606, 4615, 4631, 4620, 4613, 4663, 4784, 4934, 5000, 5039, 4968, 4905, 4834, 4759, 4745]

## ABS Population and People
ERROR: "There is no item named 'xl/externalLinks/_rels/externalLink2.xml.rels' in the archive"

## ABS Family and Community
`abs_data\Family and Community Database.xlsx`  (15,629,450 bytes)
sheet count: 3
  - Contents
  - Table 1
  - Table 2
### first sheet `Contents` — first 5 rows (truncated to 20 cols)
  row 0: ['            Australian Bureau of Statistics', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]...
  row 1: ['Data by region, 2011-25', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]...
  row 2: ['Released at 11.30am (Canberra time) 27 May 2025', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]...
  row 3: [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]...
  row 4: [None, 'Contents', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]...

## ABS Income
`abs_data\Income Database.xlsx`  (12,656,810 bytes)
sheet count: 4
  - Contents
  - Table 1
  - Table 2
  - Table 3
### first sheet `Contents` — first 5 rows (truncated to 20 cols)
  row 0: ['            Australian Bureau of Statistics', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]...
  row 1: ['Data by region, 2011-25', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]...
  row 2: ['Released at 11.30am (Canberra time) 11 November 2025', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]...
  row 3: [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]...
  row 4: [None, 'Contents', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]...

## ABS Education and Employment
`abs_data\Education and employment database.xlsx`  (14,325,582 bytes)
sheet count: 3
  - Contents
  - Table 1
  - Table 2
### first sheet `Contents` — first 5 rows (truncated to 20 cols)
  row 0: ['            Australian Bureau of Statistics', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]...
  row 1: ['Data by region, 2011-25', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]...
  row 2: ['Released at 11.30am (Canberra time) 11 November 2025', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]...
  row 3: [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]...
  row 4: [None, 'Contents', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]...

## ABS Economic and Industry Database (CSV — only 2.7KB)
`abs_data\Economic and Industry Database.csv`  (2,679 bytes)
Full contents:
```
            Australian Bureau of Statistics,,,,,,,,,,,,,,,,,,,,,,,,,
"Data by region, 2011-25",,,,,,,,,,,,,,,,,,,,,,,,,
Released at 11.30am (Canberra time) 11 November 2025,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,Contents,,,,,,,,,,,,,,,,,,,,,,,,
,Tables,,,,,,,,,,,,,,,,,,,,,,,,
,1,"ECONOMY AND INDUSTRY, Australia, State and Territory, Statistical Areas Level 2-4, Greater Capital City Statistical Areas, 2011, 2016-2024",,,,,,,,,,,,,,,,,,,,,,,
,2,"ECONOMY AND INDUSTRY, Local Government Areas, 2011, 2016-2024",,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,More information available from the ABS website,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,"Data by region, 2011-25",,,,,,,,,,,,,,,,,,,,,,,,
,Interactive Map,,,,,,,,,,,,,,,,,,,,,,,,
,Methodology,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,Inquiries,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,For further information about these and related statistics visit,,,,,,,,,,,,,,,,,,,,,,,,
,www.abs.gov.au/about/contact-us,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,� Commonwealth of Australia 2025,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,

```

## SA2 boundaries (ABS ASGS 2021)
`abs_data\SA2_2021_AUST.xlsx`  (250,022 bytes)
sheet count: 1
  - SA2_2021_AUST
### first sheet `SA2_2021_AUST` — first 3 rows
  row 0: ['SA2_CODE_2021', 'SA2_NAME_2021', 'CHANGE_FLAG_2021', 'CHANGE_LABEL_2021', 'SA3_CODE_2021', 'SA3_NAME_2021', 'SA4_CODE_2021', 'SA4_NAME_2021', 'GCCSA_CODE_2021', 'GCCSA_NAME_2021', 'STATE_CODE_2021', 'STATE_NAME_2021', 'AUS_CODE_2021', 'AUS_NAME_2021', 'AREA_ALBERS_SQKM', 'ASGS_LOCI_URI_2021']
  row 1: ['101021007', 'Braidwood', '0', 'No change', '10102', 'Queanbeyan', '101', 'Capital Region', '1RNSW', 'Rest of NSW', '1', 'New South Wales', 'AUS', 'Australia', 3418.3525, 'http://linked.data.gov.au/dataset/asgsed3/SA2/101021007']
  row 2: ['101021008', 'Karabar', '0', 'No change', '10102', 'Queanbeyan', '101', 'Capital Region', '1RNSW', 'Rest of NSW', '1', 'New South Wales', 'AUS', 'Australia', 6.9825, 'http://linked.data.gov.au/dataset/asgsed3/SA2/101021008']

## Postcode boundaries (ABS ASGS 2021)
`abs_data\POA_2021_AUST.xlsx`  (18,584,662 bytes)
sheet count: 1
  - POA_2021_AUST
### first sheet `POA_2021_AUST` — first 3 rows
  row 0: ['MB_CODE_2021', 'POA_CODE_2021', 'POA_NAME_2021', 'AUS_CODE_2021', 'AUS_NAME_2021', 'AREA_ALBERS_SQKM', 'ASGS_LOCI_URI_2021']
  row 1: ['70034860000', '0800', '0800', 'AUS', 'Australia', 0.0434, 'http://linked.data.gov.au/dataset/asgsed3/MB/70034860000']
  row 2: ['73861000000', '0800', '0800', 'AUS', 'Australia', 0.0218, 'http://linked.data.gov.au/dataset/asgsed3/MB/73861000000']

## Meshblock correspondence (ASGS edn3)
`abs_data\meshblock-correspondence-file-asgs-edn3.xlsx`  (14,590,449 bytes)
sheet count: 2
  - Metadata
  - Data
### first sheet `Metadata` — first 3 rows
  row 0: ['Meshblock correspondence file compiled and published by Queensland Treasury', None, None, None, None, None, None]
  row 1: [None, None, None, None, None, None, None]
  row 2: ['Variables', 'Description', 'Source', None, None, None, None]

## postcode_to_sa2_concordance.csv
`abs_data\postcode_to_sa2_concordance.csv`  (51,442 bytes)
  row 0: ['POSTCODE', 'SA2_CODE', 'SA2_NAME']
  row 1: ['0800', '701011001', 'DARWIN AIRPORT']
  row 2: ['0801', '701011008', 'STUART PARK']
  row 3: ['0810', '701021025', 'NIGHTCLIFF']
  row 4: ['0812', '701021020', 'LEANYER']
  row 5: ['0814', '701021025', 'NIGHTCLIFF']

## Births data — file search
Plan: 'Patrick has the file already' (ABS Cat 3301.0).
Searching for any file containing 'birth' (case-insensitive) at top-level of:
  - abs_data
  - .
  - data
  - C:\Users\Patrick Bell\Downloads

NO MATCHES — births file not present in expected locations.

## Anomaly: module2b_catchment.py in abs_data\
  `abs_data\module2b_catchment.py`  (29,674 bytes)
  Python script in data folder. Likely misplaced.
  First 15 lines:
  | """
  | module2b_catchment.py — Catchment & Market Context Enrichment
  | Remara Agent | Part of run_daily.py chain
  | 
  | INPUT:  leads_enriched.json  (from module2_enrichment.py)
  | OUTPUT: leads_catchment.json (enriched lead cards with catchment data)
  | 
  | Catchment block includes:
  |   - SA2 code + name (postcode->SA2 via fuzzy-matched concordance)
  |   - Population 0-4: latest value + CAGR growth trend
  |   - Median household income: latest value + CAGR growth trend
  |   - Estimated CCS subsidy rate at median income + gap fee sensitivity
  |   - SEIFA IRSD + IRSAD deciles (socio-economic indicators)
  |   - Supply ratio: LDC licensed places / under-5 population
  |   - NFP ratio: % of LDC centres in SA2 that are not-for-profit
