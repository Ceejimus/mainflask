CREATE SCHEMA authentication;

create sequence "authentication"."user_id_seq";

create table "authentication"."user" (
    "id" integer not null default nextval('user_id_seq'::regclass),
    "username" text not null,
    "email" text not null,
    "password_hash" bytea not null,
    "salt" bytea not null
);


create table "public"."revision" (
    "version" text not null,
    "date_applied" timestamp without time zone not null default now()
);


CREATE UNIQUE INDEX user_email_key ON authentication."user" USING btree (email);

CREATE UNIQUE INDEX user_pkey ON authentication."user" USING btree (id);

CREATE UNIQUE INDEX user_username_key ON authentication."user" USING btree (username);

alter table "authentication"."user" add constraint "user_pkey" PRIMARY KEY using index "user_pkey";

alter table "authentication"."user" add constraint "user_email_key" UNIQUE using index "user_email_key";

alter table "authentication"."user" add constraint "user_username_key" UNIQUE using index "user_username_key";


