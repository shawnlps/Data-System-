BEGIN;

ALTER TABLE authored
    ADD CONSTRAINT uq_authored_pub_order UNIQUE (pub_id, author_order);

ALTER TABLE authored
    ADD CONSTRAINT fk_authored_author
        FOREIGN KEY (author_id) REFERENCES author(author_id);

ALTER TABLE authored
    ADD CONSTRAINT fk_authored_publication
        FOREIGN KEY (pub_id) REFERENCES publication(pub_id);

ALTER TABLE edited
    ADD CONSTRAINT uq_edited_pub_order UNIQUE (pub_id, editor_order);

ALTER TABLE edited
    ADD CONSTRAINT fk_edited_editor
        FOREIGN KEY (editor_id) REFERENCES editor(editor_id);

ALTER TABLE edited
    ADD CONSTRAINT fk_edited_publication
        FOREIGN KEY (pub_id) REFERENCES publication(pub_id);

COMMIT;
