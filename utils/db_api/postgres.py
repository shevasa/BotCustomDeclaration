import logging
from typing import Union

import asyncpg
from asyncpg import Pool, Connection

from data import config


class Database:
    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME
        )

    async def execute(self, command, *args,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      fetch: bool = False,
                      execute: bool = False
                      ):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    async def create_table_users(self):
        sql = """create table if not exists users 
            (
                telegram_id      bigint not null
                    constraint users_pk
                        primary key,
                full_name        varchar,
                telephone_number varchar,
                username         varchar,
                tg_url           varchar
            );
            
            alter table users
                owner to ilya;
            """
        return await self.execute(sql, execute=True)

    async def create_table_workers(self):
        sql = """create table if not exists workers
            (
                worker_id        serial not null
                    constraint workers_pk
                        primary key,
                worker_full_name varchar,
                worker_contact   varchar,
                worker_url       integer
            );

            alter table users
                owner to ilya;
            """
        return await self.execute(sql, execute=True)

    async def create_table_document_types(self):
        sql = """create table if not exists document_types
                (
                    document_type_id   serial not null
                        constraint document_types_pk
                            primary key,
                    document_type_name varchar
                );
                
                alter table document_types
                    owner to ilya;
            """
        return await self.execute(sql, execute=True)

    async def create_table_task_status(self):
        sql = """create table if not exists task_status
                (
                    task_status_id   serial not null
                        constraint task_status_pk
                            primary key,
                    task_status_name varchar
                );
                
                alter table task_status
                    owner to ilya;
            """
        return await self.execute(sql, execute=True)

    async def create_table_task_types(self):
        sql = """create table if not exists task_types
                    (
                        task_type_id    serial not null
                            constraint task_types_pk
                                primary key,
                        task_type_name  varchar,
                        task_type_emoji varchar
                    );
                    
                    alter table task_types
                        owner to ilya;
            """
        return await self.execute(sql, execute=True)

    async def create_table_worker_task_types(self):
        sql = """create table if not exists worker_task_types
                    (
                        worker_id    integer
                            constraint "worker's_task_types_workers_worker_id_fk"
                                references workers
                                on update cascade on delete cascade,
                        task_type_id integer
                            constraint "worker's_task_types_task_types_task_type_id_fk"
                                references task_types
                                on update cascade on delete cascade
                    );
                    
                    alter table worker_task_types
                        owner to ilya;
            """
        return await self.execute(sql, execute=True)

    async def create_table_needed_documents(self):
        sql = """create table if not exists needed_documents
                    (
                        task_type_id     integer
                            constraint needed_documents_task_types_task_type_id_fk
                                references task_types
                                on update cascade on delete cascade,
                        document_type_id integer
                            constraint needed_documents_document_types_document_type_id_fk
                                references document_types
                                on update cascade on delete cascade
                    );
                    
                    alter table needed_documents
                        owner to ilya;
            """
        return await self.execute(sql, execute=True)

    async def create_table_tasks(self):
        sql = """create table if not exists tasks
                (
                    task_id             serial not null
                        constraint tasks_pk
                            primary key,
                    task_type_id        integer
                        constraint tasks_task_types_task_type_id_fk
                            references task_types
                            on update cascade on delete cascade,
                    user_tg_id          bigint
                        constraint tasks_users_telegram_id_fk
                            references users
                            on update cascade on delete cascade,
                    worker_tg_id        bigint
                        constraint tasks_workers_worker_id_fk
                            references workers
                            on update cascade on delete cascade,
                    status_id           integer
                        constraint tasks_task_status_task_status_id_fk
                            references task_status
                            on update cascade on delete cascade,
                    comment             varchar,
                    worker_comment      varchar,
                    created_at          timestamp default (CURRENT_TIMESTAMP + '03:00:00'::interval),
                    worker_comment_time timestamp,
                    admin_comment       varchar
                );
                
                alter table tasks
                    owner to ilya;
            """
        return await self.execute(sql, execute=True)

    async def create_table_documents(self):
        sql1 = """create sequence if not exists documents_document_file_id_seq;
                alter sequence documents_document_file_id_seq owner to ilya;
                """

        sql2 = """
        create table if not exists documents
                (
                    -- Only integer types can be auto increment
                    document_file_id      varchar default nextval('documents_document_file_id_seq'::regclass) not null 
                        constraint documents_pk
                            primary key,
                    task_id               integer
                        constraint documents_tasks_task_id_fk
                            references tasks
                            on update cascade on delete cascade,
                    document_type_id      integer
                        constraint documents_document_types_document_type_id_fk
                            references document_types
                            on update cascade on delete cascade,
                    document_content_type varchar,
                    text                  varchar
                );
                
                alter table documents
                    owner to ilya;
            """

        await self.execute(sql1, execute=True)

        return await self.execute(sql2, execute=True)

    async def create_and_run_procedure_insert(self):
        sql1 = """create or replace procedure insert_if_empty()
                    language plpgsql
                    as $$
                    begin
                        if (not exists(select 1 from document_types)) then
                            INSERT INTO document_types (document_type_id, document_type_name) VALUES (2, 'CMR');
                            INSERT INTO document_types (document_type_id, document_type_name) VALUES (3, 'Паспорт водителя');
                            INSERT INTO document_types (document_type_id, document_type_name) VALUES (4, 'Invoice');
                            INSERT INTO document_types (document_type_id, document_type_name) VALUES (5, 'Экспортная декларация(при наличии)');
                            INSERT INTO document_types (document_type_id, document_type_name) VALUES (8, 'Упаковочный лист(при наличии)');
                            INSERT INTO document_types (document_type_id, document_type_name) VALUES (11, 'Номер телефона водителя');
                            INSERT INTO document_types (document_type_id, document_type_name) VALUES (1, 'Техпаспорт(тягач-прицеп)');
                            INSERT INTO document_types (document_type_id, document_type_name) VALUES (12, 'Информация о пункте въезда в страну ЕС, в Турцию и место таможенной очистки(растаможка)');
                            INSERT INTO document_types (document_type_id, document_type_name) VALUES (13, 'Экспортная декларация');
                            INSERT INTO document_types (document_type_id, document_type_name) VALUES (14, 'Загран. паспорт водителя');
                            INSERT INTO document_types (document_type_id, document_type_name) VALUES (10, 'Информация о пункте въезда на территорию Украины и пункте выезда из Украины');
                            INSERT INTO document_types (document_type_id, document_type_name) VALUES (9, 'Информация о пункте въезда на территорию Республики Беларусь и пункте таможенной очистки(растаможка)');
                            INSERT INTO document_types (document_type_id, document_type_name) VALUES (15, 'Таможенное свидетельство(жёлтое)');
                            INSERT INTO document_types (document_type_id, document_type_name) VALUES (6, 'Информация о пункте въезда в страну ЕС и место таможенной очистки (растаможка)');
                        end if;
                    
                        if (not exists(select 1 from task_status)) then
                            INSERT INTO task_status (task_status_id, task_status_name) VALUES (2, 'В работе');
                            INSERT INTO task_status (task_status_id, task_status_name) VALUES (3, 'В редактировании');
                            INSERT INTO task_status (task_status_id, task_status_name) VALUES (1, 'Новая заявка');
                            INSERT INTO task_status (task_status_id, task_status_name) VALUES (5, 'Завершена');
                            INSERT INTO task_status (task_status_id, task_status_name) VALUES (4, 'Изменённая заявка');
                        end if;
                    
                        if (not exists(select 1 from task_types)) then
                            INSERT INTO task_types (task_type_id, task_type_name, task_type_emoji) VALUES (1, 'T1 ЕС', '🇪🇺');
                            INSERT INTO task_types (task_type_id, task_type_name, task_type_emoji) VALUES (2, 'МД', '🇲🇩');
                            INSERT INTO task_types (task_type_id, task_type_name, task_type_emoji) VALUES (4, 'ЭПИ Беларусь', '🇧🇾');
                            INSERT INTO task_types (task_type_id, task_type_name, task_type_emoji) VALUES (5, 'Укр. транзит', '🇺🇦');
                            INSERT INTO task_types (task_type_id, task_type_name, task_type_emoji) VALUES (3, 'ЗДП', '🇺🇦');
                            INSERT INTO task_types (task_type_id, task_type_name, task_type_emoji) VALUES (6, 'T1 Турция', '🇹🇷');
                        end if;
                        
                        if (not exists(select 1 from workers)) then
                            INSERT INTO public.workers (worker_id, worker_full_name, worker_contact, worker_url) VALUES (617857847, 'Lavrentii_ber', null, null);
                            INSERT INTO public.workers (worker_id, worker_full_name, worker_contact, worker_url) VALUES (925075502, 'Aleksandr', null, null);
                        end if;
                    
                        if (not exists(select 1 from worker_task_types)) then
                            INSERT INTO worker_task_types (worker_id, task_type_id) VALUES (925075502, 1);
                            INSERT INTO worker_task_types (worker_id, task_type_id) VALUES (925075502, 3);
                            INSERT INTO worker_task_types (worker_id, task_type_id) VALUES (925075502, 4);
                            INSERT INTO worker_task_types (worker_id, task_type_id) VALUES (925075502, 5);
                            INSERT INTO worker_task_types (worker_id, task_type_id) VALUES (925075502, 6);
                            INSERT INTO worker_task_types (worker_id, task_type_id) VALUES (617857847, 2);
                        end if;
                    
                        if (not exists(select 1 from needed_documents)) then
                            INSERT INTO needed_documents (task_type_id, document_type_id) VALUES (1, 2);
                            INSERT INTO needed_documents (task_type_id, document_type_id) VALUES (1, 4);
                            INSERT INTO needed_documents (task_type_id, document_type_id) VALUES (1, 1);
                            INSERT INTO needed_documents (task_type_id, document_type_id) VALUES (1, 5);
                            INSERT INTO needed_documents (task_type_id, document_type_id) VALUES (1, 6);
                            INSERT INTO needed_documents (task_type_id, document_type_id) VALUES (6, 2);
                            INSERT INTO needed_documents (task_type_id, document_type_id) VALUES (6, 4);
                            INSERT INTO needed_documents (task_type_id, document_type_id) VALUES (6, 1);
                            INSERT INTO needed_documents (task_type_id, document_type_id) VALUES (6, 5);
                            INSERT INTO needed_documents (task_type_id, document_type_id) VALUES (6, 12);
                            INSERT INTO needed_documents (task_type_id, document_type_id) VALUES (2, 2);
                            INSERT INTO needed_documents (task_type_id, document_type_id) VALUES (2, 4);
                            INSERT INTO needed_documents (task_type_id, document_type_id) VALUES (2, 1);
                            INSERT INTO needed_documents (task_type_id, document_type_id) VALUES (2, 3);
                            INSERT INTO needed_documents (task_type_id, document_type_id) VALUES (2, 5);
                            INSERT INTO needed_documents (task_type_id, document_type_id) VALUES (3, 2);
                            INSERT INTO needed_documents (task_type_id, document_type_id) VALUES (3, 4);
                            INSERT INTO needed_documents (task_type_id, document_type_id) VALUES (3, 13);
                            INSERT INTO needed_documents (task_type_id, document_type_id) VALUES (4, 2);
                            INSERT INTO needed_documents (task_type_id, document_type_id) VALUES (4, 4);
                            INSERT INTO needed_documents (task_type_id, document_type_id) VALUES (4, 1);
                            INSERT INTO needed_documents (task_type_id, document_type_id) VALUES (4, 14);
                            INSERT INTO needed_documents (task_type_id, document_type_id) VALUES (4, 15);
                            INSERT INTO needed_documents (task_type_id, document_type_id) VALUES (4, 8);
                            INSERT INTO needed_documents (task_type_id, document_type_id) VALUES (4, 9);
                            INSERT INTO needed_documents (task_type_id, document_type_id) VALUES (5, 2);
                            INSERT INTO needed_documents (task_type_id, document_type_id) VALUES (5, 4);
                            INSERT INTO needed_documents (task_type_id, document_type_id) VALUES (5, 1);
                            INSERT INTO needed_documents (task_type_id, document_type_id) VALUES (5, 3);
                            INSERT INTO needed_documents (task_type_id, document_type_id) VALUES (5, 10);
                            INSERT INTO needed_documents (task_type_id, document_type_id) VALUES (5, 11);
                        end if;
                        
                    end;$$"""
        sql2 = "call insert_if_empty()"
        await self.execute(sql1, execute=True)
        await self.execute(sql2, execute=True)

    async def add_user(self, telegram_id, full_name, username, tg_url, telephone_number=None):
        sql = """insert into users (telegram_id, full_name, username, tg_url, telephone_number)
        values ($1, $2, $3, $4, $5) returning *"""

        return await self.execute(sql, telegram_id, full_name, username, tg_url, telephone_number, execute=True)

    async def get_all_task_types(self):
        sql = """select task_type_name, task_type_emoji from task_types"""
        return await self.execute(sql, fetch=True)

    async def all_needed_documents_by_task_name(self, task_name):
        sql = """select dt.document_type_name, dt.document_type_id from (select task_type_id from task_types where task_type_name=$1) tt
                        left join needed_documents nd on nd.task_type_id = tt.task_type_id
                        left join document_types dt on dt.document_type_id = nd.document_type_id
                        """
        return await self.execute(sql, task_name, fetch=True)

    async def get_task_type_id_and_emoji_by_task_type_name(self, task_type_name):
        sql = """select task_type_id, task_type_emoji from task_types where task_type_name=$1"""
        return await self.execute(sql, task_type_name, fetchrow=True)

    async def get_task_type_name_by_task_id(self, task_id):
        sql = """select tt.task_type_name from tasks t
        left join task_types tt on tt.task_type_id=t.task_type_id
        where t.task_id=$1"""
        return await self.execute(sql, task_id, fetchval=True)

    async def get_document_type_name_by_id(self, document_type_id):
        sql = "select document_type_name from document_types where document_type_id=$1"
        return await self.execute(sql, document_type_id, fetchval=True)

    async def create_new_task(self, task_type_id: int, user_tg_id: int, comment: str, worker_tg_id=329760591,
                              status_id=1, worker_comment: str = ""):
        sql = """insert into tasks (task_type_id, user_tg_id, worker_tg_id, status_id, comment, worker_comment) 
        values ($1, $2, $3, $4, $5, $6) returning *"""
        return await self.execute(sql, task_type_id, user_tg_id, worker_tg_id, status_id, comment, worker_comment,
                                  fetchrow=True)

    async def save_new_document_to_db(self, document_file_id: str, task_id: int, document_type_id: int,
                                      document_content_type: str):
        sql = """insert into documents(document_file_id, task_id, document_type_id, document_content_type) values
        ($1, $2, $3, $4)"""
        return await self.execute(sql, document_file_id, task_id, document_type_id, document_content_type, execute=True)

    async def save_new_text_document_to_db(self, task_id: int, document_type_id: int,
                                           document_content_type: str, document_text: str):
        sql = """insert into documents(task_id, document_type_id, document_content_type, text) values
        ($1, $2, $3, $4)"""
        return await self.execute(sql, task_id, document_type_id, document_content_type, document_text, execute=True)

    async def get_task_by_task_id(self, task_id):
        sql = """select t.user_tg_id, t.status_id, tp.task_type_name, t.comment, a.num_of_files, ts.task_status_name, t.task_id, 
        t.worker_comment, t.admin_comment, t.worker_tg_id from tasks t
    left join task_types tp on tp.task_type_id=t.task_type_id
    left join (select task_id, count(document_file_id) as num_of_files from documents group by task_id) a on a.task_id=t.task_id
    left join task_status ts on ts.task_status_id=t.status_id 
    where t.task_id=$1"""
        return await self.execute(sql, task_id, fetchrow=True)

    async def get_tasks_by_status_id(self, status_id, worker_tg_id):
        sql = """select t.task_id, u.full_name, tp.task_type_name, ts.task_status_name, t.comment, t.worker_comment,
         w.worker_full_name from tasks t
            left join task_types tp on tp.task_type_id=t.task_type_id
            left join task_status ts on ts.task_status_id=t.status_id
            left join users u on u.telegram_id=t.user_tg_id
            left join workers w on w.worker_id=t.worker_tg_id  
            where t.status_id=$1 and t.worker_tg_id=$2"""
        return await self.execute(sql, status_id, worker_tg_id, fetch=True)

    async def get_all_task_files(self, task_id, document_type_id):
        sql = """select d.document_file_id as media, d.document_content_type as type from documents d
                where d.task_id = $1 and d.document_type_id = $2;"""
        return await self.execute(sql, task_id, document_type_id, fetch=True)

    async def get_all_tasks_by_user_tg_id(self, user_tg_id):
        sql = """select t.task_id, tp.task_type_name, t.comment, a.num_of_files, ts.task_status_name, t.task_id from tasks t
    left join task_types tp on tp.task_type_id=t.task_type_id
    left join (select task_id, count(document_file_id) as num_of_files from documents group by task_id) a on a.task_id=t.task_id
    left join task_status ts on ts.task_status_id=t.status_id 
    where t.user_tg_id=$1"""
        return await self.execute(sql, user_tg_id, fetch=True)

    async def delete_task_files_by_task_id(self, task_id):
        sql = """delete from documents where task_id=$1"""
        return await self.execute(sql, task_id, execute=True)

    async def get_document_type_id_that_can_be_text(self):
        sql = """select document_type_id from document_types where document_type_name like 'Информация%' or 
        document_type_name like 'Номер телефона%'"""
        return await self.execute(sql, fetch=True)

    async def get_document_type_id_by_doc_name(self, document_name: str):
        sql = "select document_type_id from document_types where document_type_name=$1"
        return await self.execute(sql, document_name, fetchval=True)

    async def change_task_status(self, task_id: int, new_task_status_id: int, worker_comment: Union[None, str] = None):
        if new_task_status_id == 3 and worker_comment:
            sql0 = "update tasks set status_id=$1 where task_id=$2 returning user_tg_id"
            sql1 = "update tasks set worker_comment=$1 where task_id=$2 returning user_tg_id"
            await self.execute(sql0, new_task_status_id, task_id, fetchval=True)
            return await self.execute(sql1, worker_comment, task_id, fetchval=True)
        else:
            sql = "update tasks set status_id=$1 where task_id=$2 returning user_tg_id"
            return await self.execute(sql, new_task_status_id, task_id, fetchval=True)

    async def get_number_of_tasks_by_status_id(self, status_id, worker_tg_id: int,
                                               month: bool = False, day: bool = False):
        if day:
            sql = "select count(task_id) from tasks where status_id=$1 and worker_tg_id=$2 " \
                  "and date(created_at) = current_date;"
        elif month:
            sql = "select count(task_id) from tasks where status_id=$1 and worker_tg_id=$2 " \
                  "and extract(month from created_at) = date_part('month', (select current_timestamp));"
        else:
            sql = "select count(task_id) from tasks where status_id=$1 and worker_tg_id=$2"
        return await self.execute(sql, status_id, worker_tg_id, fetchval=True)

    async def get_ignored_tasks(self):
        sql = "select t.task_id, u.full_name, t.created_at, ts.task_status_name, tt.task_type_name from tasks t " \
              "left join task_types tt on tt.task_type_id=t.task_type_id " \
              "left join users u on u.telegram_id=t.user_tg_id " \
              "left join task_status ts on ts.task_status_id=t.status_id " \
              "where age(current_timestamp+'3 hours', t.created_at)>'20 minute' " \
              "and tt.task_type_name='МД' " \
              "and t.status_id=1 or " \
              "age(current_timestamp+'3 hours', t.created_at)>'20 minute' " \
              "and tt.task_type_name='МД' " \
              "and t.status_id=4"
        return await self.execute(sql, fetch=True)

    async def add_admin_comment_by_task_id(self, task_id, admin_comment):
        sql = """update tasks set admin_comment=$2 where task_id=$1"""
        return await self.execute(sql, task_id, admin_comment, execute=True)

    async def select_worker_by_task_type_id(self, task_type_id):
        sql = 'select worker_id from worker_task_types where task_type_id=$1'
        return await self.execute(sql, task_type_id, fetchval=True)
