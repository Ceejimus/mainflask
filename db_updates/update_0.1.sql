create table "authentication"."group" (
    "id" text not null,
    "name" text not null
);


create table "authentication"."usergroup" (
    "userid" integer not null,
    "groupid" text not null
);


alter table "authentication"."user" add column "pending" boolean not null default true;

CREATE UNIQUE INDEX group_name_key ON authentication."group" USING btree (name);

CREATE UNIQUE INDEX group_pkey ON authentication."group" USING btree (id);

alter table "authentication"."group" add constraint "group_pkey" PRIMARY KEY using index "group_pkey";

alter table "authentication"."group" add constraint "group_name_key" UNIQUE using index "group_name_key";

alter table "authentication"."usergroup" add constraint "usergroup_groupid_fkey" FOREIGN KEY (groupid) REFERENCES authentication."group"(id);

alter table "authentication"."usergroup" add constraint "usergroup_userid_fkey" FOREIGN KEY (userid) REFERENCES authentication."user"(id);


