# Prompt: benchmark_jev_v1

**Stage:** benchmark only. Classification-only entrant, `typesafe/jev-1.13`, a decision model called through OpenRouter's `/api/alpha/decisions` endpoint. It takes a `state` text and a set of typed `questions` and returns a choice with probabilities for each question; it does not generate text. Its context window is 32,000 tokens, so the state is a bounded excerpt of the report (the opening pages, where the programme and design are described), prefixed with the name of the experiment unit to classify. Unlike the generative models, it is told which unit to classify, because it cannot enumerate units itself.

## System prompt

State template:

    STUDY: {project}
    EXPERIMENT UNIT TO CLASSIFY: {site_subgroup}
    REPORT EXCERPT:
    {excerpt}

Questions (one `choice` question per categorical field; the criteria are the data-dictionary definitions):

- `training_role` — instructions: "Role of training in the intervention delivered to this experiment unit." criteria: primary = "training or classroom instruction is the core service"; secondary = "training is one service among others, ancillary to the core service"; incidental = "training is a minor or occasional element".
- `has_classroom` — "Does the intervention include formal classroom instruction: vocational, GED, basic education, ESL, college?" yes / no.
- `has_ojt` — "Does the intervention include on-the-job training, apprenticeships, or structured work experience?" yes / no.
- `has_jsa` — "Does the intervention include job search assistance, job clubs, counseling, or placement services?" yes / no.
- `has_multiple_components` — "Does the intervention bundle more than one of classroom training, on-the-job training and job search assistance, or include other substantial components?" yes / no.
- `mandatory_voluntary` — "Was participation mandatory (e.g. a condition of receiving welfare) or voluntary?" mandatory / voluntary.
- `funding_public_private` — "Who funds the administration of the evaluated program (operational funding, not the evaluation)?" public = "government appropriations are the dominant funding source"; private = "philanthropic, corporate, or nonprofit self-generated funds are the dominant source"; mixed = "significant contributions from both public and private sectors".
- `admin_public_private` — "Who administers the program day-to-day?" public = "government agency such as a welfare office, workforce board, or public community college"; private = "nonprofit organization, community-based organization, or for-profit company"; mixed = "formal public-private partnership, or government program that contracts out core service delivery".
- `sector_program` — "Is this a sector program: sector-focused training by a community-based organization with employer engagement, targeting a specific industry, with employers involved in designing the curriculum?" yes / no.
