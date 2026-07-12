# Data Source Reading Map

## Vietnamese ICD-10

1. Regulation page: https://chinhphu.vn/?docid=217536&pageid=27160
2. Circular PDF: https://datafiles.chinhphu.vn/cpp/files/vbpq/2026/4/06-byt.pdf
3. Official appendix PDF: https://datafiles.chinhphu.vn/cpp/files/vbpq/2026/4/06-byt-kem.pdf
4. Lookup/cross-check portal: https://icd.kcb.vn/icd-10/icd10

Store downloaded originals and checksum details under `data/raw/icd10_vi_2026/`. Never silently
replace the official source with ICD-10-CM or an independently translated dataset.

## RxNorm 2026

1. File format: https://www.nlm.nih.gov/research/umls/rxnorm/docs/rxnormfiles.html
2. Release endpoint: https://uts-ws.nlm.nih.gov/releases?releaseType=rxnorm-full-monthly-release
3. API reference: https://lhncbc.nlm.nih.gov/RxNav/APIs/RxNormAPIs.html

Pin one exact 2026 monthly archive and record its release date and checksum. Parse `RXNCONSO.RRF`
with the documented RRF columns; do not combine multiple monthly releases.
