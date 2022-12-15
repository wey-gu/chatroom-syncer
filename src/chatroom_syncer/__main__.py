from .room_syncer import main

import asyncio

if __name__ == '__main__':
    """
    Main function to be called with python3 -m chatroom-syncer
    """
    asyncio.run(main())
