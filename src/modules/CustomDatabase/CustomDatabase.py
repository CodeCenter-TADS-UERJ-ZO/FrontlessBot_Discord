"""Custom Database"""
# pylint: disable=all
import typing
import aiosqlite


class CustomDatabase:
    """Abstraction layer for SQLite connections"""

    def __init__(
        self,
        database: aiosqlite.Connection,
        wait_func: typing.Callable | None,
    ) -> None:
        self.database: aiosqlite.Connection = database
        if wait_func is not None:
            self.wait_func: typing.Callable = wait_func

    async def insert(
        self, table: str, arguments: list[str], parameters: tuple[typing.Any]
    ) -> None:
        """Insert into the desired table in database."""
        if len(parameters) != len(arguments):
            return

        base_cmd: str = "INSERT OR IGNORE INTO"
        args_str: str = ",".join(arguments)
        _temp_parms: list[str] = []
        for _ in arguments:
            _temp_parms.append("?")
        parms_str: str = ",".join(_temp_parms)

        command: str = f"{base_cmd} {table}({args_str}) VALUES({parms_str})"

        await self.wait_func()
        async with self.database.cursor() as cursor:
            await cursor.execute(command, parameters)
        await self.database.commit()

    async def delete_where(
        self, table: str, search_key: str, parameters: typing.Any
    ) -> None:
        """Delete from the table in the search_key"""
        base_cmd: str = "DELETE FROM"
        pars_cmd: str = f"WHERE {search_key}=?"
        command: str = f"{base_cmd} {table} {pars_cmd}"
        parms: tuple = (parameters,)
        await self.wait_func()
        async with self.database.cursor() as cursor:
            await cursor.execute(command, parms)
        await self.database.commit()

    async def fetch(
        self, table: str, search_key: str = "", parameters: typing.Any = None
    ) -> list[tuple[typing.Any]]:
        """Fetch data from the database"""

        base_cmd: str = "SELECT * FROM"
        parms: tuple | None = None
        if search_key != "":
            pars_cmd: str = f"WHERE {search_key}=?"
        else:
            pars_cmd: str = ""
        command: str = f"{base_cmd} {table} {pars_cmd}"

        if parameters is not None:
            parms = (parameters,)
        else:
            parms = None

        await self.wait_func()
        async with self.database.cursor() as cursor:
            await cursor.execute(command, parms)
            return await cursor.fetchall()

    async def lock_state_func(
        self, roles: list, channels: list, curr_unix_time: int
    ) -> None:
        """."""
        base_command: str = "INSERT OR IGNORE INTO lock_state(role_id, channel_id, permissions_bin, unix_date) VALUES(?,?,?,?)"
        await self.wait_func()
        async with self.database.cursor() as cursor:
            await cursor.execute("DELETE FROM lock_state")
            for role in roles:
                for channel in channels:
                    permissions = channel.permissions_for(role)
                    await cursor.execute(
                        base_command,
                        (
                            int(role.id),
                            int(channel.id),
                            int(permissions.value),
                            curr_unix_time,
                        ),
                    )

        await self.database.commit()

    async def clear_table(self, table: str) -> None:
        await self.wait_func()
        async with self.database.cursor() as cursor:
            await cursor.execute(f"DELETE FROM {table}")
        await self.database.commit()
