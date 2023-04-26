import asyncio
import sys
import time

sys.path.append("/api")

from parsing.parsers.start_semester_parser import start_parse

if __name__ == '__main__':
    _ = time.time()

    loop = asyncio.get_event_loop()
    try:
        print("--Parse date--")
        loop.run_until_complete(start_parse())
        print("--Parsing completed--")
    except Exception as err:
        print(f"Error: {err}")
        loop.stop()
    finally:
        loop.close()

    print(time.time() - _)
