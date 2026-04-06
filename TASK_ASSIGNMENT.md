# Task Assignment

## Current Project Status

The core work of Part 1 has already been completed:

- E/R diagram is finished.
- Schema design is finished.
- DBLP XML parsing script is finished.
- Final CSV files have been generated.
- Data has been imported into the PostgreSQL database `dblp`.
- Base constraints and post-loading constraints have been added.

Handoff directory:

- `dblp_project/00_handoff/`

Its contents are organized as:

- `01_original_source/`: original-source-related files
- `02_processing_code/`: schema files and parsing script
- `03_csv_for_sql/`: final CSV files for SQL work
- `04_docs/`: ER diagram and project brief
- `README.md`: short handoff note

## Student A: Part 2 Queries and Experiments

Student A is responsible for Part 2 of the project.

### Main Tasks

1. Understand the database structure by reading:
   - `02_processing_code/schema.sql`
   - `04_docs/ER_diagram.png`
   - `README.md`

2. Use the existing PostgreSQL database `dblp` directly.
   The data-loading stage has already been completed, so there is no need to redo data processing.

3. Implement the 8 SQL queries required in the assignment, including:
   - publication type counts
   - conferences with more than 1000 papers in one year
   - 10-year window conference publication statistics
   - most collaborative authors
   - top authors for Data-related venues in recent years
   - conferences held in June with more than 200 publications
   - long-term publishing authors / earliest publication authors
   - one self-designed join query

4. Save for each query:
   - the SQL statement
   - result screenshots
   - execution time

5. Run the same queries on reduced dataset sizes:
   - full dataset
   - half-sized dataset
   - quarter-sized dataset

6. Produce final deliverables:
   - `queries.sql`
   - screenshots for query results
   - execution-time records
   - records for reduced-size experiments

### Priority

The first goal is:

- get all 8 queries working correctly
- then organize screenshots and running times

## Student B: Part 3 Indexing and Report Integration

Student B is responsible for Part 3 and report integration.

### Main Tasks

1. Read the schema and assignment materials first:
   - `02_processing_code/schema.sql`
   - `04_docs/ER_diagram.png`
   - project brief PDF

2. Review query performance after Student A finishes the main SQL queries.

3. Design indexes for slow queries.
   Possible important fields include:
   - `publication.year`
   - `publication.pub_type`
   - `publication.journal`
   - `publication.booktitle`
   - `publication.title`
   - `authored.pub_id`
   - `authored.author_id`
   - `edited.pub_id`

4. Compare performance before and after indexing:
   - run query before index
   - run query after index
   - record timing differences
   - analyze whether the index helps

5. Write Part 3 materials:
   - `CREATE INDEX` statements
   - why each index was chosen
   - which queries improved
   - which queries did not improve much and why

6. Help integrate the final report:
   - summarize Part 1 workflow briefly
   - organize Part 2 timing figures
   - write Part 3 indexing analysis

### Final Deliverables

- `indexes.sql`
- indexing performance comparison records
- Part 3 analysis text
- final report contribution for indexing/performance optimization

### Priority

The first goal is:

- identify slow queries from Student A
- optimize them with indexes
- write the analysis clearly

## Recommended Collaboration Order

1. Student A first finishes all 8 SQL queries.
2. Student B reads the schema and prepares the indexing analysis framework.
3. Student A sends the slow-query list and timing results to Student B.
4. Student B performs index experiments on the slow queries.
5. Student A organizes results/screenshots.
6. Student B organizes optimization conclusions.
7. Both sides merge materials into the final report and presentation.

## Important Notes

- Final CSV files are in:
  - `03_csv_for_sql/`

- The file `publications.csv.gz` is compressed because the full publication dataset is very large.
  To decompress it:

```bash
gunzip -k publications.csv.gz
```

- Database name:
  - `dblp`

- Data processing has already been completed.
  The next teammate should directly continue with SQL queries and indexing work.
