#!/usr/bin/env python3
"""Enter the P1 trial evaluations, outcome evidence, and revisits.

These are TRIAL evaluations under the DRAFT rubric, before Registration 2.
They are not registered verdicts. record_status = draft throughout.
"""
import csv
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
P = ROOT / "data" / "processed"
AS_OF = "2026-12-31"
CREATED_BY = "cc"
CREATED_DATE = "2026-08-26"

# evaluation_id, prediction_id, verdict, rationale, resolution_year, confidence, attribution, reading_defaulted
EVALUATIONS = [
    ("eval_simon1960", "pred_simon1960", "clearly_wrong",
     "Operationalised as: by 1980, could machines perform the range of work a human worker could perform? "
     "By 1980 deployed artificial intelligence consisted of narrow rule-based expert systems in circumscribed "
     "technical domains, with no system capable of general-purpose robotics, open-domain language use, or "
     "commonsense reasoning. The direction of the claim is contradicted at the stated horizon, not merely "
     "over-scaled. Coded on the capability_milestone track: tested on demonstrated capability, not on employment counts.",
     "1980", "high", "not_assessed", "false"),
    ("eval_rifkin1995", "pred_rifkin1995", "mostly_wrong",
     "Operationalised as: did the number of workers required to produce goods and services fall toward a "
     "near-workerless condition over the stated horizon? US total nonfarm employment rose 21 percent between "
     "1995 and 2020 and 35 percent by 2025, and the employment-population ratio fell only 2.1 percentage points "
     "between 1995 and 2019. The sectoral component of the claim fares better: manufacturing employment fell "
     "30 percent over the same period, so the direction holds within manufacturing while the aggregate claim "
     "is contradicted. Graded mostly_wrong rather than clearly_wrong because the locus-specific version survives.",
     "2020", "high", "low", "true"),
    ("eval_compton1938", "pred_compton1938", "mostly_correct",
     "Operationalised as: over the long run following 1938, did employment grow rather than contract under "
     "continued technological progress? US employment rose from 47.5 million in 1940 to 78.6 million in 1970 "
     "and nonfarm payroll employment more than doubled, while unemployment fell from 14.6 percent to 4.9 percent. "
     "Graded mostly_correct rather than clearly_correct because the claim is directional (T3), which the rubric "
     "caps at mostly_correct, and because the horizon is a defaulted reading of 'in the long run'.",
     "1970", "medium", "low", "true"),
    ("eval_freyosborne2013", "pred_freyosborne2013", "mixed",
     "Coded on the exposure_risk track, which applies a differential test: did the occupations the source ranked "
     "as high-exposure decline relative to low-exposure occupations? They did. Across 21 OECD countries from 2012 "
     "to 2019, employment in the riskiest half of occupations grew 6.1 percent against 17.8 percent in the least "
     "risky half. But no country saw net job destruction, and the retrospective literature finds the risk scores "
     "add no forecasting value over routine-task-intensity measures. The differential ranking holds; the implied "
     "scale does not. Note that the authors themselves restate the figure as exposure rather than predicted loss.",
     "2019", "medium", "low", "false"),
    ("eval_hinton2016", "pred_hinton2016", "mostly_wrong",
     "Operationalised as: by 2021, had deep learning displaced radiologists from image interpretation? It had not. "
     "Radiology faced a documented shortage rather than a surplus, and machine learning entered the specialty as "
     "a workflow tool rather than a substitute. The direction of travel — algorithms performing image-analysis "
     "tasks — was not contradicted, and the author has since conceded the timing while maintaining the direction, "
     "so the verdict is mostly_wrong rather than clearly_wrong. See the linked revisit row.",
     "2021", "medium", "low", "false"),
    ("eval_amodei2025", "pred_amodei2025", "too_early_to_tell",
     "The stated horizon runs to 2030 and has not elapsed at the cohort date of 2026-12-31. Recorded as "
     "too_early_to_tell and treated as right-censored in survival analysis; a later cohort appends a graded "
     "verdict rather than overwriting this row.",
     "", "high", "not_assessed", "false"),
]

