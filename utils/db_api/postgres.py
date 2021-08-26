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
        sql = """select t.user_tg_id, tp.task_type_name, t.comment, a.num_of_files, ts.task_status_name, t.task_id, t.worker_comment from tasks t
    left join task_types tp on tp.task_type_id=t.task_type_id
    left join (select task_id, count(document_file_id) as num_of_files from documents group by task_id) a on a.task_id=t.task_id
    left join task_status ts on ts.task_status_id=t.status_id 
    where t.task_id=$1"""
        return await self.execute(sql, task_id, fetchrow=True)

    async def get_tasks_by_status_id(self, status_id):
        sql = """select t.task_id, u.full_name, tp.task_type_name, ts.task_status_name, t.comment, t.worker_comment from tasks t
            left join task_types tp on tp.task_type_id=t.task_type_id
            left join task_status ts on ts.task_status_id=t.status_id
            left join users u on u.telegram_id=t.user_tg_id 
            where t.status_id=$1"""
        return await self.execute(sql, status_id, fetch=True)

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
        sql = """select document_type_id from document_types where document_type_name like 'Информация%'"""
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

    async def get_number_of_tasks_by_status_id(self, status_id, task_type_id: Union[int, None] = None):
        if task_type_id is None:
            sql = "select count(task_id) from tasks where status_id=$1"
            return await self.execute(sql, status_id, fetchval=True)
        else:
            sql = "select count(task_id) from tasks where status_id=$1 and task_type_id=$2"
            return await self.execute(sql, status_id, task_type_id, fetchval=True)

    async def get_ignored_tasks(self):
        sql = "select t.task_id, u.full_name, t.created_at, ts.task_status_name, tt.task_type_name from tasks t " \
              "left join task_types tt on tt.task_type_id=t.task_type_id " \
              "left join users u on u.telegram_id=t.user_tg_id " \
              "left join task_status ts on ts.task_status_id=t.status_id " \
              "where age(current_timestamp, t.created_at)>'1 minute'" \
              "and tt.task_type_name='МД' " \
              "and t.status_id=1 or t.status_id=4"
        return await self.execute(sql, fetch=True)

    async def add_admin_comment_by_task_id(self, task_id, admin_comment):
        sql = """update tasks set admin_comment=$2 where task_id=$1"""
        return await self.execute(sql, task_id, admin_comment, execute=True)

