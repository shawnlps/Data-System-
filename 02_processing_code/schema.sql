-- Final all-in-one schema for submission or one-shot setup.
-- For bulk loading, prefer:
--   1. schema_base.sql
--   2. load CSV data
--   3. schema_constraints.sql

BEGIN;

DROP TABLE IF EXISTS edited;
DROP TABLE IF EXISTS authored;
DROP TABLE IF EXISTS editor;
DROP TABLE IF EXISTS publication;
DROP TABLE IF EXISTS author;

CREATE TABLE author (
    author_id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    CONSTRAINT uq_author_name UNIQUE (name)
);

CREATE TABLE editor (
    editor_id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    CONSTRAINT uq_editor_name UNIQUE (name)
);

CREATE TABLE publication (
    pub_id BIGSERIAL PRIMARY KEY,
    pubkey TEXT NOT NULL,
    pub_type TEXT NOT NULL,
    title TEXT,
    year INT,
    journal TEXT,
    booktitle TEXT,
    pages TEXT,
    volume TEXT,
    number TEXT,
    month TEXT,
    publisher TEXT,
    address TEXT,
    isbn TEXT,
    school TEXT,
    chapter TEXT,
    url TEXT,
    ee TEXT,
    crossref TEXT,
    mdate DATE,
    publtype TEXT,
    cdate TEXT,
    CONSTRAINT uq_publication_pubkey UNIQUE (pubkey),
    CONSTRAINT chk_publication_type CHECK (
        pub_type IN (
            'article',
            'inproceedings',
            'proceedings',
            'book',
            'incollection',
            'phdthesis',
            'mastersthesis'
        )
    ),
    CONSTRAINT chk_publication_year CHECK (year IS NULL OR year BETWEEN 1900 AND 2100)
);

CREATE TABLE authored (
    author_id BIGINT NOT NULL,
    pub_id BIGINT NOT NULL,
    author_order INT NOT NULL,
    PRIMARY KEY (author_id, pub_id),
    CONSTRAINT chk_authored_order CHECK (author_order >= 1),
    CONSTRAINT uq_authored_pub_order UNIQUE (pub_id, author_order),
    CONSTRAINT fk_authored_author
        FOREIGN KEY (author_id) REFERENCES author(author_id),
    CONSTRAINT fk_authored_publication
        FOREIGN KEY (pub_id) REFERENCES publication(pub_id)
);

CREATE TABLE edited (
    editor_id BIGINT NOT NULL,
    pub_id BIGINT NOT NULL,
    editor_order INT NOT NULL,
    PRIMARY KEY (editor_id, pub_id),
    CONSTRAINT chk_edited_order CHECK (editor_order >= 1),
    CONSTRAINT uq_edited_pub_order UNIQUE (pub_id, editor_order),
    CONSTRAINT fk_edited_editor
        FOREIGN KEY (editor_id) REFERENCES editor(editor_id),
    CONSTRAINT fk_edited_publication
        FOREIGN KEY (pub_id) REFERENCES publication(pub_id)
);

COMMIT;