# evidence_id, evaluation_id, type, dataset_name, series_id, citation, url, value_summary, covers_years, notes
EVIDENCE = [
    ("evid_simon1960a", "eval_simon1960", "academic_study",
     "", "",
     "Nils J. Nilsson, The Quest for Artificial Intelligence: A History of Ideas and Achievements, "
     "Cambridge University Press, 2010, pp. 291-301.",
     "https://ai.stanford.edu/~nilsson/QAI/qai.pdf",
     "By 1980 deployed artificial intelligence consisted of narrow rule-based expert systems in circumscribed "
     "technical domains - DENDRAL for mass-spectrum interpretation, MYCIN for antimicrobial therapy selection, "
     "and R1/XCON in production at Digital Equipment Corporation from 1980 - while natural-language understanding "
     "was demonstrated only in simulated micro-worlds, speech systems handled roughly 1,000-word constrained "
     "vocabularies, and no system performed general-purpose robotics or commonsense reasoning.",
     "1960-1980",
     "Nilsson asks that the web version not be cited; cite the Cambridge University Press print edition."),
    ("evid_simon1960b", "eval_simon1960", "academic_study",
     "", "",
     "James Lighthill, 'Artificial Intelligence: A General Survey', in Artificial Intelligence: a paper symposium, "
     "Science Research Council, London, 1973.",
     "https://www.chilton-computing.org.uk/inf/literature/reports/lighthill_report/p001.htm",
     "The 1973 Science Research Council survey concluded that 'in no part of the field have the discoveries made "
     "so far produced the major impact that was then promised', attributing the shortfall to a failure to "
     "recognise the implications of the combinatorial explosion.",
     "1972-1973",
     "Contemporaneous assessment at the midpoint of Simon's twenty-year horizon."),
    ("evid_rifkin1995a", "eval_rifkin1995", "official_statistics",
     "BLS Current Employment Statistics", "CES0000000001",
     "US Bureau of Labor Statistics, Current Employment Statistics, total nonfarm employees, seasonally adjusted, "
     "annual averages.",
     "https://api.bls.gov/publicAPI/v1/timeseries/data/",
     "US total nonfarm payroll employment rose from 117.4 million in 1995 to 142.2 million in 2020 and "
     "158.4 million in 2025.",
     "1995-2025",
     "Twelve-month means; seasonally adjusted and unadjusted series agree to within 0.03 percent."),
    ("evid_rifkin1995b", "eval_rifkin1995", "official_statistics",
     "BLS Current Employment Statistics", "CES3000000001",
     "US Bureau of Labor Statistics, Current Employment Statistics, manufacturing employees, seasonally adjusted, "
     "annual averages.",
     "https://api.bls.gov/publicAPI/v1/timeseries/data/",
     "US manufacturing employment fell from 17.2 million in 1995 to 12.1 million in 2020 and 12.6 million in 2025, "
     "leaving manufacturing at 8.0 percent of nonfarm payrolls.",
     "1995-2025",
     "The sectoral series is what keeps the verdict at mostly_wrong rather than clearly_wrong."),
    ("evid_compton1938a", "eval_compton1938", "census_series",
     "Historical Statistics of the United States, Colonial Times to 1970", "Series D 5; Series D 15",
     "US Bureau of the Census, Historical Statistics of the United States, Colonial Times to 1970, "
     "Bicentennial Edition, Washington DC, 1975, pp. 126-127.",
     "https://www2.census.gov/library/publications/1975/compendia/hist_stats_colonial-1970/hist_stats_colonial-1970p1-chD.pdf",
     "US employment rose from 47.5 million in 1940 to 78.6 million in 1970, an increase of 65.5 percent.",
     "1940-1970",
     "The 1940 figure covers ages 14 and over and the 1970 figure ages 16 and over, the standard Historical "
     "Statistics pairing; the same-concept 1940 census figure is 45.1 million."),
    ("evid_compton1938b", "eval_compton1938", "official_statistics",
     "Historical Statistics / BLS", "Series D 86; LNU04000000",
     "US Bureau of the Census, Historical Statistics of the United States, Colonial Times to 1970, p. 135; "
     "US Bureau of Labor Statistics, series LNU04000000.",
     "https://www2.census.gov/library/publications/1975/compendia/hist_stats_colonial-1970/hist_stats_colonial-1970p1-chD.pdf",
     "The US unemployment rate fell from 14.6 percent in 1940 to 4.9 percent in 1970.",
     "1940-1970",
     "The 1940 rate is Lebergott's; Darby's alternative treatment, which counts relief workers as employed, "
     "gives 9.5 percent. The choice of series is stated rather than assumed."),
    ("evid_fo2013a", "eval_freyosborne2013", "academic_study",
     "OECD Social, Employment and Migration Working Papers", "No. 255",
     "Alexandre Georgieff and Anna Milanez, 'What happened to jobs at high risk of automation?', OECD Social, "
     "Employment and Migration Working Papers No. 255, OECD Publishing, Paris, 2021. DOI 10.1787/10bc97f4-en.",
     "https://www.oecd-ilibrary.org/social-issues-migration-health/what-happened-to-jobs-at-high-risk-of-automation_10bc97f4-en",
     "Across 21 OECD countries from 2012 to 2019, employment in the riskiest half of occupations grew 6.1 percent "
     "against 17.8 percent in the least risky half, a fixed-effects coefficient of -0.172 implying 1.72 percentage "
     "points lower employment growth per 10-point increase in automation risk, while every country recorded net "
     "employment growth.",
     "2012-2019",
     "The differential test the exposure_risk track requires."),
    ("evid_fo2013b", "eval_freyosborne2013", "academic_study",
     "Melbourne Institute Working Paper", "10/19",
     "Michael Coelli and Jeff Borland, 'Behind the headline number: Why not to rely on Frey and Osborne's "
     "predictions of potential job loss from automation', Melbourne Institute Working Paper No. 10/19, "
     "University of Melbourne, 2019.",
     "https://ideas.repec.org/p/iae/iaewps/wp2019n10.html",
     "Frey and Osborne's risk scores are significantly negatively related to US occupation-level employment change "
     "from 2013 to 2018 but add no forecasting value over standard routine-task-intensity measures, and the "
     "underlying binary fully-automatable coding is subjectively assigned.",
     "2013-2018",
     "The critical paper still finds the differential effect; the criticism is about calibration, not sign."),
    ("evid_hinton2016a", "eval_hinton2016", "news_retrospective",
     "", "",
     "Arjun Byju, 'The \"Godfather of AI\" Predicted I Wouldn't Have a Job. He Was Wrong.', "
     "The New Republic, 25 October 2024.",
     "https://newrepublic.com/article/187203/ai-radiology-geoffrey-hinton-nobel-prediction",
     "Eight years after the prediction, deep learning had not replaced radiologists and the specialty faced the "
     "largest radiologist shortage in its history, with imaging backlogged for months at some centres.",
     "2016-2024",
     "Written by a radiology resident; a professional-press retrospective, not peer-reviewed. An occupational "
     "employment series for radiologists is the outstanding evidence gap for this verdict."),
]

