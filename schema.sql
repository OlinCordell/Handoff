-- temp schema sketch pre alembic migration

create table handoffs (
    id serial primary key,
    current_owner text not null,
    receiving_party text,
    state text not null check (state in ('active', 'pending', 'accepted')),
    created_at timestamp not null default now(),
    updated_at timestamp not null default now()
);

create table handoff_events (
    id serial primary key
    handoff_id integer not null references handoffs(id) on delete cascade,
    action text not null,
    actor text not null,
    from_state text,
    to_state text,
    previous_owner text,
    current_owner text,
    created_at timestamp not null default now()
);