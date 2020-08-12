import async
import enum
import subprocess
import logging
import collections
import threading

import chess.engine


LOGGER = logging.getLogger(__name__)


class EngineError(Exception):
    pass

class EngineTerminatedError(EngineError):
    pass

class EngineStateError(EngineError):
    pass


class UciProtocol(asyncio.SubprocessProtocol):
    def __init__(self, *, loop=None):
        self.loop = asyncio.get_event_loop() if loop is None else loop

        self.lock = UniqueLock()
        self.busy = False

        self.stdout_buffer = bytearray()
        self.stderr_buffer = bytearray()

        self.id = {}
        self.option = chess.engine.OptionMap()

        self.returncode = self.loop.create_future()

        self.readyok = RendezvousChannel("readyok", loop=self.loop)
        self.uciok = RendezvousChannel("uciok", loop=self.loop)
        self.bestmove = RendezvousChannel("bestmove", loop=self.loop)

    def connection_made(self, transport):
        self.transport = transport
        LOGGER.debug("%s: Connection made", self)

    def connection_lost(self, exc):
        code = self.transport.get_returncode()
        LOGGER.debug("%s: Connection lost (exit code: %d, error: %s)", self, code, exc)

        # Terminate waiters.
        if exc is None:
            exc = EngineTerminatedError("engine process dead (exit code: {})".format(code))
        self.readyok.set_exception(exc)
        self.uciok.set_exception(exc)

        self.returncode.set_result(code)

    def process_exited(self):
        LOGGER.debug("%s: Process exited", self)

    def pipe_data_received(self, fd, data):
        if fd == 1:
            self.stdout_buffer.extend(data)

            while b"\n" in self.stdout_buffer:
                line, self.stdout_buffer = self.stdout_buffer.split(b"\n", 1)
                self.line_received(line.decode("utf-8"))
        elif fd == 2:
            self.stderr_buffer.extend(data)

            while b"\n" in self.stderr_buffer:
                line, self.stderr_buffer = self.stderr_buffer.split(b"\n", 1)
                self.error_line_received(line.decode("utf-8"))

    def pipe_connection_lost(self, fd, exc):
        LOGGER.debug("%s: Pipe connection lost (fd: %d, error: %s)", self, fd, exc)

    def error_line_received(self, line):
        LOGGER.warn("%s: stderr >> %s", self, line)

    def line_received(self, line):
        LOGGER.debug("%s: >> %s", self, line)

        command_and_args = line.split(" ", 1)

        if command_and_args[0] == "readyok":
            self.readyok.notify()
        elif command_and_args[0] == "uciok":
            self.uciok.notify()

        if len(command_and_args) >= 2:
            if command_and_args[0] == "id":
                self._id(command_and_args[1])

    def _id(self, args):
        property_and_arg = args.split(" ", 1)
        if len(property_and_arg) >= 2:
            self.id[property_and_arg[0]] = property_and_arg[1]

    def send_line(self, line):
        LOGGER.debug("%s: << %s", self, line)
        stdin = self.transport.get_pipe_transport(0)
        stdin.write(line.encode("utf-8"))
        stdin.write(b"\n")

    async def isready(self):
        with self.lock:
            self.send_line("isready")
            await self.readyok.wait()

    async def uci(self):
        with self.lock:
            self.send_line("uci")
            await self.uciok.wait()

    def debug(self, on=True):
        with self.lock:
            self.send_line("debug on" if on else "debug off")

    async def quit(self):
        with self.lock:
            self.send_line("quit")
            await self.returncode

    def setoption(name, value):
        with self.lock:
            if self.busy:
                raise EngineStateError("setoption while engine is busy")

            builder = ["setoption name", name, "value"]
            if value is True:
                builder.append("true")
            elif value is False:
                builder.append("false")
            elif value is None:
                builder.append("none")
            else:
                builder.append(str(value))

            self.send_line(" ".join(builder))

    def ucinewgame(self):
        with self.lock:
            if self.busy:
                raise EngineStateError("ucinewgame while engine is busy")

            self.send_line("ucinewgame")

    def go(self):
        with self.lock:
            if self.busy:
                raise EngineStateError("go while engine is busy")

            self.busy = True


    def __repr__(self):
        return "<{} at {} (pid={})>".format(type(self).__name__, hex(id(self)), self.transport.get_pid())


class UniqueLock:
    def __init__(self):
        self.lock = threading.Lock()

    def acquire(self):
        if not self.lock.acquire(False):
            raise RuntimeError("engine already in use")

    def release(self):
        self.lock.release()

    def __enter__(self):
        self.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


class RendezvousChannel:
    def __init__(self, name, *, loop=None):
        self.name = name
        self.loop = asyncio.get_event_loop() if loop is None else loop
        self.future = None
        self.cancelled = 0
        self.exception = None

    def notify(self, message=()):
        if self.cancelled > 0:
            self.cancelled -= 1
        elif self.future is not None and not self.future.done():
            self.future.set_result(message)

    def set_exception(self, exc):
        self.exception = exc
        if self.future is not None and not self.future.done():
            self.future.set_exception(exc)

    async def wait(self):
        if self.future is not None and self.future.cancelled():
            self.cancelled += 1

        if self.future is not None and self.future.done():
            self.future = None

        if self.future is not None:
            raise RuntimeError("multiple callers waiting for {}".format(self.name))

        self.future = self.loop.create_future()
        if self.exception is not None:
            self.future.set_exception(self.exception)

        return await self.future


async def main(loop):
    transport, protocol = await loop.subprocess_exec(UciProtocol, "stockfish")

    await protocol.uci()
    await protocol.uci()
    print(protocol.id)

    #await asyncio.gather(protocol.isready(), protocol.isready())

    try:
        await asyncio.wait_for(protocol.isready(), 5)
    except asyncio.TimeoutError:
        print("timeout")
    except EngineTerminatedError:
        print("engine died before timeout")


    code = await protocol.quit()
    print("quit with code:", code)

    try:
        await protocol.isready()
    except EngineTerminatedError:
        print("engine terminated unexpectedly")

    await asyncio.wait_for(protocol.returncode, timeout=None)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