# revisit_id, prediction_id, revisit_source_id, date, stance, quote, locator
REVISITS = [
    ("rev_freyosborne2024", "pred_freyosborne2013", "src_freyosborne2024", "2024-02-27", "reaffirmed",
     "while we expect AI to continue to surprise us, and for many jobs to be automated away, in the absence of "
     "major breakthroughs, we also expect the bottlenecks we outlined in our 2013 paper to continue to constrain "
     "our automation possibilities for the foreseeable future.",
     "Brown Journal of World Affairs 30(1), conclusion"),
]

REVISIT_SOURCES = [
    ("src_freyosborne2024",
     "Generative AI and the Future of Work: A Reappraisal",
     "Brown Journal of World Affairs 30(1)", "2024-02-27", "journal_article", "US", "en", "false",
     "https://ora.ox.ac.uk/objects/uuid:f52030f5-23eb-4481-a7f1-8006685edbae",
     "https://web.archive.org/web/20240531082002/https://ora.ox.ac.uk/objects/uuid:f52030f5-23eb-4481-a7f1-8006685edbae", "", "snowball",
     "Frey and Osborne's own reappraisal of their 2013 estimate; restates the 47 percent figure as exposure "
     "rather than predicted job loss"),
]


def append(name, rows):
    path = P / f"{name}.csv"
    existing = path.read_text(encoding="utf-8").splitlines()
    header_only = len(existing) <= 1
    with path.open("a", newline="", encoding="utf-8") as fh:
        csv.writer(fh, quoting=csv.QUOTE_MINIMAL, lineterminator="\n").writerows(rows)
    print(f"{name}.csv: +{len(rows)} rows (was {'empty' if header_only else len(existing) - 1})")


def main():
    ev_rows = []
    for eid, pid, verdict, rationale, resyear, conf, attrib, defaulted in EVALUATIONS:
        ev_rows.append([eid, pid, verdict, rationale, resyear, AS_OF, "jj", "", "",
                        "unblindable", conf, attrib, defaulted,
                        CREATED_BY, CREATED_DATE, "", "", "draft"])
    append("evaluations", ev_rows)
    append("outcome_evidence", [list(e) for e in EVIDENCE])

    # the revisit needs its own source row first
    src_rows = []
    for (sid, title, container, pub, stype, country, lang, istrans, url, arch, doi,
         track, notes) in REVISIT_SOURCES:
        src_rows.append([sid, title, container, pub, stype, country, lang, istrans,
                         url, arch, doi, track, "", "", "", "2026-08-26", "", notes])
    append("sources", src_rows)

    rv_rows = []
    for rid, pid, sid, date, stance, quote, locator in REVISITS:
        rv_rows.append([rid, pid, sid, date, stance, quote, locator,
                        CREATED_BY, CREATED_DATE, "", "", "draft"])
    append("revisits", rv_rows)


if __name__ == "__main__":
    main()
