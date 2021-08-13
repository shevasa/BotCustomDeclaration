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

    async def get_task_type_emoji_by_task_type_name(self, task_type_name):
        sql = """select task_type_emoji from task_types where task_type_name=$1"""
        return await self.execute(sql, task_type_name, fetchval=True)

    async def get_document_type_name_by_id(self, document_type_id):
        sql = "select document_type_name from document_types where document_type_id=$1"
        return await self.execute(sql, document_type_id, fetchval=True)
